import pygame
import random
import socket
from src.settings import *
from src.road.road import Road
from src.cars.player import Player
from src.cars.obstacle import ObstacleCar
from src.coins.coin import Coin
from src.score.score_manager import ScoreManager
from src.ui.ui_manager import UIManager
from src.audio.audio_manager import AudioManager
from src.network import PacketType, HostServer, ClientPeer

MIN_OBSTACLE_GAP = 300


class GameMode:
    SINGLEPLAYER = 0
    HOST = 1
    CLIENT = 2


class GameState:
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    ENTERING_NAME = 3
    PAUSED = 4
    MP_CLIENT_SETUP = 5
    MP_WAITING = 6
    MP_RESULT = 7
    SKIN_SELECT = 8
    LOOTBOX_SHOP = 9
    PAYWALL = 10


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("F1 TURBO")
        self.clock = pygame.time.Clock()
        self.running = True

        self.score_manager = ScoreManager()
        self.ui_manager = UIManager()
        self.audio = AudioManager()

        self.state = GameState.MENU
        self.mode = GameMode.SINGLEPLAYER
        self.player_name = ""

        self.road = None
        self.player = None
        self.players = []
        self.obstacles = []
        self.coins_on_road = []

        self.current_speed = INITIAL_SCROLL_SPEED
        self.obstacle_spawn_rate = 8
        self.last_difficulty_score = 0

        self.network = None
        self.network_seed = None
        self.local_player_index = 0
        self.remote_input = {"left": False, "right": False, "up": False, "down": False, "frame": 0}
        self.local_input = {"left": False, "right": False, "up": False, "down": False, "frame": 0}
        self.frame_count = 0
        self.join_ip = ""
        self.connection_message = ""
        self.multiplayer_result_text = ""
        self.connection_lost = False
        self.local_crashed = False
        self.remote_crashed = False
        self.multiplayer_crash_sent = False
        self.host_setup_sent = False

        self.selected_skin_index = 0
        self.lootbox_result = None
        self.paywall_message = None

    def get_local_ip(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip.startswith("127."):
                raise ValueError
            return local_ip
        except Exception:
            return "127.0.0.1"

    def get_selected_skin(self):
        unlocked = sorted(self.score_manager.unlocked_skins)
        if self.selected_skin_index not in unlocked:
            self.selected_skin_index = unlocked[0] if unlocked else 0
        return CAR_SKINS[self.selected_skin_index]

    def reset_game(self, seed=None, multiplayer=False):
        skin = self.get_selected_skin()
        if multiplayer:
            self.network_seed = seed if seed is not None else random.randint(0, 2**31 - 1)
            self.rng = random.Random(self.network_seed)
            self.road = Road(self.rng)
            self.players = [
                Player(WIDTH // 2, HEIGHT - 130, color=skin["body"], skin=skin),
                Player(WIDTH // 2, HEIGHT - 130, color=OBSTACLE_COLOR)
            ]
            self.player = self.players[self.local_player_index]
        else:
            self.rng = random.Random()
            self.road = Road(self.rng)
            self.player = Player(WIDTH // 2, HEIGHT - 130, color=skin["body"], skin=skin)
            self.players = [self.player]
        self.obstacles = []
        self.coins_on_road = []
        self.score_manager.reset_score()
        self.score_manager.reset_session_coins()
        self.current_speed = INITIAL_SCROLL_SPEED
        self.obstacle_spawn_rate = 8
        self.last_difficulty_score = 0
        self.player_name = ""
        self.frame_count = 0
        self.local_input = {"left": False, "right": False, "up": False, "down": False, "frame": 0}
        self.remote_input = {"left": False, "right": False, "up": False, "down": False, "frame": 0}
        self.local_crashed = False
        self.remote_crashed = False
        self.multiplayer_crash_sent = False
        self.audio.start_engine()

    def increase_difficulty(self):
        if self.current_speed < MAX_SCROLL_SPEED:
            self.current_speed += SPEED_INCREASE
        if self.obstacle_spawn_rate > 3:
            self.obstacle_spawn_rate -= OBSTACLE_SPAWN_INCREASE

    def update_difficulty(self):
        score = self.score_manager.get_current_score()
        if score >= self.last_difficulty_score + DIFFICULTY_INCREASE_INTERVAL:
            self.increase_difficulty()
            self.last_difficulty_score = score

    def spawn_obstacle(self):
        if self.obstacles:
            highest = min(o.y for o in self.obstacles)
            if highest > -MIN_OBSTACLE_GAP:
                return
        if self.rng.randint(0, self.obstacle_spawn_rate) == 0:
            new_obstacle = ObstacleCar(-OBSTACLE_HEIGHT)
            new_obstacle.offset = self.rng.randint(-ROAD_WIDTH // 3, ROAD_WIDTH // 3)
            self.obstacles.append(new_obstacle)

    def spawn_coin(self):
        if self.rng.randint(0, COIN_SPAWN_CHANCE) == 0:
            center = self.road.get_center_at(-50)
            offset = self.rng.randint(-ROAD_WIDTH // 3, ROAD_WIDTH // 3)
            self.coins_on_road.append(Coin(center + offset, -30))

    def update_obstacles(self):
        for o in self.obstacles:
            o.y += self.current_speed
        before = len(self.obstacles)
        self.obstacles = [o for o in self.obstacles if o.y < HEIGHT + 200]
        passed = before - len(self.obstacles)
        if passed > 0:
            self.score_manager.increment_score(passed * 10)

    def update_coins(self):
        for coin in self.coins_on_road:
            coin.update(self.current_speed)
        pr = pygame.Rect(self.player.x - PLAYER_WIDTH // 2, self.player.y, PLAYER_WIDTH, PLAYER_HEIGHT)
        collected = [c for c in self.coins_on_road if pr.colliderect(c.get_rect())]
        for c in collected:
            self.score_manager.add_coins(COIN_VALUE)
            self.coins_on_road.remove(c)
        self.coins_on_road = [c for c in self.coins_on_road if not c.is_offscreen()]

    def check_collisions(self, player):
        center_at_player = self.road.get_center_at(player.y + PLAYER_HEIGHT // 2)
        le = center_at_player - ROAD_WIDTH // 2
        re = center_at_player + ROAD_WIDTH // 2
        if player.x - PLAYER_WIDTH // 2 < le or player.x + PLAYER_WIDTH // 2 > re:
            return True
        pr = pygame.Rect(player.x - PLAYER_WIDTH // 2, player.y, PLAYER_WIDTH, PLAYER_HEIGHT)
        for o in self.obstacles:
            c = self.road.get_center_at(o.y + OBSTACLE_HEIGHT // 2) + o.offset
            orect = pygame.Rect(c - OBSTACLE_WIDTH // 2, o.y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
            if pr.colliderect(orect):
                return True
        return False

    def open_lootbox(self):
        if not self.score_manager.spend_coins(LOOTBOX_COST):
            return None
        skin_idx = random.randint(0, len(CAR_SKINS) - 1)
        skin = CAR_SKINS[skin_idx]
        is_new = self.score_manager.unlock_skin(skin_idx)
        if is_new:
            return {"skin_name": skin["name"], "skin_index": skin_idx, "is_new": True, "refund": 0}
        else:
            refund = int(LOOTBOX_COST * DUPLICATE_REFUND_PERCENT)
            self.score_manager.add_coins(refund)
            self.score_manager.session_coins -= refund
            return {"skin_name": skin["name"], "skin_index": skin_idx, "is_new": False, "refund": refund}

    # --- Input handlers ---
    def handle_menu_input(self, event, mouse_pos, mouse_clicked):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.audio.play_sfx('click')
            self.mode = GameMode.SINGLEPLAYER
            self.reset_game()
            self.state = GameState.PLAYING

    def handle_join_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and len(self.join_ip) > 0:
                self.audio.play_sfx('click')
                self.network = ClientPeer(self.join_ip, MULTIPLAYER_PORT)
                self.network.connect()
                if self.network.is_connected():
                    self.connection_message = f"Pripojene na {self.join_ip}:{MULTIPLAYER_PORT}. Cakam..."
                    self.network.send_packet({"type": PacketType.HELLO, "role": "client"})
                    self.state = GameState.MP_WAITING
                else:
                    self.connection_message = "Nepodarilo sa pripojit."
            elif event.key == pygame.K_BACKSPACE:
                self.join_ip = self.join_ip[:-1]
            elif len(self.join_ip) < 22:
                if event.unicode.isdigit() or event.unicode == '.' or event.unicode == ':':
                    self.join_ip += event.unicode

    def handle_playing_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = GameState.PAUSED

    def handle_paused_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.audio.play_sfx('click'); self.state = GameState.PLAYING
            elif event.key == pygame.K_q:
                self.audio.stop_engine(); self.cleanup_network(); self.state = GameState.MENU

    def handle_game_over_input(self, event, mouse_pos, mouse_clicked):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                score = self.score_manager.get_current_score()
                if self.score_manager.is_highscore(score):
                    self.audio.play_sfx('highscore'); self.state = GameState.ENTERING_NAME
                else:
                    self.audio.play_sfx('click'); self.state = GameState.MENU
            elif event.key == pygame.K_ESCAPE:
                self.audio.play_sfx('click'); self.state = GameState.MENU

    def handle_multiplayer_result_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: self.request_rematch()
            elif event.key == pygame.K_ESCAPE: self.cleanup_network(); self.state = GameState.MENU

    def handle_name_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.player_name) > 0:
                self.audio.play_sfx('click')
                self.score_manager.add_score(self.player_name, self.score_manager.get_current_score())
                self.state = GameState.MENU
            elif event.key == pygame.K_BACKSPACE:
                if len(self.player_name) > 0: self.audio.play_sfx('click')
                self.player_name = self.player_name[:-1]
            elif len(self.player_name) < 15:
                if event.unicode.isalnum() or event.unicode == ' ':
                    self.audio.play_sfx('click'); self.player_name += event.unicode

    def handle_skin_input(self, event):
        if event.type == pygame.KEYDOWN:
            ul = sorted(self.score_manager.unlocked_skins) or [0]
            cp = 0
            for i, idx in enumerate(ul):
                if idx == self.selected_skin_index: cp = i; break
            if event.key == pygame.K_LEFT:
                self.audio.play_sfx('click'); cp = (cp-1)%len(ul); self.selected_skin_index = ul[cp]
            elif event.key == pygame.K_RIGHT:
                self.audio.play_sfx('click'); cp = (cp+1)%len(ul); self.selected_skin_index = ul[cp]
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.audio.play_sfx('click'); self.state = GameState.MENU

    def handle_lootbox_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.audio.play_sfx('click'); self.lootbox_result = None; self.state = GameState.MENU
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.lootbox_result:
                    self.audio.play_sfx('click'); self.lootbox_result = None
                elif self.score_manager.coins >= LOOTBOX_COST:
                    self.audio.play_sfx('click'); self.lootbox_result = self.open_lootbox()

    def handle_paywall_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.audio.play_sfx('click'); self.paywall_message = None; self.state = GameState.LOOTBOX_SHOP

    # --- Multiplayer ---
    def start_host_session(self):
        self.mode = GameMode.HOST; self.local_player_index = 0
        self.network = HostServer(port=MULTIPLAYER_PORT); self.network.start()
        self.connection_message = f"Cakam na hraca...\nIP: {self.get_local_ip()}:{MULTIPLAYER_PORT}"
        self.state = GameState.MP_WAITING
        self.reset_game(seed=random.randint(0, 2**31-1), multiplayer=True); self.host_setup_sent = False

    def send_setup(self):
        if self.network and self.mode == GameMode.HOST and self.network.is_connected():
            self.network.send_packet({"type": PacketType.SETUP, "seed": self.network_seed}); self.host_setup_sent = True

    def send_start(self):
        if self.network and self.network.is_connected():
            self.network.send_packet({"type": PacketType.START})

    def send_input(self, left, right, up=False, down=False):
        if self.network and self.network.is_connected():
            self.network.send_packet({"type": PacketType.INPUT, "frame": self.frame_count, "player": self.local_player_index, "left": left, "right": right, "up": up, "down": down})

    def send_crash(self, pi):
        if self.network and self.network.is_connected() and not self.multiplayer_crash_sent:
            self.network.send_packet({"type": PacketType.CRASH, "player": pi, "frame": self.frame_count}); self.multiplayer_crash_sent = True

    def send_result(self, outcome):
        if self.network and self.network.is_connected():
            self.network.send_packet({"type": PacketType.RESULT, "outcome": outcome})

    def send_rematch_response(self):
        if self.network and self.network.is_connected():
            self.network.send_packet({"type": PacketType.REMATCH_RESPONSE})

    def request_rematch(self):
        if self.network and self.network.is_connected():
            self.network.send_packet({"type": PacketType.REMATCH_REQUEST})
            self.connection_message = "Ziadost odoslana. Cakam..."; self.state = GameState.MP_WAITING

    def cleanup_network(self):
        if self.network:
            try: self.network.send_packet({"type": PacketType.DISCONNECT})
            except: pass
            self.network.stop()
        self.network = None; self.connection_message = ""; self.connection_lost = False

    def process_network_messages(self):
        if not self.network: return
        for packet in self.network.get_packets():
            if not isinstance(packet, dict) or "type" not in packet: continue
            (self.handle_host_packet if self.mode == GameMode.HOST else self.handle_client_packet)(packet)

    def handle_host_packet(self, packet):
        pt = packet["type"]
        if pt == PacketType.HELLO:
            self.connection_message = "Hrac sa pripojil. Cakam na READY..."
            if not self.host_setup_sent: self.send_setup()
        elif pt == PacketType.READY:
            self.connection_message = "Hrac je pripraveny. Startujem..."
            self.send_start(); self.state = GameState.PLAYING; self.frame_count = 0
        elif pt == PacketType.INPUT:
            if packet.get("player") == 1:
                for k in ["left","right","up","down"]: self.remote_input[k] = packet.get(k, False)
                self.remote_input["frame"] = packet.get("frame", self.frame_count)
        elif pt == PacketType.CRASH:
            self.remote_crashed = True
            if self.local_crashed and packet.get("frame") == self.frame_count:
                self.multiplayer_result_text = "DRAW"; self.send_result("DRAW"); self.state = GameState.MP_RESULT
            elif not self.local_crashed:
                self.multiplayer_result_text = "WIN"; self.send_result("WIN"); self.state = GameState.MP_RESULT
        elif pt == PacketType.REMATCH_REQUEST:
            if self.state == GameState.MP_RESULT:
                self.send_rematch_response(); self.network_seed = random.randint(0, 2**31-1)
                self.reset_game(seed=self.network_seed, multiplayer=True); self.host_setup_sent = False
                self.state = GameState.MP_WAITING; self.send_setup()
        elif pt == PacketType.DISCONNECT:
            self.connection_lost = True; self.connection_message = "Spojenie prerusene."
            self.multiplayer_result_text = "CONNECTION LOST"; self.state = GameState.MP_RESULT

    def handle_client_packet(self, packet):
        pt = packet["type"]
        if pt == PacketType.SETUP:
            self.network_seed = packet.get("seed"); self.local_player_index = 1
            self.reset_game(seed=self.network_seed, multiplayer=True)
            self.player = self.players[self.local_player_index]
            self.network.send_packet({"type": PacketType.READY})
            self.connection_message = "Nastavenie hotove. Cakam na start..."; self.state = GameState.MP_WAITING
        elif pt == PacketType.START:
            self.state = GameState.PLAYING; self.frame_count = 0
        elif pt == PacketType.INPUT:
            if packet.get("player") == 0:
                for k in ["left","right","up","down"]: self.remote_input[k] = packet.get(k, False)
                self.remote_input["frame"] = packet.get("frame", self.frame_count)
        elif pt == PacketType.RESULT:
            self.multiplayer_result_text = packet.get("outcome", "LOSE"); self.state = GameState.MP_RESULT
        elif pt == PacketType.REMATCH_RESPONSE:
            self.connection_message = "Rematch akceptovany. Cakam..."; self.state = GameState.MP_WAITING
        elif pt == PacketType.DISCONNECT:
            self.connection_lost = True; self.multiplayer_result_text = "CONNECTION LOST"; self.state = GameState.MP_RESULT

    # --- Update ---
    def update_singleplayer(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.road.update(self.current_speed)
        self.spawn_obstacle(); self.spawn_coin()
        self.update_obstacles(); self.update_coins(); self.update_difficulty()
        self.audio.update_engine_pitch(self.current_speed)
        self.score_manager.increment_score(self.current_speed / 100)
        if self.check_collisions(self.player):
            self.audio.stop_engine(); self.audio.play_sfx('crash'); self.state = GameState.GAME_OVER

    def update_multiplayer(self):
        if not self.network or not self.network.is_connected(): return
        keys = pygame.key.get_pressed()
        left, right, up, down = keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]
        self.local_input.update({"left": left, "right": right, "up": up, "down": down, "frame": self.frame_count})
        self.send_input(left, right, up, down)
        self.players[self.local_player_index].update(left=left, right=right, up=up, down=down)
        ri = 1 - self.local_player_index
        self.players[ri].update(left=self.remote_input["left"], right=self.remote_input["right"],
                                up=self.remote_input.get("up", False), down=self.remote_input.get("down", False))
        self.road.update(self.current_speed); self.spawn_obstacle(); self.update_obstacles(); self.update_difficulty()
        self.audio.update_engine_pitch(self.current_speed)
        self.score_manager.increment_score(self.current_speed / 100)
        if self.check_collisions(self.players[self.local_player_index]):
            if not self.local_crashed:
                self.local_crashed = True; self.send_crash(self.local_player_index)
                if self.mode == GameMode.CLIENT:
                    self.connection_message = "Krach. Cakam na vysledok..."; self.state = GameState.MP_WAITING
                elif self.mode == GameMode.HOST and not self.remote_crashed:
                    self.multiplayer_result_text = "LOSE"; self.send_result("LOSE"); self.state = GameState.MP_RESULT
        if self.mode == GameMode.HOST and self.remote_crashed and self.state != GameState.MP_RESULT:
            self.multiplayer_result_text = "WIN"; self.send_result("WIN"); self.state = GameState.MP_RESULT
        self.frame_count += 1

    # --- Draw ---
    def draw_game(self):
        self.screen.fill(GRASS_COLOR)
        self.road.draw(self.screen)
        for coin in self.coins_on_road: coin.draw(self.screen)
        for o in self.obstacles:
            c = self.road.get_center_at(o.y + OBSTACLE_HEIGHT // 2) + o.offset
            o.draw(self.screen, c)
        if self.mode == GameMode.SINGLEPLAYER: self.player.draw(self.screen)
        else:
            for p in self.players: p.draw(self.screen)
        self.ui_manager.draw_hud(self.screen, int(self.score_manager.get_current_score()), self.current_speed,
                                 self.audio, self.score_manager.session_coins)

    def draw_pause_screen(self):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((10,10,15,200)); self.screen.blit(ov, (0,0))
        pr = pygame.Rect(WIDTH//2-250, HEIGHT//2-150, 500, 300)
        self.ui_manager.draw_glass_panel(self.screen, pr, 255)
        self.ui_manager.draw_text(self.screen, "PAUZA", self.ui_manager.font_large, UI_GOLD, WIDTH//2, pr.y+80, center=True)
        self.ui_manager.draw_text(self.screen, "ESC - Pokracovat", self.ui_manager.font_medium, UI_TEXT_MAIN, WIDTH//2, pr.y+160, center=True)
        self.ui_manager.draw_text(self.screen, "Q - Spat do menu", self.ui_manager.font_medium, UI_TEXT_DIM, WIDTH//2, pr.y+210, center=True)

    def draw_multiplayer_status(self):
        self.ui_manager.draw_connection_status(self.screen, "Multiplayer", self.connection_message)

    def draw_multiplayer_result(self):
        r = self.multiplayer_result_text
        c = {"WIN": "VYHRAL SI", "LOSE": "PREHRAL SI", "DRAW": "REMIZA"}.get(r, r)
        self.ui_manager.draw_multiplayer_result(self.screen, c)

    # --- Main Loop ---
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m: self.audio.toggle_mute()
                    elif event.key == pygame.K_PLUS:
                        if self.audio.muted: self.audio.toggle_mute()
                        self.audio.change_volume(0.1)
                    elif event.key == pygame.K_MINUS:
                        self.audio.change_volume(-0.1)
                        if self.audio.engine_volume <= 0.01 and not self.audio.muted: self.audio.toggle_mute()
                if event.type == pygame.MOUSEBUTTONDOWN: mouse_clicked = True

                if self.state == GameState.MENU: self.handle_menu_input(event, mouse_pos, mouse_clicked)
                elif self.state == GameState.MP_CLIENT_SETUP: self.handle_join_input(event)
                elif self.state == GameState.PLAYING: self.handle_playing_input(event)
                elif self.state == GameState.PAUSED: self.handle_paused_input(event)
                elif self.state == GameState.MP_RESULT: self.handle_multiplayer_result_input(event)
                elif self.state == GameState.GAME_OVER: self.handle_game_over_input(event, mouse_pos, mouse_clicked)
                elif self.state == GameState.ENTERING_NAME: self.handle_name_input(event)
                elif self.state == GameState.SKIN_SELECT: self.handle_skin_input(event)
                elif self.state == GameState.LOOTBOX_SHOP: self.handle_lootbox_input(event)
                elif self.state == GameState.PAYWALL: self.handle_paywall_input(event)

            self.process_network_messages()

            if self.state == GameState.MENU:
                action = self.ui_manager.draw_menu(self.screen, self.score_manager.get_highscores(),
                                                   self.score_manager.coins, mouse_pos, mouse_clicked)
                if action == "single":
                    self.audio.play_sfx('click'); self.mode = GameMode.SINGLEPLAYER
                    self.reset_game(); self.state = GameState.PLAYING
                elif action == "skins":
                    self.audio.play_sfx('click'); self.state = GameState.SKIN_SELECT
                elif action == "lootbox":
                    self.audio.play_sfx('click'); self.lootbox_result = None; self.state = GameState.LOOTBOX_SHOP
                elif action == "host":
                    self.audio.play_sfx('click'); self.start_host_session()
                elif action == "join":
                    self.audio.play_sfx('click'); self.mode = GameMode.CLIENT
                    self.join_ip = ""; self.state = GameState.MP_CLIENT_SETUP

            elif self.state == GameState.SKIN_SELECT:
                action = self.ui_manager.draw_skin_selector(self.screen, self.selected_skin_index,
                    self.score_manager.unlocked_skins, mouse_pos, mouse_clicked)
                ul = sorted(self.score_manager.unlocked_skins) or [0]
                cp = 0
                for i, idx in enumerate(ul):
                    if idx == self.selected_skin_index: cp = i; break
                if action == "prev":
                    self.audio.play_sfx('click'); cp = (cp-1)%len(ul); self.selected_skin_index = ul[cp]
                elif action == "next":
                    self.audio.play_sfx('click'); cp = (cp+1)%len(ul); self.selected_skin_index = ul[cp]
                elif action in ("select", "back"):
                    self.audio.play_sfx('click'); self.state = GameState.MENU

            elif self.state == GameState.LOOTBOX_SHOP:
                action = self.ui_manager.draw_lootbox_shop(self.screen, self.score_manager.coins,
                    len(self.score_manager.unlocked_skins), len(CAR_SKINS),
                    mouse_pos, mouse_clicked, self.lootbox_result)
                if action == "buy":
                    self.audio.play_sfx('click'); self.lootbox_result = self.open_lootbox()
                elif action == "paywall":
                    self.audio.play_sfx('click'); self.paywall_message = None; self.state = GameState.PAYWALL
                elif action == "back":
                    self.audio.play_sfx('click'); self.lootbox_result = None; self.state = GameState.MENU
                if self.lootbox_result and mouse_clicked:
                    self.audio.play_sfx('click'); self.lootbox_result = None

            elif self.state == GameState.PAYWALL:
                action = self.ui_manager.draw_paywall(self.screen, self.score_manager.coins, mouse_pos, mouse_clicked)
                if action == "close":
                    self.audio.play_sfx('click'); self.paywall_message = None; self.state = GameState.LOOTBOX_SHOP
                elif action and action.startswith("pkg_"):
                    # Fake purchase - show message
                    self.audio.play_sfx('click')
                    self.paywall_message = True

                # If message showing, any click dismisses back to shop
                if self.paywall_message and mouse_clicked:
                    self.paywall_message = None; self.state = GameState.LOOTBOX_SHOP

            elif self.state == GameState.MP_CLIENT_SETUP:
                self.screen.fill(GRASS_COLOR)
                action = self.ui_manager.draw_multiplayer_setup(self.screen, "JOIN GAME",
                    "Zadaj IP hostitela a stlac ENTER:", self.join_ip, mouse_pos, mouse_clicked)
                if action == "join" and len(self.join_ip) > 0:
                    self.audio.play_sfx('click')
                    self.network = ClientPeer(self.join_ip, MULTIPLAYER_PORT); self.network.connect()
                    if self.network.is_connected():
                        self.connection_message = f"Pripojene na {self.join_ip}:{MULTIPLAYER_PORT}. Cakam..."
                        self.network.send_packet({"type": PacketType.HELLO, "role": "client"})
                        self.state = GameState.MP_WAITING
                    else:
                        self.connection_message = "Nepodarilo sa pripojit."
                elif action == "back":
                    self.state = GameState.MENU

            elif self.state == GameState.MP_WAITING:
                self.screen.fill(GRASS_COLOR); self.draw_multiplayer_status()
            elif self.state == GameState.PLAYING:
                if self.mode == GameMode.SINGLEPLAYER: self.update_singleplayer()
                else: self.update_multiplayer()
                self.draw_game()
            elif self.state == GameState.PAUSED:
                self.draw_game(); self.draw_pause_screen()
            elif self.state == GameState.GAME_OVER:
                self.draw_game()
                score = self.score_manager.get_current_score()
                if self.ui_manager.draw_game_over_screen(self.screen, int(score),
                        self.score_manager.is_highscore(score), self.score_manager.session_coins, mouse_pos, mouse_clicked):
                    self.audio.play_sfx('click'); self.state = GameState.MENU
            elif self.state == GameState.ENTERING_NAME:
                self.draw_game()
                self.ui_manager.draw_game_over_screen(self.screen, int(self.score_manager.get_current_score()), True,
                                                      self.score_manager.session_coins, mouse_pos, False)
                self.ui_manager.draw_name_input(self.screen, self.player_name)
            elif self.state == GameState.MP_RESULT:
                self.draw_game(); self.draw_multiplayer_result()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_TAB]:
                self.ui_manager.draw_leaderboard(self.screen, self.score_manager.get_highscores())

            pygame.display.flip()

        self.cleanup_network()
        pygame.quit()

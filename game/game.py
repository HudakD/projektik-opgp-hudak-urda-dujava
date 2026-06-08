import pygame
import random
import socket
import math
import time
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
    COLLECTION = 11
    EFFECTS_SHOP = 12
    EQUIP_EFFECTS = 13
    MP_HOST_SETUP = 14
    MP_LOBBY = 15
    MP_COUNTDOWN = 16
    MP_LEADERBOARD = 17


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
        self.player_inputs = {}
        self.local_input = {"left": False, "right": False, "up": False, "down": False, "frame": 0}
        self.frame_count = 0
        self.join_ip = ""
        self.join_name = ""
        self.join_active_field = "ip"
        self.host_name = ""
        self.host_player_count = MIN_MULTIPLAYER_PLAYERS
        self.chat_input = ""
        self.chat_active = False
        self.chat_messages = []
        self.lobby_players = []
        self.target_player_count = MIN_MULTIPLAYER_PLAYERS
        self.client_player_map = {}
        self.connection_message = ""
        self.multiplayer_result_text = ""
        self.connection_lost = False
        self.player_crashed = {}
        self.survival_stats = {}
        self.multiplayer_leaderboard = []
        self.multiplayer_round_active = False
        self.round_start_time = 0
        self.countdown_started_at = 0
        self.countdown_value = MULTIPLAYER_COUNTDOWN_SECONDS
        self.last_countdown_value = None
        self.leaderboard_started_at = 0
        self.last_state_broadcast_frame = -1
        self.local_crashed = False
        self.remote_crashed = False
        self.multiplayer_crash_sent = False
        self.host_setup_sent = False

        self.selected_skin_index = 0
        self.lootbox_result = None
        self.paywall_message = None
        self.effect_box_result = None
        self.effect_equip_category = 0
        self.effect_particles = []
        self.effect_trails = []
        self.effect_frame = 0

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

    def sanitize_player_name(self, name, fallback="Player"):
        clean = "".join(ch for ch in name.strip() if ch.isalnum() or ch in (" ", "_", "-"))
        clean = " ".join(clean.split())
        return (clean[:16] or fallback)

    def get_start_position(self, index, total):
        usable_width = ROAD_WIDTH - PLAYER_WIDTH - 40
        if total <= 1:
            x = WIDTH // 2
        else:
            x = WIDTH // 2 - usable_width // 2 + int(usable_width * index / (total - 1))
        y = HEIGHT - 130 - (index % 2) * 58
        return x, y

    def get_skin_by_index(self, skin_index):
        if isinstance(skin_index, int) and 0 <= skin_index < len(CAR_SKINS):
            return CAR_SKINS[skin_index]
        return CAR_SKINS[0]

    def reset_game(self, seed=None, multiplayer=False, players_info=None):
        skin = self.get_selected_skin()
        if multiplayer:
            self.network_seed = seed if seed is not None else random.randint(0, 2**31 - 1)
            self.rng = random.Random(self.network_seed)
            self.road = Road(self.rng)
            roster = sorted(players_info or self.lobby_players, key=lambda p: p.get("index", 0))
            total = max(1, len(roster))
            self.players = []
            for i, info in enumerate(roster):
                start_x, start_y = self.get_start_position(i, total)
                car_skin = self.get_skin_by_index(info.get("skin_index", 0))
                self.players.append(Player(start_x, start_y, color=car_skin["body"], skin=car_skin))
            if 0 <= self.local_player_index < len(self.players):
                self.player = self.players[self.local_player_index]
            elif self.players:
                self.local_player_index = 0
                self.player = self.players[0]
            else:
                self.player = None
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
        self.player_inputs = {
            i: {"left": False, "right": False, "up": False, "down": False, "frame": 0}
            for i in range(len(self.players))
        }
        self.player_crashed = {i: False for i in range(len(self.players))}
        self.survival_stats = {
            i: {"duration": 0.0, "crashed": False, "place": None}
            for i in range(len(self.players))
        }
        self.local_crashed = False
        self.remote_crashed = False
        self.multiplayer_round_active = multiplayer
        self.multiplayer_crash_sent = False
        self.audio.start_engine()
        self.effect_particles = []
        self.effect_trails = []
        self.effect_frame = 0

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

        sm = self.score_manager
        sm.pity_epic += 1
        sm.pity_legendary += 1

        if sm.pity_legendary >= PITY_LEGENDARY_THRESHOLD:
            target_rarity = RARITY_LEGENDARY
        elif sm.pity_epic >= PITY_EPIC_THRESHOLD:
            if random.randint(1, 100) <= 20:
                target_rarity = RARITY_LEGENDARY
            else:
                target_rarity = RARITY_EPIC
        else:
            roll = random.randint(1, 100)
            cumulative = 0
            target_rarity = RARITY_COMMON
            for rarity, weight in RARITY_WEIGHTS.items():
                cumulative += weight
                if roll <= cumulative:
                    target_rarity = rarity
                    break

        candidates = [i for i, s in enumerate(CAR_SKINS) if s.get("rarity") == target_rarity]
        if not candidates:
            candidates = list(range(len(CAR_SKINS)))
        skin_idx = random.choice(candidates)
        skin = CAR_SKINS[skin_idx]
        actual_rarity = skin.get("rarity", RARITY_COMMON)

        if actual_rarity == RARITY_LEGENDARY:
            sm.pity_legendary = 0
            sm.pity_epic = 0
        elif actual_rarity in (RARITY_EPIC,):
            sm.pity_epic = 0
        sm.save_pity()

        is_new = sm.unlock_skin(skin_idx)
        if is_new:
            return {"skin_name": skin["name"], "skin_index": skin_idx, "is_new": True,
                    "refund": 0, "rarity": actual_rarity,
                    "pity_epic": sm.pity_epic, "pity_legendary": sm.pity_legendary}
        else:
            refund = RARITY_REFUND.get(actual_rarity, 50)
            sm.add_coins(refund)
            sm.session_coins -= refund
            return {"skin_name": skin["name"], "skin_index": skin_idx, "is_new": False,
                    "refund": refund, "rarity": actual_rarity,
                    "pity_epic": sm.pity_epic, "pity_legendary": sm.pity_legendary}

    def open_effect_box(self):
        if not self.score_manager.spend_coins(EFFECT_BOX_COST):
            return None

        sm = self.score_manager
        sm.pity_epic += 1
        sm.pity_legendary += 1

        if sm.pity_legendary >= PITY_LEGENDARY_THRESHOLD:
            target_rarity = RARITY_LEGENDARY
        elif sm.pity_epic >= PITY_EPIC_THRESHOLD:
            if random.randint(1, 100) <= 20:
                target_rarity = RARITY_LEGENDARY
            else:
                target_rarity = RARITY_EPIC
        else:
            roll = random.randint(1, 100)
            cumulative = 0
            target_rarity = RARITY_COMMON
            for rarity, weight in RARITY_WEIGHTS.items():
                cumulative += weight
                if roll <= cumulative:
                    target_rarity = rarity
                    break

        candidates = [i for i, e in enumerate(EFFECTS) if e.get("rarity") == target_rarity]
        if not candidates:
            candidates = list(range(len(EFFECTS)))
        effect_idx = random.choice(candidates)
        effect = EFFECTS[effect_idx]
        actual_rarity = effect.get("rarity", RARITY_COMMON)

        if actual_rarity == RARITY_LEGENDARY:
            sm.pity_legendary = 0
            sm.pity_epic = 0
        elif actual_rarity in (RARITY_EPIC,):
            sm.pity_epic = 0
        sm.save_pity()

        is_new = sm.unlock_effect(effect_idx)
        if is_new:
            return {"effect_name": effect["name"], "effect_index": effect_idx,
                    "effect_type": effect["type"], "color": effect["color"],
                    "is_new": True, "refund": 0, "rarity": actual_rarity,
                    "pity_epic": sm.pity_epic, "pity_legendary": sm.pity_legendary}
        else:
            refund = RARITY_REFUND.get(actual_rarity, 50)
            sm.add_coins(refund)
            sm.session_coins -= refund
            return {"effect_name": effect["name"], "effect_index": effect_idx,
                    "effect_type": effect["type"], "color": effect["color"],
                    "is_new": False, "refund": refund, "rarity": actual_rarity,
                    "pity_epic": sm.pity_epic, "pity_legendary": sm.pity_legendary}

    # --- Input handlers ---
    def handle_menu_input(self, event, mouse_pos, mouse_clicked):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.audio.play_sfx('click')
            self.mode = GameMode.SINGLEPLAYER
            self.reset_game()
            self.state = GameState.PLAYING

    def handle_host_setup_input(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.start_host_session()
        elif event.key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        elif event.key == pygame.K_LEFT:
            self.host_player_count = max(MIN_MULTIPLAYER_PLAYERS, self.host_player_count - 1)
        elif event.key == pygame.K_RIGHT:
            self.host_player_count = min(MAX_MULTIPLAYER_PLAYERS, self.host_player_count + 1)
        elif event.key == pygame.K_BACKSPACE:
            self.host_name = self.host_name[:-1]
        elif len(self.host_name) < 16 and (event.unicode.isalnum() or event.unicode in (" ", "_", "-")):
            self.host_name += event.unicode

    def handle_join_input(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_TAB:
            self.join_active_field = "name" if self.join_active_field == "ip" else "ip"
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.connect_to_host()
        elif event.key == pygame.K_ESCAPE:
            self.cleanup_network()
            self.state = GameState.MENU
        elif event.key == pygame.K_BACKSPACE:
            if self.join_active_field == "ip":
                self.join_ip = self.join_ip[:-1]
            else:
                self.join_name = self.join_name[:-1]
        elif self.join_active_field == "ip" and len(self.join_ip) < 22:
            if event.unicode.isdigit() or event.unicode in ('.', ':'):
                self.join_ip += event.unicode
        elif self.join_active_field == "name" and len(self.join_name) < 16:
            if event.unicode.isalnum() or event.unicode in (" ", "_", "-"):
                self.join_name += event.unicode

    def handle_lobby_input(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.chat_active:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.send_chat_message()
                self.chat_active = False
            elif event.key == pygame.K_ESCAPE:
                self.chat_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.chat_input = self.chat_input[:-1]
            elif len(self.chat_input) < 90 and event.unicode and event.unicode >= " ":
                self.chat_input += event.unicode
            return

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.chat_active = True
        elif event.key == pygame.K_r:
            self.toggle_ready()
        elif event.key == pygame.K_s and self.mode == GameMode.HOST:
            self.try_start_countdown()
        elif event.key == pygame.K_ESCAPE:
            self.cleanup_network()
            self.state = GameState.MENU

    def handle_multiplayer_leaderboard_input(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            if self.mode == GameMode.HOST:
                self.return_to_lobby_after_round()
        elif event.key == pygame.K_ESCAPE:
            self.cleanup_network()
            self.state = GameState.MENU

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
                if self.lootbox_result and self.ui_manager.lootbox_anim_frame > 235:
                    self.audio.play_sfx('click'); self.lootbox_result = None
                elif not self.lootbox_result and self.score_manager.coins >= LOOTBOX_COST:
                    self.audio.play_sfx('click'); self.lootbox_result = self.open_lootbox()
                    self.ui_manager.lootbox_anim_frame = 0

    def handle_paywall_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.audio.play_sfx('click'); self.paywall_message = None; self.state = GameState.LOOTBOX_SHOP

    def handle_collection_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.audio.play_sfx('click'); self.state = GameState.MENU

    def handle_effects_shop_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.audio.play_sfx('click'); self.effect_box_result = None; self.state = GameState.MENU
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.effect_box_result and self.ui_manager.lootbox_anim_frame > 235:
                    self.audio.play_sfx('click'); self.effect_box_result = None
                elif not self.effect_box_result and self.score_manager.coins >= EFFECT_BOX_COST:
                    self.audio.play_sfx('click'); self.effect_box_result = self.open_effect_box()
                    self.ui_manager.lootbox_anim_frame = 0

    def handle_equip_effects_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.audio.play_sfx('click'); self.state = GameState.MENU
            elif event.key == pygame.K_LEFT:
                self.audio.play_sfx('click')
                self.effect_equip_category = (self.effect_equip_category - 1) % len(EFFECT_TYPE_LABELS)
            elif event.key == pygame.K_RIGHT:
                self.audio.play_sfx('click')
                self.effect_equip_category = (self.effect_equip_category + 1) % len(EFFECT_TYPE_LABELS)

    # --- Multiplayer ---
    def start_host_session(self):
        self.cleanup_network()
        self.mode = GameMode.HOST
        self.local_player_index = 0
        self.target_player_count = max(MIN_MULTIPLAYER_PLAYERS,
                                       min(MAX_MULTIPLAYER_PLAYERS, self.host_player_count))
        self.host_name = self.sanitize_player_name(self.host_name, "Host")
        self.network = HostServer(
            port=MULTIPLAYER_PORT,
            backlog=self.target_player_count,
            max_clients=self.target_player_count - 1,
        )
        self.network.start()
        self.client_player_map = {}
        self.chat_messages = []
        self.chat_input = ""
        self.chat_active = False
        self.lobby_players = [{
            "index": 0,
            "client_id": None,
            "name": self.host_name,
            "ready": False,
            "is_host": True,
            "skin_index": self.selected_skin_index,
        }]
        self.players = []
        self.obstacles = []
        self.coins_on_road = []
        self.connection_message = f"IP: {self.get_local_ip()}:{MULTIPLAYER_PORT}"
        self.state = GameState.MP_LOBBY
        self.multiplayer_round_active = False

    def connect_to_host(self):
        if not self.join_ip.strip():
            self.connection_message = "Zadaj IP hostitela."
            return
        self.cleanup_network()
        host = self.join_ip.strip()
        port = MULTIPLAYER_PORT
        if ":" in host and host.count(":") == 1:
            host_part, port_part = host.rsplit(":", 1)
            if port_part.isdigit():
                host = host_part
                port = int(port_part)
        self.mode = GameMode.CLIENT
        self.join_name = self.sanitize_player_name(self.join_name, "Player")
        self.network = ClientPeer(host, port)
        self.network.connect()
        if self.network.is_connected():
            self.connection_message = f"Pripojene na {host}:{port}. Cakam na lobby..."
            self.network.send_packet({
                "type": PacketType.HELLO,
                "role": "client",
                "name": self.join_name,
                "skin_index": self.selected_skin_index,
            })
            self.state = GameState.MP_LOBBY
        else:
            self.connection_message = "Nepodarilo sa pripojit."
            self.network = None

    def get_public_lobby_players(self):
        players = []
        for p in sorted(self.lobby_players, key=lambda item: item.get("index", 0)):
            players.append({
                "index": p.get("index", 0),
                "name": p.get("name", "Player"),
                "ready": bool(p.get("ready", False)),
                "is_host": bool(p.get("is_host", False)),
                "skin_index": p.get("skin_index", 0),
            })
        return players

    def reindex_lobby_players(self):
        self.lobby_players.sort(key=lambda p: (not p.get("is_host", False), p.get("index", 0)))
        self.client_player_map = {}
        for index, player_info in enumerate(self.lobby_players):
            player_info["index"] = index
            client_id = player_info.get("client_id")
            if client_id is not None:
                self.client_player_map[client_id] = index
        self.local_player_index = 0

    def get_player_index_for_client(self, client_id):
        return self.client_player_map.get(client_id)

    def broadcast_lobby_state(self):
        if self.mode != GameMode.HOST or not self.network:
            return
        self.reindex_lobby_players()
        base_packet = {
            "type": PacketType.LOBBY_STATE,
            "phase": "lobby",
            "players": self.get_public_lobby_players(),
            "target_count": self.target_player_count,
            "chat": self.chat_messages[-8:],
        }
        for client_id, player_index in self.client_player_map.items():
            packet = dict(base_packet)
            packet["your_index"] = player_index
            self.network.send_packet(packet, client_id=client_id)

    def add_chat_message(self, sender, message, broadcast=True):
        msg = " ".join(str(message).strip().split())
        if not msg:
            return
        entry = {"sender": self.sanitize_player_name(sender, "Player"), "message": msg[:90]}
        self.chat_messages.append(entry)
        self.chat_messages = self.chat_messages[-8:]
        if broadcast and self.mode == GameMode.HOST and self.network:
            self.network.send_packet({"type": PacketType.CHAT, "entry": entry})

    def send_chat_message(self):
        msg = self.chat_input.strip()
        self.chat_input = ""
        if not msg:
            return
        if self.mode == GameMode.HOST:
            self.add_chat_message(self.host_name, msg)
        elif self.network and self.network.is_connected():
            self.network.send_packet({"type": PacketType.CHAT, "message": msg})

    def toggle_ready(self):
        if self.state != GameState.MP_LOBBY:
            return
        if self.mode == GameMode.HOST:
            if self.lobby_players:
                self.lobby_players[0]["ready"] = not self.lobby_players[0].get("ready", False)
                self.broadcast_lobby_state()
        elif self.network and self.network.is_connected():
            current = False
            for p in self.lobby_players:
                if p.get("index") == self.local_player_index:
                    current = bool(p.get("ready", False))
                    break
            self.network.send_packet({"type": PacketType.READY, "ready": not current})

    def all_lobby_ready(self):
        return (
            len(self.lobby_players) == self.target_player_count and
            all(p.get("ready", False) for p in self.lobby_players)
        )

    def try_start_countdown(self):
        if self.mode != GameMode.HOST or self.state != GameState.MP_LOBBY:
            return
        if len(self.lobby_players) < self.target_player_count:
            self.connection_message = "Cakam na vsetkych hracov."
            return
        if not self.all_lobby_ready():
            self.connection_message = "Kazdy hrac musi dat READY."
            return
        self.start_countdown()

    def start_countdown(self):
        self.network_seed = random.randint(0, 2**31 - 1)
        self.reset_game(seed=self.network_seed, multiplayer=True, players_info=self.lobby_players)
        self.multiplayer_round_active = False
        self.multiplayer_leaderboard = []
        self.countdown_started_at = time.time()
        self.countdown_value = MULTIPLAYER_COUNTDOWN_SECONDS
        self.last_countdown_value = None
        self.state = GameState.MP_COUNTDOWN
        self.broadcast_start_packet()
        self.broadcast_countdown(force=True)

    def broadcast_start_packet(self):
        if self.mode != GameMode.HOST or not self.network:
            return
        base_packet = {
            "type": PacketType.START,
            "seed": self.network_seed,
            "players": self.get_public_lobby_players(),
            "target_count": self.target_player_count,
            "countdown": MULTIPLAYER_COUNTDOWN_SECONDS,
        }
        for client_id, player_index in self.client_player_map.items():
            packet = dict(base_packet)
            packet["your_index"] = player_index
            self.network.send_packet(packet, client_id=client_id)

    def broadcast_countdown(self, force=False):
        if self.mode != GameMode.HOST or not self.network:
            return
        if force or self.countdown_value != self.last_countdown_value:
            self.network.send_packet({"type": PacketType.COUNTDOWN, "value": self.countdown_value})
            self.last_countdown_value = self.countdown_value

    def begin_multiplayer_round(self):
        self.round_start_time = time.time()
        self.frame_count = 0
        self.multiplayer_round_active = True
        self.state = GameState.PLAYING
        if self.mode == GameMode.HOST and self.network:
            self.network.send_packet({"type": PacketType.GAME_BEGIN})

    def send_input(self, left, right, up=False, down=False):
        if self.network and self.network.is_connected() and self.mode == GameMode.CLIENT:
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
        self.network = None
        self.client_player_map = {}
        self.connection_message = ""
        self.connection_lost = False
        self.multiplayer_round_active = False

    def process_network_messages(self):
        if not self.network: return
        for packet in self.network.get_packets():
            if not isinstance(packet, dict) or "type" not in packet: continue
            (self.handle_host_packet if self.mode == GameMode.HOST else self.handle_client_packet)(packet)

    def handle_host_packet(self, packet):
        pt = packet["type"]
        if pt == PacketType.HELLO:
            client_id = packet.get("_client_id")
            if client_id in self.client_player_map:
                return
            if len(self.lobby_players) >= self.target_player_count:
                if self.network:
                    self.network.send_packet({"type": PacketType.SERVER_FULL}, client_id=client_id)
                return
            name = self.sanitize_player_name(packet.get("name", ""), f"Player {len(self.lobby_players) + 1}")
            self.lobby_players.append({
                "index": len(self.lobby_players),
                "client_id": client_id,
                "name": name,
                "ready": False,
                "is_host": False,
                "skin_index": packet.get("skin_index", 0),
            })
            self.reindex_lobby_players()
            self.add_chat_message("SYSTEM", f"{name} sa pripojil.", broadcast=True)
            self.connection_message = f"IP: {self.get_local_ip()}:{MULTIPLAYER_PORT}"
            self.broadcast_lobby_state()
        elif pt == PacketType.READY:
            idx = self.get_player_index_for_client(packet.get("_client_id"))
            if idx is not None and 0 <= idx < len(self.lobby_players):
                self.lobby_players[idx]["ready"] = bool(packet.get("ready", False))
                self.broadcast_lobby_state()
        elif pt == PacketType.CHAT:
            idx = self.get_player_index_for_client(packet.get("_client_id"))
            if idx is not None and 0 <= idx < len(self.lobby_players):
                self.add_chat_message(self.lobby_players[idx].get("name", "Player"), packet.get("message", ""))
        elif pt == PacketType.NAME:
            idx = self.get_player_index_for_client(packet.get("_client_id"))
            if idx is not None and 0 <= idx < len(self.lobby_players):
                self.lobby_players[idx]["name"] = self.sanitize_player_name(packet.get("name", ""), "Player")
                self.broadcast_lobby_state()
        elif pt == PacketType.INPUT:
            idx = self.get_player_index_for_client(packet.get("_client_id"))
            if idx is not None and packet.get("player") == idx:
                self.player_inputs[idx] = {
                    "left": packet.get("left", False),
                    "right": packet.get("right", False),
                    "up": packet.get("up", False),
                    "down": packet.get("down", False),
                    "frame": packet.get("frame", self.frame_count),
                }
        elif pt == PacketType.CRASH:
            pass
        elif pt == PacketType.REMATCH_REQUEST:
            pass
        elif pt == PacketType.DISCONNECT:
            self.handle_client_disconnect(packet.get("_client_id"))

    def handle_client_packet(self, packet):
        pt = packet["type"]
        if pt == PacketType.LOBBY_STATE:
            self.lobby_players = packet.get("players", [])
            self.target_player_count = packet.get("target_count", self.target_player_count)
            self.local_player_index = packet.get("your_index", self.local_player_index)
            self.chat_messages = packet.get("chat", self.chat_messages)[-8:]
            if packet.get("phase") == "lobby":
                self.state = GameState.MP_LOBBY
                self.multiplayer_round_active = False
        elif pt == PacketType.CHAT:
            entry = packet.get("entry")
            if isinstance(entry, dict):
                self.chat_messages.append(entry)
                self.chat_messages = self.chat_messages[-8:]
        elif pt == PacketType.START:
            self.network_seed = packet.get("seed")
            self.lobby_players = packet.get("players", self.lobby_players)
            self.target_player_count = packet.get("target_count", len(self.lobby_players))
            self.local_player_index = packet.get("your_index", self.local_player_index)
            self.countdown_value = packet.get("countdown", MULTIPLAYER_COUNTDOWN_SECONDS)
            self.countdown_started_at = time.time()
            self.reset_game(seed=self.network_seed, multiplayer=True, players_info=self.lobby_players)
            self.multiplayer_round_active = False
            self.state = GameState.MP_COUNTDOWN
        elif pt == PacketType.COUNTDOWN:
            self.countdown_value = packet.get("value", self.countdown_value)
        elif pt == PacketType.GAME_BEGIN:
            self.begin_multiplayer_round()
        elif pt == PacketType.GAME_STATE:
            self.apply_game_state(packet)
        elif pt == PacketType.RESULT:
            self.multiplayer_leaderboard = packet.get("leaderboard", [])
            self.leaderboard_started_at = time.time()
            self.multiplayer_round_active = False
            self.audio.stop_engine()
            self.state = GameState.MP_LEADERBOARD
        elif pt == PacketType.REMATCH_RESPONSE:
            self.connection_message = "Rematch akceptovany. Cakam..."; self.state = GameState.MP_WAITING
        elif pt == PacketType.SERVER_FULL:
            self.connection_message = "Lobby je plne."
            if self.network:
                self.network.stop()
            self.network = None
            self.state = GameState.MP_CLIENT_SETUP
        elif pt == PacketType.DISCONNECT:
            self.connection_lost = True
            self.multiplayer_result_text = "CONNECTION LOST"
            self.state = GameState.MP_RESULT

    def handle_client_disconnect(self, client_id):
        if client_id is None:
            return
        idx = self.get_player_index_for_client(client_id)
        leaving_name = None
        if idx is not None and 0 <= idx < len(self.lobby_players):
            leaving_name = self.lobby_players[idx].get("name", "Player")
        if self.state in (GameState.PLAYING, GameState.MP_COUNTDOWN) and idx is not None:
            self.mark_player_crashed(idx)
            self.client_player_map.pop(client_id, None)
            for player_info in self.lobby_players:
                if player_info.get("client_id") == client_id:
                    player_info["disconnected"] = True
            if leaving_name:
                self.add_chat_message("SYSTEM", f"{leaving_name} sa odpojil.", broadcast=False)
            return
        self.lobby_players = [p for p in self.lobby_players if p.get("client_id") != client_id]
        self.reindex_lobby_players()
        if leaving_name:
            self.add_chat_message("SYSTEM", f"{leaving_name} sa odpojil.", broadcast=True)
        self.broadcast_lobby_state()

    def update_countdown(self):
        if self.mode == GameMode.HOST:
            elapsed = time.time() - self.countdown_started_at
            self.countdown_value = max(0, MULTIPLAYER_COUNTDOWN_SECONDS - int(elapsed))
            self.broadcast_countdown()
            if elapsed >= MULTIPLAYER_COUNTDOWN_SECONDS and not self.multiplayer_round_active:
                self.begin_multiplayer_round()
        else:
            elapsed = time.time() - self.countdown_started_at
            self.countdown_value = max(0, self.countdown_value if self.countdown_value else 0)
            if elapsed > MULTIPLAYER_COUNTDOWN_SECONDS + 3 and not self.multiplayer_round_active:
                self.connection_message = "Cakam na start od hosta..."

    def mark_player_crashed(self, index):
        if self.player_crashed.get(index, False):
            return
        self.player_crashed[index] = True
        duration = self.frame_count / FPS
        self.survival_stats.setdefault(index, {})["duration"] = duration
        self.survival_stats[index]["crashed"] = True
        if index == self.local_player_index:
            self.local_crashed = True
            self.audio.play_sfx('crash')

    def get_alive_player_indices(self):
        return [i for i in range(len(self.players)) if not self.player_crashed.get(i, False)]

    def broadcast_game_state(self):
        if self.mode != GameMode.HOST or not self.network:
            return
        players_payload = []
        for i, player in enumerate(self.players):
            players_payload.append({
                "index": i,
                "x": round(player.x, 2),
                "y": round(player.y, 2),
                "crashed": self.player_crashed.get(i, False),
                "duration": round(self.survival_stats.get(i, {}).get("duration", self.frame_count / FPS), 2),
            })
        obstacles_payload = []
        for obstacle in self.obstacles:
            obstacles_payload.append({
                "y": round(obstacle.y, 2),
                "offset": getattr(obstacle, "offset", 0),
            })
        self.network.send_packet({
            "type": PacketType.GAME_STATE,
            "frame": self.frame_count,
            "speed": self.current_speed,
            "score": self.score_manager.get_current_score(),
            "players": players_payload,
            "obstacles": obstacles_payload,
        })

    def apply_game_state(self, packet):
        if not self.players and self.lobby_players:
            self.reset_game(seed=self.network_seed, multiplayer=True, players_info=self.lobby_players)
        self.frame_count = packet.get("frame", self.frame_count)
        self.current_speed = packet.get("speed", self.current_speed)
        self.score_manager.current_score = packet.get("score", self.score_manager.current_score)
        for player_state in packet.get("players", []):
            idx = player_state.get("index")
            if idx is None or idx < 0:
                continue
            while idx >= len(self.players):
                x, y = self.get_start_position(idx, max(idx + 1, len(self.lobby_players)))
                self.players.append(Player(x, y, color=OBSTACLE_COLOR))
            self.players[idx].x = player_state.get("x", self.players[idx].x)
            self.players[idx].y = player_state.get("y", self.players[idx].y)
            self.player_crashed[idx] = bool(player_state.get("crashed", False))
            self.survival_stats.setdefault(idx, {})["duration"] = player_state.get("duration", 0.0)
        if 0 <= self.local_player_index < len(self.players):
            self.player = self.players[self.local_player_index]
            self.local_crashed = self.player_crashed.get(self.local_player_index, False)
        self.obstacles = []
        for obstacle_state in packet.get("obstacles", []):
            obstacle = ObstacleCar(obstacle_state.get("y", -OBSTACLE_HEIGHT))
            obstacle.offset = obstacle_state.get("offset", 0)
            self.obstacles.append(obstacle)

    def finish_multiplayer_round(self):
        if self.state == GameState.MP_LEADERBOARD:
            return
        total_duration = self.frame_count / FPS
        results = []
        for info in self.get_public_lobby_players():
            idx = info.get("index", 0)
            stats = self.survival_stats.get(idx, {})
            duration = stats.get("duration", total_duration)
            if not self.player_crashed.get(idx, False):
                duration = total_duration
                self.survival_stats.setdefault(idx, {})["duration"] = duration
            results.append({
                "index": idx,
                "name": info.get("name", "Player"),
                "duration": round(duration, 2),
                "score": int(self.score_manager.get_current_score()),
                "crashed": self.player_crashed.get(idx, False),
            })
        results.sort(key=lambda r: (r["duration"], not r["crashed"]), reverse=True)
        for place, result in enumerate(results, start=1):
            result["place"] = place
        self.multiplayer_leaderboard = results
        self.leaderboard_started_at = time.time()
        self.multiplayer_round_active = False
        self.audio.stop_engine()
        self.state = GameState.MP_LEADERBOARD
        if self.network:
            self.network.send_packet({"type": PacketType.RESULT, "leaderboard": results})

    def return_to_lobby_after_round(self):
        if self.mode != GameMode.HOST:
            return
        self.lobby_players = [p for p in self.lobby_players if not p.get("disconnected", False)]
        self.reindex_lobby_players()
        for player_info in self.lobby_players:
            player_info["ready"] = False
        self.players = []
        self.player = None
        self.obstacles = []
        self.coins_on_road = []
        self.player_inputs = {}
        self.player_crashed = {}
        self.survival_stats = {}
        self.multiplayer_round_active = False
        self.chat_active = False
        self.chat_input = ""
        self.state = GameState.MP_LOBBY
        self.broadcast_lobby_state()

    # --- Update ---
    def update_singleplayer(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.road.update(self.current_speed)
        self.spawn_obstacle(); self.spawn_coin()
        self.update_obstacles(); self.update_coins(); self.update_difficulty()
        self.audio.update_engine_pitch(self.current_speed)
        self.score_manager.increment_score(self.current_speed / 100)
        self._update_effect_particles()
        if self.check_collisions(self.player):
            self.audio.stop_engine(); self.audio.play_sfx('crash'); self.state = GameState.GAME_OVER

    def update_multiplayer(self):
        if not self.network or not self.network.is_connected():
            return
        keys = pygame.key.get_pressed()
        left, right, up, down = keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]
        self.local_input.update({"left": left, "right": right, "up": up, "down": down, "frame": self.frame_count})

        if self.mode == GameMode.CLIENT:
            if not self.player_crashed.get(self.local_player_index, False):
                self.send_input(left, right, up, down)
            if self.road:
                self.road.update(self.current_speed)
            for obstacle in self.obstacles:
                obstacle.y += self.current_speed
            self.audio.update_engine_pitch(self.current_speed)
            self._update_effect_particles()
            self.frame_count += 1
            return

        self.player_inputs[0] = dict(self.local_input)
        for index, player in enumerate(self.players):
            if self.player_crashed.get(index, False):
                continue
            inp = self.player_inputs.get(index, {})
            player.update(
                left=inp.get("left", False),
                right=inp.get("right", False),
                up=inp.get("up", False),
                down=inp.get("down", False),
            )

        self.road.update(self.current_speed)
        self.spawn_obstacle()
        self.update_obstacles()
        self.update_difficulty()
        self.audio.update_engine_pitch(self.current_speed)
        self.score_manager.increment_score(self.current_speed / 100)
        self._update_effect_particles()

        for index, player in enumerate(self.players):
            if not self.player_crashed.get(index, False) and self.check_collisions(player):
                self.mark_player_crashed(index)

        if len(self.get_alive_player_indices()) <= 1 and len(self.players) > 1:
            self.finish_multiplayer_round()
            self.broadcast_game_state()
            return

        self.broadcast_game_state()
        self.frame_count += 1

    # --- Effect particles update ---
    def _update_effect_particles(self):
        if not self.player:
            return
        active = self.score_manager.get_active_effects()
        px, py = self.player.x, self.player.y
        self.effect_frame += 1

        # Exhaust particles
        exhaust = active.get(EFFECT_EXHAUST)
        if exhaust and self.effect_frame % 3 == 0:
            col = exhaust["color"]
            self.effect_particles.append({
                "x": px + random.randint(-8, 8),
                "y": py + PLAYER_HEIGHT - 5,
                "vx": random.uniform(-1.0, 1.0),
                "vy": random.uniform(1.5, 3.5),
                "life": random.randint(15, 30),
                "max_life": 30,
                "color": col,
                "size": random.randint(3, 7),
                "type": "exhaust",
            })

        # Trail
        trail = active.get(EFFECT_TRAIL)
        if trail:
            self.effect_trails.append({"x": px - PLAYER_WIDTH // 2 + 8, "y": py + PLAYER_HEIGHT - 10, "life": 40, "color": trail["color"]})
            self.effect_trails.append({"x": px + PLAYER_WIDTH // 2 - 8, "y": py + PLAYER_HEIGHT - 10, "life": 40, "color": trail["color"]})

        # Boost sparks on close obstacle pass
        boost = active.get(EFFECT_BOOST)
        if boost:
            for o in self.obstacles:
                c = self.road.get_center_at(o.y + OBSTACLE_HEIGHT // 2) + o.offset
                dist = math.sqrt((px - c) ** 2 + (py - o.y) ** 2)
                if dist < 50 and random.random() < 0.4:
                    self.effect_particles.append({
                        "x": px + random.randint(-20, 20),
                        "y": py + random.randint(0, PLAYER_HEIGHT),
                        "vx": random.uniform(-3, 3),
                        "vy": random.uniform(-3, 1),
                        "life": random.randint(8, 18),
                        "max_life": 18,
                        "color": boost["color"],
                        "size": random.randint(2, 5),
                        "type": "boost",
                    })

        # Decay particles
        for p in self.effect_particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
        self.effect_particles = [p for p in self.effect_particles if p["life"] > 0]

        # Decay trails
        for t in self.effect_trails:
            t["y"] += self.current_speed
            t["life"] -= 1
        self.effect_trails = [t for t in self.effect_trails if t["life"] > 0]

    # --- Draw ---
    def draw_game(self):
        self.screen.fill(GRASS_COLOR)
        if not self.road:
            self.ui_manager.draw_animated_bg(self.screen)
            return
        self.road.draw(self.screen)
        for coin in self.coins_on_road: coin.draw(self.screen)
        for o in self.obstacles:
            c = self.road.get_center_at(o.y + OBSTACLE_HEIGHT // 2) + o.offset
            o.draw(self.screen, c)
        self._draw_player_with_effects()
        self.ui_manager.draw_hud(self.screen, int(self.score_manager.get_current_score()), self.current_speed,
                                 self.audio, self.score_manager.session_coins)
        if self.mode != GameMode.SINGLEPLAYER and self.player_crashed.get(self.local_player_index, False):
            self.ui_manager.draw_spectator_banner(self.screen)

    def _draw_player_with_effects(self):
        if not self.player:
            return
        active = self.score_manager.get_active_effects()
        px, py = self.player.x, self.player.y

        # GLOW: pulsing circle behind car
        glow = active.get(EFFECT_GLOW)
        if glow:
            pulse = 0.6 + 0.4 * math.sin(self.effect_frame * 0.08)
            r = int(50 * pulse)
            glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            alpha = int(60 * pulse)
            pygame.draw.circle(glow_surf, (*glow["color"], alpha), (r, r), r)
            self.screen.blit(glow_surf, (px - r, py + PLAYER_HEIGHT // 2 - r))

        # TRAIL: position history on road
        trail = active.get(EFFECT_TRAIL)
        if trail:
            for t in self.effect_trails:
                a = int(180 * t["life"] / 40)
                trail_surf = pygame.Surface((6, 4), pygame.SRCALPHA)
                trail_surf.fill((*t["color"], a))
                self.screen.blit(trail_surf, (int(t["x"]), int(t["y"])))

        # Draw the car itself
        if self.mode == GameMode.SINGLEPLAYER:
            self.player.draw(self.screen)
        else:
            lobby_by_index = {p.get("index"): p for p in self.lobby_players}
            for i, p in enumerate(self.players):
                if self.player_crashed.get(i, False):
                    continue
                p.draw(self.screen)
                info = lobby_by_index.get(i, {})
                label = info.get("name", f"P{i + 1}")[:14]
                label_color = UI_GOLD if i == self.local_player_index else UI_TEXT_MAIN
                self.ui_manager.draw_text(self.screen, label, self.ui_manager.font_small,
                                          label_color, int(p.x), int(p.y - 18), center=True)

        # EXHAUST & BOOST particles
        for p in self.effect_particles:
            a = int(220 * p["life"] / p["max_life"])
            p_surf = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*p["color"], a), (p["size"], p["size"]), p["size"])
            self.screen.blit(p_surf, (int(p["x"]) - p["size"], int(p["y"]) - p["size"]))

        # AURA: speed lines at high speed
        aura = active.get(EFFECT_AURA)
        if aura and self.current_speed > MAX_SCROLL_SPEED * 0.5:
            intensity = (self.current_speed - MAX_SCROLL_SPEED * 0.5) / (MAX_SCROLL_SPEED * 0.5)
            num_lines = int(6 * intensity)
            aura_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for i in range(num_lines):
                lx = px + random.randint(-120, 120)
                ly = py + random.randint(-40, PLAYER_HEIGHT)
                length = random.randint(20, 60)
                a = int(100 * intensity * random.random())
                pygame.draw.line(aura_surf, (*aura["color"], a), (lx, ly), (lx, ly + length), 2)
            self.screen.blit(aura_surf, (0, 0))

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
                elif self.state == GameState.MP_HOST_SETUP: self.handle_host_setup_input(event)
                elif self.state == GameState.MP_CLIENT_SETUP: self.handle_join_input(event)
                elif self.state == GameState.MP_LOBBY: self.handle_lobby_input(event)
                elif self.state == GameState.MP_LEADERBOARD: self.handle_multiplayer_leaderboard_input(event)
                elif self.state == GameState.PLAYING: self.handle_playing_input(event)
                elif self.state == GameState.PAUSED: self.handle_paused_input(event)
                elif self.state == GameState.MP_RESULT: self.handle_multiplayer_result_input(event)
                elif self.state == GameState.GAME_OVER: self.handle_game_over_input(event, mouse_pos, mouse_clicked)
                elif self.state == GameState.ENTERING_NAME: self.handle_name_input(event)
                elif self.state == GameState.SKIN_SELECT: self.handle_skin_input(event)
                elif self.state == GameState.LOOTBOX_SHOP: self.handle_lootbox_input(event)
                elif self.state == GameState.PAYWALL: self.handle_paywall_input(event)
                elif self.state == GameState.COLLECTION: self.handle_collection_input(event)
                elif self.state == GameState.EFFECTS_SHOP: self.handle_effects_shop_input(event)
                elif self.state == GameState.EQUIP_EFFECTS: self.handle_equip_effects_input(event)

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
                elif action == "effects":
                    self.audio.play_sfx('click'); self.effect_box_result = None; self.state = GameState.EFFECTS_SHOP
                elif action == "equip":
                    self.audio.play_sfx('click'); self.state = GameState.EQUIP_EFFECTS
                elif action == "collection":
                    self.audio.play_sfx('click'); self.state = GameState.COLLECTION
                elif action == "host":
                    self.audio.play_sfx('click'); self.mode = GameMode.HOST
                    if not self.host_name:
                        self.host_name = "Host"
                    self.state = GameState.MP_HOST_SETUP
                elif action == "join":
                    self.audio.play_sfx('click'); self.mode = GameMode.CLIENT
                    self.join_ip = ""
                    if not self.join_name:
                        self.join_name = "Player"
                    self.join_active_field = "ip"
                    self.state = GameState.MP_CLIENT_SETUP

            elif self.state == GameState.MP_HOST_SETUP:
                action = self.ui_manager.draw_host_setup(self.screen, self.host_name,
                                                          self.host_player_count, mouse_pos, mouse_clicked)
                if action == "minus":
                    self.audio.play_sfx('click')
                    self.host_player_count = max(MIN_MULTIPLAYER_PLAYERS, self.host_player_count - 1)
                elif action == "plus":
                    self.audio.play_sfx('click')
                    self.host_player_count = min(MAX_MULTIPLAYER_PLAYERS, self.host_player_count + 1)
                elif action == "create":
                    self.audio.play_sfx('click')
                    self.start_host_session()
                elif action == "back":
                    self.audio.play_sfx('click')
                    self.state = GameState.MENU

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
                    mouse_pos, mouse_clicked, self.lootbox_result,
                    self.score_manager.pity_epic, self.score_manager.pity_legendary)
                if action == "buy":
                    self.audio.play_sfx('click'); self.lootbox_result = self.open_lootbox()
                    self.ui_manager.lootbox_anim_frame = 0
                elif action == "paywall":
                    self.audio.play_sfx('click'); self.paywall_message = None; self.state = GameState.PAYWALL
                elif action == "back":
                    self.audio.play_sfx('click'); self.lootbox_result = None; self.state = GameState.MENU
                if self.lootbox_result and mouse_clicked and self.ui_manager.lootbox_anim_frame > 235:
                    self.audio.play_sfx('click'); self.lootbox_result = None

            elif self.state == GameState.EFFECTS_SHOP:
                action = self.ui_manager.draw_effects_shop(self.screen, self.score_manager.coins,
                    len(self.score_manager.unlocked_effects), len(EFFECTS),
                    mouse_pos, mouse_clicked, self.effect_box_result,
                    self.score_manager.pity_epic, self.score_manager.pity_legendary)
                if action == "buy":
                    self.audio.play_sfx('click'); self.effect_box_result = self.open_effect_box()
                    self.ui_manager.lootbox_anim_frame = 0
                elif action == "paywall":
                    self.audio.play_sfx('click'); self.paywall_message = None; self.state = GameState.PAYWALL
                elif action == "back":
                    self.audio.play_sfx('click'); self.effect_box_result = None; self.state = GameState.MENU
                if self.effect_box_result and mouse_clicked and self.ui_manager.lootbox_anim_frame > 235:
                    self.audio.play_sfx('click'); self.effect_box_result = None

            elif self.state == GameState.EQUIP_EFFECTS:
                action = self.ui_manager.draw_equip_effects(self.screen,
                    self.score_manager.unlocked_effects, self.score_manager.equipped_effects,
                    self.effect_equip_category, mouse_pos, mouse_clicked)
                if action == "back":
                    self.audio.play_sfx('click'); self.state = GameState.MENU
                elif action == "prev_cat":
                    self.audio.play_sfx('click')
                    self.effect_equip_category = (self.effect_equip_category - 1) % len(EFFECT_TYPE_LABELS)
                elif action == "next_cat":
                    self.audio.play_sfx('click')
                    self.effect_equip_category = (self.effect_equip_category + 1) % len(EFFECT_TYPE_LABELS)
                elif action and action.startswith("equip_"):
                    idx = int(action.split("_")[1])
                    self.audio.play_sfx('click'); self.score_manager.equip_effect(idx)
                elif action and action.startswith("unequip_"):
                    etype = action.split("_", 1)[1]
                    self.audio.play_sfx('click'); self.score_manager.unequip_effect(etype)

            elif self.state == GameState.PAYWALL:
                action = self.ui_manager.draw_paywall(self.screen, self.score_manager.coins, mouse_pos, mouse_clicked)
                if action == "close":
                    self.audio.play_sfx('click'); self.paywall_message = None; self.state = GameState.LOOTBOX_SHOP
                elif action and action.startswith("pkg_"):
                    self.audio.play_sfx('click')
                    pkg_idx = int(action.split("_")[1])
                    if pkg_idx < len(COIN_PACKAGES) and COIN_PACKAGES[pkg_idx].get("admin", False):
                        self.score_manager.add_coins(COIN_PACKAGES[pkg_idx]["coins"])
                        self.paywall_message = True
                    else:
                        self.paywall_message = True
                if self.paywall_message and mouse_clicked:
                    self.paywall_message = None; self.state = GameState.LOOTBOX_SHOP

            elif self.state == GameState.COLLECTION:
                action = self.ui_manager.draw_collection(self.screen, self.score_manager.unlocked_skins,
                                                          mouse_pos, mouse_clicked)
                if action == "back":
                    self.audio.play_sfx('click'); self.state = GameState.MENU

            elif self.state == GameState.MP_CLIENT_SETUP:
                action = self.ui_manager.draw_join_setup(self.screen, self.join_ip, self.join_name,
                                                         self.join_active_field, mouse_pos, mouse_clicked)
                if action == "ip":
                    self.join_active_field = "ip"
                elif action == "name":
                    self.join_active_field = "name"
                elif action == "join" and len(self.join_ip) > 0:
                    self.audio.play_sfx('click')
                    self.connect_to_host()
                elif action == "back":
                    self.audio.play_sfx('click')
                    self.state = GameState.MENU

            elif self.state == GameState.MP_LOBBY:
                can_start = self.mode == GameMode.HOST and self.all_lobby_ready()
                host_info = self.connection_message
                action = self.ui_manager.draw_multiplayer_lobby(
                    self.screen,
                    self.get_public_lobby_players() if self.mode == GameMode.HOST else self.lobby_players,
                    self.target_player_count,
                    self.chat_messages,
                    self.chat_input,
                    self.chat_active,
                    self.mode == GameMode.HOST,
                    can_start,
                    host_info,
                    self.local_player_index,
                    mouse_pos,
                    mouse_clicked,
                )
                if action == "chat":
                    self.chat_active = True
                elif action == "ready":
                    self.audio.play_sfx('click')
                    self.toggle_ready()
                elif action == "start":
                    self.audio.play_sfx('click')
                    self.try_start_countdown()
                elif action == "back":
                    self.audio.play_sfx('click')
                    self.cleanup_network()
                    self.state = GameState.MENU

            elif self.state == GameState.MP_COUNTDOWN:
                self.update_countdown()
                self.draw_game()
                self.ui_manager.draw_countdown_lights(self.screen, self.countdown_value)

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
            elif self.state == GameState.MP_LEADERBOARD:
                action = self.ui_manager.draw_multiplayer_leaderboard(
                    self.screen, self.multiplayer_leaderboard,
                    self.mode == GameMode.HOST, mouse_pos, mouse_clicked
                )
                if action == "lobby":
                    self.audio.play_sfx('click')
                    self.return_to_lobby_after_round()
                elif self.mode == GameMode.HOST and self.leaderboard_started_at:
                    if time.time() - self.leaderboard_started_at >= MULTIPLAYER_LEADERBOARD_SECONDS:
                        self.return_to_lobby_after_round()
            elif self.state == GameState.MP_RESULT:
                self.draw_game(); self.draw_multiplayer_result()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_TAB]:
                self.ui_manager.draw_leaderboard(self.screen, self.score_manager.get_highscores())

            pygame.display.flip()

        self.cleanup_network()
        pygame.quit()

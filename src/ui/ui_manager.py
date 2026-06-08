import pygame
import math
from src.settings import *


class ModernButton:
    def __init__(self, x, y, width, height, text, font, accent_color=UI_ACCENT, special_border=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hover_progress = 0.0
        self.is_hovered = False
        self.accent_color = accent_color
        self.special_border = special_border

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * 0.2

    def draw(self, screen):
        alpha = int(180 + 75 * self.hover_progress)
        # Determine base background color (UI_PANEL_BG for most, accent_color for prominent buttons)
        base_bg = self.accent_color if self.accent_color == UI_ACCENT_GREEN else UI_PANEL_BG

        bg_color = (
            int(base_bg[0] + (self.accent_color[0] - base_bg[0]) * 0.2 * self.hover_progress),
            int(base_bg[1] + (self.accent_color[1] - base_bg[1]) * 0.2 * self.hover_progress),
            int(base_bg[2] + (self.accent_color[2] - base_bg[2]) * 0.2 * self.hover_progress),
        )
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*bg_color, alpha), s.get_rect(), border_radius=12)
        border_color = (
            int(self.accent_color[0] + (UI_TEXT_MAIN[0] - self.accent_color[0]) * (1 - self.hover_progress)),
            int(self.accent_color[1] + (UI_TEXT_MAIN[1] - self.accent_color[1]) * (1 - self.hover_progress)),
            int(self.accent_color[2] + (UI_TEXT_MAIN[2] - self.accent_color[2]) * (1 - self.hover_progress))
        )
        border_width = 3 if self.hover_progress < 0.5 else 4
        if self.special_border and self.hover_progress > 0:
            # Draw special border with gaps and lines
            border_rect = s.get_rect()
            border_color_alpha = (*border_color, alpha) # Use the calculated border_color with alpha

            # Draw top and bottom borders
            pygame.draw.line(s, border_color_alpha, border_rect.topleft, border_rect.topright, border_width)
            pygame.draw.line(s, border_color_alpha, border_rect.bottomleft, border_rect.bottomright, border_width)

            # Draw left border with gap
            gap_size = border_rect.height // 3
            pygame.draw.line(s, border_color_alpha, border_rect.topleft, (border_rect.midleft[0], border_rect.centery - gap_size // 2), border_width)
            pygame.draw.line(s, border_color_alpha, (border_rect.midleft[0], border_rect.centery + gap_size // 2), border_rect.bottomleft, border_width)

            # Draw right border with gap
            pygame.draw.line(s, border_color_alpha, border_rect.topright, (border_rect.midright[0], border_rect.centery - gap_size // 2), border_width)
            pygame.draw.line(s, border_color_alpha, (border_rect.midright[0], border_rect.centery + gap_size // 2), border_rect.bottomright, border_width)

            # Draw short lines from the gaps
            line_length = 15
            pygame.draw.line(s, border_color_alpha, (border_rect.midleft[0], border_rect.centery - line_length // 2), (border_rect.midleft[0] - line_length, border_rect.centery - line_length // 2), border_width)
            pygame.draw.line(s, border_color_alpha, (border_rect.midleft[0], border_rect.centery + line_length // 2), (border_rect.midleft[0] - line_length, border_rect.centery + line_length // 2), border_width)
            pygame.draw.line(s, border_color_alpha, (border_rect.midright[0], border_rect.centery - line_length // 2), (border_rect.midright[0] + line_length, border_rect.centery - line_length // 2), border_width)
            pygame.draw.line(s, border_color_alpha, (border_rect.midright[0], border_rect.centery + line_length // 2), (border_rect.midright[0] + line_length, border_rect.centery + line_length // 2), border_width)

        else:
            pygame.draw.rect(s, border_color, s.get_rect(), border_width, border_radius=12)
        screen.blit(s, self.rect.topleft)
        text_color = UI_TEXT_MAIN
        y_offset = -2 * self.hover_progress
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(self.rect.centerx + 2, self.rect.centery + 2 + y_offset))
        screen.blit(shadow_surf, shadow_rect)
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery + y_offset))
        screen.blit(text_surf, text_rect)
        if self.hover_progress > 0.05: # Adjusted threshold for glow
            glow_rect = pygame.Rect(self.rect.x - 7, self.rect.y - 7, self.rect.width + 14, self.rect.height + 14) # Increased glow size
            pygame.draw.rect(screen, (*self.accent_color, int(50 * self.hover_progress)), glow_rect, 3, border_radius=18) # Increased glow alpha and width

    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.is_hovered and mouse_clicked


class UIManager:
    def __init__(self, audio_manager):
        pygame.font.init()
        self.audio = audio_manager
        self.font_title = pygame.font.SysFont("impact", 100)
        if not self.font_title:
            self.font_title = pygame.font.Font(None, 100)
        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tech = pygame.font.SysFont("consolas", 24, bold=True)

        bw, bh = 300, 48
        cx = WIDTH // 2 - bw // 2

        # New UI Buttons
        # Play button at bottom-left
        play_btn_w, play_btn_h = 250, 70
        play_btn_x = 50
        play_btn_y = HEIGHT - play_btn_h - 70 # Moved down by 10 more pixels
        self.play_button = ModernButton(play_btn_x, play_btn_y, play_btn_w, play_btn_h, "HRAŤ", self.font_large, UI_ACCENT, special_border=True)

        # Mode selection buttons (initially positioned to the right of play button)
        mode_btn_w, mode_btn_h = 220, 50 # Widened
        mode_btn_x = play_btn_x + play_btn_w + 30
        mode_btn_y_start = play_btn_y + (play_btn_h - (mode_btn_h * 2 + 10)) // 2 # Center vertically relative to play button

        self.singleplayer_button = ModernButton(mode_btn_x, mode_btn_y_start, mode_btn_w, mode_btn_h, "SINGLEPLAYER", self.font_medium)
        self.multiplayer_button = ModernButton(mode_btn_x, mode_btn_y_start + mode_btn_h + 10, mode_btn_w, mode_btn_h, "MULTIPLAYER", self.font_medium)

        # Top navigation buttons
        nav_btn_w, nav_btn_h = 160, 40
        nav_y = 50
        nav_spacing = 20
        # Calculate total width of navigation buttons
        total_nav_width = (nav_btn_w * 5) + (nav_spacing * 4) # 5 buttons: Collection, Garage, Lootbox, Equip, Effects
        current_nav_x = (WIDTH // 2) - (total_nav_width // 2) # Center alignment

        self.collection_nav_button = ModernButton(current_nav_x, nav_y, nav_btn_w, nav_btn_h, "KOLEKCIA", self.font_medium)
        current_nav_x += nav_btn_w + nav_spacing
        self.garage_nav_button = ModernButton(current_nav_x, nav_y, nav_btn_w, nav_btn_h, "GARAZ", self.font_medium)
        current_nav_x += nav_btn_w + nav_spacing
        self.lootbox_nav_button = ModernButton(current_nav_x, nav_y, nav_btn_w, nav_btn_h, "LOOTBOX", self.font_medium)
        current_nav_x += nav_btn_w + nav_spacing
        self.equip_nav_button = ModernButton(current_nav_x, nav_y, nav_btn_w, nav_btn_h, "VYBAVENIE", self.font_medium)
        current_nav_x += nav_btn_w + nav_spacing
        self.effects_nav_button = ModernButton(current_nav_x, nav_y, nav_btn_w, nav_btn_h, "EFEKTY", self.font_medium)

        # Existing buttons that are still relevant or need new positions
        self.continue_button = ModernButton(cx, HEIGHT // 2 + 80, bw, bh, "POKRAČOVAŤ", self.font_medium)
        self.setup_join_button = ModernButton(cx, HEIGHT // 2 + 40, bw, 60, "PRIPOJIŤ SA", self.font_medium)
        self.setup_back_button = ModernButton(cx, HEIGHT // 2 + 110, bw, 60, "SPÄŤ", self.font_medium)
        self.back_btn = ModernButton(cx, HEIGHT - 65, bw, 50, "SPÄŤ", self.font_medium)
        self.buy_box_btn = ModernButton(cx, HEIGHT // 2 + 130, bw, 55, f"KÚPIŤ BOX ({LOOTBOX_COST}c)", self.font_medium)
        self.buy_effect_btn = ModernButton(cx, HEIGHT // 2 + 130, bw, 55, f"KÚPIŤ BOX ({EFFECT_BOX_COST}c)", self.font_medium)
        self.buy_coins_btn = ModernButton(cx, HEIGHT // 2 + 215, bw, 50, "KÚPIŤ MINCE", self.font_medium)
        self.prev_btn = ModernButton(WIDTH // 2 - 320, HEIGHT // 2 - 30, 80, 80, "<", self.font_large)
        self.next_btn = ModernButton(WIDTH // 2 + 240, HEIGHT // 2 - 30, 80, 80, ">", self.font_large)
        self.select_btn = ModernButton(cx, HEIGHT // 2 + 180, bw, 55, "VYBRAŤ", self.font_medium)
        self.paywall_close_btn = ModernButton(cx, HEIGHT - 60, bw, 50, "ZAVRIEŤ", self.font_medium)
        self.setup_create_button = ModernButton(cx, HEIGHT // 2 + 115, bw, 58, "VYTVORIT", self.font_medium)
        self.ready_button = ModernButton(WIDTH // 2 - 330, HEIGHT - 82, 220, 54, "READY", self.font_medium)
        self.lobby_start_button = ModernButton(WIDTH // 2 - 90, HEIGHT - 82, 180, 54, "START", self.font_medium)
        self.lobby_back_button = ModernButton(WIDTH // 2 + 115, HEIGHT - 82, 220, 54, "SPAT", self.font_medium)

        self.play_button_active = False # State to manage visibility of mode buttons

        self.play_button_active = False # State to manage visibility of mode buttons
        self.paywall_buttons = []
        self.time_tracker = 0
        self.lootbox_anim_frame = 0
        self.lootbox_particles = []
        self.lootbox_roulette_strip = []
        self.lootbox_roulette_winner_idx = 0
        self.lootbox_roulette_target_x = 0

    def draw_glass_panel(self, screen, rect, alpha=200, border=True):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill((*UI_PANEL_BG, alpha))
        screen.blit(s, rect.topleft)
        if border:
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)
            cl = 20
            pygame.draw.line(screen, UI_ACCENT, rect.topleft, (rect.x + cl, rect.y), 3)
            pygame.draw.line(screen, UI_ACCENT, rect.topleft, (rect.x, rect.y + cl), 3)
            pygame.draw.line(screen, UI_ACCENT, rect.bottomright, (rect.right - cl, rect.bottom), 3)
            pygame.draw.line(screen, UI_ACCENT, rect.bottomright, (rect.right, rect.bottom - cl), 3)

    def draw_glowing_text(self, screen, text, font, color, center_pos, glow_radius=2):
        glow_surf = font.render(text, True, color)
        for x in range(-glow_radius, glow_radius + 1):
            for y in range(-glow_radius, glow_radius + 1):
                r = glow_surf.get_rect(center=(center_pos[0] + x, center_pos[1] + y))
                s = glow_surf.copy(); s.set_alpha(30); screen.blit(s, r)
        main_surf = font.render(text, True, (255, 255, 255))
        screen.blit(main_surf, main_surf.get_rect(center=center_pos))

    def draw_animated_bg(self, screen):
        self.time_tracker += 1
        screen.fill(UI_BG_DARK)
        gs = 60
        offset = (self.time_tracker * 0.5) % gs
        for x in range(0, WIDTH, gs):
            pygame.draw.line(screen, (40, 40, 60), (x, 0), (x, HEIGHT))
        for y in range(-gs, HEIGHT, gs):
            dy = y + offset
            a = min(255, int((dy / HEIGHT) * 50))
            pygame.draw.line(screen, (40 + a//2, 40 + a//2, 60 + a), (0, dy), (WIDTH, dy))

    def _draw_car(self, screen, skin, cx, cy, scale=1.0):
        w, h = int(PLAYER_WIDTH * scale), int(PLAYER_HEIGHT * scale)
        x, y = cx, cy - h // 2
        bc, sc, wc, hc = skin["body"], skin["spoiler"], skin["wing"], skin["helmet"]
        pygame.draw.rect(screen, (20,20,20), (x-w//2-int(8*scale), y+h-int(60*scale), int(22*scale), int(40*scale)))
        pygame.draw.rect(screen, (20,20,20), (x+w//2-int(14*scale), y+h-int(60*scale), int(22*scale), int(40*scale)))
        pygame.draw.rect(screen, bc, (x-w//4, y+int(25*scale), w//2, h-int(40*scale)))
        pygame.draw.polygon(screen, bc, [(x-w//4, y+int(25*scale)), (x+w//4, y+int(25*scale)), (x, y)])
        pygame.draw.rect(screen, (20,20,20), (x-w//2-int(4*scale), y+int(25*scale), int(16*scale), int(28*scale)))
        pygame.draw.rect(screen, (20,20,20), (x+w//2-int(12*scale), y+int(25*scale), int(16*scale), int(28*scale)))
        pygame.draw.rect(screen, sc, (x-w//2, y+h-int(15*scale), w, int(15*scale)))
        pygame.draw.rect(screen, wc, (x-w//3, y+int(10*scale), int(w//1.5), int(8*scale)))
        pygame.draw.circle(screen, hc, (x, y+h//2+int(8*scale)), max(1, int(w//5)))

    def draw_menu(self, screen, highscores, coins, mouse_pos, mouse_clicked):
        self.draw_animated_bg(screen)
        shadow = self.font_title.render("F1 TURBO", True, (0,0,0))
        screen.blit(shadow, shadow.get_rect(center=(WIDTH//2+5, 205)))
        self.draw_glowing_text(screen, "F1 TURBO", self.font_title, UI_ACCENT, (WIDTH//2, 200), 4)
        self.draw_text(screen, "ULTIMATE RACING EXPERIENCE", self.font_small, UI_TEXT_DIM, WIDTH//2, 255, center=True)
        self.draw_text(screen, f"COINS: {coins}", self.font_tech, UI_GOLD, WIDTH-260, 145)

        # Update and draw main play button
        self.play_button.update(mouse_pos)
        self.play_button.draw(screen)

        ret_val = None

        # Conditionally show mode selection buttons
        if self.play_button_active:
            self.singleplayer_button.update(mouse_pos)
            self.multiplayer_button.update(mouse_pos)
            self.singleplayer_button.draw(screen)
            self.multiplayer_button.draw(screen)
            if self.singleplayer_button.is_clicked(mouse_pos, mouse_clicked):
                ret_val = "single"
                self.play_button_active = False
            elif self.multiplayer_button.is_clicked(mouse_pos, mouse_clicked):
                ret_val = "multiplayer_selection" 
                self.play_button_active = False
        elif self.play_button.is_clicked(mouse_pos, mouse_clicked):
            self.play_button_active = True
            self.audio.play_sfx('click')

        # Update and draw top navigation buttons
        self.collection_nav_button.update(mouse_pos)
        self.garage_nav_button.update(mouse_pos)
        self.lootbox_nav_button.update(mouse_pos)
        self.effects_nav_button.update(mouse_pos)
        self.equip_nav_button.update(mouse_pos) # Add this line

        self.collection_nav_button.draw(screen)
        self.garage_nav_button.draw(screen)
        self.lootbox_nav_button.draw(screen)
        self.effects_nav_button.draw(screen)
        self.equip_nav_button.draw(screen) # Add this line

        if self.collection_nav_button.is_clicked(mouse_pos, mouse_clicked): return "collection"
        if self.garage_nav_button.is_clicked(mouse_pos, mouse_clicked): return "skins" # Garage maps to skins for now
        if self.lootbox_nav_button.is_clicked(mouse_pos, mouse_clicked): return "lootbox"
        if self.effects_nav_button.is_clicked(mouse_pos, mouse_clicked): return "effects"
        if self.equip_nav_button.is_clicked(mouse_pos, mouse_clicked): return "equip" # Add this line

        pr = pygame.Rect(WIDTH//2-350, 420, 700, 135)
        self.draw_glass_panel(screen, pr)
        self.draw_text(screen, "TOP JAZDCi", self.font_medium, UI_GOLD, WIDTH//2, 437, center=True)
        yo = 465
        for i, e in enumerate(highscores[:3]):
            c = UI_GOLD if i==0 else UI_TEXT_MAIN
            self.draw_text(screen, f"{i+1}.", self.font_small, c, pr.x+150, yo)
            self.draw_text(screen, e['name'][:12], self.font_small, UI_TEXT_DIM, pr.x+200, yo)
            screen.blit(self.font_tech.render(f"{int(e['score']):05d}", True, UI_ACCENT), (pr.right-200, yo))
            yo += 28
        self.draw_text(screen, "[ TAB: TOP 20 ] [ ESC: PAUZA ] [ M: MUTE ]", self.font_tech, (80,80,100), WIDTH//2, HEIGHT-15, center=True)
        return ret_val

    def draw_multiplayer_mode_select(self, screen, mouse_pos, mouse_clicked):
        self.draw_animated_bg(screen)
        self.draw_glowing_text(screen, "MULTIPLAYER", self.font_large, UI_ACCENT, (WIDTH // 2, HEIGHT // 2 - 150), 3)

        host_btn_w, host_btn_h = 300, 60
        host_btn_x = WIDTH // 2 - host_btn_w // 2
        host_btn_y = HEIGHT // 2 - 50

        join_btn_w, join_btn_h = 300, 60
        join_btn_x = WIDTH // 2 - join_btn_w // 2
        join_btn_y = HEIGHT // 2 + 30

        self.host_button = ModernButton(host_btn_x, host_btn_y, host_btn_w, host_btn_h, "HOST GAME", self.font_medium)
        self.join_button = ModernButton(join_btn_x, join_btn_y, join_btn_w, join_btn_h, "JOIN GAME", self.font_medium)

        self.host_button.update(mouse_pos)
        self.join_button.update(mouse_pos)
        self.back_btn.update(mouse_pos)

        self.host_button.draw(screen)
        self.join_button.draw(screen)
        self.back_btn.draw(screen)

        if self.host_button.is_clicked(mouse_pos, mouse_clicked):
            return "host"
        if self.join_button.is_clicked(mouse_pos, mouse_clicked):
            return "join"
        if self.back_btn.is_clicked(mouse_pos, mouse_clicked):
            return "back"
        return None

    def draw_lootbox_shop(self, screen, coins, unlocked_count, total_count, mouse_pos, mouse_clicked,
                           result_info=None, pity_epic=0, pity_legendary=0):
        self.draw_animated_bg(screen)
        self.draw_glowing_text(screen, "LOOTBOX", self.font_large, UI_GOLD, (WIDTH//2, 45), 3)
        self.draw_text(screen, f"Tvoje mince: {coins}", self.font_medium, UI_GOLD, WIDTH//2, 95, center=True)
        self.draw_text(screen, f"Odomknute: {unlocked_count}/{total_count}", self.font_small, UI_TEXT_DIM, WIDTH//2, 128, center=True)
        pity_panel = pygame.Rect(WIDTH//2 - 180, 148, 360, 52)
        self.draw_glass_panel(screen, pity_panel, 180)
        ep_left = PITY_EPIC_THRESHOLD - pity_epic
        leg_left = PITY_LEGENDARY_THRESHOLD - pity_legendary
        self.draw_text(screen, f"Zaruceny EPICKY za: {ep_left} boxov", self.font_small, RARITY_COLORS[RARITY_EPIC], WIDTH//2, 157, center=True)
        self.draw_text(screen, f"Zaruceny LEGENDARNY za: {leg_left} boxov", self.font_small, RARITY_COLORS[RARITY_LEGENDARY], WIDTH//2, 178, center=True)
        pr = pygame.Rect(WIDTH//2-250, 210, 500, 220)
        self.draw_glass_panel(screen, pr, 230)
        bx, by = WIDTH//2, 305
        pygame.draw.rect(screen, (60,50,30), (bx-50, by-40, 100, 80), border_radius=8)
        pygame.draw.rect(screen, UI_GOLD, (bx-50, by-40, 100, 80), 3, border_radius=8)
        pygame.draw.rect(screen, UI_GOLD, (bx-5, by-40, 10, 80))
        pygame.draw.rect(screen, UI_GOLD, (bx-50, by-5, 100, 10))
        q = self.font_large.render("?", True, UI_GOLD)
        screen.blit(q, q.get_rect(center=(bx, by)))
        self.draw_text(screen, f"Cena: {LOOTBOX_COST} minci", self.font_medium, UI_TEXT_MAIN, WIDTH//2, 380, center=True)
        if result_info:
            self._draw_lootbox_result(screen, result_info)
        if not result_info:
            can_buy = coins >= LOOTBOX_COST
            self.buy_box_btn.update(mouse_pos); self.buy_box_btn.draw(screen)
            if not can_buy:
                self.draw_text(screen, "Nemas dostatok minci!", self.font_small, UI_WARNING, WIDTH//2, HEIGHT//2+200, center=True)
            self.buy_coins_btn.update(mouse_pos); self.buy_coins_btn.draw(screen)
            if self.buy_box_btn.is_clicked(mouse_pos, mouse_clicked) and can_buy: return "buy"
            if self.buy_coins_btn.is_clicked(mouse_pos, mouse_clicked): return "paywall"
        self.back_btn.update(mouse_pos); self.back_btn.draw(screen)
        if self.back_btn.is_clicked(mouse_pos, mouse_clicked): return "back"
        return None

    def _draw_lootbox_result(self, screen, info):
        import random as _rnd
        self.lootbox_anim_frame += 1
        af = self.lootbox_anim_frame
        CARD_W, CARD_H, CARD_GAP = 90, 110, 6
        CARD_STRIDE = CARD_W + CARD_GAP
        SCROLL_FRAMES = 180
        PAUSE_FRAMES = 30
        REVEAL_FRAME = SCROLL_FRAMES + PAUSE_FRAMES
        STRIP_SIZE = 50
        WINNER_IDX = 42
        rarity = info.get("rarity", RARITY_COMMON)
        rarity_color = RARITY_COLORS.get(rarity, UI_TEXT_DIM)
        if af == 1:
            self.lootbox_particles = []
            self.lootbox_roulette_strip = []
            for _ in range(STRIP_SIZE):
                self.lootbox_roulette_strip.append(_rnd.randint(0, len(CAR_SKINS) - 1))
            self.lootbox_roulette_strip[WINNER_IDX] = info["skin_index"]
            self.lootbox_roulette_winner_idx = WINNER_IDX
            self.lootbox_roulette_target_x = WINNER_IDX * CARD_STRIDE + CARD_W // 2
            if not info.get("is_new"):
                for _ in range(20):
                    angle = _rnd.uniform(0, 6.28)
                    speed = _rnd.uniform(2, 6)
                    self.lootbox_particles.append({"x": WIDTH//2, "y": HEIGHT//2, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed-3, "life": _rnd.randint(40,80), "size": _rnd.randint(4,10)})
        ov_alpha = min(230, af * 10)
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, ov_alpha))
        screen.blit(ov, (0, 0))
        if af <= SCROLL_FRAMES + PAUSE_FRAMES:
            if af <= SCROLL_FRAMES:
                t = af / SCROLL_FRAMES
                eased = 1.0 - (1.0 - t) ** 3
            else:
                eased = 1.0
            scroll = eased * self.lootbox_roulette_target_x
            vp_y = HEIGHT // 2 - CARD_H // 2 - 30
            vp_h = CARD_H + 40
            indicator_x = WIDTH // 2
            vp_bg = pygame.Surface((WIDTH, vp_h), pygame.SRCALPHA)
            vp_bg.fill((10, 12, 20, 220))
            screen.blit(vp_bg, (0, vp_y))
            pygame.draw.rect(screen, rarity_color, (0, vp_y, WIDTH, vp_h), 2)
            for i, skin_idx in enumerate(self.lootbox_roulette_strip):
                card_center_x = i * CARD_STRIDE + CARD_W // 2 - scroll + indicator_x
                card_x = int(card_center_x - CARD_W // 2)
                card_y = vp_y + 20
                if card_x + CARD_W < -10 or card_x > WIDTH + 10: continue
                skin = CAR_SKINS[skin_idx]
                skin_rarity = skin.get("rarity", RARITY_COMMON)
                rc = RARITY_COLORS.get(skin_rarity, UI_TEXT_DIM)
                card_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
                card_surf.fill((25, 30, 45, 240))
                screen.blit(card_surf, (card_x, card_y))
                pygame.draw.rect(screen, rc, (card_x, card_y, CARD_W, CARD_H), 2, border_radius=4)
                rar_label = RARITY_LABELS.get(skin_rarity, "")
                rl_surf = pygame.font.Font(None, 16).render(rar_label, True, rc)
                screen.blit(rl_surf, rl_surf.get_rect(midtop=(card_x + CARD_W // 2, card_y + 4)))
                self._draw_car(screen, skin, card_x + CARD_W // 2, card_y + 68, 0.5)
                nm_surf = pygame.font.Font(None, 18).render(skin["name"][:10], True, UI_TEXT_MAIN)
                screen.blit(nm_surf, nm_surf.get_rect(midbottom=(card_x + CARD_W // 2, card_y + CARD_H - 3)))
            pygame.draw.line(screen, UI_GOLD, (indicator_x, vp_y - 5), (indicator_x, vp_y + vp_h + 5), 3)
            pygame.draw.polygon(screen, UI_GOLD, [(indicator_x-8, vp_y-5), (indicator_x+8, vp_y-5), (indicator_x, vp_y+8)])
            pygame.draw.polygon(screen, UI_GOLD, [(indicator_x-8, vp_y+vp_h+5), (indicator_x+8, vp_y+vp_h+5), (indicator_x, vp_y+vp_h-8)])
            if af > SCROLL_FRAMES * 0.7:
                win_cx = WINNER_IDX * CARD_STRIDE + CARD_W // 2 - scroll + indicator_x
                win_x = int(win_cx - CARD_W // 2)
                glow_a = int(80 * min(1.0, (af - SCROLL_FRAMES * 0.7) / (SCROLL_FRAMES * 0.3)))
                glow_surf = pygame.Surface((CARD_W + 10, CARD_H + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*rarity_color, glow_a), glow_surf.get_rect(), border_radius=6)
                screen.blit(glow_surf, (win_x - 5, vp_y + 15))
            if af < SCROLL_FRAMES:
                blink = abs(math.sin(af * 0.15))
                ot_surf = self.font_medium.render("OTVARAM...", True, UI_GOLD)
                ot_surf.set_alpha(int(255 * blink))
                screen.blit(ot_surf, ot_surf.get_rect(center=(WIDTH // 2, vp_y - 30)))
            else:
                flash_a = int(200 + 55 * math.sin((af - SCROLL_FRAMES) * 0.5))
                rar_surf = self.font_large.render(RARITY_LABELS.get(rarity, ""), True, rarity_color)
                rar_surf.set_alpha(flash_a)
                screen.blit(rar_surf, rar_surf.get_rect(center=(WIDTH // 2, vp_y - 30)))
            return
        reveal_af = af - REVEAL_FRAME
        if reveal_af < 8:
            flash_a = int(120 * (1.0 - reveal_af / 8))
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((*rarity_color, flash_a))
            screen.blit(flash_surf, (0, 0))
        pw, ph = 500, 340
        pr = pygame.Rect(WIDTH // 2 - pw // 2, HEIGHT // 2 - ph // 2, pw, ph)
        self.draw_glass_panel(screen, pr, 250)
        pygame.draw.rect(screen, rarity_color, (pr.x, pr.y, pr.width, 4))
        pulse = 0.5 + 0.5 * math.sin(reveal_af * 0.15)
        if info.get("is_new"):
            glow_r = int(3 + 2 * pulse)
            self.draw_glowing_text(screen, "NOVY SKIN!", self.font_large, rarity_color, (WIDTH//2, pr.y+40), glow_r)
            rar_surf = self.font_small.render(RARITY_LABELS.get(rarity, ""), True, rarity_color)
            screen.blit(rar_surf, rar_surf.get_rect(center=(WIDTH//2, pr.y+80)))
            skin = CAR_SKINS[info.get("skin_index", 0)]
            name_y = pr.y + 115
            name_surf = self.font_large.render(info.get("skin_name", ""), True, skin["body"])
            name_glow = self.font_large.render(info.get("skin_name", ""), True, (min(255,skin["body"][0]+60), min(255,skin["body"][1]+60), min(255,skin["body"][2]+60)))
            name_glow.set_alpha(int(100 + 80 * pulse))
            screen.blit(name_glow, name_glow.get_rect(center=(WIDTH//2+2, name_y+2)))
            screen.blit(name_surf, name_surf.get_rect(center=(WIDTH//2, name_y)))
            if reveal_af > 5:
                car_scale = min(2.0, (reveal_af - 5) * 0.12)
                if car_scale > 0.3:
                    self._draw_car(screen, skin, WIDTH//2, pr.y + int(ph*0.68), car_scale)
            if reveal_af > 10 and rarity in (RARITY_EPIC, RARITY_LEGENDARY):
                for i in range(6):
                    sx = WIDTH//2 + int(90*math.sin(reveal_af*0.1+i*1.1))
                    sy = pr.y + int(ph*0.6) + int(45*math.cos(reveal_af*0.12+i*1.4))
                    spark_a = int(180*abs(math.sin(reveal_af*0.2+i)))
                    spark_surf = pygame.Surface((8,8), pygame.SRCALPHA)
                    pygame.draw.circle(spark_surf, (*rarity_color, spark_a), (4,4), 4)
                    screen.blit(spark_surf, (sx, sy))
        else:
            glow_r = int(3 + 2 * pulse)
            self.draw_glowing_text(screen, "DUPLIKAT!", self.font_large, UI_WARNING, (WIDTH//2, pr.y+40), glow_r)
            rar_surf = self.font_small.render(RARITY_LABELS.get(rarity, ""), True, rarity_color)
            screen.blit(rar_surf, rar_surf.get_rect(center=(WIDTH//2, pr.y+78)))
            self.draw_text(screen, f"{info.get('skin_name','')} (uz mas)", self.font_medium, UI_TEXT_DIM, WIDTH//2, pr.y+110, center=True)
            refund = info.get('refund', 0)
            shown = int(refund * min(1.0, reveal_af/30)) if reveal_af < 35 else refund
            refund_color = UI_GOLD
            if reveal_af > 25:
                flash = int(30*abs(math.sin(reveal_af*0.2)))
                refund_color = (255, min(255,215+flash), flash)
            refund_surf = self.font_large.render(f"+{shown} minci", True, refund_color)
            screen.blit(refund_surf, refund_surf.get_rect(center=(WIDTH//2, pr.y+165)))
            for p in self.lootbox_particles:
                if p["life"] > 0:
                    p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["vy"]+=0.15; p["life"]-=1
                    p_alpha = min(255, p["life"]*6)
                    p_surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
                    pygame.draw.circle(p_surf, (255,215,0,p_alpha), (p["size"],p["size"]), p["size"])
                    pygame.draw.circle(p_surf, (200,170,0,p_alpha), (p["size"],p["size"]), p["size"], 1)
                    screen.blit(p_surf, (int(p["x"])-p["size"], int(p["y"])-p["size"]))
            if reveal_af > 5:
                coin_r = int(22+5*math.sin(reveal_af*0.2))
                coin_x, coin_y = WIDTH//2, pr.y+240
                glow_surf = pygame.Surface((coin_r*4, coin_r*4), pygame.SRCALPHA)
                glow_a = int(60*pulse)
                pygame.draw.circle(glow_surf, (255,215,0,glow_a), (coin_r*2, coin_r*2), coin_r*2)
                screen.blit(glow_surf, (coin_x-coin_r*2, coin_y-coin_r*2))
                pygame.draw.circle(screen, UI_GOLD, (coin_x, coin_y), coin_r)
                pygame.draw.circle(screen, (200,170,0), (coin_x, coin_y), coin_r, 3)
                dollar_font = pygame.font.Font(None, coin_r+4)
                dt = dollar_font.render("$", True, (180,150,0))
                screen.blit(dt, dt.get_rect(center=(coin_x, coin_y+1)))
        if reveal_af > 25:
            blink = abs(math.sin(reveal_af * 0.08))
            cont_surf = self.font_small.render("Klikni pre pokracovanie", True, UI_TEXT_DIM)
            cont_surf.set_alpha(int(255 * blink))
            screen.blit(cont_surf, cont_surf.get_rect(center=(WIDTH//2, pr.bottom-25)))

    def draw_effects_shop(self, screen, coins, unlocked_count, total_count, mouse_pos, mouse_clicked,
                          result_info=None, pity_epic=0, pity_legendary=0):
        self.draw_animated_bg(screen)
        theme = (180, 60, 255)
        self.draw_glowing_text(screen, "EFEKTY", self.font_large, theme, (WIDTH//2, 45), 3)
        self.draw_text(screen, f"Tvoje mince: {coins}", self.font_medium, UI_GOLD, WIDTH//2, 95, center=True)
        self.draw_text(screen, f"Odomknute: {unlocked_count}/{total_count}", self.font_small, UI_TEXT_DIM, WIDTH//2, 128, center=True)
        pity_panel = pygame.Rect(WIDTH//2-180, 148, 360, 52)
        self.draw_glass_panel(screen, pity_panel, 180)
        ep_left = PITY_EPIC_THRESHOLD - pity_epic
        leg_left = PITY_LEGENDARY_THRESHOLD - pity_legendary
        self.draw_text(screen, f"Zaruceny EPICKY za: {ep_left} boxov", self.font_small, RARITY_COLORS[RARITY_EPIC], WIDTH//2, 157, center=True)
        self.draw_text(screen, f"Zaruceny LEGENDARNY za: {leg_left} boxov", self.font_small, RARITY_COLORS[RARITY_LEGENDARY], WIDTH//2, 178, center=True)
        pr = pygame.Rect(WIDTH//2-250, 210, 500, 220)
        self.draw_glass_panel(screen, pr, 230)
        bx, by = WIDTH//2, 305
        pygame.draw.rect(screen, (40, 30, 60), (bx-50, by-40, 100, 80), border_radius=8)
        pygame.draw.rect(screen, theme, (bx-50, by-40, 100, 80), 3, border_radius=8)
        pygame.draw.rect(screen, theme, (bx-5, by-40, 10, 80))
        pygame.draw.rect(screen, theme, (bx-50, by-5, 100, 10))
        star_font = pygame.font.Font(None, 50)
        star_surf = star_font.render("*", True, theme)
        screen.blit(star_surf, star_surf.get_rect(center=(bx, by)))
        self.draw_text(screen, f"Cena: {EFFECT_BOX_COST} minci", self.font_medium, UI_TEXT_MAIN, WIDTH//2, 380, center=True)
        if result_info:
            self._draw_effect_result(screen, result_info)
        if not result_info:
            can_buy = coins >= EFFECT_BOX_COST
            self.buy_effect_btn.update(mouse_pos); self.buy_effect_btn.draw(screen)
            if not can_buy:
                self.draw_text(screen, "Nemas dostatok minci!", self.font_small, UI_WARNING, WIDTH//2, HEIGHT//2+200, center=True)
            self.buy_coins_btn.update(mouse_pos); self.buy_coins_btn.draw(screen)
            if self.buy_effect_btn.is_clicked(mouse_pos, mouse_clicked) and can_buy: return "buy"
            if self.buy_coins_btn.is_clicked(mouse_pos, mouse_clicked): return "paywall"
        self.back_btn.update(mouse_pos); self.back_btn.draw(screen)
        if self.back_btn.is_clicked(mouse_pos, mouse_clicked): return "back"
        return None

    def _draw_effect_result(self, screen, info):
        import random as _rnd
        self.lootbox_anim_frame += 1
        af = self.lootbox_anim_frame
        CARD_W, CARD_H, CARD_GAP = 90, 110, 6
        CARD_STRIDE = CARD_W + CARD_GAP
        SCROLL_FRAMES = 180
        PAUSE_FRAMES = 30
        REVEAL_FRAME = SCROLL_FRAMES + PAUSE_FRAMES
        STRIP_SIZE = 50
        WINNER_IDX = 42
        rarity = info.get("rarity", RARITY_COMMON)
        rarity_color = RARITY_COLORS.get(rarity, UI_TEXT_DIM)
        if af == 1:
            self.lootbox_particles = []
            self.lootbox_roulette_strip = []
            for _ in range(STRIP_SIZE):
                self.lootbox_roulette_strip.append(_rnd.randint(0, len(EFFECTS) - 1))
            self.lootbox_roulette_strip[WINNER_IDX] = info["effect_index"]
            self.lootbox_roulette_target_x = WINNER_IDX * CARD_STRIDE + CARD_W // 2
            if not info.get("is_new"):
                for _ in range(20):
                    angle = _rnd.uniform(0, 6.28)
                    speed = _rnd.uniform(2, 6)
                    self.lootbox_particles.append({"x": WIDTH//2, "y": HEIGHT//2, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed-3, "life": _rnd.randint(40,80), "size": _rnd.randint(4,10)})
        ov_alpha = min(230, af * 10)
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, ov_alpha))
        screen.blit(ov, (0, 0))
        if af <= SCROLL_FRAMES + PAUSE_FRAMES:
            t = af / SCROLL_FRAMES if af <= SCROLL_FRAMES else 1.0
            eased = 1.0 - (1.0 - t) ** 3
            scroll = eased * self.lootbox_roulette_target_x
            vp_y = HEIGHT // 2 - CARD_H // 2 - 30
            vp_h = CARD_H + 40
            indicator_x = WIDTH // 2
            vp_bg = pygame.Surface((WIDTH, vp_h), pygame.SRCALPHA)
            vp_bg.fill((10, 12, 20, 220))
            screen.blit(vp_bg, (0, vp_y))
            pygame.draw.rect(screen, rarity_color, (0, vp_y, WIDTH, vp_h), 2)
            for i, eff_idx in enumerate(self.lootbox_roulette_strip):
                card_center_x = i * CARD_STRIDE + CARD_W // 2 - scroll + indicator_x
                card_x = int(card_center_x - CARD_W // 2)
                card_y = vp_y + 20
                if card_x + CARD_W < -10 or card_x > WIDTH + 10: continue
                eff = EFFECTS[eff_idx]
                eff_rarity = eff.get("rarity", RARITY_COMMON)
                rc = RARITY_COLORS.get(eff_rarity, UI_TEXT_DIM)
                card_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
                card_surf.fill((25, 30, 45, 240))
                screen.blit(card_surf, (card_x, card_y))
                pygame.draw.rect(screen, rc, (card_x, card_y, CARD_W, CARD_H), 2, border_radius=4)
                rar_label = RARITY_LABELS.get(eff_rarity, "")
                rl_surf = pygame.font.Font(None, 16).render(rar_label, True, rc)
                screen.blit(rl_surf, rl_surf.get_rect(midtop=(card_x+CARD_W//2, card_y+4)))
                type_label = EFFECT_TYPE_LABELS.get(eff["type"], "")
                tl_surf = pygame.font.Font(None, 18).render(type_label, True, UI_TEXT_DIM)
                screen.blit(tl_surf, tl_surf.get_rect(center=(card_x+CARD_W//2, card_y+45)))
                pygame.draw.circle(screen, eff["color"], (card_x+CARD_W//2, card_y+72), 16)
                pygame.draw.circle(screen, (255,255,255), (card_x+CARD_W//2, card_y+72), 16, 2)
                nm_surf = pygame.font.Font(None, 16).render(eff["name"][:10], True, UI_TEXT_MAIN)
                screen.blit(nm_surf, nm_surf.get_rect(midbottom=(card_x+CARD_W//2, card_y+CARD_H-3)))
            pygame.draw.line(screen, UI_GOLD, (indicator_x, vp_y-5), (indicator_x, vp_y+vp_h+5), 3)
            pygame.draw.polygon(screen, UI_GOLD, [(indicator_x-8,vp_y-5),(indicator_x+8,vp_y-5),(indicator_x,vp_y+8)])
            pygame.draw.polygon(screen, UI_GOLD, [(indicator_x-8,vp_y+vp_h+5),(indicator_x+8,vp_y+vp_h+5),(indicator_x,vp_y+vp_h-8)])
            if af > SCROLL_FRAMES * 0.7:
                win_cx = WINNER_IDX * CARD_STRIDE + CARD_W // 2 - scroll + indicator_x
                win_x = int(win_cx - CARD_W // 2)
                glow_a = int(80 * min(1.0, (af - SCROLL_FRAMES*0.7)/(SCROLL_FRAMES*0.3)))
                glow_surf = pygame.Surface((CARD_W+10, CARD_H+10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*rarity_color, glow_a), glow_surf.get_rect(), border_radius=6)
                screen.blit(glow_surf, (win_x-5, vp_y+15))
            if af < SCROLL_FRAMES:
                blink = abs(math.sin(af * 0.15))
                ot_surf = self.font_medium.render("OTVARAM...", True, (180, 60, 255))
                ot_surf.set_alpha(int(255 * blink))
                screen.blit(ot_surf, ot_surf.get_rect(center=(WIDTH//2, vp_y-30)))
            else:
                flash_a = int(200+55*math.sin((af-SCROLL_FRAMES)*0.5))
                rar_surf = self.font_large.render(RARITY_LABELS.get(rarity, ""), True, rarity_color)
                rar_surf.set_alpha(flash_a)
                screen.blit(rar_surf, rar_surf.get_rect(center=(WIDTH//2, vp_y-30)))
            return
        reveal_af = af - REVEAL_FRAME
        if reveal_af < 8:
            flash_a = int(120*(1.0-reveal_af/8))
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((*rarity_color, flash_a))
            screen.blit(flash_surf, (0, 0))
        pw, ph = 500, 340
        pr = pygame.Rect(WIDTH//2-pw//2, HEIGHT//2-ph//2, pw, ph)
        self.draw_glass_panel(screen, pr, 250)
        pygame.draw.rect(screen, rarity_color, (pr.x, pr.y, pr.width, 4))
        pulse = 0.5 + 0.5 * math.sin(reveal_af * 0.15)
        eff_color = info.get("color", (255,255,255))
        if info.get("is_new"):
            glow_r = int(3 + 2 * pulse)
            self.draw_glowing_text(screen, "NOVY EFEKT!", self.font_large, rarity_color, (WIDTH//2, pr.y+40), glow_r)
            rar_surf = self.font_small.render(RARITY_LABELS.get(rarity, ""), True, rarity_color)
            screen.blit(rar_surf, rar_surf.get_rect(center=(WIDTH//2, pr.y+80)))
            type_label = EFFECT_TYPE_LABELS.get(info.get("effect_type",""), "")
            self.draw_text(screen, type_label, self.font_medium, UI_TEXT_DIM, WIDTH//2, pr.y+110, center=True)
            name_surf = self.font_large.render(info.get("effect_name", ""), True, eff_color)
            name_glow = self.font_large.render(info.get("effect_name", ""), True, (min(255,eff_color[0]+60), min(255,eff_color[1]+60), min(255,eff_color[2]+60)))
            name_glow.set_alpha(int(100+80*pulse))
            screen.blit(name_glow, name_glow.get_rect(center=(WIDTH//2+2, pr.y+152)))
            screen.blit(name_surf, name_surf.get_rect(center=(WIDTH//2, pr.y+150)))
            if reveal_af > 5:
                cr = int(30 + 10*math.sin(reveal_af*0.15))
                pygame.draw.circle(screen, eff_color, (WIDTH//2, pr.y+230), cr)
                pygame.draw.circle(screen, (255,255,255), (WIDTH//2, pr.y+230), cr, 3)
        else:
            glow_r = int(3 + 2 * pulse)
            self.draw_glowing_text(screen, "DUPLIKAT!", self.font_large, UI_WARNING, (WIDTH//2, pr.y+40), glow_r)
            rar_surf = self.font_small.render(RARITY_LABELS.get(rarity, ""), True, rarity_color)
            screen.blit(rar_surf, rar_surf.get_rect(center=(WIDTH//2, pr.y+78)))
            self.draw_text(screen, f"{info.get('effect_name','')} (uz mas)", self.font_medium, UI_TEXT_DIM, WIDTH//2, pr.y+110, center=True)
            refund = info.get('refund', 0)
            shown = int(refund*min(1.0, reveal_af/30)) if reveal_af < 35 else refund
            refund_color = UI_GOLD
            if reveal_af > 25:
                flash = int(30*abs(math.sin(reveal_af*0.2)))
                refund_color = (255, min(255,215+flash), flash)
            refund_surf = self.font_large.render(f"+{shown} minci", True, refund_color)
            screen.blit(refund_surf, refund_surf.get_rect(center=(WIDTH//2, pr.y+165)))
            for p in self.lootbox_particles:
                if p["life"] > 0:
                    p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["vy"]+=0.15; p["life"]-=1
                    p_alpha = min(255, p["life"]*6)
                    p_surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
                    pygame.draw.circle(p_surf, (255,215,0,p_alpha), (p["size"],p["size"]), p["size"])
                    screen.blit(p_surf, (int(p["x"])-p["size"], int(p["y"])-p["size"]))
        if reveal_af > 25:
            blink = abs(math.sin(reveal_af * 0.08))
            cont_surf = self.font_small.render("Klikni pre pokracovanie", True, UI_TEXT_DIM)
            cont_surf.set_alpha(int(255 * blink))
            screen.blit(cont_surf, cont_surf.get_rect(center=(WIDTH//2, pr.bottom-25)))

    def draw_equip_effects(self, screen, unlocked_effects, equipped_effects, category, mouse_pos, mouse_clicked):
        self.draw_animated_bg(screen)
        self.draw_glowing_text(screen, "VYBAVENIE", self.font_large, UI_ACCENT, (WIDTH//2, 45), 3)
        types = list(EFFECT_TYPE_LABELS.keys())
        cat_type = types[category % len(types)]
        cat_label = EFFECT_TYPE_LABELS[cat_type]
        self.draw_text(screen, f"< {cat_label} >", self.font_large, UI_GOLD, WIDTH//2, 100, center=True)
        # Display equipped count
        equipped_count = len([idx for idx in equipped_effects.values() if idx is not None])
        self.draw_text(screen, f"Vybavenych: {equipped_count}/{len(EFFECT_TYPE_LABELS)}", self.font_small, UI_TEXT_DIM, WIDTH//2, 135, center=True)
        cat_effects = [(i, e) for i, e in enumerate(EFFECTS) if e["type"] == cat_type]
        card_w, card_h = 200, 120
        gap = 16
        grid_w = 2 * card_w + gap
        grid_x = WIDTH // 2 - grid_w // 2
        grid_y = 160
        equipped_idx = equipped_effects.get(cat_type)
        for idx, (ei, eff) in enumerate(cat_effects):
            col = idx % 2
            row = idx // 2
            cx = grid_x + col * (card_w + gap)
            cy = grid_y + row * (card_h + gap)
            is_unlocked = ei in unlocked_effects
            is_equipped = equipped_idx == ei
            rarity = eff.get("rarity", RARITY_COMMON)
            rc = RARITY_COLORS.get(rarity, UI_TEXT_DIM)
            card_rect = pygame.Rect(cx, cy, card_w, card_h)
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if is_equipped:
                card_surf.fill((40, 60, 40, 240))
            elif is_unlocked:
                card_surf.fill((30, 35, 55, 240))
            else:
                card_surf.fill((15, 15, 22, 240))
            screen.blit(card_surf, (cx, cy))
            border_c = UI_ACCENT if is_equipped else (rc if is_unlocked else (50, 50, 60))
            pygame.draw.rect(screen, border_c, card_rect, 2 if not is_equipped else 3, border_radius=6)
            pygame.draw.circle(screen, eff["color"] if is_unlocked else (40,40,50), (cx+30, cy+40), 18)
            pygame.draw.circle(screen, (255,255,255) if is_unlocked else (60,60,70), (cx+30, cy+40), 18, 2)
            rar_label = RARITY_LABELS.get(rarity, "")
            rl_surf = pygame.font.Font(None, 16).render(rar_label, True, rc if is_unlocked else (60,60,80))
            screen.blit(rl_surf, rl_surf.get_rect(midtop=(cx+card_w//2+15, cy+5)))
            name_c = UI_TEXT_MAIN if is_unlocked else UI_TEXT_DIM
            nm_surf = pygame.font.Font(None, 22).render(eff["name"], True, name_c)
            screen.blit(nm_surf, nm_surf.get_rect(midleft=(cx+58, cy+42)))
            if is_equipped:
                eq_surf = pygame.font.Font(None, 18).render("AKTIVNY", True, UI_ACCENT)
                screen.blit(eq_surf, eq_surf.get_rect(midbottom=(cx+card_w//2, cy+card_h-8)))
            elif not is_unlocked:
                lk_surf = pygame.font.Font(None, 18).render("ZAMKNUTY", True, (70,70,90))
                screen.blit(lk_surf, lk_surf.get_rect(midbottom=(cx+card_w//2, cy+card_h-8)))
        bw, bh = 120, 45
        nav_y = HEIGHT - 130
        prev_cat_btn = ModernButton(WIDTH//2-bw-80, nav_y, bw, bh, "< SPAT", self.font_small)
        next_cat_btn = ModernButton(WIDTH//2+80, nav_y, bw, bh, "DALEJ >", self.font_small)
        prev_cat_btn.update(mouse_pos); prev_cat_btn.draw(screen)
        next_cat_btn.update(mouse_pos); next_cat_btn.draw(screen)
        if prev_cat_btn.is_clicked(mouse_pos, mouse_clicked): return "prev_cat"
        if next_cat_btn.is_clicked(mouse_pos, mouse_clicked): return "next_cat"
        for idx, (ei, eff) in enumerate(cat_effects):
            col = idx % 2
            row = idx // 2
            cx = grid_x + col * (card_w + gap)
            cy = grid_y + row * (card_h + gap)
            is_unlocked = ei in unlocked_effects
            is_equipped = equipped_idx == ei
            if not is_unlocked:
                continue
            btn_y = cy + card_h - 30
            btn_w, btn_h = 80, 24
            if is_equipped:
                btn = ModernButton(cx + card_w - btn_w - 5, btn_y, btn_w, btn_h, "ZRUSIT", pygame.font.Font(None, 18))
                btn.update(mouse_pos); btn.draw(screen)
                if btn.is_clicked(mouse_pos, mouse_clicked): return f"unequip_{cat_type}"
            else:
                btn = ModernButton(cx + card_w - btn_w - 5, btn_y, btn_w, btn_h, "NASADIT", pygame.font.Font(None, 18))
                btn.update(mouse_pos); btn.draw(screen)
                if btn.is_clicked(mouse_pos, mouse_clicked): return f"equip_{ei}"
        self.back_btn.update(mouse_pos); self.back_btn.draw(screen)
        if self.back_btn.is_clicked(mouse_pos, mouse_clicked): return "back"
        return None

    def draw_paywall(self, screen, coins, mouse_pos, mouse_clicked):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((0,0,0,230)); screen.blit(ov, (0,0))
        panel = pygame.Rect(WIDTH//2-350, 20, 700, 700)
        self.draw_glass_panel(screen, panel, 250)
        self.draw_glowing_text(screen, "OBCHOD S MINCAMI", self.font_large, UI_GOLD, (WIDTH//2, 75), 3)
        self.draw_text(screen, f"Tvoj zostatok: {coins} minci", self.font_medium, UI_TEXT_MAIN, WIDTH//2, 120, center=True)
        pw, ph, sy, gap, cx = 300, 75, 145, 18, WIDTH//2
        self.paywall_buttons = []
        for i, pkg in enumerate(COIN_PACKAGES):
            py = sy + i * (ph + gap)
            pkg_rect = pygame.Rect(cx - pw//2, py, pw, ph)
            popular = pkg["name"] == "POPULAR"
            admin_pkg = pkg.get("admin", False)
            cs = pygame.Surface((pw, ph), pygame.SRCALPHA)
            if admin_pkg: cs.fill((80,30,80,255))
            elif popular: cs.fill((50,70,40,255))
            else: cs.fill((30,35,50,255))
            screen.blit(cs, pkg_rect.topleft)
            bc = (200,100,255) if admin_pkg else UI_GOLD if popular else UI_ACCENT
            pygame.draw.rect(screen, bc, pkg_rect, 2, border_radius=8)
            if popular:
                badge = self.font_small.render("NAJLEPSIA PONUKA", True, UI_GOLD)
                screen.blit(badge, badge.get_rect(midtop=(cx, py+2)))
            if admin_pkg:
                badge = self.font_small.render("SPECIALNE PRE ADAMA", True, (200,100,255))
                screen.blit(badge, badge.get_rect(midtop=(cx, py+2)))
            name_y = py + (22 if (popular or admin_pkg) else 6)
            coins_y = name_y + 26
            self.draw_text(screen, pkg["name"], self.font_medium, UI_TEXT_MAIN, pkg_rect.x+20, name_y)
            self.draw_text(screen, f"{pkg['coins']} minci", self.font_small, UI_GOLD, pkg_rect.x+50, coins_y)
            icon_y = coins_y + 10
            pygame.draw.circle(screen, UI_GOLD, (pkg_rect.x+30, icon_y), 9)
            pygame.draw.circle(screen, (200,170,0), (pkg_rect.x+30, icon_y), 9, 2)
            ps = self.font_medium.render(pkg["price"], True, UI_ACCENT if not admin_pkg else (200,100,255))
            screen.blit(ps, ps.get_rect(midright=(pkg_rect.right-15, py+ph//2)))
            btn = ModernButton(pkg_rect.x, pkg_rect.y, pkg_rect.width, pkg_rect.height, "", self.font_small)
            btn.update(mouse_pos)
            self.paywall_buttons.append(btn)
        last_pkg_bottom = sy + (len(COIN_PACKAGES)-1)*(ph+gap)+ph
        self.draw_text(screen, "DEMO - platby nie su aktivne", self.font_small, UI_WARNING, WIDTH//2, last_pkg_bottom+15, center=True)
        self.draw_text(screen, "Mince ziskavas hranim a zbieranim na trati!", self.font_small, UI_TEXT_DIM, WIDTH//2, last_pkg_bottom+38, center=True)
        self.paywall_close_btn.update(mouse_pos); self.paywall_close_btn.draw(screen)
        if self.paywall_close_btn.is_clicked(mouse_pos, mouse_clicked): return "close"
        for i, btn in enumerate(self.paywall_buttons):
            if btn.is_clicked(mouse_pos, mouse_clicked): return f"pkg_{i}"
        return None

    def draw_skin_selector(self, screen, skin_index, unlocked_skins, mouse_pos, mouse_clicked):
        self.draw_animated_bg(screen)
        self.draw_glowing_text(screen, "GARAZ", self.font_large, UI_ACCENT, (WIDTH//2, 50), 3)
        ul = sorted(unlocked_skins) if unlocked_skins else [0]
        cp = 0
        for i, idx in enumerate(ul):
            if idx == skin_index: cp = i; break
        ai = ul[cp]; skin = CAR_SKINS[ai]
        panel = pygame.Rect(WIDTH//2-250, 90, 500, 420)
        self.draw_glass_panel(screen, panel, 230)
        self.draw_text(screen, skin["name"], self.font_large, skin["body"], WIDTH//2, 140, center=True)
        self._draw_car(screen, skin, WIDTH//2, 310, 2.5)
        self.draw_text(screen, f"{cp+1} / {len(ul)}", self.font_small, UI_TEXT_DIM, WIDTH//2, 500, center=True)
        locked = len(CAR_SKINS) - len(unlocked_skins)
        if locked > 0:
            self.draw_text(screen, f"Zamknute: {locked} skinov (kup si lootbox!)", self.font_small, UI_TEXT_DIM, WIDTH//2, 530, center=True)
        self.prev_btn.update(mouse_pos); self.prev_btn.draw(screen)
        self.next_btn.update(mouse_pos); self.next_btn.draw(screen)
        self.select_btn.update(mouse_pos); self.select_btn.draw(screen)
        self.back_btn.update(mouse_pos); self.back_btn.draw(screen)
        if self.prev_btn.is_clicked(mouse_pos, mouse_clicked): return "prev"
        if self.next_btn.is_clicked(mouse_pos, mouse_clicked): return "next"
        if self.select_btn.is_clicked(mouse_pos, mouse_clicked): return "select"
        if self.back_btn.is_clicked(mouse_pos, mouse_clicked): return "back"
        return None

    def _draw_input_box(self, screen, rect, label, value, active=False, placeholder=""):
        self.draw_text(screen, label, self.font_small, UI_TEXT_DIM, rect.x, rect.y - 26)
        pygame.draw.rect(screen, (0, 0, 0), rect, border_radius=8)
        pygame.draw.rect(screen, UI_ACCENT if active else (90, 100, 120), rect, 3 if active else 2, border_radius=8)
        cursor = "_" if active and (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        text = value if value else placeholder
        color = UI_TEXT_MAIN if value else UI_TEXT_DIM
        screen.blit(self.font_medium.render(text + cursor, True, color), (rect.x + 16, rect.y + 14))

    def draw_host_setup(self, screen, host_name, player_count, mouse_pos, mouse_clicked):
        self.draw_animated_bg(screen)
        panel = pygame.Rect(WIDTH // 2 - 360, HEIGHT // 2 - 240, 720, 520)
        self.draw_glass_panel(screen, panel, 238)
        self.draw_glowing_text(screen, "HOST LOBBY", self.font_large, UI_ACCENT, (WIDTH // 2, panel.y + 58), 3)

        name_rect = pygame.Rect(WIDTH // 2 - 260, panel.y + 135, 520, 58)
        self._draw_input_box(screen, name_rect, "MENO HOSTA", host_name, True, "Host")

        self.draw_text(screen, "POCET HRACOV V LOBBY", self.font_small, UI_TEXT_DIM,
                       WIDTH // 2, panel.y + 235, center=True)
        count_rect = pygame.Rect(WIDTH // 2 - 80, panel.y + 260, 160, 70)
        pygame.draw.rect(screen, (0, 0, 0), count_rect, border_radius=10)
        pygame.draw.rect(screen, UI_GOLD, count_rect, 2, border_radius=10)
        self.draw_text(screen, str(player_count), self.font_large, UI_TEXT_MAIN,
                       WIDTH // 2, count_rect.centery + 2, center=True)

        minus_btn = ModernButton(count_rect.x - 85, count_rect.y + 5, 65, 60, "<", self.font_large)
        plus_btn = ModernButton(count_rect.right + 20, count_rect.y + 5, 65, 60, ">", self.font_large)
        minus_btn.update(mouse_pos); minus_btn.draw(screen)
        plus_btn.update(mouse_pos); plus_btn.draw(screen)

        self.draw_text(screen, "Sipky vlavo/vpravo menia pocet hracov.", self.font_small, UI_TEXT_DIM,
                       WIDTH // 2, panel.y + 350, center=True)
        self.setup_create_button.rect.center = (WIDTH // 2, panel.y + 415)
        self.setup_back_button.rect.center = (WIDTH // 2, panel.y + 485)
        self.setup_create_button.update(mouse_pos); self.setup_create_button.draw(screen)
        self.setup_back_button.update(mouse_pos); self.setup_back_button.draw(screen)

        if minus_btn.is_clicked(mouse_pos, mouse_clicked): return "minus"
        if plus_btn.is_clicked(mouse_pos, mouse_clicked): return "plus"
        if self.setup_create_button.is_clicked(mouse_pos, mouse_clicked): return "create"
        if self.setup_back_button.is_clicked(mouse_pos, mouse_clicked): return "back"
        return None

    def draw_join_setup(self, screen, ip_text, name_text, active_field, mouse_pos, mouse_clicked):
        self.draw_animated_bg(screen)
        panel = pygame.Rect(WIDTH // 2 - 380, HEIGHT // 2 - 250, 760, 540)
        self.draw_glass_panel(screen, panel, 238)
        self.draw_glowing_text(screen, "JOIN GAME", self.font_large, UI_ACCENT, (WIDTH // 2, panel.y + 58), 3)

        ip_rect = pygame.Rect(WIDTH // 2 - 280, panel.y + 135, 560, 58)
        name_rect = pygame.Rect(WIDTH // 2 - 280, panel.y + 235, 560, 58)
        self._draw_input_box(screen, ip_rect, "IP HOSTITELA", ip_text, active_field == "ip", "192.168.0.100")
        self._draw_input_box(screen, name_rect, "TVOJE MENO", name_text, active_field == "name", "Player")
        self.draw_text(screen, "TAB prepina pole, ENTER sa pripoji.", self.font_small, UI_TEXT_DIM,
                       WIDTH // 2, panel.y + 330, center=True)

        self.setup_join_button.rect.center = (WIDTH // 2, panel.y + 405)
        self.setup_back_button.rect.center = (WIDTH // 2, panel.y + 475)
        self.setup_join_button.update(mouse_pos); self.setup_join_button.draw(screen)
        self.setup_back_button.update(mouse_pos); self.setup_back_button.draw(screen)

        if mouse_clicked and ip_rect.collidepoint(mouse_pos): return "ip"
        if mouse_clicked and name_rect.collidepoint(mouse_pos): return "name"
        if self.setup_join_button.is_clicked(mouse_pos, mouse_clicked): return "join"
        if self.setup_back_button.is_clicked(mouse_pos, mouse_clicked): return "back"
        return None

    def draw_multiplayer_lobby(self, screen, players, target_count, chat_messages, chat_input,
                               chat_active, is_host, can_start, host_info, local_index,
                               mouse_pos, mouse_clicked):
        self.draw_animated_bg(screen)
        self.draw_glowing_text(screen, "MULTIPLAYER LOBBY", self.font_large, UI_ACCENT,
                               (WIDTH // 2, 54), 3)
        self.draw_text(screen, host_info, self.font_small, UI_TEXT_DIM, WIDTH // 2, 94, center=True)

        left = pygame.Rect(70, 120, 510, 460)
        right = pygame.Rect(620, 120, 590, 460)
        self.draw_glass_panel(screen, left, 230)
        self.draw_glass_panel(screen, right, 230)
        self.draw_text(screen, f"HRACI {len(players)}/{target_count}", self.font_medium, UI_GOLD,
                       left.x + 28, left.y + 22)
        self.draw_text(screen, "CHAT", self.font_medium, UI_GOLD, right.x + 28, right.y + 22)

        local_ready = False
        y = left.y + 78
        for slot in range(target_count):
            row = pygame.Rect(left.x + 24, y, left.width - 48, 48)
            if slot % 2 == 0:
                surf = pygame.Surface((row.width, row.height), pygame.SRCALPHA)
                surf.fill((255, 255, 255, 12))
                screen.blit(surf, row.topleft)
            player = next((p for p in players if p.get("index") == slot), None)
            if player:
                skin_index = player.get("skin_index", 0)
                if not isinstance(skin_index, int):
                    skin_index = 0
                skin = CAR_SKINS[skin_index % len(CAR_SKINS)]
                pygame.draw.circle(screen, skin["body"], (row.x + 22, row.centery), 10)
                name_color = UI_GOLD if player.get("index") == local_index else UI_TEXT_MAIN
                self.draw_text(screen, player.get("name", "Player")[:16], self.font_small, name_color,
                               row.x + 46, row.y + 13)
                badge = "HOST" if player.get("is_host") else ("READY" if player.get("ready") else "WAIT")
                badge_color = UI_GOLD if player.get("is_host") else (GAUGE_LOW if player.get("ready") else UI_WARNING)
                self.draw_text(screen, badge, self.font_tech, badge_color, row.right - 110, row.y + 12)
                if player.get("index") == local_index:
                    local_ready = bool(player.get("ready"))
            else:
                self.draw_text(screen, f"Volny slot {slot + 1}", self.font_small, UI_TEXT_DIM,
                               row.x + 46, row.y + 13)
            y += 58

        chat_y = right.y + 78
        for entry in chat_messages[-8:]:
            sender = str(entry.get("sender", ""))[:14]
            message = str(entry.get("message", ""))[:70]
            self.draw_text(screen, sender + ":", self.font_small, UI_ACCENT, right.x + 28, chat_y)
            self.draw_text(screen, message, self.font_small, UI_TEXT_MAIN, right.x + 170, chat_y)
            chat_y += 38

        input_rect = pygame.Rect(right.x + 24, right.bottom - 72, right.width - 48, 48)
        self._draw_input_box(screen, input_rect, "", chat_input, chat_active, "Klikni alebo ENTER pre chat")

        self.ready_button.text = "UNREADY" if local_ready else "READY"
        self.ready_button.update(mouse_pos); self.ready_button.draw(screen)
        if is_host:
            self.lobby_start_button.text = "START" if can_start else "CAKAJ"
            self.lobby_start_button.update(mouse_pos); self.lobby_start_button.draw(screen)
            if not can_start:
                self.draw_text(screen, "Treba plne lobby a READY od kazdeho.", self.font_small, UI_TEXT_DIM,
                               WIDTH // 2, HEIGHT - 105, center=True)
        self.lobby_back_button.update(mouse_pos); self.lobby_back_button.draw(screen)

        if mouse_clicked and input_rect.collidepoint(mouse_pos): return "chat"
        if self.ready_button.is_clicked(mouse_pos, mouse_clicked): return "ready"
        if is_host and can_start and self.lobby_start_button.is_clicked(mouse_pos, mouse_clicked): return "start"
        if self.lobby_back_button.is_clicked(mouse_pos, mouse_clicked): return "back"
        return None

    def draw_countdown_lights(self, screen, countdown_value):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 145))
        screen.blit(ov, (0, 0))
        panel = pygame.Rect(WIDTH // 2 - 310, 95, 620, 230)
        self.draw_glass_panel(screen, panel, 245)
        self.draw_text(screen, "STARTING GRID", self.font_medium, UI_GOLD,
                       WIDTH // 2, panel.y + 35, center=True)
        light_y = panel.y + 120
        radius = 34
        gap = 88
        active_count = MULTIPLAYER_COUNTDOWN_SECONDS - max(1, countdown_value) + 1
        for i in range(MULTIPLAYER_COUNTDOWN_SECONDS):
            x = WIDTH // 2 - gap * 2 + i * gap
            pygame.draw.circle(screen, (20, 20, 25), (x, light_y), radius + 6)
            if countdown_value <= 0:
                color = GAUGE_LOW
            elif i < active_count:
                color = UI_WARNING
            else:
                color = (55, 25, 30)
            pygame.draw.circle(screen, color, (x, light_y), radius)
            pygame.draw.circle(screen, (255, 255, 255), (x - 10, light_y - 10), 7)
        label = "GO!" if countdown_value <= 0 else str(countdown_value)
        self.draw_glowing_text(screen, label, self.font_large,
                               GAUGE_LOW if countdown_value <= 0 else UI_WARNING,
                               (WIDTH // 2, panel.y + 190), 3)

    def draw_spectator_banner(self, screen):
        banner = pygame.Rect(WIDTH // 2 - 190, 58, 380, 42)
        surf = pygame.Surface((banner.width, banner.height), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 185))
        screen.blit(surf, banner.topleft)
        pygame.draw.rect(screen, UI_WARNING, banner, 2, border_radius=8)
        self.draw_text(screen, "SPECTATING - si vyradeny", self.font_small, UI_WARNING,
                       banner.centerx, banner.centery + 1, center=True)

    def draw_multiplayer_leaderboard(self, screen, results, is_host, mouse_pos, mouse_clicked):
        self.draw_animated_bg(screen)
        panel = pygame.Rect(WIDTH // 2 - 380, 70, 760, 560)
        self.draw_glass_panel(screen, panel, 245)
        self.draw_glowing_text(screen, "ROUND LEADERBOARD", self.font_large, UI_GOLD,
                               (WIDTH // 2, panel.y + 55), 3)
        headers_y = panel.y + 120
        self.draw_text(screen, "#", self.font_small, UI_TEXT_DIM, panel.x + 55, headers_y)
        self.draw_text(screen, "MENO", self.font_small, UI_TEXT_DIM, panel.x + 120, headers_y)
        self.draw_text(screen, "CAS", self.font_small, UI_TEXT_DIM, panel.x + 410, headers_y)
        self.draw_text(screen, "STAV", self.font_small, UI_TEXT_DIM, panel.x + 560, headers_y)
        y = headers_y + 38
        for result in results[:8]:
            color = UI_GOLD if result.get("place") == 1 else UI_TEXT_MAIN
            self.draw_text(screen, str(result.get("place", "-")), self.font_small, color, panel.x + 55, y)
            self.draw_text(screen, str(result.get("name", "Player"))[:18], self.font_small, color, panel.x + 120, y)
            self.draw_text(screen, f"{float(result.get('duration', 0.0)):.2f}s", self.font_tech, UI_ACCENT,
                           panel.x + 410, y)
            state = "OUT" if result.get("crashed", False) else "WIN"
            self.draw_text(screen, state, self.font_tech, UI_WARNING if state == "OUT" else GAUGE_LOW,
                           panel.x + 560, y)
            y += 42
        if is_host:
            self.continue_button.text = "LOBBY"
            self.continue_button.rect.center = (WIDTH // 2, panel.bottom - 50)
            self.continue_button.update(mouse_pos); self.continue_button.draw(screen)
            if self.continue_button.is_clicked(mouse_pos, mouse_clicked): return "lobby"
        else:
            self.draw_text(screen, "Cakam, kym host vrati lobby...", self.font_small, UI_TEXT_DIM,
                           WIDTH // 2, panel.bottom - 50, center=True)
        return None

    def draw_multiplayer_setup(self, screen, title, prompt, current_text, mouse_pos, mouse_clicked):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((0,0,0,220)); screen.blit(ov, (0,0))
        pr = pygame.Rect(WIDTH//2-360, HEIGHT//2-180, 720, 500)
        self.draw_glass_panel(screen, pr, 235)
        self.draw_text(screen, title, self.font_large, UI_ACCENT, WIDTH//2, pr.y+70, center=True)
        self.draw_text(screen, prompt, self.font_medium, UI_TEXT_MAIN, WIDTH//2, pr.y+150, center=True)
        self.draw_text(screen, "Podpora formatu: 192.168.0.100 alebo 10.0.0.5", self.font_small, UI_TEXT_DIM, WIDTH//2, pr.y+190, center=True)
        ir = pygame.Rect(WIDTH//2-260, pr.y+220, 520, 60)
        pygame.draw.rect(screen, (0,0,0), ir, border_radius=10)
        pygame.draw.rect(screen, UI_ACCENT, ir, 3, border_radius=10)
        cursor = "_" if (pygame.time.get_ticks()//500)%2==0 else ""
        d = current_text if current_text else "IP hostitela..."
        tc = UI_TEXT_MAIN if current_text else UI_TEXT_DIM
        screen.blit(self.font_medium.render(d+cursor, True, tc), (ir.x+20, ir.y+15))
        self.setup_join_button.rect.center = (WIDTH//2, ir.y+80+30)
        self.setup_back_button.rect.center = (WIDTH//2, ir.y+150+30)
        self.setup_join_button.update(mouse_pos); self.setup_join_button.draw(screen)
        self.setup_back_button.update(mouse_pos); self.setup_back_button.draw(screen)
        if self.setup_join_button.is_clicked(mouse_pos, mouse_clicked): return "join"
        if self.setup_back_button.is_clicked(mouse_pos, mouse_clicked): return "back"
        return None

    def draw_connection_status(self, screen, title, status, details=None):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((0,0,0,220)); screen.blit(ov, (0,0))
        pr = pygame.Rect(WIDTH//2-360, HEIGHT//2-180, 720, 360)
        self.draw_glass_panel(screen, pr, 235)
        self.draw_text(screen, title, self.font_large, UI_ACCENT, WIDTH//2, pr.y+80, center=True)
        self.draw_text(screen, status, self.font_medium, UI_TEXT_MAIN, WIDTH//2, pr.y+170, center=True)
        if details:
            self.draw_text(screen, details, self.font_small, UI_TEXT_DIM, WIDTH//2, pr.y+220, center=True)

    def draw_multiplayer_result(self, screen, result_text):
        ov = pygame.Surface((WIDTH, HEIGHT)); ov.set_alpha(220); ov.fill((5,5,10)); screen.blit(ov, (0,0))
        pr = pygame.Rect(WIDTH//2-360, HEIGHT//2-180, 720, 360)
        self.draw_glass_panel(screen, pr, 245)
        self.draw_glowing_text(screen, result_text, self.font_large, UI_GOLD, (WIDTH//2, pr.y+120))
        self.draw_text(screen, "Stlac R pre rematch alebo ESC pre navrat do menu", self.font_small, UI_TEXT_DIM, WIDTH//2, pr.y+220, center=True)

    def draw_leaderboard(self, screen, highscores):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((0,0,0,215)); screen.blit(ov, (0,0))
        pr = pygame.Rect(WIDTH//2-250, HEIGHT//2-340, 500, 680)
        self.draw_glass_panel(screen, pr, 245)
        self.draw_glowing_text(screen, "TOP 20 REKORDOV", self.font_medium, UI_GOLD, (WIDTH//2, pr.y+45))
        yo = pr.y + 110
        for i, e in enumerate(highscores[:20]):
            c = UI_GOLD if i==0 else UI_TEXT_MAIN
            if i%2==0:
                s = pygame.Surface((pr.width-40, 24), pygame.SRCALPHA); s.fill((255,255,255,10)); screen.blit(s, (pr.x+20, yo-2))
            self.draw_text(screen, f"{i+1}.", self.font_small, c, pr.x+40, yo)
            self.draw_text(screen, e['name'][:15], self.font_small, UI_TEXT_MAIN, pr.x+100, yo)
            self.draw_text(screen, f"{int(e['score']):06d}", self.font_tech, UI_ACCENT, pr.right-120, yo)
            yo += 27

    def draw_hud(self, screen, score, speed, audio_manager, coins=0):
        th = 50
        s = pygame.Surface((WIDTH, th)); s.set_alpha(230); s.fill((10,10,15)); screen.blit(s, (0,0))
        pygame.draw.line(screen, UI_ACCENT, (0, th), (WIDTH, th), 2)
        self.draw_text(screen, "SCORE", self.font_small, UI_TEXT_DIM, 40, 12)
        screen.blit(self.font_tech.render(f"{int(score):06d}", True, UI_TEXT_MAIN), (130, 10))
        self.draw_text(screen, f"${coins}", self.font_tech, UI_GOLD, 280, 10)
        vp = int(audio_manager.engine_volume*100) if not audio_manager.muted else 0
        vc = UI_ACCENT if not audio_manager.muted else UI_WARNING
        vt = f"VOL: {vp}%" if not audio_manager.muted else "MUTE"
        self.draw_text(screen, vt, self.font_tech, vc, 380, 10)
        lv = int(score // DIFFICULTY_INCREASE_INTERVAL) + 1
        lr = self.draw_text(screen, f"STAGE {lv}", self.font_medium, UI_GOLD, WIDTH//2, 25, center=True)
        pygame.draw.circle(screen, UI_WARNING, (lr.left-20, 25), 5)
        pygame.draw.circle(screen, UI_WARNING, (lr.right+20, 25), 5)
        self.draw_digital_tachometer(screen, speed)

    def draw_digital_tachometer(self, screen, speed):
        pw, ph = 200, 140
        px, py = WIDTH - pw - 20, 70
        pr = pygame.Rect(px, py, pw, ph)
        s = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(s, (*UI_PANEL_BG, 240), s.get_rect(), border_radius=10)
        screen.blit(s, (px, py))
        pygame.draw.rect(screen, UI_ACCENT, pr, 2, border_radius=10)
        cs, ct = 15, 3
        corners = [[(px,py),(px+cs,py)],[(px,py),(px,py+cs)],[(px+pw,py),(px+pw-cs,py)],[(px+pw,py),(px+pw,py+cs)],
                   [(px,py+ph),(px+cs,py+ph)],[(px,py+ph),(px,py+ph-cs)],[(px+pw,py+ph),(px+pw-cs,py+ph)],[(px+pw,py+ph),(px+pw,py+ph-cs)]]
        for c in corners: pygame.draw.line(screen, UI_ACCENT, c[0], c[1], ct)
        self.draw_text(screen, "SPEED", self.font_small, UI_TEXT_DIM, px+pw//2, py+20, center=True)
        sv = int(speed*18); sr = min(speed/MAX_SCROLL_SPEED, 1.0)
        color = GAUGE_LOW if sr<0.5 else GAUGE_MID if sr<0.8 else GAUGE_HIGH
        sf = pygame.font.Font(None, 70); st = str(sv)
        for ox in range(-2,3):
            for oy in range(-2,3):
                if ox!=0 or oy!=0:
                    g = sf.render(st, True, color); g.set_alpha(20)
                    screen.blit(g, g.get_rect(center=(px+pw//2+ox, py+70+oy)))
        main_speed_surf = sf.render(st, True, (255, 255, 255))
        screen.blit(main_speed_surf, main_speed_surf.get_rect(center=(px + pw // 2, py + 70)))
        self.draw_text(screen, "KM/H", self.font_tech, UI_TEXT_DIM, px+pw//2, py+105, center=True)
        bw, bh2 = pw-40, 6; bx, by = px+20, py+ph-20
        pygame.draw.rect(screen, (30,30,40), (bx, by, bw, bh2), border_radius=3)
        fw = int(bw * sr)
        if fw > 0:
            pygame.draw.rect(screen, color, (bx, by, fw, bh2), border_radius=3)
            for i in range(0, fw, 2):
                pa = int(50+50*math.sin(self.time_tracker*0.1+i*0.1))
                ps = pygame.Surface((2, bh2), pygame.SRCALPHA); ps.fill((*color, pa)); screen.blit(ps, (bx+i, by))

    def draw_game_over_screen(self, screen, score, is_highscore, coins_earned, mouse_pos, mouse_clicked):
        ov = pygame.Surface((WIDTH, HEIGHT)); ov.set_alpha(240); ov.fill((5,5,10)); screen.blit(ov, (0,0))
        pw2, ph2 = 600, 440
        px2, py2 = WIDTH//2-pw2//2, HEIGHT//2-ph2//2
        pr = pygame.Rect(px2, py2, pw2, ph2)
        gr = pr.copy(); gr.inflate_ip(20, 20)
        pygame.draw.rect(screen, (UI_WARNING[0], UI_WARNING[1], UI_WARNING[2], 50), gr, border_radius=20)
        self.draw_glass_panel(screen, pr, 255)
        title = "MISSION FAILED" if not is_highscore else "NEW RECORD!"
        color = UI_WARNING if not is_highscore else UI_GOLD
        self.draw_glowing_text(screen, title, self.font_large, color, (WIDTH//2, py2+50))
        pygame.draw.rect(screen, (0,0,0), (WIDTH//2-150, py2+100, 300, 80), border_radius=10)
        pygame.draw.rect(screen, color, (WIDTH//2-150, py2+100, 300, 80), 2, border_radius=10)
        self.draw_text(screen, "FINAL SCORE", self.font_small, UI_TEXT_DIM, WIDTH//2, py2+115, center=True)
        self.draw_text(screen, str(int(score)), self.font_large, (255,255,255), WIDTH//2, py2+150, center=True)
        self.draw_text(screen, f"Mince ziskane: +{coins_earned}", self.font_medium, UI_GOLD, WIDTH//2, py2+210, center=True)
        if is_highscore:
            self.draw_text(screen, "Zadaj meno a stlac ENTER", self.font_small, UI_ACCENT, WIDTH//2, py2+260, center=True)
        else:
            self.continue_button.text = "POKRACOVAT"
            self.continue_button.rect.center = (WIDTH//2, py2+320)
            self.continue_button.update(mouse_pos); self.continue_button.draw(screen)
            return self.continue_button.is_clicked(mouse_pos, mouse_clicked)
        return False

    def draw_name_input(self, screen, name):
        ir = pygame.Rect(WIDTH//2-200, HEIGHT//2+50, 400, 60)
        pygame.draw.rect(screen, (0,0,0), ir, border_radius=5)
        pygame.draw.rect(screen, UI_ACCENT, ir, 2, border_radius=5)
        cursor = "_" if (pygame.time.get_ticks()//500)%2==0 else ""
        screen.blit(self.font_medium.render(name+cursor, True, UI_TEXT_MAIN), (ir.x+20, ir.y+15))

    def draw_collection(self, screen, unlocked_skins, mouse_pos, mouse_clicked):
        self.draw_animated_bg(screen)
        self.draw_glowing_text(screen, "KOLEKCIA", self.font_large, UI_ACCENT, (WIDTH//2, 45), 3)
        total = len(CAR_SKINS)
        unlocked = len(unlocked_skins)
        pct = int(100 * unlocked / total) if total > 0 else 0
        bar_w, bar_h = 500, 20
        bar_x, bar_y = WIDTH//2 - bar_w//2, 85
        pygame.draw.rect(screen, (30,30,40), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
        fill_w = int(bar_w * unlocked / total) if total > 0 else 0
        if fill_w > 0:
            pygame.draw.rect(screen, UI_ACCENT, (bar_x, bar_y, fill_w, bar_h), border_radius=10)
        self.draw_text(screen, f"{unlocked}/{total} ({pct}%)", self.font_small, UI_TEXT_MAIN, WIDTH//2, bar_y+bar_h//2+1, center=True)
        if unlocked == total:
            self.draw_text(screen, "KOMPLETNA KOLEKCIA! +500 minci bonus", self.font_small, UI_GOLD, WIDTH//2, bar_y+bar_h+22, center=True)
        else:
            missing = total - unlocked
            self.draw_text(screen, f"Chyba ti {missing} skinov - otvor lootbox!", self.font_small, UI_TEXT_DIM, WIDTH//2, bar_y+bar_h+22, center=True)
        cols = 4
        card_w, card_h = 140, 180
        gap_x, gap_y = 18, 18
        grid_w = cols * card_w + (cols-1) * gap_x
        grid_x = WIDTH//2 - grid_w//2
        grid_y = 155
        for i, skin in enumerate(CAR_SKINS):
            row = i // cols
            col = i % cols
            cx = grid_x + col * (card_w + gap_x)
            cy = grid_y + row * (card_h + gap_y)
            is_unlocked = i in unlocked_skins
            rarity = skin.get("rarity", RARITY_COMMON)
            rc = RARITY_COLORS.get(rarity, UI_TEXT_DIM)
            card_rect = pygame.Rect(cx, cy, card_w, card_h)
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if is_unlocked: card_surf.fill((30,35,55,240))
            else: card_surf.fill((15,15,22,240))
            screen.blit(card_surf, (cx, cy))
            pygame.draw.rect(screen, rc if is_unlocked else (50,50,60), card_rect, 2, border_radius=6)
            if is_unlocked:
                rar_label = RARITY_LABELS.get(rarity, "")
                rl_surf = pygame.font.Font(None, 16).render(rar_label, True, rc)
                screen.blit(rl_surf, rl_surf.get_rect(midtop=(cx+card_w//2, cy+5)))
                self._draw_car(screen, skin, cx+card_w//2, cy+105, 0.8)
                nm_surf = pygame.font.Font(None, 20).render(skin["name"], True, UI_TEXT_MAIN)
                screen.blit(nm_surf, nm_surf.get_rect(midbottom=(cx+card_w//2, cy+card_h-6)))
            else:
                dark_skin = {k: (30,30,40) if k in ("body","spoiler","wing","helmet") else v for k, v in skin.items()}
                self._draw_car(screen, dark_skin, cx+card_w//2, cy+105, 0.8)
                lock_font = pygame.font.Font(None, 40)
                lock_surf = lock_font.render("?", True, (60,60,80))
                screen.blit(lock_surf, lock_surf.get_rect(center=(cx+card_w//2, cy+90)))
                rar_label = RARITY_LABELS.get(rarity, "")
                rl_surf = pygame.font.Font(None, 16).render(rar_label, True, (60,60,80))
                screen.blit(rl_surf, rl_surf.get_rect(midtop=(cx+card_w//2, cy+5)))
                lk_surf = pygame.font.Font(None, 18).render("ZAMKNUTY", True, (70,70,90))
                screen.blit(lk_surf, lk_surf.get_rect(midbottom=(cx+card_w//2, cy+card_h-6)))
        self.back_btn.update(mouse_pos); self.back_btn.draw(screen)
        if self.back_btn.is_clicked(mouse_pos, mouse_clicked): return "back"
        return None

    def draw_text(self, screen, text, font, color, x, y, center=False):
        ts = font.render(text, True, color)
        tr = ts.get_rect()
        if center: tr.center = (x, y)
        else: tr.topleft = (x, y)
        screen.blit(ts, tr)
        return tr

import pygame
import math
from src.settings import *


class ModernButton:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hover_progress = 0.0
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * 0.2

    def draw(self, screen):
        alpha = int(180 + 75 * self.hover_progress)
        bg_color = (
            int(UI_PANEL_BG[0] + (UI_ACCENT[0] - UI_PANEL_BG[0]) * 0.1 * self.hover_progress),
            int(UI_PANEL_BG[1] + (UI_ACCENT[1] - UI_PANEL_BG[1]) * 0.1 * self.hover_progress),
            int(UI_PANEL_BG[2] + (UI_ACCENT[2] - UI_PANEL_BG[2]) * 0.1 * self.hover_progress),
        )
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*bg_color, alpha), s.get_rect(), border_radius=12)
        border_color = (
            int(100 + (UI_ACCENT[0] - 100) * self.hover_progress),
            int(100 + (UI_ACCENT[1] - 100) * self.hover_progress),
            int(100 + (UI_ACCENT[2] - 100) * self.hover_progress)
        )
        border_width = 2 if self.hover_progress < 0.5 else 3
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
        if self.hover_progress > 0.1:
            glow_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 5, self.rect.width + 10, self.rect.height + 10)
            pygame.draw.rect(screen, (*UI_ACCENT, int(30 * self.hover_progress)), glow_rect, 2, border_radius=15)

    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.is_hovered and mouse_clicked


class UIManager:
    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("impact", 100)
        if not self.font_title:
            self.font_title = pygame.font.Font(None, 100)
        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tech = pygame.font.SysFont("consolas", 24, bold=True)

        bw, bh = 320, 55
        cx = WIDTH // 2 - bw // 2
        self.start_button = ModernButton(cx, 250, bw, bh, "START RACE", self.font_medium)
        self.skins_button = ModernButton(cx, 320, bw, bh, "GARAZ", self.font_medium)
        self.lootbox_button = ModernButton(cx, 390, bw, bh, "LOOTBOX", self.font_medium)
        self.host_button = ModernButton(cx, 460, bw, bh, "HOST GAME", self.font_medium)
        self.join_button = ModernButton(cx, 530, bw, bh, "JOIN GAME", self.font_medium)
        self.continue_button = ModernButton(cx, HEIGHT // 2 + 80, bw, bh, "POKRAČOVAŤ", self.font_medium)
        self.setup_join_button = ModernButton(cx, HEIGHT // 2 + 40, bw, 60, "PRIPOJIŤ SA", self.font_medium)
        self.setup_back_button = ModernButton(cx, HEIGHT // 2 + 110, bw, 60, "SPÄŤ", self.font_medium)
        self.back_btn = ModernButton(cx, HEIGHT - 80, bw, 50, "SPÄŤ", self.font_medium)
        self.buy_box_btn = ModernButton(cx, HEIGHT // 2 + 160, bw, 55, f"KÚPIŤ BOX ({LOOTBOX_COST}c)", self.font_medium)
        self.buy_coins_btn = ModernButton(cx, HEIGHT // 2 + 230, bw, 50, "KÚPIŤ MINCE", self.font_medium)
        self.prev_btn = ModernButton(WIDTH // 2 - 320, HEIGHT // 2 - 30, 80, 80, "<", self.font_large)
        self.next_btn = ModernButton(WIDTH // 2 + 240, HEIGHT // 2 - 30, 80, 80, ">", self.font_large)
        self.select_btn = ModernButton(cx, HEIGHT // 2 + 180, bw, 55, "VYBRAŤ", self.font_medium)
        self.paywall_close_btn = ModernButton(cx, HEIGHT - 70, bw, 50, "ZAVRIEŤ", self.font_medium)
        self.paywall_buttons = []
        self.time_tracker = 0

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
        screen.blit(shadow, shadow.get_rect(center=(WIDTH//2+5, 105)))
        self.draw_glowing_text(screen, "F1 TURBO", self.font_title, UI_ACCENT, (WIDTH//2, 100), 4)
        self.draw_text(screen, "ULTIMATE RACING EXPERIENCE", self.font_small, UI_TEXT_DIM, WIDTH//2, 155, center=True)
        self.draw_text(screen, f"COINS: {coins}", self.font_tech, UI_GOLD, WIDTH-260, 155)
        for b in [self.start_button, self.skins_button, self.lootbox_button, self.host_button, self.join_button]:
            b.update(mouse_pos); b.draw(screen)
        pr = pygame.Rect(WIDTH//2-350, 600, 700, 120)
        self.draw_glass_panel(screen, pr)
        self.draw_text(screen, "TOP JAZDCI", self.font_medium, UI_GOLD, WIDTH//2, 620, center=True)
        yo = 648
        for i, e in enumerate(highscores[:3]):
            c = UI_GOLD if i==0 else UI_TEXT_MAIN
            self.draw_text(screen, f"{i+1}.", self.font_small, c, pr.x+150, yo)
            self.draw_text(screen, e['name'][:12], self.font_small, UI_TEXT_DIM, pr.x+200, yo)
            screen.blit(self.font_tech.render(f"{int(e['score']):05d}", True, UI_ACCENT), (pr.right-200, yo))
            yo += 30
        self.draw_text(screen, "[ TAB: TOP 20 ] [ ESC: PAUZA ] [ M: MUTE ]", self.font_tech, (80,80,100), WIDTH//2, HEIGHT-20, center=True)
        if self.start_button.is_clicked(mouse_pos, mouse_clicked): return "single"
        if self.skins_button.is_clicked(mouse_pos, mouse_clicked): return "skins"
        if self.lootbox_button.is_clicked(mouse_pos, mouse_clicked): return "lootbox"
        if self.host_button.is_clicked(mouse_pos, mouse_clicked): return "host"
        if self.join_button.is_clicked(mouse_pos, mouse_clicked): return "join"
        return None

    def draw_lootbox_shop(self, screen, coins, unlocked_count, total_count, mouse_pos, mouse_clicked, result_info=None):
        self.draw_animated_bg(screen)
        self.draw_glowing_text(screen, "LOOTBOX", self.font_large, UI_GOLD, (WIDTH//2, 55), 3)
        self.draw_text(screen, f"Tvoje mince: {coins}", self.font_medium, UI_GOLD, WIDTH//2, 110, center=True)
        self.draw_text(screen, f"Odomknute: {unlocked_count}/{total_count}", self.font_small, UI_TEXT_DIM, WIDTH//2, 145, center=True)
        pr = pygame.Rect(WIDTH//2-250, 170, 500, 260)
        self.draw_glass_panel(screen, pr, 230)
        bx, by = WIDTH//2, 280
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
                self.draw_text(screen, "Nemas dostatok minci!", self.font_small, UI_WARNING, WIDTH//2, HEIGHT//2+225, center=True)
            self.buy_coins_btn.update(mouse_pos); self.buy_coins_btn.draw(screen)
            if self.buy_box_btn.is_clicked(mouse_pos, mouse_clicked) and can_buy: return "buy"
            if self.buy_coins_btn.is_clicked(mouse_pos, mouse_clicked): return "paywall"
        self.back_btn.update(mouse_pos); self.back_btn.draw(screen)
        if self.back_btn.is_clicked(mouse_pos, mouse_clicked): return "back"
        return None

    def _draw_lootbox_result(self, screen, info):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((0,0,0,180)); screen.blit(ov, (0,0))
        pr = pygame.Rect(WIDTH//2-250, HEIGHT//2-160, 500, 320)
        self.draw_glass_panel(screen, pr, 250)
        if info.get("is_new"):
            self.draw_glowing_text(screen, "NOVY SKIN!", self.font_large, UI_GOLD, (WIDTH//2, pr.y+50), 3)
            skin = CAR_SKINS[info.get("skin_index", 0)]
            self.draw_text(screen, info.get("skin_name",""), self.font_large, skin["body"], WIDTH//2, pr.y+120, center=True)
            self._draw_car(screen, skin, WIDTH//2, pr.y+210, 2.0)
        else:
            self.draw_glowing_text(screen, "DUPLIKAT!", self.font_large, UI_WARNING, (WIDTH//2, pr.y+50), 3)
            self.draw_text(screen, f"{info.get('skin_name','')} (uz mas)", self.font_medium, UI_TEXT_DIM, WIDTH//2, pr.y+120, center=True)
            self.draw_text(screen, f"Vratene: +{info.get('refund',0)} minci", self.font_medium, UI_GOLD, WIDTH//2, pr.y+175, center=True)
        self.draw_text(screen, "Klikni pre pokracovanie", self.font_small, UI_TEXT_DIM, WIDTH//2, pr.y+280, center=True)

    def draw_paywall(self, screen, coins, mouse_pos, mouse_clicked):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((0,0,0,230)); screen.blit(ov, (0,0))
        panel = pygame.Rect(WIDTH//2-350, 30, 700, 650)
        self.draw_glass_panel(screen, panel, 250)
        self.draw_glowing_text(screen, "OBCHOD S MINCAMI", self.font_large, UI_GOLD, (WIDTH//2, 75), 3)
        self.draw_text(screen, f"Tvoj zostatok: {coins} minci", self.font_medium, UI_TEXT_MAIN, WIDTH//2, 120, center=True)
        pw, ph, sy, gap, cx = 300, 105, 165, 15, WIDTH//2
        self.paywall_buttons = []
        for i, pkg in enumerate(COIN_PACKAGES):
            py = sy + i * (ph + gap)
            pkg_rect = pygame.Rect(cx - pw//2, py, pw, ph)
            popular = pkg["name"] == "POPULAR"
            cs = pygame.Surface((pw, ph), pygame.SRCALPHA)
            cs.fill(((50,70,40) if popular else (30,35,50), 255))
            screen.blit(cs, pkg_rect.topleft)
            bc = UI_GOLD if popular else UI_ACCENT
            pygame.draw.rect(screen, bc, pkg_rect, 2, border_radius=8)
            if popular:
                badge = self.font_small.render("NAJLEPSIA PONUKA", True, UI_GOLD)
                screen.blit(badge, badge.get_rect(center=(cx, py - 2)))
            self.draw_text(screen, pkg["name"], self.font_medium, UI_TEXT_MAIN, pkg_rect.x + 20, py + 8)
            self.draw_text(screen, f"{pkg['coins']} minci", self.font_small, UI_GOLD, pkg_rect.x + 20, py + 42)
            # Coin icon
            pygame.draw.circle(screen, UI_GOLD, (pkg_rect.x + 25, py + 75), 10)
            pygame.draw.circle(screen, (200,170,0), (pkg_rect.x + 25, py + 75), 10, 2)
            # Price
            ps = self.font_medium.render(pkg["price"], True, UI_ACCENT)
            screen.blit(ps, ps.get_rect(midright=(pkg_rect.right - 15, py + ph//2)))
            btn = ModernButton(pkg_rect.x, pkg_rect.y, pkg_rect.width, pkg_rect.height, "", self.font_small)
            btn.update(mouse_pos)
            self.paywall_buttons.append(btn)
        self.draw_text(screen, "DEMO - platby nie su aktivne", self.font_small, UI_WARNING, WIDTH//2, panel.bottom - 65, center=True)
        self.draw_text(screen, "Mince ziskavas hranim a zbieranim na trati!", self.font_small, UI_TEXT_DIM, WIDTH//2, panel.bottom - 40, center=True)
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
        screen.blit(sf.render(st, True, (255,255,255)), sf.get_rect(center=(px+pw//2, py+70)))
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

    def draw_text(self, screen, text, font, color, x, y, center=False):
        ts = font.render(text, True, color)
        tr = ts.get_rect()
        if center: tr.center = (x, y)
        else: tr.topleft = (x, y)
        screen.blit(ts, tr)
        return tr

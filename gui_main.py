# gui_main.py
import pygame
import math
import sys
from settings import MAP_SIZE, STATION_ID
from LOOP import GameEngine
from mechanics import process_arrival

# === 視覺設定 ===
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
BG_COLOR = (20, 20, 30)
NODE_COLOR = (60, 60, 80)
TEXT_COLOR = (200, 200, 200)
HIGHLIGHT_COLOR = (255, 215, 0)
BTN_COLOR = (50, 50, 70)
BTN_HOVER_COLOR = (70, 70, 90)

# 精神條與墓碑顏色
BAR_BG_COLOR = (50, 0, 0)
BAR_FILL_COLOR = (0, 200, 100)
BAR_LOW_COLOR = (200, 50, 50)
GRAVE_COLOR = (80, 80, 80)
GRAVE_TEXT_COLOR = (150, 150, 150)

# 推理介面設定
POSSIBLE_ROLES = ["一般人", "殺手", "散播者", "醫生", "邪教徒", "關鍵人物"]
SOLVE_PANEL_COLOR = (40, 40, 50)

CENTER_X, CENTER_Y = SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2
RADIUS = 250
NODE_RADIUS = 30

class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.hovered = False

    def draw(self, screen, font):
        color = BTN_HOVER_COLOR if self.hovered else BTN_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (100,100,100), self.rect, 2, border_radius=5)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.callback()
            return True
        return False

class GameVisualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Loop Game - Final Ver.")
        try:
            self.font = pygame.font.SysFont("Microsoft JhengHei", 16)
            self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        except:
            self.font = pygame.font.SysFont("Arial", 16)
            self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        
        self.engine = GameEngine()
        self.log_messages = ["遊戲開始... 按 [Next Phase] 推進"]
        
        self.selected_char = None
        self.action_mode = None 
        self.phase_idx = 0
        self.phases = ["日出", "早上", "中午", "黃昏", "夜晚"]
        
        panel_x = SCREEN_WIDTH - 280
        y_start = 120
        self.buttons = [
            Button(panel_x, y_start, 120, 40, "Next Phase", self.next_phase),
            Button(panel_x, y_start + 60, 100, 35, "Swap (交換)", lambda: self.set_mode("SWAP")),
            Button(panel_x + 110, y_start + 60, 100, 35, "Move (移動)", lambda: self.set_mode("MOVE")),
            Button(panel_x, y_start + 100, 100, 35, "Ask (詢問)", self.action_ask),
            Button(panel_x + 110, y_start + 100, 100, 35, "Mark (標記)", self.action_mark),
            Button(panel_x, y_start + 140, 210, 35, "Solve (推理)", self.action_solve),
        ]

        # 推理介面變數
        self.is_solving = False
        self.show_result = False
        self.result_message = ""
        self.guess_indices = {} 
        for char in self.engine.characters:
            self.guess_indices[char.id] = 0

    def log(self, text):
        print(text)
        self.log_messages.insert(0, text)
        if len(self.log_messages) > 18:
            self.log_messages.pop()

    def next_phase(self):
        if self.show_result or self.is_solving: return
        current_phase = self.phases[self.phase_idx]
        if current_phase == "中午":
            self.log(">>> 結束中午行動")
        
        self.phase_idx = (self.phase_idx + 1) % len(self.phases)
        new_phase = self.phases[self.phase_idx]
        self.log(f"--- 进入階段: {new_phase} ---")
        
        if new_phase == "日出": self.engine.phase_sunrise()
        elif new_phase == "早上": self.engine.phase_morning()
        elif new_phase == "中午": 
            self.engine.phase_noon()
            self.log("請點擊角色並選擇行動...")
        elif new_phase == "黃昏": self.engine.phase_dusk()
        elif new_phase == "夜晚": self.engine.phase_night()

    def set_mode(self, mode):
        if self.phases[self.phase_idx] != "中午":
            self.log("⚠️ 只有中午可以行動")
            return
        if not self.selected_char:
            self.log("請先點擊選擇一位角色")
            return
        self.action_mode = mode
        self.log(f"模式已切換為: {mode}，請選擇目標...")

    def handle_map_click(self, pos):
        clicked_char = None
        char_positions = self.get_all_char_positions()
        for char, char_pos in char_positions:
            if math.hypot(pos[0] - char_pos[0], pos[1] - char_pos[1]) < 20:
                clicked_char = char
                break
        
        clicked_loc = None
        for i in range(MAP_SIZE):
            node_pos = self.get_node_pos(i)
            if math.hypot(pos[0] - node_pos[0], pos[1] - node_pos[1]) < NODE_RADIUS:
                clicked_loc = i
                break
        if math.hypot(pos[0] - CENTER_X, pos[1] - CENTER_Y) < 60:
            clicked_loc = STATION_ID

        if self.action_mode == "SWAP":
            if clicked_char and clicked_char != self.selected_char:
                c1, c2 = self.selected_char, clicked_char
                if c1.location == STATION_ID or c2.location == STATION_ID:
                    self.log("❌ 車站內無法交換")
                else:
                    self.log(f"🔄 交換: {c1.name} <-> {c2.name}")
                    c1.location, c2.location = c2.location, c1.location 
                self.action_mode = None
                self.selected_char = None
        elif self.action_mode == "MOVE":
            if clicked_loc is not None:
                if self.selected_char.location == STATION_ID:
                    self.log(f"🚑 救出: {self.selected_char.name} -> Loc{clicked_loc}")
                    process_arrival(self.selected_char, clicked_loc)
                else:
                    self.log("❌ 只能移動車站內的角色")
                self.action_mode = None
                self.selected_char = None
        else:
            if clicked_char:
                self.selected_char = clicked_char
                self.log(f"已選中: {clicked_char.name}")

    def action_ask(self):
        if self.phases[self.phase_idx] != "中午" or not self.selected_char: return
        target = self.selected_char
        if target.intrigue:
            self.log("❌ 對方笑容詭異，無法溝通！")
        else:
            target.known = True
            self.log(f"🔍 確認身分: {target.name} 是 {target.role}")

    def action_mark(self):
        if not self.selected_char: return
        if self.selected_char.guess_role is None:
            self.selected_char.guess_role = "殺手?"
            self.log(f"已標記 {self.selected_char.name}")
        else:
            self.selected_char.guess_role = None
            self.log("已清除標記")

    def action_solve(self):
         self.is_solving = True 

    def get_node_pos(self, location_id):
        if location_id == STATION_ID: return (CENTER_X, CENTER_Y)
        angle_deg = 270 - (location_id * 30)
        angle_rad = math.radians(angle_deg)
        return (CENTER_X + RADIUS * math.cos(angle_rad), CENTER_Y + RADIUS * math.sin(angle_rad))

    def get_all_char_positions(self):
        res = []
        loc_counts = {} 
        for char in self.engine.characters:
            if char.is_dead: continue
            base_pos = self.get_node_pos(char.location)
            count = loc_counts.get(char.location, 0)
            offset_x = (count % 3 - 1) * 18
            offset_y = (count // 3) * 18
            loc_counts[char.location] = count + 1
            res.append((char, (base_pos[0] + offset_x, base_pos[1] + offset_y)))
        return res

    def draw_detail_panel(self):
        if not self.selected_char: return
        char = self.selected_char
        panel_rect = pygame.Rect(SCREEN_WIDTH - 280, 420, 260, 300)
        s = pygame.Surface((panel_rect.width, panel_rect.height))
        s.set_alpha(200)
        s.fill((40, 40, 50))
        self.screen.blit(s, (panel_rect.x, panel_rect.y))
        pygame.draw.rect(self.screen, (100, 100, 120), panel_rect, 2)

        x_start = panel_rect.x + 20
        y_cursor = panel_rect.y + 20
        name_surf = self.title_font.render(char.name, True, HIGHLIGHT_COLOR)
        self.screen.blit(name_surf, (x_start, y_cursor))
        
        y_cursor += 80
        bar_width = 220
        bar_height = 20
        pygame.draw.rect(self.screen, BAR_BG_COLOR, (x_start, y_cursor, bar_width, bar_height))
        if char.max_sanity > 0:
            ratio = max(0, char.sanity / char.max_sanity)
            fill_width = int(bar_width * ratio)
            color = BAR_FILL_COLOR if char.sanity > 1 else BAR_LOW_COLOR
            pygame.draw.rect(self.screen, color, (x_start, y_cursor, fill_width, bar_height))
        
        sanity_txt = f"精神: {char.sanity}/{char.max_sanity}"
        self.screen.blit(self.font.render(sanity_txt, True, (255, 255, 255)), (x_start, y_cursor - 25))

        y_cursor += 50
        region_names = ["神社", "醫院", "都市", "學校"]
        forbidden_str = "無"
        if char.forbidden_region != -1:
            forbidden_str = region_names[char.forbidden_region]
        self.screen.blit(self.font.render(f"🚫 禁地: {forbidden_str}", True, (255, 100, 100)), (x_start, y_cursor))

        y_cursor += 40
        role_str = "???"
        role_color = (150, 150, 150)
        if char.known:
            role_str = f"【真身: {char.role}】"
            role_color = (100, 255, 255)
        elif char.guess_role:
            role_str = f"[筆記: {char.guess_role}?]"
            role_color = (255, 255, 100)
        self.screen.blit(self.font.render(role_str, True, role_color), (x_start, y_cursor))
        
        if char.intrigue:
            self.screen.blit(self.font.render("😈 詭異笑容...", True, (200, 50, 200)), (x_start, y_cursor + 30))

    def draw_graves(self):
        loc_counts = {}
        for grave in self.engine.graves:
            base_pos = self.get_node_pos(grave.location)
            count = loc_counts.get(grave.location, 0)
            offset_x = (count % 3 - 1) * 15 + 5
            offset_y = (count // 3) * 15 + 5
            loc_counts[grave.location] = count + 1
            draw_pos = (base_pos[0] + offset_x, base_pos[1] + offset_y)
            
            grave_rect = pygame.Rect(0, 0, 16, 20)
            grave_rect.center = draw_pos
            pygame.draw.rect(self.screen, GRAVE_COLOR, grave_rect, border_radius=3)
            pygame.draw.rect(self.screen, (50, 50, 50), grave_rect, 1, border_radius=3)
            info_text = f"{grave.char_name[0]}D{grave.day}"
            text_surf = self.font.render(info_text, True, GRAVE_TEXT_COLOR)
            self.screen.blit(text_surf, (draw_pos[0]-10, draw_pos[1]+10))

    def draw_solve_panel(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        panel_w, panel_h = 800, 600
        panel_x, panel_y = (SCREEN_WIDTH - panel_w)//2, (SCREEN_HEIGHT - panel_h)//2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, SOLVE_PANEL_COLOR, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 2, border_radius=10)

        title = self.title_font.render("=== 揭露真相 ===", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (panel_x + 300, panel_y + 20))
        
        active_chars = self.engine.characters
        col_width = 350
        start_x = panel_x + 50
        start_y = panel_y + 100
        self.arrow_buttons = []
        
        for idx, char in enumerate(active_chars):
            col = idx % 2
            row = idx // 2
            x = start_x + col * col_width
            y = start_y + row * 60
            
            name_color = (255, 255, 255)
            if char.is_dead: name_color = (150, 50, 50)
            self.screen.blit(self.font.render(f"{char.name}:", True, name_color), (x, y))
            
            current_role_idx = self.guess_indices.get(char.id, 0)
            role_name = POSSIBLE_ROLES[current_role_idx]
            
            left_rect = pygame.Rect(x + 100, y - 5, 30, 30)
            pygame.draw.rect(self.screen, BTN_COLOR, left_rect, border_radius=3)
            self.screen.blit(self.font.render("<", True, (255,255,255)), (x + 110, y))
            self.arrow_buttons.append((left_rect, "left", char.id))
            
            role_color = HIGHLIGHT_COLOR if role_name != "一般人" else TEXT_COLOR
            self.screen.blit(self.font.render(role_name, True, role_color), (x + 145, y))
            
            right_rect = pygame.Rect(x + 250, y - 5, 30, 30)
            pygame.draw.rect(self.screen, BTN_COLOR, right_rect, border_radius=3)
            self.screen.blit(self.font.render(">", True, (255,255,255)), (x + 260, y))
            self.arrow_buttons.append((right_rect, "right", char.id))

        self.submit_btn_rect = pygame.Rect(panel_x + panel_w//2 - 110, panel_y + panel_h - 70, 100, 40)
        self.cancel_btn_rect = pygame.Rect(panel_x + panel_w//2 + 10, panel_y + panel_h - 70, 100, 40)
        
        pygame.draw.rect(self.screen, (50, 150, 50), self.submit_btn_rect, border_radius=5)
        self.screen.blit(self.font.render("提交", True, (255, 255, 255)), (self.submit_btn_rect.x + 35, self.submit_btn_rect.y + 10))

        pygame.draw.rect(self.screen, (150, 50, 50), self.cancel_btn_rect, border_radius=5)
        self.screen.blit(self.font.render("取消", True, (255, 255, 255)), (self.cancel_btn_rect.x + 35, self.cancel_btn_rect.y + 10))

    def handle_solve_click(self, pos):
        for rect, direction, char_id in self.arrow_buttons:
            if rect.collidepoint(pos):
                current_idx = self.guess_indices[char_id]
                if direction == "left": self.guess_indices[char_id] = (current_idx - 1) % len(POSSIBLE_ROLES)
                else: self.guess_indices[char_id] = (current_idx + 1) % len(POSSIBLE_ROLES)
                return

        if self.submit_btn_rect.collidepoint(pos):
            self.calculate_final_score()
            self.is_solving = False
            self.show_result = True
            return
        if self.cancel_btn_rect.collidepoint(pos):
            self.is_solving = False

    def calculate_final_score(self):
        correct_count = 0
        mystery_count = 0
        special_chars = [c for c in self.engine.characters if c.role != "一般人"]
        total_mystery = len(special_chars)
        details = []

        for char in self.engine.characters:
            guess_idx = self.guess_indices[char.id]
            guess_role = POSSIBLE_ROLES[guess_idx]
            is_correct = (guess_role == char.role)
            if is_correct:
                correct_count += 1
                if char.role != "一般人": mystery_count += 1
            if not is_correct or char.role != "一般人":
                mark = "✅" if is_correct else "❌"
                details.append(f"{mark} {char.name}: 猜[{guess_role}] / 真[{char.role}]")

        if mystery_count == total_mystery:
            self.result_message = f"🎉 完美勝利！\n找出所有 {total_mystery} 個真相！\n"
        else:
            self.result_message = f"💀 失敗...\n只找出 {mystery_count}/{total_mystery} 個真相。\n"
        self.result_message += "\n".join(details)

    def draw_result_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        lines = self.result_message.split('\n')
        y = 100
        for line in lines:
            color = (100, 255, 100) if "✅" in line or "勝利" in line else (255, 100, 100)
            if "真" in line: color = (200, 200, 200)
            self.screen.blit(self.font.render(line, True, color), (100, y))
            y += 30
        self.screen.blit(self.font.render("按 [ESC] 退出", True, (255, 255, 0)), (100, y + 50))

    def draw(self):
        self.screen.fill(BG_COLOR)
        points = [self.get_node_pos(i) for i in range(MAP_SIZE)]
        pygame.draw.lines(self.screen, (50, 50, 50), True, points, 2)
        
        for i in range(MAP_SIZE):
            pos = self.get_node_pos(i)
            color = [(100, 50, 50), (50, 100, 50), (50, 50, 100), (80, 80, 50)][i // 3]
            pygame.draw.circle(self.screen, color, pos, NODE_RADIUS)
            lbl = self.font.render(str(i), True, (200,200,200))
            self.screen.blit(lbl, (pos[0]-5, pos[1]-10))

        pygame.draw.circle(self.screen, (40, 40, 40), (CENTER_X, CENTER_Y), 60)
        pygame.draw.circle(self.screen, (100, 100, 100), (CENTER_X, CENTER_Y), 60, 2)
        
        self.draw_graves()

        for char, pos in self.get_all_char_positions():
             color = (200, 200, 200)
             if char.role == "殺手" and char.known: color = (255, 50, 50)
             elif char.sanity <= 1: color = (100, 100, 255)
             if char == self.selected_char:
                pygame.draw.circle(self.screen, HIGHLIGHT_COLOR, pos, 12) 
             pygame.draw.circle(self.screen, color, pos, 8)
             name_text = char.name[0]
             if char.guess_role: name_text += "?"
             self.screen.blit(self.font.render(name_text, True, (255, 255, 255)), (pos[0]-6, pos[1]-25))

        panel_rect = pygame.Rect(SCREEN_WIDTH - 300, 0, 300, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (30, 30, 40), panel_rect)
        pygame.draw.line(self.screen, (100, 100, 100), (SCREEN_WIDTH - 300, 0), (SCREEN_WIDTH - 300, SCREEN_HEIGHT))

        title = self.title_font.render(f"Day {self.engine.day}", True, HIGHLIGHT_COLOR)
        phase_txt = self.font.render(f"階段: {self.phases[self.phase_idx]}", True, TEXT_COLOR)
        self.screen.blit(title, (panel_rect.x + 20, 20))
        self.screen.blit(phase_txt, (panel_rect.x + 20, 60))

        if self.action_mode:
            self.screen.blit(self.font.render(f"正在: {self.action_mode}...", True, (255, 100, 100)), (panel_rect.x + 20, 90))

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.check_hover(mouse_pos)
            btn.draw(self.screen, self.font)

        log_y = 380
        for msg in self.log_messages[:5]:
            self.screen.blit(self.font.render(msg, True, (150, 150, 150)), (panel_rect.x + 10, log_y))
            log_y += 20

        self.draw_detail_panel()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.show_result:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        running = False
                elif self.is_solving:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.handle_solve_click(event.pos)
                else: 
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            clicked_btn = False
                            for btn in self.buttons:
                                if btn.check_click(event.pos):
                                    clicked_btn = True
                                    break
                            if not clicked_btn:
                                self.handle_map_click(event.pos)

            if self.show_result:
                self.draw_result_overlay()
            else:
                self.draw() 
                if self.is_solving:
                    self.draw_solve_panel()

            pygame.display.flip()
            clock.tick(30)
        pygame.quit()
        sys.exit()

if __name__ == "__LOOP__":
    game = GameVisualizer()
    game.run()
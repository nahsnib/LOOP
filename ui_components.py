# ui_components.py
import pygame

# 顏色定義
BTN_COLOR = (50, 50, 70)
BTN_HOVER_COLOR = (70, 70, 90)
LOG_BG_COLOR = (20, 20, 20)

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

class GameLogger:
    """處理遊戲訊息的儲存與提取"""
    def __init__(self, max_display_lines=18):
        self.messages = []       # 暫存顯示用的訊息 (最近的)
        self.full_history = []   # 完整的歷史紀錄
        self.max_display = max_display_lines

    def log(self, text):
        """接收新訊息"""
        # 為了除錯方便，我們依然保留 print 到終端機的功能
        print(text) 
        
        self.messages.insert(0, text)
        if len(self.messages) > self.max_display:
            self.messages.pop()
        
        self.full_history.append(text)

    def get_recent(self):
        """取得最近的 N 條訊息"""
        return self.messages

    def get_full_history(self):
        """取得完整歷史"""
        return self.full_history
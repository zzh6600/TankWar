import pygame
from config import *


class StartScene:
    """游戏开始场景"""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 48)
        self.title_font = pygame.font.SysFont(None, 72)
        self.start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
        self.quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.collidepoint(event.pos):
                return GAME_PLAYING
            elif self.quit_button.collidepoint(event.pos):
                return None  # 返回None表示退出游戏
        return GAME_START

    def update(self):
        """更新场景"""
        pass

    def draw(self):
        """绘制场景"""
        self.screen.fill(BLACK)

        # 绘制标题
        title = self.title_font.render("TankWar", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title, title_rect)

        # 绘制开始按钮
        pygame.draw.rect(self.screen, BLUE, self.start_button)
        start_text = self.font.render("start", True, WHITE)
        start_text_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_text_rect)

        # 绘制退出按钮
        pygame.draw.rect(self.screen, RED, self.quit_button)
        quit_text = self.font.render("exit", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)

        # 绘制操作说明
        controls = self.font.render(" arrow keys to move, spacebar to shoot", True, WHITE)
        controls_rect = controls.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(controls, controls_rect)
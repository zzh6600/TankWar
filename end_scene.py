import pygame
from config import *


class EndScene:
    """游戏结束场景"""

    def __init__(self, screen, victory):
        self.screen = screen
        self.victory = victory
        self.font = pygame.font.SysFont(None, 48)
        self.title_font = pygame.font.SysFont(None, 72)
        self.restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
        self.quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.restart_button.collidepoint(event.pos):
                return GAME_PLAYING
            elif self.quit_button.collidepoint(event.pos):
                return None  # 返回None表示退出游戏
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return GAME_START

        return GAME_OVER

    def update(self):
        """更新场景"""
        pass

    def draw(self):
        """绘制场景"""
        self.screen.fill(BLACK)

        # 绘制结果
        if self.victory:
            result = self.title_font.render("win!", True, GREEN)
        else:
            result = self.title_font.render("you lose!", True, RED)

        result_rect = result.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(result, result_rect)

        # 绘制重新开始按钮
        pygame.draw.rect(self.screen, BLUE, self.restart_button)
        restart_text = self.font.render("restart", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(restart_text, restart_text_rect)

        # 绘制退出按钮
        pygame.draw.rect(self.screen, RED, self.quit_button)
        quit_text = self.font.render("exit", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)
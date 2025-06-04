import pygame
from config import *


class Bullet(pygame.sprite.Sprite):
    """炮弹类"""

    def __init__(self, x, y, direction, level):
        super().__init__()
        self.direction = direction
        self.level = level
        self.speed = BULLET_SPEED * level  # 炮弹速度由发射坦克等级决定
        self.damage = BULLET_DAMAGE

        # 创建炮弹图像
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(topleft=(x, y))

        # 记录初始位置（用于调试）
        self.start_x = x
        self.start_y = y

    def update(self):
        """更新炮弹位置"""
        # 使用 rect 的移动方法直接更新位置
        if self.direction == UP:
            self.rect.y -= self.speed
        elif self.direction == DOWN:
            self.rect.y += self.speed
        elif self.direction == LEFT:
            self.rect.x -= self.speed
        elif self.direction == RIGHT:
            self.rect.x += self.speed

        # 检查是否超出屏幕边界（使用 rect 直接检测）
        if not self.rect.colliderect(pygame.display.get_surface().get_rect()):
            return False

        return True
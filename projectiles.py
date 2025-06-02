import pygame
from config import *


class Bullet(pygame.sprite.Sprite):
    """炮弹类"""

    def __init__(self, x, y, direction, level):
        super().__init__()
        self.x = x
        self.y = y
        self.direction = direction
        self.level = level
        self.speed = BULLET_SPEED * level  # 炮弹速度由发射坦克等级决定
        self.damage = BULLET_DAMAGE

        # 创建炮弹图像
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        """更新炮弹位置"""
        if self.direction == UP:
            self.y -= self.speed
        elif self.direction == DOWN:
            self.y += self.speed
        elif self.direction == LEFT:
            self.x -= self.speed
        elif self.direction == RIGHT:
            self.x += self.speed

        self.rect.topleft = (self.x, self.y)

        # 检查是否超出屏幕边界
        if (self.x < 0 or self.x > SCREEN_WIDTH or
                self.y < 0 or self.y > SCREEN_HEIGHT):
            return False

        return True
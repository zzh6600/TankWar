import pygame
import random
from config import *


class Fruit(pygame.sprite.Sprite):
    """果实类"""

    def __init__(self, x, y, fruit_type):
        super().__init__()
        self.x = x
        self.y = y
        self.fruit_type = fruit_type
        self.lifetime = 300  # 果实存在时间

        # 根据果实类型设置不同的颜色
        if fruit_type == FRUIT_STAR:
            self.color = YELLOW
        elif fruit_type == FRUIT_TANK:
            self.color = GREEN
        elif fruit_type == FRUIT_GUN:
            self.color = RED
        elif fruit_type == FRUIT_SHELL:
            self.color = BLUE

        self.image = pygame.Surface((20, 20))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        """更新果实状态"""
        self.lifetime -= 1
        return self.lifetime > 0

    def apply_effect(self, player):
        """应用果实效果"""
        if self.fruit_type == FRUIT_STAR:
            player.upgrade()
        elif self.fruit_type == FRUIT_TANK:
            player.lives += 1
        elif self.fruit_type == FRUIT_GUN:
            for bullet in player.bullets:
                bullet.speed += 2
        elif self.fruit_type == FRUIT_SHELL:
            player.max_bullets = min(player.max_bullets + 1, 2)

        return True  # 返回效果是否已应用


def create_random_fruit(x, y):
    """创建随机类型的果实"""
    fruit_types = [FRUIT_STAR, FRUIT_TANK, FRUIT_GUN, FRUIT_SHELL]
    fruit_type = random.choice(fruit_types)
    return Fruit(x, y, fruit_type)
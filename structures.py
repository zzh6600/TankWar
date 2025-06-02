import pygame
from config import *


class Structure(pygame.sprite.Sprite):
    """地图建筑基类"""

    def __init__(self, x, y, image=None, health=1):
        super().__init__()
        self.x = x
        self.y = y
        self.health = health

        if image:
            self.image = image
        else:
            self.image = pygame.Surface((30, 30))
            self.image.fill(WHITE)

        self.rect = self.image.get_rect(topleft=(x, y))

    def hit(self, damage):
        """被击中处理"""
        self.health -= damage
        return self.health <= 0


class Brick(Structure):
    """红砖类"""

    def __init__(self, x, y):
        super().__init__(x, y, health=BRICK_HP)
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)


class Iron(Structure):
    """铁墙类"""

    def __init__(self, x, y):
        super().__init__(x, y, health=IRON_HP)
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)


class River(Structure):
    """河流类"""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)


class Forest(Structure):
    """森林类"""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.Surface((30, 30))
        self.image.fill(GREEN)


class Headquarters(Structure):
    """司令部类"""

    def __init__(self, x, y):
        super().__init__(x, y, health=HEADQUARTERS_HP)
        self.image = pygame.Surface((40, 40))
        self.image.fill(YELLOW)
        self.is_destroyed = False

    def hit(self, damage):
        """被击中处理"""
        result = super().hit(damage)
        if result:
            self.is_destroyed = True
            self.image.fill(RED)  # 司令部被摧毁后变红
        return result
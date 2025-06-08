import pygame
import random
from config import *
from resources import ResourceLoader


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

        # self.image = pygame.Surface((20, 20))
        # self.image.fill(self.color)
        # self.rect = self.image.get_rect(topleft=(x, y))

        fruit_filename = self._get_image_filename(self.fruit_type)
        fruit_image = self.load_image(fruit_filename, self.color)
        fruit_image = pygame.transform.scale(fruit_image, (FRUIT_SIZE, FRUIT_SIZE))

        self.image = fruit_image
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

    def _get_image_filename(self, fruit_type):
        if  fruit_type == FRUIT_STAR:
            return 'food_star.png'
        elif fruit_type == FRUIT_TANK:
            return 'food_tank.png'
        elif fruit_type == FRUIT_GUN:
            return 'food_gun.png'
        elif fruit_type == FRUIT_SHELL:
            return 'food_shell.png'

    @staticmethod
    def load_image(filename, default_color, size=(30, 30)):
        """加载建筑图片，失败时返回默认颜色的Surface"""
        image, _ = ResourceLoader.load_image(filename)
        if image:
            return image
        else:
            print(f"使用默认颜色替代 {filename}")
            surface = pygame.Surface(size)
            surface.fill(default_color)
            return surface
def create_random_fruit(x, y):
    """创建随机类型的果实"""
    fruit_types = [FRUIT_STAR, FRUIT_TANK, FRUIT_GUN, FRUIT_SHELL]
    fruit_type = random.choice(fruit_types)
    return Fruit(x, y, fruit_type)




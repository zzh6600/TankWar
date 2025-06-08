import pygame
from config import *
from resources import ResourceLoader


class Structure(pygame.sprite.Sprite):
    """地图建筑基类"""
    def __init__(self, x, y, image=None, health=1):
        super().__init__()
        self.x = x
        self.y = y
        self.health = health
        self.can_pass_tank = False  # 默认坦克不能穿过
        self.can_pass_bullet = False  # 默认子弹不能穿过
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        if image:
            self.image = image
        else:
            self.image = pygame.Surface((30, 30))
            self.image.fill(WHITE)
        self.hit_sound = ResourceLoader.load_sound('bang.wav')

    @staticmethod
    def load_structure_image(filename, default_color, size=(30, 30)):
        """加载建筑图片，失败时返回默认颜色的Surface"""
        image, _ = ResourceLoader.load_image(filename)
        if image:
            return image
        else:
            print(f"使用默认颜色替代 {filename}")
            surface = pygame.Surface(size)
            surface.fill(default_color)
            return surface

    def hit(self, damage):
        """被击中处理"""
        self.health -= damage

        try:
            self.hit_sound.play()
        except AttributeError:
            print("无法播放建筑被击中音效")

        return self.health <= 0


class Brick(Structure):
    """红砖类"""
    def __init__(self, x, y):
        brick_image = self.load_structure_image('brick.png', RED)
        brick_image = pygame.transform.scale(brick_image, (TILE_SIZE, TILE_SIZE))

        super().__init__(x, y, image=brick_image, health=BRICK_HP)

        self.can_pass_tank = False
        self.can_pass_bullet = False

class Iron(Structure):
    """铁墙类"""
    def __init__(self, x, y):
        # 加载并缩放图片到 TILE_SIZE
        iron_image = self.load_structure_image('iron.png', BLUE)
        iron_image = pygame.transform.scale(iron_image, (TILE_SIZE, TILE_SIZE))
        super().__init__(x, y, image=iron_image, health=IRON_HP)
        self.can_pass_tank = False  # 坦克不能穿过铁墙
        self.can_pass_bullet = False  # 子弹不能穿过铁墙


class River(Structure):
    """河流类"""
    def __init__(self, x, y):
        river_image = self.load_structure_image('river.png', BLUE)
        river_image = pygame.transform.scale(river_image, (TILE_SIZE, TILE_SIZE))
        super().__init__(x, y, image=river_image)
        self.can_pass_tank = False  # 坦克不能过河
        self.can_pass_bullet = True  # 子弹可以过河


class Forest(Structure):
    """森林类"""
    def __init__(self, x, y):
        forest_image = self.load_structure_image('forest.png', GREEN)
        forest_image = pygame.transform.scale(forest_image, (TILE_SIZE, TILE_SIZE))
        super().__init__(x, y, image=forest_image)
        self.can_pass_tank = True  # 坦克可以穿过森林
        self.can_pass_bullet = True  # 子弹可以穿过森林


class Headquarters(Structure):
    """司令部类"""

    def __init__(self, x, y):
        hq_image = self.load_structure_image('home.png', YELLOW, size=(40, 40))
        super().__init__(x, y, image=hq_image, health=HEADQUARTERS_HP)
        self.is_destroyed = False

    def hit(self, damage):
        """被击中处理"""
        result = super().hit(damage)
        if result:
            self.is_destroyed = True
            # 尝试加载被摧毁的图片，失败则填充红色
            destroyed_image = self.load_structure_image('home_destroyed.png', RED, size=(40, 40))
            self.image = destroyed_image
        return result
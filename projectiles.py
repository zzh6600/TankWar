import pygame
from config import *
from resources import ResourceLoader


class Bullet(pygame.sprite.Sprite):
    """炮弹类"""

    def __init__(self, x, y, direction, level):
        # 创建炮弹图像
        super().__init__()
        self.direction = direction
        self.level = level
        self.speed = BULLET_SPEED * level  # 炮弹速度由发射坦克等级决定
        self.damage = BULLET_DAMAGE

        # bullet_filename = self._get_image_filename(direction)
        # bullet_image = self.load_structure_image(bullet_filename, RED)
        # bullet_image = pygame.transform.scale(bullet_image, (BULLET_SIZE, BULLET_SIZE))
        # self.image = bullet_image
        # self.rect = self.image.get_rect(topleft=(x, y))
        # 获取子弹图像路径（假设方向与文件名对应，如"bullet_up.png"）
        bullet_filename = self._get_image_filename(direction)

        # 关键：使用 convert_alpha() 保留透明通道
        # bullet_image = self.load_structure_image(bullet_filename, RED).convert_alpha()
        bullet_image = pygame.image.load(bullet_filename).convert_alpha()
        bullet_image = pygame.transform.scale(bullet_image, (BULLET_SIZE, BULLET_SIZE))  # 按需缩放

        self.image = bullet_image
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

    def _get_image_filename(self, direction):
        if direction == UP:
            return './images/bullet_up.png'
        elif direction == DOWN:
            return './images/bullet_down.png'
        elif direction == LEFT:
            return './images/bullet_left.png'
        elif direction == RIGHT:
            return './images/bullet_right.png'

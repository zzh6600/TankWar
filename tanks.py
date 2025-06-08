import pygame
import random
from config import *
from projectiles import Bullet
from resources import ResourceLoader

# 定义方向与图片编号的映射（1=上，2=右，3=下，4=左）
DIRECTION_MAP = {
    UP: 1,
    RIGHT: 4,
    DOWN: 2,
    LEFT: 3
}


class Tank(pygame.sprite.Sprite):
    """坦克基类"""


    def __init__(self, x, y, color, health, level=TANK_LEVEL_1):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.health = health
        self.max_health = health
        self.level = level
        self.direction = UP  # 初始方向为上
        self.bullets = []
        self.max_bullets = 1

        self.shoot_cooldown = 30
        self.shoot_timer = 0
        self.dx = 0  # 水平移动量
        self.dy = 0  # 垂直移动量

        # 加载坦克图片（根据等级和方向）
        self.images = self._load_images()
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect(topleft=(x, y))

        # 延迟加载音效
        self.shoot_sound = ResourceLoader.load_sound('fire.wav')
        self.hit_sound = ResourceLoader.load_sound('hit.wav')

        self.last_direction = None

    def _load_images(self):
        """根据等级和方向加载坦克图片"""
        images = {}
        for direction, img_num in DIRECTION_MAP.items():
            # 生成图片文件名（玩家坦克和敌方坦克在子类中差异）
            image_name = self._get_image_filename(self.level, img_num)

            # 加载图片，失败则用默认颜色方块
            image, _ = ResourceLoader.load_image(image_name)
            if not image:
                print(f"警告：无法加载坦克图片 {image_name}，使用默认颜色")
                image = pygame.Surface((TANK_SIZE, TANK_SIZE))
                image.fill(self.color)

            images[direction] = image
        return images

    def _get_image_filename(self, level, direction_num):
        """生成图片文件名（由子类实现）"""
        raise NotImplementedError("子类必须实现 _get_image_filename 方法")

    def update(self):
        """空实现，移动量由子类（PlayerTank/EnemyTank）计算"""
        pass  # 玩家坦克的移动量在 handle_input() 中设置，敌人坦克在子类中实现

    def apply_movement(self):
        """应用移动量到位置"""
        self.x += self.dx
        self.y += self.dy
        self.rect.topleft = (self.x, self.y)

    def reset_movement(self):
        """重置移动（发生碰撞时调用）"""
        self.dx = 0
        self.dy = 0

    def _update_shoot_cooldown(self):
        """更新射击冷却时间"""
        if not self.can_shoot:
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_cooldown:
                self. can_shoot = True
                self.shoot_timer = 0



    def shoot(self):
        """射击方法，添加炮弹数量限制"""
        if not self.can_shoot():
            return None
        # 记录射击时间
        self.last_shot_time = pygame.time.get_ticks()
        # 创建子弹
        bullet_x, bullet_y = self.get_bullet_spawn_position()
        bullet = Bullet(bullet_x, bullet_y, self.direction, self.level)
        self.bullets.append(bullet)  # 直接添加到玩家的炮弹列表
        return bullet

    def can_shoot(self):
        """检查是否可以射击：地图中没有自己的炮弹时才能发射"""
        return len(self.bullets) == 0
    def _create_bullet(self):
        """创建炮弹（根据坦克方向和等级）"""
        center_x = self.x + TANK_SIZE // 2
        center_y = self.y + TANK_SIZE // 2
        bullet_x = center_x - BULLET_SIZE // 2
        bullet_y = center_y - BULLET_SIZE // 2

        # 根据方向调整炮弹初始位置
        if self.direction == UP:
            bullet_y -= TANK_SIZE // 2
        elif self.direction == DOWN:
            bullet_y += TANK_SIZE // 2
        elif self.direction == LEFT:
            bullet_x -= TANK_SIZE // 2
        elif self.direction == RIGHT:
            bullet_x += TANK_SIZE // 2

        return Bullet(bullet_x, bullet_y, self.direction, self.level)

    def hit(self, damage):
        """被击中处理"""
        self.health -= damage
        if self.health <= 0:
            self.hit_sound.play()
        return self.health <= 0

    def upgrade(self):
        """升级坦克（提升等级并重新加载图片）"""
        if self.level < TANK_LEVEL_3:
            self.level += 1
            self.max_health += 1
            self.health = self.max_health
            self.images = self._load_images()  # 重新加载升级后的图片

    def get_bullet_spawn_position(self):
        """计算子弹生成位置（从坦克中心或炮口发射）"""
        center_x = self.rect.centerx
        center_y = self.rect.centery
        bullet_size = BULLET_SIZE  # 假设在 config.py 中定义

        # 根据方向调整子弹位置，使其从炮口发射
        if self.direction == UP:
            return (center_x - bullet_size // 2, self.rect.top)
        elif self.direction == DOWN:
            return (center_x - bullet_size // 2, self.rect.bottom - bullet_size)
        elif self.direction == LEFT:
            return (self.rect.left, center_y - bullet_size // 2)
        elif self.direction == RIGHT:
            return (self.rect.right - bullet_size, center_y - bullet_size // 2)

class PlayerTank(Tank):
    """玩家坦克类（L1-L3等级，方向1-4）"""

    def __init__(self, x, y):
        super().__init__(x, y, GREEN, 1, TANK_LEVEL_1)
        self.lives = 3  # 初始三条命
        self.speed = PLAYER_SPEED  # 玩家速度（可在config中定义）
        self.health = self.max_health
        self.spawn_x = x  # 保存出生点X坐标
        self.spawn_y = y  # 保存出生点Y坐标
        self.invincible = False  # 无敌状态
        self.invincible_timer = 0  # 无敌计时器

    def hit(self, damage):
        """被击中处理，生命值减少时回到出生点"""
        if self.invincible:  # 无敌状态不扣血
            return False

        self.health -= damage

        # 检查生命值是否减少
        if self.health < 0:
            self.health = 1
            self.respawn()  # 回到出生点
            self.set_invincible(INVINCIBLE_TIME)  # 设置无敌状态（毫秒）

        return self.health <= 0

    def respawn(self):
        """回到出生点"""
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.rect.topleft = (self.x, self.y)
        self.direction = UP  # 重置方向为上

    def set_invincible(self, duration_ms):
        """设置无敌状态"""
        self.invincible = True
        self.invincible_timer = duration_ms

        # 创建子弹
        bullet_x, bullet_y = self.get_bullet_spawn_position()
        bullet = Bullet(bullet_x, bullet_y, self.direction, self.level)
        self.bullets.append(bullet)  # 直接添加到玩家的炮弹列表
        return bullet
    def _get_image_filename(self, level, direction_num):
        """生成玩家坦克图片名：tank_L[等级]_[方向].png"""
        return f"tank_L{level}_{direction_num}.png"

    def reset(self):
        """重置坦克状态（死亡后复活）"""
        self.health = self.max_health
        self.level = TANK_LEVEL_1
        self.max_bullets = 1
        self.images = self._load_images()  # 重置为L1图片
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def handle_input(self):
        """处理玩家输入并更新方向和移动量"""
        keys = pygame.key.get_pressed()
        new_direction = self.direction
        self.dx = 0  # 默认移动量为0
        self.dy = 0

        if keys[pygame.K_UP]:
            new_direction = UP
            self.dy = -self.speed
        elif keys[pygame.K_DOWN]:
            new_direction = DOWN
            self.dy = self.speed
        elif keys[pygame.K_LEFT]:
            new_direction = LEFT
            self.dx = -self.speed
        elif keys[pygame.K_RIGHT]:
            new_direction = RIGHT
            self.dx = self.speed

        # 仅在方向改变时更新图像
        if new_direction != self.direction:
            self.direction = new_direction
            self.image = self.images[self.direction]
class EnemyTank(Tank):
    """敌方坦克类（四种类型，方向1-4）"""

    def __init__(self, x, y, enemy_type):
        # 敌方类型映射：1=普通，2=快速，3=装甲，4=精英（对应enemy_1_1.png等）
        self.enemy_type = enemy_type  # 1-4
        self.speed = self._get_speed_by_type(enemy_type)
        health = self._get_health_by_type(enemy_type)
        super().__init__(x, y, WHITE, health)  # 敌方默认颜色可在config中调整
        self.move_timer = 0
        self.move_interval = random.randint(200, 400)  # 随机移动间隔

    def _get_speed_by_type(self, enemy_type):
        """根据敌方类型获取速度"""
        speed_map = {
            1: ENEMY_SPEED,  # 普通
            2: ENEMY_SPEED * 1.5,  # 快速
            3: ENEMY_SPEED * 0.8,  # 装甲（速度慢）
            4: ENEMY_SPEED * 1.2  # 精英（中等速度）
        }
        # speed_map = {
        #     1: 0.1,  # 普通
        #     2: 0.1,  # 快速
        #     3: 0.1,  # 装甲（速度慢）
        #     4: 0.1  # 精英（中等速度）
        # }
        return speed_map.get(enemy_type, ENEMY_SPEED)

    def _get_health_by_type(self, enemy_type):
        """根据敌方类型获取生命值"""
        health_map = {
            1: 1,  # 普通
            2: 2,  # 快速
            3: 3,  # 装甲
            4: 4  # 精英
        }
        return health_map.get(enemy_type, 1)

    def _get_image_filename(self, level, direction_num):
        """生成敌方坦克图片名：enemy_[类型]_[方向].png（忽略等级，用类型代替）"""
        return f"enemy_{self.enemy_type}_{direction_num}.png"

    def update(self):
        """敌人AI：随机移动和射击"""
        # 随机改变方向
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            rrr = random.randint(0, 3)
            if rrr == 0:
                self.direction = UP
                self.dy += -self.speed
            elif rrr == 1:
                self.direction = DOWN
                self.dy += self.speed
            elif rrr == 2:
                self.direction = LEFT
                self.dx += -self.speed
            elif rrr == 3:
                self.direction = RIGHT
                self.dx += self.speed
            self.move_timer = 0
            self.move_interval = random.randint(200, 400)

        # 随机射击
        if random.random() < 0.01:  # 1%概率射击
            self.shoot()

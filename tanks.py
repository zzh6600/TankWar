import pygame
import random
from config import *
from projectiles import Bullet
from resources import ResourceLoader


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
        self.direction = UP
        self.speed = PLAYER_SPEED
        self.bullets = []
        self.max_bullets = 1
        self.can_shoot = True
        self.shoot_cooldown = 30
        self.shoot_timer = 0
        self.images = self._load_images()
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect(topleft=(x, y))

    def _load_images(self):
        """加载坦克图像"""
        # 实际实现中应根据坦克类型和方向加载不同的图像
        images = [
            pygame.Surface((TANK_SIZE, TANK_SIZE)),  # 上
            pygame.Surface((TANK_SIZE, TANK_SIZE)),  # 右
            pygame.Surface((TANK_SIZE, TANK_SIZE)),  # 下
            pygame.Surface((TANK_SIZE, TANK_SIZE))  # 左
        ]

        for i in range(4):
            images[i].fill(self.color)

        return images

    def update(self):
        """更新坦克状态"""
        self.image = self.images[self.direction]

        # 更新射击冷却计时器
        if not self.can_shoot:
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_cooldown:
                self.can_shoot = True
                self.shoot_timer = 0

    def move(self, direction):
        """移动坦克"""
        old_x, old_y = self.x, self.y
        self.direction = direction

        if direction == UP:
            self.y -= self.speed
        elif direction == DOWN:
            self.y += self.speed
        elif direction == LEFT:
            self.x -= self.speed
        elif direction == RIGHT:
            self.x += self.speed

        # 边界检查
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - TANK_SIZE:
            self.x = SCREEN_WIDTH - TANK_SIZE

        if self.y < 0:
            self.y = 0
        elif self.y > SCREEN_HEIGHT - TANK_SIZE:
            self.y = SCREEN_HEIGHT - TANK_SIZE

        self.rect.topleft = (self.x, self.y)

    def shoot(self):
        """发射炮弹"""
        if self.can_shoot and len(self.bullets) < self.max_bullets:
            # 创建炮弹
            bullet_x = self.x + TANK_SIZE // 2 - BULLET_SIZE // 2
            bullet_y = self.y + TANK_SIZE // 2 - BULLET_SIZE // 2

            # 根据坦克方向调整炮弹初始位置
            if self.direction == UP:
                bullet_y -= TANK_SIZE // 2
            elif self.direction == DOWN:
                bullet_y += TANK_SIZE // 2
            elif self.direction == LEFT:
                bullet_x -= TANK_SIZE // 2
            elif self.direction == RIGHT:
                bullet_x += TANK_SIZE // 2

            bullet = Bullet(bullet_x, bullet_y, self.direction, self.level)
            self.bullets.append(bullet)

            # 设置射击冷却
            self.can_shoot = False

    def hit(self, damage):
        """被击中处理"""
        self.health -= damage
        return self.health <= 0

    def upgrade(self):
        """升级坦克"""
        if self.level < TANK_LEVEL_3:
            self.level += 1
            self.max_health += 1
            self.health = self.max_health
            # 可以在这里增加其他升级效果


class PlayerTank(Tank):
    """玩家坦克类"""

    def __init__(self, x, y):
        super().__init__(x, y, GREEN, 1, TANK_LEVEL_1)
        self.lives = 3  # 初始有3条命

    def reset(self):
        """重置坦克状态"""
        self.health = self.max_health
        self.level = TANK_LEVEL_1
        self.max_bullets = 1


class EnemyTank(Tank):
    """敌方坦克类"""

    def __init__(self, x, y, enemy_type):
        self.enemy_type = enemy_type

        # 根据敌方坦克类型设置属性
        if enemy_type == ENEMY_NORMAL:
            super().__init__(x, y, WHITE, 1)
            self.speed = ENEMY_SPEED
        elif enemy_type == ENEMY_FAST:
            super().__init__(x, y, WHITE, 2)
            self.speed = ENEMY_SPEED * 1.5
        elif enemy_type == ENEMY_ARMOR:
            super().__init__(x, y, WHITE, 3)
            self.speed = ENEMY_SPEED * 0.8
        elif enemy_type == ENEMY_TARGET:
            super().__init__(x, y, RED, 4)
            self.speed = ENEMY_SPEED

        self.move_timer = 0
        self.move_interval = random.randint(60, 120)  # 随机移动间隔

    def update(self):
        """更新敌方坦克状态"""
        super().update()

        # 随机移动逻辑
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.move(random.randint(0, 3))
            self.move_timer = 0
            self.move_interval = random.randint(60, 120)

        # 随机射击逻辑
        if random.random() < 0.01:  # 1%的概率射击
            self.shoot()
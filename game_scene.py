import pygame
import random
from config import *
from tanks import PlayerTank, EnemyTank
from projectiles import Bullet
from structures import Brick, Iron, River, Forest, Headquarters
from items import Fruit, create_random_fruit


class GameScene:
    """游戏主场景"""

    def __init__(self, screen):
        self.screen = screen
        self.player = PlayerTank(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemies = []
        self.bricks = []
        self.irons = []
        self.rivers = []
        self.forests = []
        self.headquarters = Headquarters(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 60)
        self.fruits = []
        self.bullets = []
        self.explosions = []
        self.enemies_destroyed = 0
        self.total_enemies = 20
        self.spawned_enemies = 0
        self.last_spawn_time = 0
        self.spawn_interval = 180  # 敌人生成间隔
        self.game_over = False
        self.victory = False
        self.font = pygame.font.SysFont(None, 36)

        # 初始化地图
        self._init_map()

    def _init_map(self):
        """初始化地图"""
        # 创建围墙
        for x in range(0, SCREEN_WIDTH, 30):
            self.bricks.append(Brick(x, 0))
            self.bricks.append(Brick(x, SCREEN_HEIGHT - 30))

        for y in range(30, SCREEN_HEIGHT - 30, 30):
            self.bricks.append(Brick(0, y))
            self.bricks.append(Brick(SCREEN_WIDTH - 30, y))

        # 在地图中随机放置一些砖块和铁墙
        for _ in range(30):
            x = random.randint(60, SCREEN_WIDTH - 90)
            y = random.randint(60, SCREEN_HEIGHT - 150)
            self.bricks.append(Brick(x, y))

        for _ in range(15):
            x = random.randint(60, SCREEN_WIDTH - 90)
            y = random.randint(60, SCREEN_HEIGHT - 150)
            self.irons.append(Iron(x, y))

        # 在司令部周围放置保护墙
        hq_x = self.headquarters.x
        hq_y = self.headquarters.y

        for i in range(-1, 2):
            for j in range(-1, 0):
                if i != 0 or j != 0:
                    self.bricks.append(Brick(hq_x + i * 30, hq_y + j * 30))

    def _spawn_enemy(self):
        """生成敌人"""
        if (self.spawned_enemies < self.total_enemies and
                pygame.time.get_ticks() - self.last_spawn_time > self.spawn_interval):

            # 随机选择生成位置
            spawn_positions = [
                (50, 50),
                (SCREEN_WIDTH // 2 - 20, 50),
                (SCREEN_WIDTH - 100, 50)
            ]

            pos = random.choice(spawn_positions)

            # 确保连续3辆非目标坦克后一定会出现一辆目标坦克
            non_target_count = sum(1 for e in self.enemies if e.enemy_type != ENEMY_TARGET)
            if non_target_count >= 3:
                enemy_type = ENEMY_TARGET
            else:
                enemy_type = random.choice([ENEMY_NORMAL, ENEMY_FAST, ENEMY_ARMOR, ENEMY_TARGET])

            enemy = EnemyTank(pos[0], pos[1], enemy_type)
            self.enemies.append(enemy)
            self.spawned_enemies += 1
            self.last_spawn_time = pygame.time.get_ticks()

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.QUIT:
            return None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.shoot()

        return GAME_PLAYING if not self.game_over else GAME_OVER

    def update(self):
        """更新场景"""
        if self.game_over:
            return

        # 生成敌人
        self._spawn_enemy()

        # 更新玩家
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.player.move(UP)
        elif keys[pygame.K_DOWN]:
            self.player.move(DOWN)
        elif keys[pygame.K_LEFT]:
            self.player.move(LEFT)
        elif keys[pygame.K_RIGHT]:
            self.player.move(RIGHT)

        self.player.update()

        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update()

            # 检查敌人与玩家的碰撞
            if pygame.sprite.collide_rect(enemy, self.player):
                # 坦克相撞，双方都受到伤害
                if self.player.hit(1):
                    if self.player.lives > 0:
                        self.player.lives -= 1
                        self.player.reset()
                    else:
                        self.game_over = True

                if enemy.hit(1):
                    self.enemies.remove(enemy)
                    self.enemies_destroyed += 1
                    # 目标坦克被摧毁后生成果实
                    if enemy.enemy_type == ENEMY_TARGET:
                        fruit = create_random_fruit(enemy.x, enemy.y)
                        self.fruits.append(fruit)

            # 更新敌人炮弹
            for bullet in enemy.bullets[:]:
                if not bullet.update():
                    enemy.bullets.remove(bullet)
                    continue

                # 检查敌人炮弹与玩家的碰撞
                if pygame.sprite.collide_rect(bullet, self.player):
                    enemy.bullets.remove(bullet)
                    if self.player.hit(bullet.damage):
                        if self.player.lives > 0:
                            self.player.lives -= 1
                            self.player.reset()
                        else:
                            self.game_over = True

                # 检查敌人炮弹与建筑的碰撞
                hit_brick = False
                for brick in self.bricks[:]:
                    if pygame.sprite.collide_rect(bullet, brick):
                        enemy.bullets.remove(bullet)
                        if brick.hit(bullet.damage):
                            self.bricks.remove(brick)
                        hit_brick = True
                        break

                if hit_brick:
                    continue

                for iron in self.irons[:]:
                    if pygame.sprite.collide_rect(bullet, iron):
                        enemy.bullets.remove(bullet)
                        if iron.hit(bullet.damage):
                            self.irons.remove(iron)
                        break

                # 检查敌人炮弹与司令部的碰撞
                if pygame.sprite.collide_rect(bullet, self.headquarters):
                    enemy.bullets.remove(bullet)
                    if self.headquarters.hit(bullet.damage):
                        self.game_over = True

        # 更新玩家炮弹
        for bullet in self.player.bullets[:]:
            if not bullet.update():
                self.player.bullets.remove(bullet)
                continue

            # 检查玩家炮弹与敌人的碰撞
            hit_enemy = False
            for enemy in self.enemies[:]:
                if pygame.sprite.collide_rect(bullet, enemy):
                    self.player.bullets.remove(bullet)
                    if enemy.hit(bullet.damage):
                        self.enemies.remove(enemy)
                        self.enemies_destroyed += 1
                        # 目标坦克被摧毁后生成果实
                        if enemy.enemy_type == ENEMY_TARGET:
                            fruit = create_random_fruit(enemy.x, enemy.y)
                            self.fruits.append(fruit)
                    hit_enemy = True
                    break

            if hit_enemy:
                continue

            # 检查玩家炮弹与建筑的碰撞
            hit_brick = False
            for brick in self.bricks[:]:
                if pygame.sprite.collide_rect(bullet, brick):
                    self.player.bullets.remove(bullet)
                    if brick.hit(bullet.damage):
                        self.bricks.remove(brick)
                    hit_brick = True
                    break

            if hit_brick:
                continue

            for iron in self.irons[:]:
                if pygame.sprite.collide_rect(bullet, iron):
                    self.player.bullets.remove(bullet)
                    if iron.hit(bullet.damage):
                        self.irons.remove(iron)
                    break

            # 检查玩家炮弹与司令部的碰撞
            if pygame.sprite.collide_rect(bullet, self.headquarters):
                self.player.bullets.remove(bullet)
                if self.headquarters.hit(bullet.damage):
                    self.game_over = True

        # 更新果实
        for fruit in self.fruits[:]:
            if not fruit.update():
                self.fruits.remove(fruit)
                continue

            # 检查玩家是否吃到果实
            if pygame.sprite.collide_rect(fruit, self.player):
                fruit.apply_effect(self.player)
                self.fruits.remove(fruit)

        # 检查游戏胜利条件
        if self.enemies_destroyed >= self.total_enemies and not self.game_over:
            self.victory = True
            self.game_over = True

    def draw(self):
        """绘制场景"""
        self.screen.fill(BLACK)

        # 绘制建筑
        for brick in self.bricks:
            self.screen.blit(brick.image, brick.rect)

        for iron in self.irons:
            self.screen.blit(iron.image, iron.rect)

        for river in self.rivers:
            self.screen.blit(river.image, river.rect)

        for forest in self.forests:
            self.screen.blit(forest.image, forest.rect)

        # 绘制司令部
        self.screen.blit(self.headquarters.image, self.headquarters.rect)

        # 绘制果实
        for fruit in self.fruits:
            self.screen.blit(fruit.image, fruit.rect)

        # 绘制玩家
        self.screen.blit(self.player.image, self.player.rect)

        # 绘制玩家炮弹
        for bullet in self.player.bullets:
            self.screen.blit(bullet.image, bullet.rect)

        # 绘制敌人
        for enemy in self.enemies:
            self.screen.blit(enemy.image, enemy.rect)

            # 绘制敌人炮弹
            for bullet in enemy.bullets:
                self.screen.blit(bullet.image, bullet.rect)

        # 绘制UI
        lives_text = self.font.render(f"剩余坦克: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 10))

        enemies_text = self.font.render(f"已消灭敌人: {self.enemies_destroyed}/{self.total_enemies}", True, WHITE)
        self.screen.blit(enemies_text, (10, 40))

        level_text = self.font.render(f"坦克等级: {self.player.level}", True, WHITE)
        self.screen.blit(level_text, (10, 70))

        # 如果游戏结束，显示游戏结束信息
        if self.game_over:
            game_over_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            game_over_surf.fill((0, 0, 0, 180))
            self.screen.blit(game_over_surf, (0, 0))

            if self.victory:
                result_text = self.font.render("win!", True, GREEN)
            else:
                result_text = self.font.render("you lose!", True, RED)

            result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(result_text, result_rect)

            restart_text = self.font.render("按ESC键返回主菜单", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(restart_text, restart_rect)
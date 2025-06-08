import pygame
import random
from config import *
from map import GameMap
from tanks import PlayerTank, EnemyTank
from projectiles import Bullet
from structures import Brick, Iron, River, Forest, Headquarters
from items import Fruit, create_random_fruit


class GameScene:
    """游戏主场景"""
    def __init__(self, screen, level=1):
        self.screen = screen
        self.map = GameMap(level)
        self.headquarters = self.map.headquarters
        self.player = PlayerTank(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200)
        self.enemies = []
        self.fruits = []
        self.bullets = []
        self.explosions = []
        self.enemies_destroyed = 0
        self.total_enemies = 20
        self.spawned_enemies = 0
        self.last_spawn_time = 0
        self.game_over = False
        self.victory = False
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 72)
        self.non_target_counter = 0  # 连续非目标坦克计数器
        self.spawn_interval = 1500  # 生成间隔（毫秒）

    def _spawn_enemy(self):
        """生成敌人（带数量限制和目标坦克规则）"""
        # 总敌人未达上限，且当前存活敌人少于5辆
        if self.enemies_destroyed < self.total_enemies and len(self.enemies) < 5:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_spawn_time > self.spawn_interval:
                # 随机选择生成位置（示例位置，可自定义）
                spawn_positions = [
                    (50, 50),
                    (SCREEN_WIDTH // 2 - 20, 50),
                    (SCREEN_WIDTH - 100, 50),
                    (50, SCREEN_HEIGHT - 100),
                    (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
                ]
                pos = random.choice(spawn_positions)

                # 检查是否需要强制生成目标坦克
                if self.non_target_counter >= 3:
                    enemy_type = ENEMY_TARGET
                    self.non_target_counter = 0  # 重置计数器
                else:
                    # 随机生成非目标坦克（普通/快速/装甲）或目标坦克（概率可调整）
                    # 非目标类型占比75%，目标类型占比25%（可通过权重调整）
                    possible_types = [ENEMY_NORMAL, ENEMY_FAST, ENEMY_ARMOR] * 3 + [ENEMY_TARGET]
                    enemy_type = random.choice(possible_types)
                    if enemy_type != ENEMY_TARGET:
                        self.non_target_counter += 1
                    else:
                        self.non_target_counter = 0  # 生成目标坦克后重置计数器

                # 创建敌人并添加到列表
                enemy = EnemyTank(pos[0], pos[1], enemy_type)
                self.enemies.append(enemy)
                self.last_spawn_time = current_time

    def handle_event(self, event):
        """处理事件，包括射击"""
        if event.type == pygame.QUIT:
            return None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.shoot()  # 调用 shoot() 方法，内部已处理数量限制

        return GAME_PLAYING if not self.game_over else GAME_OVER

    def update(self):
        if self.game_over:
            return

        self._spawn_enemy()
        # 更新玩家
        if not self.game_over:
            self.player.handle_input()  # 处理输入并设置移动量
            if not self._check_tank_map_collision(self.player):
                self.player.apply_movement()  # 直接应用移动量

        # 更新敌人（敌人的移动逻辑在 EnemyTank.update() 中）
        for enemy in self.enemies[:]:
            enemy.update()  # 敌人AI逻辑
            if not self._check_tank_map_collision(enemy):
                enemy.image = enemy.images[enemy.direction]
                enemy.apply_movement()
            else:
                enemy.dy = 0
                enemy.dx = 0



        # 更新敌人炮弹
        for enemy in self.enemies[:]:
            bullets_to_remove = []
            for bullet in enemy.bullets:
                if not bullet.update():
                    bullets_to_remove.append(bullet)
                    continue

                # 检查与地图元素的碰撞
                hit_structure = None
                for structure in self.map.structures:
                    if pygame.sprite.collide_rect(bullet, structure):
                        hit_structure = structure
                        break
                #检查与司令部的碰撞
                if pygame.sprite.collide_rect(bullet, self.headquarters):
                    self.game_over  = True
                if hit_structure:
                    # 炮弹可以穿过森林和河流，不处理碰撞
                    if isinstance(hit_structure, Forest) or isinstance(hit_structure, River):
                        continue

                    enemy.bullets.remove(bullet)
                    if isinstance(hit_structure, Brick):
                        if hit_structure.hit(bullet.damage):
                            self.map.structures.remove(hit_structure)
                    elif isinstance(hit_structure, Iron):
                        pass  # 铁墙阻挡但不摧毁
                    elif isinstance(hit_structure, Headquarters):
                        if hit_structure.hit(bullet.damage):
                            self.game_over = True
                    continue  # 跳过后续碰撞检测

                # 检查与玩家的碰撞
                if pygame.sprite.collide_rect(bullet, self.player):
                    enemy.bullets.remove(bullet)
                    if self.player.hit(bullet.damage):
                        if self.player.lives > 0:
                            self.player.lives -= 1
                            self.player.reset()
                        else:
                            self.game_over = True

        # 更新玩家炮弹
        bullets_to_remove = []
        for bullet in self.player.bullets:
            if not bullet.update():
                bullets_to_remove.append(bullet)
                continue

            # 检查与地图元素的碰撞
            hit_structure = None
            for structure in self.map.structures:
                if pygame.sprite.collide_rect(bullet, structure):
                    hit_structure = structure
                    break
            #  检查与司令部的碰撞
            if pygame.sprite.collide_rect(bullet, self.headquarters):
                self.game_over = True
            if hit_structure:
                # 炮弹可以穿过森林和河流，不处理碰撞
                if isinstance(hit_structure, Forest) or isinstance(hit_structure, River):
                    continue
                bullets_to_remove.append(bullet)  # 标记为需要移除
                if isinstance(hit_structure, Brick):
                    if hit_structure.hit(bullet.damage):
                        self.map.structures.remove(hit_structure)
                elif isinstance(hit_structure, Iron):
                    pass  # 铁墙阻挡但不摧毁
                elif isinstance(hit_structure, Headquarters):
                    if hit_structure.hit(bullet.damage):
                        self.game_over = True
                continue  # 跳过后续碰撞检测

            # 检查与敌人坦克的碰撞
            hit_enemy = None
            for enemy in self.enemies[:]:
                if pygame.sprite.collide_rect(bullet, enemy):
                    hit_enemy = enemy
                    break

            if hit_enemy:
                bullets_to_remove.append(bullet)  # 标记为需要移除
                self.player.bullets.remove(bullet)
                if hit_enemy.hit(bullet.damage):
                    self.enemies.remove(hit_enemy)
                    self.enemies_destroyed += 1
                    if hit_enemy.enemy_type == ENEMY_TARGET:
                        fruit = create_random_fruit(hit_enemy.x, hit_enemy.y)
                        self.fruits.append(fruit)
                    # 检查是否胜利
                    if self.enemies_destroyed >= self.total_enemies:
                        self.victory = True
        # 统一移除炮弹
        for bullet in bullets_to_remove:
            if bullet in self.player.bullets:
                self.player.bullets.remove(bullet)

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

    #
    # game_scene.py
    def _check_tank_map_collision(self, tank):
        old_rect = tank.rect.copy()

        # 应用移动量
        tank.rect.x += tank.dx
        tank.rect.y += tank.dy

        # 检查碰撞
        collision = any(
            not structure.can_pass_tank and tank.rect.colliderect(structure.rect)
            for structure in self.map.structures
        )

        if collision:
            tank.rect = old_rect  # 恢复位置
            tank.reset_movement()  # 重置移动量（dx/dy=0）
            return True
        return False

    def draw(self):
        """绘制场景"""
        self.screen.fill(BLACK)

        # 绘制地图元素
        for structure in self.map.structures:
            self.screen.blit(structure.image, structure.rect)
            # 调试：绘制铁墙的碰撞矩形（仅开发阶段使用）
            # if isinstance(structure, Iron):
            #     pygame.draw.rect(self.screen, RED, structure.rect, 1)
            # if isinstance(structure, River):
            #     pygame.draw.rect(self.screen, RED, structure.rect, 1)
            # if isinstance(structure, Brick):
            #     pygame.draw.rect(self.screen, RED, structure.rect, 1)

        # 绘制司令部
        self.screen.blit(self.map.headquarters.image, self.map.headquarters.rect)

        # 绘制果实
        for fruit in self.fruits:
            self.screen.blit(fruit.image, fruit.rect)

        # 绘制玩家
        self.screen.blit(self.player.image, self.player.rect)
        pygame.draw.rect(
                self.screen,  # 目标表面
                (0, 255, 0),  # 绿色
                self.player.rect,  # 玩家坦克的rect
                2  # 边框宽度
            )

        # 绘制玩家炮弹
        for bullet in self.player.bullets:
            self.screen.blit(bullet.image, bullet.rect)
            # pygame.draw.rect(self.screen, RED, bullet.rect, 1)
        # 绘制敌人
        for enemy in self.enemies:
            self.screen.blit(enemy.image, enemy.rect)

            # 绘制敌人炮弹
            for bullet in enemy.bullets:
                self.screen.blit(bullet.image, bullet.rect)

        # 绘制UI
        lives_text = self.font.render(f"Life: {self.player.lives}", True, RED)
        self.screen.blit(lives_text, (10, 10))

        lives_text = self.font.render(f"tolerance: {self.player.health}", True, RED)
        self.screen.blit(lives_text, (10, 40))

        enemies_text = self.font.render(f"destroyed: {self.enemies_destroyed}/{self.total_enemies}", True, WHITE)
        self.screen.blit(enemies_text, (10, 70))

        level_text = self.font.render(f"level: {self.player.level}", True, WHITE)
        self.screen.blit(level_text, (10, 100))

        # 如果游戏结束，显示游戏结束信息
        if self.game_over:
            game_over_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            game_over_surf.fill((0, 0, 0, 180))
            self.screen.blit(game_over_surf, (0, 0))

            if self.victory:
                result_text = self.title_font.render("win!", True, GREEN)
            else:
                result_text = self.title_font.render("boom!", True, RED)

            result_text2 = self.title_font.render("press any key to go on~!", True, WHITE)
            result_rect2 = result_text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(result_text2, result_rect2)
            self.screen.blit(result_text, result_rect)


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
        self.spawn_interval = 180
        self.game_over = False
        self.victory = False
        self.font = pygame.font.SysFont(None, 36)



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
            if self._check_tank_map_collision(enemy):
                enemy.reset_movement()



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
        for enemy in self.enemies[:]:
            for bullet in list(enemy.bullets):
                if not bullet.update():
                    enemy.bullets.remove(bullet)
                    continue

                # 检查与地图元素的碰撞
                hit_structure = None
                for structure in self.map.structures:
                    if pygame.sprite.collide_rect(bullet, structure):
                        hit_structure = structure
                        break

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
            if isinstance(structure, Iron):
                pygame.draw.rect(self.screen, RED, structure.rect, 1)

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
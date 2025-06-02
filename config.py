import pygame
import os
import os

# 游戏窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 坦克设置
TANK_SIZE = 40
PLAYER_SPEED = 5
ENEMY_SPEED = 3

# 炮弹设置
BULLET_SIZE = 10
BULLET_SPEED = 8
BULLET_DAMAGE = 1

# 游戏元素设置
BRICK_HP = 1
IRON_HP = 999  # 不可摧毁
HEADQUARTERS_HP = 1

# 资源路径
RESOURCE_PATH = {
    'images': './images',
    'music': './music'
}

# 方向定义
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

# 坦克等级
TANK_LEVEL_1 = 1
TANK_LEVEL_2 = 2
TANK_LEVEL_3 = 3

# 敌方坦克类型
ENEMY_NORMAL = 1
ENEMY_FAST = 2
ENEMY_ARMOR = 3
ENEMY_TARGET = 4

# 果实类型
FRUIT_STAR = 'star'  # 坦克升级
FRUIT_TANK = 'tank'  # 增加备用坦克
FRUIT_GUN = 'gun'    # 炮弹速度增加
FRUIT_SHELL = 'shell'  # 允许同时发射两发炮弹

# 游戏状态
GAME_START = 0
GAME_PLAYING = 1
GAME_OVER = 2
GAME_WIN = 3
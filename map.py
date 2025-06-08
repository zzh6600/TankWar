# map.py
import random

import pygame
from config import *
from structures import Brick, Iron, River, Forest, Headquarters


class GameMap:
    """游戏地图类，负责管理地图数据和生成地图元素"""
    def __init__(self, level=1):
        self.level = level
        self.tile_size = TILE_SIZE  # 初始化格子尺寸
        self.structures = []  # 存储所有地图结构
        self.headquarters = None  # 司令部对象
        self.matrix = self._load_map_matrix(level)  # 加载地图矩阵
        self._generate_structures()  # 生成地图元素

    def _load_map_matrix(self, level=1):
        if level == 1:
            # 地形类型定义
            EMPTY = 0  # 空地
            BRICK = 1  # 红砖（可摧毁）
            IRON = 2  # 铁墙（不可摧毁）
            RIVER = 3  # 河流（坦克不可通过，子弹可通过）
            FOREST = 4  # 森林（坦克/子弹均可通过）
            HQ = 5  # 司令部（不可摧毁）

            # 顶部围墙（行0）
            top_wall = [IRON] * 26

            # 中间区域（行1-18）
            middle_rows = [
                # 行1-2：对称河流+森林混合带
                [IRON, EMPTY, FOREST, EMPTY, FOREST, EMPTY, FOREST, RIVER, FOREST, RIVER, EMPTY, EMPTY, EMPTY, EMPTY,
                 EMPTY, EMPTY, RIVER, FOREST, RIVER, FOREST, EMPTY, FOREST, EMPTY, FOREST, EMPTY, IRON],
                [IRON, EMPTY, FOREST, EMPTY, FOREST, EMPTY, FOREST, RIVER, FOREST, RIVER, EMPTY, EMPTY, EMPTY, EMPTY,
                 EMPTY, EMPTY, RIVER, FOREST, RIVER, FOREST, EMPTY, FOREST, EMPTY, FOREST, EMPTY, IRON],

                # 行3-7：红砖矩阵+纵向通道
                [IRON, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, EMPTY, EMPTY, EMPTY, EMPTY,
                 BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, IRON],
                [IRON, BRICK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, BRICK, BRICK, EMPTY, EMPTY, EMPTY, EMPTY,
                 BRICK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, BRICK, BRICK, IRON],
                [IRON, BRICK, EMPTY, BRICK, BRICK, BRICK, BRICK, BRICK, EMPTY, BRICK, BRICK, EMPTY, BRICK, BRICK, BRICK,
                 BRICK, EMPTY, BRICK, BRICK, BRICK, BRICK, BRICK, EMPTY, BRICK, BRICK, IRON],
                [IRON, BRICK, EMPTY, BRICK, EMPTY, EMPTY, EMPTY, BRICK, EMPTY, BRICK, BRICK, EMPTY, BRICK, EMPTY, EMPTY,
                 EMPTY, BRICK, EMPTY, BRICK, EMPTY, EMPTY, EMPTY, BRICK, EMPTY, BRICK, IRON],
                [IRON, BRICK, EMPTY, BRICK, BRICK, BRICK, BRICK, BRICK, EMPTY, BRICK, BRICK, EMPTY, BRICK, BRICK, BRICK,
                 BRICK, EMPTY, BRICK, BRICK, BRICK, BRICK, BRICK, EMPTY, BRICK, BRICK, IRON],

                # 行8-10：中心湖泊+铁桥通道
                [IRON, EMPTY, EMPTY, EMPTY, RIVER, RIVER, RIVER, EMPTY, EMPTY, EMPTY, RIVER, RIVER, RIVER, RIVER, RIVER,
                 RIVER, RIVER, RIVER, RIVER, RIVER, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, IRON],
                [IRON, EMPTY, IRON, IRON, IRON, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                 EMPTY, EMPTY, EMPTY, IRON, IRON, IRON, EMPTY, EMPTY, EMPTY, EMPTY, IRON],
                [IRON, EMPTY, IRON, EMPTY, EMPTY, EMPTY, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK,
                 BRICK, BRICK, EMPTY, EMPTY, IRON, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, IRON],

                # 行11-15：森林迷宫+横向通道
                [IRON, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST,
                 BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, IRON],
                [IRON, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK,
                 FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, IRON],
                [IRON, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, EMPTY, EMPTY, EMPTY, EMPTY,
                 EMPTY, EMPTY, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, IRON],
                [IRON, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, EMPTY, EMPTY, EMPTY, EMPTY,
                 EMPTY, EMPTY, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, IRON],
                [IRON, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST,
                 BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, FOREST, BRICK, IRON],

                # 行16-17：司令部前哨防御
                [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                 EMPTY, EMPTY,
                 EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
                [BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK,
                 BRICK,
                 BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK, BRICK],
            ]

            # 底部围墙（行18，司令部居中）
            bottom_wall = [IRON] * 12 + [HQ] + [IRON] * 13  # 司令部位于x=12（更靠左，增加防御难度）

            return [top_wall] + middle_rows + [bottom_wall]
        return []

    # map.py
    def _generate_structures(self):
        for y, row in enumerate(self.matrix):
            for x, tile in enumerate(row):
                # 限制在 MAX_COLS 和 MAX_ROWS 内
                if x >= MAX_COLS or y >= MAX_ROWS:
                    continue
                pos_x = x * self.tile_size
                pos_y = y * self.tile_size

                if tile == TILE_HEADQUARTERS:
                    # 创建司令部对象并赋值给 self.headquarters
                    self.headquarters = Headquarters(pos_x, pos_y)
                    # 在司令部周围添加保护墙（可选）
                    for i in (-1, 0, 1):
                        for j in (-1,):
                            if i == 0 and j == 0:
                                continue
                            self.structures.append(Brick(pos_x + i * self.tile_size, pos_y + j * self.tile_size))
                elif tile == TILE_BRICK:
                    self.structures.append(Brick(pos_x, pos_y))
                elif tile == TILE_IRON:
                    self.structures.append(Iron(pos_x, pos_y))
                elif tile == TILE_RIVER:
                    self.structures.append(River(pos_x, pos_y))
                elif tile == TILE_FOREST:
                    self.structures.append(Forest(pos_x, pos_y))

    def is_tile_blocking(self, x, y):
        """检查指定位置的格子是否阻挡坦克移动"""
        # 边界检查
        if x < 0 or x >= len(self.matrix[0]) or y < 0 or y >= len(self.matrix):
            return True

        tile = self.matrix[y][x]
        # 阻挡坦克的地形：红砖、铁墙、河流、司令部、边界
        return tile in (TILE_BRICK, TILE_IRON, TILE_RIVER, TILE_HEADQUARTERS)

    def get_tile_at(self, x, y):
        """获取指定位置的地图元素类型"""
        if 0 <= y < len(self.matrix) and 0 <= x < len(self.matrix[y]):
            return self.matrix[y][x]
        return TILE_EMPTY  # 超出边界视为空地
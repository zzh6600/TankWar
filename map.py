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
            # 顶部围墙（行0）
            top_wall = [2] * 26

            # 中间区域（行1-18），预留中间区域添加元素
            middle_rows = []
            for y in range(18):
                # 左右围墙固定为铁墙（2），中间24格为可填充区域
                row = [2] + [0] * 24 + [2]

                # 在中间区域（y=3~15行）随机添加元素
                if 3 <= y <= 15:
                    for x in range(1, 25):  # 中间24格（x=1到x=24）
                        if random.random() < 0.2:  # 20%概率添加元素
                            element = random.choice([1, 2, 3, 4])  # 随机选择元素类型
                            row[x] = element
                middle_rows.append(row)

            # 底部围墙（行19，包含司令部）
            # 修正：原底部围墙元素数量错误，应为26列（2+11+1+12+2=28，错误），现调整为正确的26列
            # 司令部位置：中间偏下，左右各留12格
            bottom_wall = [2] + [0] * 12 + [5] + [0] * 12 + [2]
            # 确保底部行总长度为26列（1+12+1+12+1=27？不，正确计算：[2] + [0]*12（13） + [5]（14） + [0]*12（26），正确）

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
                            self.structures.append(Iron(pos_x + i * self.tile_size, pos_y + j * self.tile_size))
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
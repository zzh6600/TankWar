import pygame
from config import RESOURCE_PATH

import sys
import os

class ResourceLoader:
    """资源加载工具类"""

    # 静态变量存储已加载的音效
    _sounds = {}

    @staticmethod
    def load_image(name, colorkey=None):
        """加载图片资源"""
        fullname = os.path.join(RESOURCE_PATH['images'], name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as message:
            print(f"无法加载图片: {fullname}")
            raise SystemExit(message)

        # 转换为优化后的Surface
        image = image.convert()

        # 设置透明色
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)

        return image, image.get_rect()

    @staticmethod
    def load_sound(name):
        """加载音效资源（延迟初始化）"""
        if name in ResourceLoader._sounds:
            return ResourceLoader._sounds[name]

        if not pygame.mixer or not pygame.mixer.get_init():
            print("警告: 混音器未初始化，音效将无法播放")

            class NoneSound:
                def play(self): pass

            sound = NoneSound()
        else:
            fullname = os.path.join(RESOURCE_PATH['music'], name)
            try:
                sound = pygame.mixer.Sound(fullname)
                print(f"成功加载音效: {fullname}")
            except pygame.error as e:
                print(f"无法加载音效: {fullname}")
                print(f"错误详情: {str(e)}")

                class NoneSound:
                    def play(self): pass

                sound = NoneSound()

        # 缓存音效
        ResourceLoader._sounds[name] = sound
        return sound

    @staticmethod
    def load_music(name):
        """加载背景音乐"""
        fullname = os.path.join(RESOURCE_PATH['music'], name)
        try:
            pygame.mixer.music.load(fullname)
        except pygame.error as message:
            print(f"无法加载音乐: {fullname}")

    @staticmethod
    def load_all_images(directory, colorkey=None, accept=('.png', '.jpg', '.bmp')):
        """加载目录下的所有图片"""
        images = {}
        for filename in os.listdir(directory):
            if filename.lower().endswith(accept):
                name = os.path.splitext(filename)[0]
                images[name] = ResourceLoader.load_image(filename, colorkey)
        return images

    @staticmethod
    def load_all_sounds(directory, accept=('.wav', '.mp3', '.ogg', '.mdi')):
        """加载目录下的所有音效"""
        sounds = {}
        for filename in os.listdir(directory):
            if filename.lower().endswith(accept):
                name = os.path.splitext(filename)[0]
                sounds[name] = ResourceLoader.load_sound(filename)
        return sounds
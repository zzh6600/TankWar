import pygame
import sys
from config import *
from start_scene import StartScene
from game_scene import GameScene
from end_scene import EndScene
from resources import ResourceLoader

class TankWarGame:
    """坦克大战游戏主类"""

    def __init__(self):
        pygame.init()
        # 强制初始化混音器并设置参数
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("混音器初始化成功")
        except pygame.error as e:
            print(f"混音器初始化失败: {e}")
            # 可以选择在此处退出游戏，或者使用静默模式
            # sys.exit(1)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TankWar")

        self.clock = pygame.time.Clock()
        self.running = True
        self.current_scene = None
        self.scene_state = GAME_START

        # 加载资源
        self._load_resources()

        # 初始化场景
        self._init_scenes()  # 初始化场景，但不创建游戏场景实例

        def _init_scenes(self):
            """初始化场景（延迟创建游戏场景，避免复用旧实例）"""
            self.scenes = {
                GAME_START: StartScene(self.screen),
                GAME_PLAYING: None,  # 动态创建
                GAME_OVER: None  # 动态创建
            }
            self.current_scene = self.scenes[GAME_START]

        def reset_game(self):
            """完全重置游戏，创建全新的游戏场景和结束场景"""
            self.scenes[GAME_PLAYING] = GameScene(self.screen)  # 新建游戏场景
            self.scenes[GAME_OVER] = EndScene(self.screen, victory=False)  # 新建结束场景
            self.scene_state = GAME_PLAYING  # 直接进入游戏场景（或根据需求返回开始场景）

        def handle_events(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                next_state = self.current_scene.handle_event(event)

                if next_state is not None:
                    if next_state == GAME_PLAYING:
                        # 从开始场景或结束场景进入游戏时，重置游戏
                        self.reset_game()
                    elif next_state == GAME_OVER:
                        # 传递胜利状态
                        self.scenes[GAME_OVER] = EndScene(
                            self.screen,
                            self.scenes[GAME_PLAYING].victory
                        )

                    self.scene_state = next_state
                    self.current_scene = self.scenes.get(next_state, self.scenes[GAME_START])

    def _load_resources(self):
        """加载游戏资源"""
        try:
            ResourceLoader.load_music('start.wav')
            pygame.mixer.music.play(1)  # -1 表示循环播放
        except pygame.error as e:
            print(f"加载背景音乐失败: {e}")

    def _init_scenes(self):
        """初始化游戏场景"""
        self.scenes = {
            GAME_START: StartScene(self.screen),
            GAME_PLAYING: GameScene(self.screen),
            GAME_OVER: EndScene(self.screen, False)
        }

        self.current_scene = self.scenes[self.scene_state]

    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # 处理场景事件
            next_state = self.current_scene.handle_event(event)

            # 场景切换
            if next_state is not None and next_state != self.scene_state:
                self.scene_state = next_state

                # 如果切换到游戏结束场景，传递胜利状态
                if self.scene_state == GAME_OVER:
                    self.scenes[GAME_OVER] = EndScene(self.screen, self.scenes[GAME_PLAYING].victory)
                # 如果切换到游戏开始场景，重置游戏
                if self.scene_state == GAME_START:
                    self.scenes[GAME_PLAYING] = GameScene(self.screen)
                    self.scenes[GAME_OVER] = EndScene(self.screen, False)

                self.current_scene = self.scenes[self.scene_state]
            elif next_state is None:
                self.running = False



    def update(self):
        """更新游戏状态"""
        if self.running:
            self.current_scene.update()

    def draw(self):
        """绘制游戏画面"""
        if self.running:
            self.current_scene.draw()
            pygame.display.flip()

    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = TankWarGame()
    game.run()
    pygame.quit()
    sys.exit()
import time
import cv2
from Logger.ScriptLogger import logger
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key


class InitEnvironment:
    def __init__(self, game_window):
        self.window = game_window
        self.keyboard = KeyboardController()
        self.init_done = False
        self.max_retries = 3

    def press_esc(self):
        """使用 pynput 硬件级模拟按键（绕过一梦江湖虚拟输入检测）"""
        logger.info("正在发送物理级 ESC 键...")
        try:
            self.keyboard.press(Key.esc)
            time.sleep(0.1)
            self.keyboard.release(Key.esc)

            # 备用方案
            import keyboard

            keyboard.press_and_release("esc")
            time.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"发送ESC失败: {e}")
            return False

    def is_settings_opened(self):
        """识别设置界面是否打开"""
        img = self.window.screenshot()
        if img is None:
            return False

        template_path = "Resources/templates/settings_flag.png"
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            logger.warning("未找到设置识别模板，请检查路径！")
            return False

        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val >= threshold:
            logger.info(f"检测到设置界面（置信度: {max_val:.3f}）")
            return True
        return False

    def switch_to_pc_mode(self):
        """先点击手游模式，再切换到端游模式"""
        hand_mode_coords = [(1030, 680), (1030, 680)]
        pc_mode_coords = [(1180, 680), (1180, 680)]

        logger.info("正在切换为端游模式...")
        for x, y in hand_mode_coords:
            self.window.click(x, y, delay=0.8)
        time.sleep(1.2)
        for x, y in pc_mode_coords:
            self.window.click(x, y, delay=0.8)
        time.sleep(1.0)

    def escape_stuck(self):
        """脱离卡死，等待角色回到复活点"""
        logger.info("执行脱离卡死...")
        self.window.click(1180, 480, delay=0.5)
        time.sleep(3.5)

    def close_settings(self):
        """关闭设置界面"""
        logger.info("关闭设置界面...")
        self.press_esc()
        time.sleep(1.0)

    def run(self):
        if self.init_done:
            logger.info("初始化已完成，跳过重复执行")
            return True

        logger.info("开始执行环境初始化...")

        success = False
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"第 {attempt} 次尝试打开设置界面...")
            self.press_esc()
            time.sleep(2.0)

            if self.is_settings_opened():
                self.switch_to_pc_mode()
                self.escape_stuck()
                self.close_settings()
                logger.info("环境初始化完成！已切换端游模式 + 脱离卡死")
                self.init_done = True
                success = True
                break
            else:
                logger.warning("未检测到设置界面")

        if not success:
            logger.error("初始化失败！请手动按 ESC 打开设置并切换为端游模式")
            try:
                import ctypes

                ctypes.windll.user32.MessageBoxW(
                    0,
                    "请手动按 ESC 打开游戏设置界面\n然后切换为【端游模式】\n完成后点击“确定”脚本将继续运行",
                    "需要手动初始化环境",
                    1,
                )
            except Exception:
                pass
            logger.info("等待用户手动完成初始化...")
            self.init_done = True

        return True

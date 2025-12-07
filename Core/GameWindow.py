# Core/GameWindow.py   ← 完整替换整个文件（这次直接给你最干净版本）

import win32gui
import win32con
import win32api
import time
import pyautogui
import numpy as np

class GameWindow:
    def __init__(self):
        self.hwnd = None
        self.target_w = 1280
        self.target_h = 720

    def find_window(self):
        """精准查找一梦江湖游戏主窗口（绝不绑定脚本自己）"""
        def callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return True

            # 排除我们自己的脚本窗口（标题包含“脚本助手”或类名含 Qt）
            class_name = win32gui.GetClassName(hwnd)
            if ("脚本助手" in title or
                "Qt5QWindowIcon" in class_name or
                "python" in title.lower()):
                return True

            # 一梦江湖正式客户端特征：标题包含“一梦江湖”，且窗口足够大
            if "一梦江湖" in title:
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    w = rect[2] - rect[0]
                    h = rect[3] - rect[1]
                    if w >= 800 and h >= 600:  # 排除登录器小窗
                        extra.append((hwnd, title, w, h))
                except:
                    pass
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if not windows:
            return False, "未找到一梦江湖游戏主窗口！\n请确认游戏已进入游戏（不是登录器）"

        # 选最大的那个窗口（通常就是游戏主窗口）
        windows.sort(key=lambda x: x[2] * x[3], reverse=True)
        self.hwnd = windows[0][0]
        self.title = windows[0][1]
        return True, f"绑定成功：{self.title[:40]}"

        # Core/GameWindow.py  ← 只替换下面两个方法

    def force_resize_to_topleft(self):
        """强制 1280×720 + 贴左上角 (0,0) + 完全无边框"""
        if not self.hwnd or not win32gui.IsWindow(self.hwnd):
            return False, "窗口已失效"

        # 1) 记录原始状态（用于恢复）
        self.original_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_STYLE)
        self.original_exstyle = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        self.original_rect = win32gui.GetWindowRect(self.hwnd)

        # 2) 切换为无边框（POPUP）。注意：无边框时 外框尺寸=客户区尺寸，禁止再加边框补偿
        new_style = win32con.WS_POPUP | win32con.WS_VISIBLE
        new_exstyle = self.original_exstyle & ~win32con.WS_EX_APPWINDOW  # 可选：不占任务栏
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_STYLE, new_style)
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, new_exstyle)

        # 3) 还原最大化状态，设置精确尺寸到 (0,0, 1280×720)
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetWindowPos(
            self.hwnd, win32con.HWND_TOP,
            0, 0, 1280, 720,
            win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW | win32con.SWP_NOZORDER
        )

        # 4) 校验一次客户区大小；若首帧未生效，短暂等待后重试
        cr = win32gui.GetClientRect(self.hwnd)
        cw, ch = cr[2] - cr[0], cr[3] - cr[1]
        if (cw, ch) != (1280, 720):
            time.sleep(0.2)
            win32gui.SetWindowPos(
                self.hwnd, win32con.HWND_TOP,
                0, 0, 1280, 720,
                win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW | win32con.SWP_NOZORDER
            )
        return True, "已强制为无边框 1280×720 并移动到 (0,0)"

    def restore_original_window(self):
        """恢复游戏窗口原始边框、大小、位置"""
        if not self.hwnd or not win32gui.IsWindow(self.hwnd):
            return
        try:
            # 如果没有记录过原样式，直接跳过，避免异常
            orig_style = getattr(self, "original_style", None)
            orig_ex = getattr(self, "original_exstyle", None)
            orig_rect = getattr(self, "original_rect", None)
            if orig_style is None or orig_ex is None or orig_rect is None:
                return

            win32gui.SetWindowLong(self.hwnd, win32con.GWL_STYLE, orig_style)
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, orig_ex)
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            win32gui.SetWindowPos(
                self.hwnd, win32con.HWND_TOP,
                orig_rect[0], orig_rect[1],
                orig_rect[2] - orig_rect[0],
                orig_rect[3] - orig_rect[1],
                win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW | win32con.SWP_NOZORDER
            )
        except Exception:
            pass

    def click(self, x, y, delay=0.1):
        """基于客户区坐标点击（完美免疫系统缩放）"""
        if not self.hwnd:
            return False
        try:
            lParam = win32api.MAKELPARAM(x, y)
            win32gui.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
            win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            time.sleep(delay)
            win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lParam)
            return True
        except:
            return False

    def screenshot(self):
        """截取游戏客户区"""
        if not self.hwnd:
            return None
        try:
            left, top = win32gui.ClientToScreen(self.hwnd, (0, 0))
            right, bottom = win32gui.ClientToScreen(self.hwnd, (1280, 720))
            img = pyautogui.screenshot(region=(left, top, 1280, 720))
            return np.array(img)
        except:
            return None

    def bring_to_front(self):
        """将游戏窗口激活到前台，保证按键/点击可用"""
        if not self.hwnd or not win32gui.IsWindow(self.hwnd):
            return False
        try:
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(self.hwnd)
            return True
        except Exception:
            return False

    def is_valid(self):
        return self.hwnd and win32gui.IsWindow(self.hwnd)


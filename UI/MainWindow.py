# UI/MainWindow.py  （完整替换整个文件）
from PyQt5.QtWidgets import QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
import os
import time
import win32gui

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("一梦江湖 · 脚本助手")
        self.setGeometry(100, 100, 1100, 720)
        self.setMinimumSize(1000, 650)
        self.game_window = None  # 全局保存游戏窗口实例

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧导航栏
        self.init_left_menu(layout)

        # 右侧内容区
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget, stretch=1)

        # 初始化页面
        self.init_pages()

        # 默认显示主页并高亮
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.update_menu_highlight(self.home_btn)

    def init_left_menu(self, layout):
        menu = QWidget()
        menu.setFixedWidth(130)
        menu.setStyleSheet("background-color: #1e1e1e;")
        menu_layout = QVBoxLayout(menu)
        menu_layout.setAlignment(Qt.AlignTop)
        menu_layout.setSpacing(15)
        menu_layout.setContentsMargins(15, 60, 15, 60)

        # 样式
        normal_style = """
            QPushButton {
                background-color: transparent;
                color: #cccccc;
                text-align: left;
                padding: 16px 20px;
                font-size: 17px;
                font-weight: bold;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover { background-color: #333333; color: white; }
        """
        active_style = """
            QPushButton {
                background-color: #0d7377;
                color: white;
                text-align: left;
                padding: 16px 20px;
                font-size: 17px;
                font-weight: bold;
                border-radius: 12px;
            }
        """

        buttons = [
            ("主页", self.show_home),
            ("任务", self.show_task),
            ("运行", self.show_run),
            ("设置", self.show_settings),
        ]

        self.menu_buttons = {}
        for text, func in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(normal_style)
            btn.clicked.connect(lambda checked, f=func, b=btn: (f(), self.update_menu_highlight(b)))
            menu_layout.addWidget(btn)
            self.menu_buttons[text] = btn

        # 保存引用用于高亮
        self.home_btn = self.menu_buttons["主页"]
        self.task_btn = self.menu_buttons["任务"]
        self.run_btn = self.menu_buttons["运行"]
        self.settings_btn = self.menu_buttons["设置"]

        layout.addWidget(menu)

    def update_menu_highlight(self, active_btn):
        for btn in self.menu_buttons.values():
            btn.setStyleSheet("""
                QPushButton { background-color: transparent; color: #cccccc; padding: 16px 20px; border-radius: 12px; }
                QPushButton:hover { background-color: #333333; color: white; }
            """)
        active_btn.setStyleSheet("""
            QPushButton { background-color: #0d7377; color: white; padding: 16px 20px; border-radius: 12px; }
        """)

    def init_pages(self):
        from UI.HomePage import HomePage
        from UI.TaskPage import TaskPage
        from UI.RunPage import RunPage
        from UI.SettingsPage import SettingsPage

        self.home_page = HomePage()
        self.task_page = TaskPage()
        self.run_page = RunPage()
        self.settings_page = SettingsPage()

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.task_page)
        self.stacked_widget.addWidget(self.run_page)
        self.stacked_widget.addWidget(self.settings_page)

    def show_home(self): self.stacked_widget.setCurrentWidget(self.home_page); self.update_menu_highlight(self.home_btn)
    def show_task(self): self.stacked_widget.setCurrentWidget(self.task_page); self.update_menu_highlight(self.task_btn)
    def show_run(self):  self.stacked_widget.setCurrentWidget(self.run_page);  self.update_menu_highlight(self.run_btn)
    def show_settings(self): self.stacked_widget.setCurrentWidget(self.settings_page); self.update_menu_highlight(self.settings_btn)

# UI/MainWindow.py  ← 只加这一个方法（放在 class 最后面）

    def closeEvent(self, event):
        """窗口真正关闭时触发，一定会执行"""
        print("[MainWindow] 正在关闭，准备恢复游戏窗口...")
        if hasattr(self, "game_window") and self.game_window:
            if getattr(self.game_window, "hwnd", None) and win32gui.IsWindow(self.game_window.hwnd):
                try:
                    print("[恢复窗口] 正在恢复边框和原始位置...")
                    self.game_window.restore_original_window()
                    time.sleep(0.4)  # 必须留足时间，否则恢复失败
                except Exception as e:
                    print(f"[恢复失败] {e}")
        event.accept()  # 允许关闭
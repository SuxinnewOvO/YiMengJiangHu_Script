# UI/RunPage.py   ← 完整替换
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from Logger.ScriptLogger import logger
import time

class RunThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.running = True

    def run(self):
        try:
            game = self.main_window.game_window
            if not game or not game.is_valid():
                self.log_signal.emit("错误：游戏窗口未绑定！请先在任务页点击“绑定窗口”")
                return

            # 获取执行列表
            exec_list = self.main_window.task_page.exec_list
            task_count = exec_list.count()

            if task_count == 0:
                self.log_signal.emit("执行列表为空！请在任务页添加任务")
                return

            self.log_signal.emit(f"开始执行 {task_count} 个任务...")

            for i in range(task_count):
                if not self.running:
                    self.log_signal.emit("任务已被手动停止")
                    break

                item = exec_list.item(i)
                task_name = item.text()
                self.log_signal.emit(f"[{i+1}/{task_count}] 正在执行：{task_name}")

                # 这里未来会调用真正的任务逻辑
                if task_name == "课业":
                    self.log_signal.emit("课业任务执行中...（待实现）")
                    time.sleep(3)
                elif task_name == "每日一卦":
                    self.log_signal.emit("每日一卦任务执行中...（待实现）")
                    time.sleep(3)

                self.log_signal.emit(f"{task_name} 已完成")

            self.log_signal.emit("所有任务执行完成！")
        except Exception as e:
            self.log_signal.emit(f"执行出错：{e}")
        finally:
            self.finished_signal.emit()

class RunPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 按钮区
        top = QHBoxLayout()
        self.start_btn = QPushButton("开始运行")
        self.stop_btn = QPushButton("停止运行")
        self.stop_btn.setEnabled(False)

        self.start_btn.setStyleSheet("background: #4CAF50; color: white; font-size: 18px; padding: 12px;")
        self.stop_btn.setStyleSheet("background: #f44336; color: white; font-size: 18px; padding: 12px;")

        top.addWidget(self.start_btn)
        top.addWidget(self.stop_btn)
        top.addStretch()
        layout.addLayout(top)

        # 日志区
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # 连接按钮
        self.start_btn.clicked.connect(self.start_running)
        self.stop_btn.clicked.connect(self.stop_running)

        # 日志重定向
        logger.set_text_widget(self.log_text)

        self.thread = None

    def start_running(self):
        if self.thread and self.thread.isRunning():
            return

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_text.clear()
        logger.info("脚本开始运行...")

        # 获取主窗口
        main_window = self.window()
        self.thread = RunThread(main_window)
        self.thread.log_signal.connect(logger.info)
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.start()

    def stop_running(self):
        if self.thread and self.thread.isRunning():
            self.thread.running = False
            self.thread.wait()
        logger.info("已强制停止")

    def on_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        logger.info("任务线程已结束")
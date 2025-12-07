from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QListWidget, QPushButton, QVBoxLayout,
                             QLabel, QInputDialog, QMessageBox, QListWidgetItem)
from PyQt5.QtCore import Qt, QDir, QTimer
from Core.GameWindow import GameWindow
from Logger.ScriptLogger import logger
from Tasks.InitEnvironment import InitEnvironment
import json
import os
import threading

# 专门存放执行列表的文件夹
LISTS_DIR = "ExecutionLists"

if not os.path.exists(LISTS_DIR):
    os.makedirs(LISTS_DIR)

class TaskPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25)


        # 第一栏：任务列表
        left = QVBoxLayout()
        title1 = QLabel("任务列表")
        title1.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title1.setAlignment(Qt.AlignCenter)
        self.task_list = QListWidget()
        self.task_list.addItems(["课业", "每日一卦"])
        self.task_list.setStyleSheet("font-size: 16px; padding: 8px;")
        self.task_list.itemDoubleClicked.connect(self.add_to_execution)
        left.addWidget(title1)
        left.addWidget(self.task_list)

        # 第二栏：执行列表
        mid = QVBoxLayout()
        title2 = QLabel("执行列表（双击删除 | 可拖动排序）")
        title2.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title2.setAlignment(Qt.AlignCenter)
        self.exec_list = QListWidget()
        self.exec_list.setDragDropMode(QListWidget.InternalMove)
        self.exec_list.setDefaultDropAction(Qt.MoveAction)
        self.exec_list.setStyleSheet("font-size: 16px; padding: 8px;")
        self.exec_list.itemDoubleClicked.connect(self.remove_from_execution)
        mid.addWidget(title2)
        mid.addWidget(self.exec_list)

        # 第三栏：按钮区
        right = QVBoxLayout()
        right.addSpacing(40)

        # 绑定窗口按钮（保持强调色块、凸显可点击性）
        self.bind_btn = QPushButton("绑定窗口")
        self.init_btn = QPushButton("初始化")
        self.bind_btn.setFixedHeight(60)
        self.init_btn.setFixedHeight(60)
        self.bind_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px; font-weight: bold;
                color: white;
                background-color: #0d7377;
                border: 2px solid #0a5a5d;
                border-radius: 12px;
                padding: 10px 16px;
            }
            QPushButton:hover { background-color: #0a5a5d; }
            QPushButton:pressed { background-color: #085054; }
        """)
        self.init_btn.setStyleSheet(self.bind_btn.styleSheet())

        # 其它功能按钮：恢复之前的立体按钮质感，避免像输入框
        btn_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #0d7377;
                background-color: #f4f9ff;
                border: 2px solid #0d7377;
                border-radius: 10px;
                padding: 10px 18px;
            }
            QPushButton:hover { background-color: #e4f4ff; }
            QPushButton:pressed { background-color: #cce7ff; }
        """

        self.save_btn = QPushButton("保存列表")
        self.load_btn = QPushButton("读取列表")
        self.reset_btn = QPushButton("重置列表")

        for btn in (self.save_btn, self.load_btn, self.reset_btn):
            btn.setFixedHeight(55)
            btn.setStyleSheet(btn_style)

        right.addWidget(self.bind_btn)
        right.addWidget(self.init_btn)
        right.addSpacing(20)
        right.addWidget(self.save_btn)
        right.addWidget(self.load_btn)
        right.addWidget(self.reset_btn)
        right.addStretch()

        # 连接信号
        self.save_btn.clicked.connect(self.save_execution_list)
        self.load_btn.clicked.connect(self.load_execution_list)
        self.reset_btn.clicked.connect(self.reset_execution_list)
        self.bind_btn.clicked.connect(self.bind_game_window)
        self.init_btn.clicked.connect(self.run_manual_init)

        layout.addLayout(left, 1)
        layout.addLayout(mid, 1)
        layout.addLayout(right, 1)



    def add_to_execution(self, item):
        text = item.text()
        if text not in [self.exec_list.item(i).text() for i in range(self.exec_list.count())]:
            self.exec_list.addItem(text)

    def remove_from_execution(self, item):
        row = self.exec_list.row(item)
        self.exec_list.takeItem(row)

    def save_execution_list(self):
        name, ok = QInputDialog.getText(self, "保存执行列表", "请输入方案名称：", text="默认方案")
        if not ok or not name.strip():
            return
        name = "".join(c for c in name if c.isalnum() or c in " _-")[:30]  # 过滤非法字符
        if not name:
            name = "未命名方案"

        items = [self.exec_list.item(i).text() for i in range(self.exec_list.count())]
        data = {"name": name, "tasks": items}

        filepath = os.path.join(LISTS_DIR, f"{name}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "成功", f"执行列表已保存：\n{name}")
            self.load_btn.setText(f"读取列表 ({len(os.listdir(LISTS_DIR))})")  # 显示数量
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败：{e}")

    def load_execution_list(self):
        files = [f for f in os.listdir(LISTS_DIR) if f.endswith(".json")]
        if not files:
            QMessageBox.information(self, "提示", "当前没有已保存的执行列表")
            return

        items = []
        for f in files:
            try:
                with open(os.path.join(LISTS_DIR, f), "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    items.append((data.get("name", f.split(".")[0]), os.path.join(LISTS_DIR, f)))
            except:
                continue

        names = [name for name, _ in items]
        name, ok = QInputDialog.getItem(self, "读取执行列表", f"选择一个方案（共 {len(names)} 个）", names, 0, False)
        if not ok:
            return

        selected_path = next(path for n, path in items if n == name)
        with open(selected_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.exec_list.clear()
        for task in data.get("tasks", []):
            self.exec_list.addItem(task)

        QMessageBox.information(self, "成功", f"已加载方案：{data.get('name', '未知')}")

    def reset_execution_list(self):
        if self.exec_list.count() == 0:
            QMessageBox.information(self, "提示", "执行列表已为空")
            return
        reply = QMessageBox.question(self, "确认重置", "确定要清空当前执行列表吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.exec_list.clear()
            QMessageBox.information(self, "完成", "执行列表已重置")

    def bind_game_window(self):
        self.bind_btn.setEnabled(False)
        self.bind_btn.setText("正在绑定...")

        try:
            from Core.GameWindow import GameWindow
            from Logger.ScriptLogger import logger

            game = GameWindow()
            success, msg = game.find_window()
            if not success:
                QMessageBox.critical(self, "绑定失败", msg)
                logger.error(f"绑定失败：{msg}")
                self.bind_btn.setText("绑定窗口")
                self.bind_btn.setEnabled(True)
                return

            logger.info(f"找到游戏窗口：{getattr(game, 'title', '未知')}")

            success, msg = game.force_resize_to_topleft()
            if not success:
                QMessageBox.warning(self, "调整窗口失败", msg)
                logger.warning(f"调整窗口失败：{msg}")
            else:
                logger.info("窗口强制调整成功 → 1280×720 + 贴左上角 (0,0)")

                # 保存到全局
                main_window = self.window()
                if main_window:
                    main_window.game_window = game

                QMessageBox.information(self, "绑定成功",
                                        "游戏窗口已成功绑定并强制为 1280×720\n位置：屏幕左上角 (0,0)\n已自动屏蔽“窗口已失效”弹窗")

                logger.info("绑定完成，如需初始化请点击右侧【初始化】按钮")
                self.bind_btn.setText("重新绑定")

        except Exception as e:
            import traceback
            error_msg = f"绑定过程发生未知错误：\n{str(e)}\n\n{traceback.format_exc()}"
            logger.error(error_msg)
            QMessageBox.critical(self, "绑定崩溃", error_msg)
            self.bind_btn.setText("绑定窗口")
        finally:
            self.bind_btn.setEnabled(True)

    def run_manual_init(self):
        game = getattr(self.window(), "game_window", None)
        if not game:
            QMessageBox.warning(self, "未绑定窗口", "请先绑定游戏窗口，再执行初始化。")
            logger.warning("初始化请求被拒绝：未找到已绑定的游戏窗口")
            return

        self.init_btn.setEnabled(False)
        self.init_btn.setText("初始化中...")

        def worker():
            try:
                logger.info("开始执行手动初始化任务...")
                init_task = InitEnvironment(game)
                init_task.run()
                logger.info("手动初始化任务执行完毕")
            except Exception as e:
                logger.error(f"初始化任务出现异常：{e}")
                QMessageBox.critical(self, "初始化失败", f"初始化时出现异常：\n{e}")
            finally:
                QTimer.singleShot(0, self._reset_init_button)

        threading.Thread(target=worker, daemon=True).start()

    def _reset_init_button(self):
        self.init_btn.setEnabled(True)
        self.init_btn.setText("初始化")
# UI/HomePage.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtCore import Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(30)

        title = QLabel("Su楚留香·全自动脚本助手")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #0d7377;")
        title.setAlignment(Qt.AlignCenter)

        info = QTextEdit()
        info.setReadOnly(True)
        info.setStyleSheet("font-size: 16px; background: #f8f9fa; border: 1px solid #ddd; padding: 20px;")
        info.setFixedHeight(400)
        info.setText("""
    欢迎使用一梦江湖全自动脚本 v1.0

    当前已支持功能：
    • 课业自动完成
    • 每日一卦自动领取与完成
    • 执行队列自由排序（支持拖动）
    • 执行列表保存/读取（可快速切换方案）
    • 游戏窗口自动绑定与缩放适配
    • 完整日志实时查看

    使用方法：
    1. 在【设置】页填写游戏路径与缩放比例并保存
    2. 在【任务】页双击添加需要执行的任务
    3. 可拖动调整执行顺序，或保存常用方案
    4. 切换到【运行】页点击 “开始运行”

    作者：SuZhang     版本：2025.12.06
        """.strip())

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()
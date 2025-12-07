# UI/SettingsPage.py  （完整替换）
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QFileDialog, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from Utils.ConfigManager import ConfigManager

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(30)

        title = QLabel("脚本设置")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form.setSpacing(25)

        self.game_path_edit = QLineEdit()
        self.game_path_edit.setFixedHeight(55)
        self.game_path_edit.setStyleSheet("font-size: 18px; padding: 10px;")

        self.scale_edit = QLineEdit()
        self.scale_edit.setFixedHeight(55)
        self.scale_edit.setStyleSheet("font-size: 18px; padding: 10px;")
        self.scale_edit.setPlaceholderText("如：1.0 或 1.5")

        btn_choose = QPushButton("选择游戏启动程序")
        btn_save = QPushButton("保存设置")

        for btn in (btn_choose, btn_save):
            btn.setFixedHeight(55)
            btn.setStyleSheet("font-size: 20px; font-weight: bold; background: #0d7377; color: white; border-radius: 10px;")

        btn_choose.clicked.connect(self.select_game_path)
        btn_save.clicked.connect(self.save_settings)

        form.addRow("<b>游戏启动路径：</b>", self.game_path_edit)
        form.addRow("", btn_choose)
        form.addRow("<b>屏幕缩放比例（如1.5）：</b>", self.scale_edit)
        form.addRow("", btn_save)

        layout.addLayout(form)
        layout.addStretch()

        self.load_settings()

    def select_game_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择一梦江湖客户端", "", "可执行文件 (*.exe)")
        if path:
            self.game_path_edit.setText(path)

    def save_settings(self):
        scale_text = self.scale_edit.text().strip()
        try:
            scale = float(scale_text) if scale_text else 1.0
            if scale <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "错误", "缩放比例必须是大于0的数字！")
            return

        self.config.save({
            "game_path": self.game_path_edit.text(),
            "scale": str(scale)
        })
        QMessageBox.information(self, "成功", "设置已保存！")

    def load_settings(self):
        cfg = self.config.load()
        self.game_path_edit.setText(cfg.get("game_path", ""))
        self.scale_edit.setText(cfg.get("scale", "1.0"))
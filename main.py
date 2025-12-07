# main.py  ← 完整替换成这个版本
import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from UI.MainWindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
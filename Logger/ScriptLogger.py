# Logger/ScriptLogger.py
import logging
from PyQt5.QtCore import QObject, pyqtSignal

class TextEditHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.append(msg)

class Logger(QObject):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("Script")
        self.logger.setLevel(logging.INFO)

    def set_text_widget(self, widget):
        handler = TextEditHandler(widget)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(handler)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

logger = Logger()
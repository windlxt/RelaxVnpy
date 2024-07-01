from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
from PySide6.QtGui import QColor, QPainter, QPalette, QFont
from PySide6.QtCore import Qt


class MultiColorButton(QPushButton):
    def __init__(self, text='', parent=None):
        super(MultiColorButton, self).__init__(text, parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        palette = self.palette()

        # 设置文本格式，根据需要设置颜色
        formats = [
            (self.text().split(' ')[0], QColor(255, 0, 0)),  # 红色
            (' ' + self.text().split(' ')[1], QColor(0, 255, 0)),  # 绿色
            (' ' + self.text().split(' ')[2], QColor(0, 0, 255)),  # 蓝色
        ]

        # 绘制文本
        y = self.fontMetrics().ascent() + 1
        x = 0
        for text, color in formats:
            painter.setPen(QColor(color))
            painter.drawText(x, y, text)
            x += painter.fontMetrics().boundingRect(text).width()


class ExampleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Multi-color Button Example')

        button = MultiColorButton('Hello Multi-color World')

        vbox = QVBoxLayout()
        vbox.addWidget(button)

        self.setLayout(vbox)
        self.show()


if __name__ == '__main__':
    app = QApplication([])
    ex = ExampleApp()
    app.exec()
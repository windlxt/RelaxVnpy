from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QSizePolicy
from PySide6.QtGui import QPainter, QPen, QBrush
from PySide6.QtCore import Qt


class PaintWidget(QWidget):
    def __init__(self, parent=None):
        super(PaintWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.i = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.blue, 1))
        painter.setBrush(QBrush(Qt.red))
        painter.drawEllipse(10, 10, 100, 50)
        self.i = self.i+ 1
        print('i = ', self.i)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.paint_widget = PaintWidget(self)
        self.setCentralWidget(self.paint_widget)

        self.ii = 0

    def resizeEvent(self, event):
        self.paint_widget.update()

    def paintEvent(self, event):
        self.ii = self.ii+ 1
        print('ii = ', self.ii)


def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()


if __name__ == '__main__':
    main()
"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月07日
"""
from vnpy.event import EventEngine
import vnpy.trader.engine

from PySide6 import QtGui
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSize, QRect, QMetaObject, QPoint
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QStackedWidget, \
    QToolBar, QWidget, QSizePolicy, QVBoxLayout, QLayout, QTextEdit, QMenuBar, QMenu, QStatusBar, QPushButton, QHBoxLayout

from .future_window import FutureWindow
from .. import utility


class TradingPlatformWindow(QWidget):
    """
    主窗口
    """
    def __init__(self, main_engine, event_engine):
        """初始化窗口"""
        super().__init__()
        self.main_engine = main_engine
        self.event_engine = event_engine

        self.resize(utility.SCREEN_RECT.width() / 2, utility.SCREEN_RECT.height() / 2)

        self.vlayout = QVBoxLayout(self)
        # 显示文本
        self.textEdit = QTextEdit()
        self.textEdit.setText('量化交易系统：第 < 1.0 > 无极版')
        self.textEdit.setAlignment(Qt.AlignCenter)
        self.vlayout.addWidget(self.textEdit)
        # 创建按钮
        self.pbtn_stock = QPushButton('股票')
        self.pbtn_stock.setFixedHeight(50)
        self.pbtn_future = QPushButton('期货')
        self.pbtn_future.setFixedHeight(50)
        self.pbtn_other = QPushButton('其他')
        self.pbtn_other.setFixedHeight(50)

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.pbtn_stock)
        self.hlayout.addWidget(self.pbtn_future)
        self.hlayout.addWidget(self.pbtn_other)
        self.vlayout.addLayout(self.hlayout)

        self.bind()

    def bind(self):
        self.pbtn_stock.clicked.connect(self.open_stock_window)
        self.pbtn_future.clicked.connect(self.open_future_window)
        self.pbtn_other.clicked.connect(self.open_other_window)

    def open_stock_window(self):
        pass

    def open_future_window(self):
        future_window = FutureWindow(self.main_engine, self.event_engine)
        future_window.showMaximized()

    def open_other_window(self):
        pass










"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月07日
"""
import vnpy
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout

from vnpy.trader.ui.future_window import FutureWindow
from vnpy_datamanager_stock.ui.stock_widget_database import StockManagerWidget
from .stock_main_window import StockMainWindow
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

        self.window_title: str = f"量化交易系统 - {vnpy.__version__}   [{utility.TRADER_DIR}]"
        self.resize(utility.SCREEN_RECT.width() / 3, utility.SCREEN_RECT.height() / 3)

        self.init_ui()
        self.bind()

    def init_ui(self):
        self.setWindowTitle(self.window_title)
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
        self.pbtn_data_manager = QPushButton('数据管理')
        self.pbtn_data_manager.setFixedHeight(50)
        self.pbtn_funds_manager = QPushButton('资金管理')
        self.pbtn_funds_manager.setFixedHeight(50)
        self.pbtn_server = QPushButton('服务器模式')
        self.pbtn_server.setFixedHeight(50)
        self.pbtn_close = QPushButton('关闭')
        self.pbtn_close.setFixedHeight(50)

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.pbtn_stock)
        self.hlayout.addWidget(self.pbtn_future)
        self.hlayout.addWidget(self.pbtn_data_manager)
        self.hlayout.addWidget(self.pbtn_funds_manager)
        self.hlayout.addWidget(self.pbtn_server)
        self.hlayout.addWidget(self.pbtn_close)
        self.vlayout.addLayout(self.hlayout)

    def bind(self):
        self.pbtn_stock.clicked.connect(self.open_stock_window)
        self.pbtn_future.clicked.connect(self.open_future_window)
        self.pbtn_data_manager.clicked.connect(self.open_data_manager)
        self.pbtn_funds_manager.clicked.connect(self.open_funds_manager)
        self.pbtn_server.clicked.connect(self.open_server_window)
        self.pbtn_close.clicked.connect(self.close)

    @Slot()
    def open_stock_window(self):
        print('open stock window.')
        win = StockMainWindow(self.main_engine, self.event_engine)
        win.showMaximized()

    @Slot()
    def open_future_window(self):
        self.future_window = FutureWindow(self.main_engine, self.event_engine)
        self.future_window.showMaximized()

    @Slot()
    def open_data_manager(self):
        print('open data manager.')
        self.data_manager_window = StockManagerWidget(self.main_engine, self.event_engine)
        self.data_manager_window.show()

    @Slot()
    def open_funds_manager(self):
        print('open funds manager window.')
        pass

    @Slot()
    def open_server_window(self):
        print('open server window.')
        pass

    @Slot()
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Call main engine close function before exit.
        """
        self.main_engine.close()

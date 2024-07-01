"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年06月22日
"""
import qdarkstyle
import pandas as pd
from threading import Thread

from PySide6.QtWidgets import QWidget, QApplication, QCheckBox, QVBoxLayout, \
    QPushButton, QHBoxLayout, QLabel, QFrame, QRadioButton, QGridLayout, QStackedWidget, \
    QHeaderView, QTableWidget, QTreeWidget, QTreeWidgetItem, QTextEdit, QLineEdit, \
    QComboBox, QDateEdit, QTableWidgetItem, QDialog, QFormLayout, QFileDialog, QMessageBox, QLayout
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtCore import Slot, QDate, Qt, Signal

from vnpy_filter_backtester_stock.stock_filter_engine import StockFilterEngine
from vnpy.trader.engine import MainEngine, EventEngine, Event


class StockFilterWidget(QWidget):
    """筛选股票窗口"""
    def __init__(self, main_engine=None, event_engine=None) -> None:
        """"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        # 获取股票数据的引擎
        self.stock_engine = StockFilterEngine(self.main_engine, self.event_engine)

        self.setWindowTitle("筛选股票窗口")
        self.resize(1920, 1080)
        # Set up icon
        icon = QIcon("/vnpy_filter_backtester_stock/ui/filter.ico")
        self.setWindowIcon(icon)

        self.init_ui()

    def init_ui(self):
        """初始化窗口"""
        self.pbtn = QPushButton('   按钮   ', self)

    @Slot()
    def closeEvent(self, event: QCloseEvent) -> None:
        self.main_engine.close()


if __name__ == '__main__':
    app = QApplication()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))

    eng = EventEngine()
    main_eng = MainEngine(eng)

    win = StockFilterWidget(main_eng, eng)
    win.show()
    app.exec()

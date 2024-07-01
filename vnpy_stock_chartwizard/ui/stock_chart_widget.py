import qdarkstyle
import qtawesome as qta
from copy import copy
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from tzlocal import get_localzone_name

from PySide6.QtWidgets import QApplication, QWidget, QTabWidget, QLineEdit, QPushButton, QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy, QListWidget
from PySide6.QtCore import Signal, Slot, QSize, Qt
from PySide6.QtGui import QCloseEvent

from vnpy.event import EventEngine, Event
from vnpy.chart import StockChartWidget, CandleItem, VolumeItem
from vnpy.trader.engine import MainEngine

from vnpy.trader.event import EVENT_TICK
from vnpy.trader.object import ContractData, TickData, BarData, SubscribeRequest
from vnpy.trader.utility import BarGenerator, ZoneInfo, printr
from vnpy.trader.constant import Interval
from vnpy_spreadtrading.base import SpreadData, EVENT_SPREAD_DATA
from vnpy.trader.setting import SETTINGS

from vnpy_stock_chartwizard.stock_chart_engine import APP_NAME, EVENT_STOCK_CHART_HISTORY, StockChartWizardEngine


class StockChartWizardWidget(QWidget):
    """股票K线图显示窗口"""

    signal_history: Signal = Signal(Event)

    instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            # cls._instance = super(Singleton, cls).__new__(cls)
            cls._instance = super().__new__(cls, *args, **kwargs)  # 类的属性
        return cls._instance

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        if not self.instance:
            super().__init__()

            self.main_engine: MainEngine = main_engine
            self.event_engine: EventEngine = event_engine

            self.chart_engine: StockChartWizardEngine = StockChartWizardEngine(self.main_engine, self.event_engine)
            self.charts = []

            self.init_ui()
            self.register_event()

            self.instance = self._instance

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("股票K线图表")

        self.ledit_stock_code: QLineEdit = QLineEdit()
        self.ledit_stock_code.returnPressed.connect(self.process_ledit_show_chart)

        pbtn_icon = qta.icon('fa.bar-chart',
                             options=[{'color': 'red', 'opacity': 0.7}])
        pbtn_k_chart: QPushButton = QPushButton(pbtn_icon, "显示K线图")
        pbtn_k_chart.setIconSize(QSize(25, 25))
        pbtn_k_chart.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pbtn_k_chart.setFixedSize(130, 30)
        pbtn_k_chart.clicked.connect(self.process_ledit_show_chart)

        self.lw_chart_stock = QListWidget()
        self.lw_chart_stock.clicked.connect(self.process_listwidget_show_chart)

        vlayout: QVBoxLayout = QVBoxLayout()
        vlayout.addWidget(QLabel("股票代码："))
        vlayout.addWidget(self.ledit_stock_code)
        vlayout.addWidget(pbtn_k_chart)
        vlayout.addWidget(self.lw_chart_stock)

        widget_left = QWidget()
        widget_left.setLayout(vlayout)
        widget_left.setFixedWidth(150)

        self.tab_stock_chart: QTabWidget = QTabWidget()

        hlayout_all: QHBoxLayout = QHBoxLayout()
        hlayout_all.addWidget(widget_left)
        hlayout_all.addWidget(self.tab_stock_chart)

        self.setLayout(hlayout_all)

    def create_chart(self) -> StockChartWidget:
        """"""
        chart: StockChartWidget = StockChartWidget()
        chart.add_plot("candle", hide_x_axis=True)
        chart.add_plot("volume", maximum_height=200)
        chart.add_item(CandleItem, "candle", "candle")
        chart.add_item(VolumeItem, "volume", "volume")
        chart.add_cursor()
        return chart

    @Slot()
    def process_ledit_show_chart(self):
        stock_code: str = self.ledit_stock_code.text()
        if not stock_code:
            return

        self.process_show_k_line_chart(stock_code)

    @Slot()
    def process_listwidget_show_chart(self):
        stock_code = None
        for item in self.lw_chart_stock.selectedItems():
            stock_code: str = item.get_data()['code']

        if stock_code:
            self.process_show_k_line_chart(stock_code)

    def process_show_k_line_chart(self, stock_code) -> None:
        """显示K线图"""

        stock_code_name = self.chart_engine.get_code_name(stock_code)
        # 创建 日、周、月 股票K线图
        self.tab_stock_chart.clear()
        self.charts.clear()

        chart_daily: StockChartWidget = self.create_chart()
        self.charts.append(chart_daily)
        self.tab_stock_chart.addTab(chart_daily, stock_code_name+'_日K线')

        chart_week: StockChartWidget = self.create_chart()
        self.charts.append(chart_week)
        self.tab_stock_chart.addTab(chart_week, stock_code_name + '_周K线')

        chart_month: StockChartWidget = self.create_chart()
        self.charts.append(chart_month)
        self.tab_stock_chart.addTab(chart_month, stock_code_name + '_月K线')

        # Query history data
        self.startdate: str = SETTINGS["database.startdate"]
        start = datetime.strptime(self.startdate, '%Y-%m-%d')
        end: datetime = datetime.now(ZoneInfo(get_localzone_name()))

        # 查询 日、周、月 K线
        self.chart_engine.query_history(stock_code, 'd | w | m', start, end)

    def register_event(self) -> None:
        """"""
        self.signal_history.connect(self.process_history_event)
        self.event_engine.register(EVENT_STOCK_CHART_HISTORY, self.signal_history.emit)

    def process_history_event(self, event: Event) -> None:
        """"""
        history: List = event.data
        if not history:
            return

        # 逐个更新 日、周、月 K线图
        chart_daily: StockChartWidget = self.charts[0]
        chart_daily.update_history(history[0])

        chart_week: StockChartWidget = self.charts[1]
        chart_week.update_history(history[1])

        chart_month: StockChartWidget = self.charts[2]
        chart_month.update_history(history[2])

    def show(self) -> None:
        self.showMaximized()

    # @Slot()
    # def closeEvent(self, event: QCloseEvent) -> None:
    #     self.main_engine.close()


if __name__ == '__main__':
    app = QApplication()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))

    eng = EventEngine()
    main_eng = MainEngine(eng)

    win = StockChartWizardWidget(main_eng, eng)
    win.showMaximized()
    app.exec()

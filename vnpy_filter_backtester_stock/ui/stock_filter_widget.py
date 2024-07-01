"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年06月22日
"""
from types import ModuleType
from importlib import import_module
import qdarkstyle
import pandas as pd
import qtawesome as qta
from threading import Thread

from PySide6.QtWidgets import QWidget, QApplication, QCheckBox, QVBoxLayout, \
    QPushButton, QHBoxLayout, QLabel, QFrame, QRadioButton, QGridLayout, QStackedWidget, \
    QHeaderView, QTableWidget, QTreeWidget, QTreeWidgetItem, QTextEdit, QLineEdit, \
    QComboBox, QDateEdit, QTableWidgetItem, QDialog, QFormLayout, QFileDialog, QMessageBox, QLayout, QListWidget, QStyle, QSizePolicy
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtCore import Slot, QDate, Qt, Signal, QSize

from vnpy_filter_backtester_stock.stock_filter_engine import StockFilterEngine, MyListWidgetItem
from vnpy.trader.engine import MainEngine, EventEngine, Event
from vnpy_stock_chartwizard.ui import StockChartWizardWidget


class StockFilterWidget(QWidget):
    """筛选股票窗口"""
    def __init__(self, main_engine=None, event_engine=None) -> None:
        """"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        # 获取股票数据的引擎
        self.filter_engine = StockFilterEngine(self.main_engine, self.event_engine)

        self.setWindowTitle("筛选股票窗口")
        self.resize(1920, 1080)
        # Set up icon
        icon = QIcon("/vnpy_filter_backtester_stock/ui/filter.ico")
        self.setWindowIcon(icon)

        self.cb_index_list = []
        self.cb_stock_list = []

        # TODO: 从文件夹中读取策略
        self.index_strategys = ['all']
        self.index_strategys.extend(self.filter_engine.get_all_index_strategies())
        self.stock_strategys = ['all']
        self.stock_strategys.extend(self.filter_engine.get_all_stock_strategies())

        self.init_ui()

    def init_ui(self):
        """初始化窗口"""
        # 1. 设置 筛选指数 窗口
        self.vlayout_index = QVBoxLayout()
        self.label_filter_index = QLabel('筛选指数策略：')
        self.label_filter_index.setStyleSheet("QLabel{"
                                              "text-align : center;"
                                              "font-family:'Microsoft YaHei';"
                                              "font-size:18px;"
                                              "color:yellow;}")

        self.cb_filter_index_strategy = QComboBox()
        self.cb_filter_index_strategy.addItems(self.index_strategys)
        self.cb_index_list.append(self.cb_filter_index_strategy)

        self.hlayout_1 = QHBoxLayout()
        add_icon = qta.icon('ph.plus-bold',
                                    options=[{'color': 'red', 'opacity': 0.7}])
        self.pbtn_add_strategy_index = QPushButton(add_icon, '')
        self.pbtn_add_strategy_index.setFixedWidth(30)
        self.pbtn_add_strategy_index.clicked.connect(self.add_combo_box_index)

        minus_icon = qta.icon('ph.minus-bold',
                            options=[{'color': 'cyan', 'opacity': 0.7}])
        self.pbtn_minus_strategy_index = QPushButton(minus_icon, '')
        self.pbtn_minus_strategy_index.setFixedWidth(30)
        self.pbtn_minus_strategy_index.clicked.connect(self.minus_combo_box_index)

        self.pbtn_filter_index = QPushButton("筛选指数")
        self.pbtn_filter_index.clicked.connect(self.filter_index_by_strategies)

        self.hlayout_1.addWidget(self.pbtn_add_strategy_index)
        self.hlayout_1.addWidget(self.pbtn_minus_strategy_index)
        self.hlayout_1.addWidget(self.pbtn_filter_index)

        self.lw_index = QListWidget()
        self.filter_engine.load_index_all(self.lw_index)

        self.pbtn_show_index_k_chart = QPushButton('查看指数K线图')
        self.pbtn_show_index_k_chart.setStyleSheet("QPushButton{"
                                            "text-align : center;"
                                            "font-family:'Microsoft YaHei';"
                                            "font-size:18px;"
                                            "color:cyan;}")
        self.pbtn_show_index_k_chart.clicked.connect(self.process_show_k_line_chart)

        self.vlayout_index.addWidget(self.label_filter_index)
        self.vlayout_index.addWidget(self.cb_filter_index_strategy)
        self.vlayout_index.addLayout(self.hlayout_1)
        self.vlayout_index.addWidget(self.lw_index)
        self.vlayout_index.addWidget(self.pbtn_show_index_k_chart)

        # 2. 增加按钮
        arrow_right_icon = qta.icon('mdi.share-all',
                                    options=[{'color': 'cyan', 'opacity': 0.7}])
        pbtn_1 = QPushButton(arrow_right_icon, '')
        pbtn_1.setIconSize(QSize(40, 40))
        pbtn_1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pbtn_1.setFixedSize(40, 40)

        arrow_right_double_icon = qta.icon('mdi.expand-all',
                                           options=[{'color': 'cyan', 'opacity': 0.7}])
        pbtn_2 = QPushButton(arrow_right_double_icon, '')
        pbtn_2.setIconSize(QSize(40, 40))
        pbtn_2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pbtn_2.setFixedSize(40, 40)
        pbtn_2.clicked.connect(self.load_stock_all)
        vlayout_pbtn1 = QVBoxLayout()
        vlayout_pbtn1.addWidget(pbtn_1)
        vlayout_pbtn1.addWidget(pbtn_2)

        # 3. 设置 筛选股票 窗口
        self.vlayout_stock = QVBoxLayout()
        self.label_filter_stock = QLabel('筛选股票策略：')
        self.label_filter_stock.setStyleSheet("QLabel{"
                                            "text-align : center;"
                                            "font-family:'Microsoft YaHei';"
                                            "font-size:18px;"
                                            "color:yellow;}")

        self.cb_filter_stock_strategy = QComboBox()
        self.cb_filter_stock_strategy.addItems(self.stock_strategys)
        self.cb_stock_list.append(self.cb_filter_stock_strategy)

        self.hlayout_2 = QHBoxLayout()
        add_icon = qta.icon('ph.plus-bold',
                            options=[{'color': 'red', 'opacity': 0.7}])
        self.pbtn_add_strategy_stock = QPushButton(add_icon, '')
        self.pbtn_add_strategy_stock.setFixedWidth(30)
        self.pbtn_add_strategy_stock.clicked.connect(self.add_combo_box_stock)

        minus_icon = qta.icon('ph.minus-bold',
                              options=[{'color': 'cyan', 'opacity': 0.7}])
        self.pbtn_minus_strategy_stock = QPushButton(minus_icon, '')
        self.pbtn_minus_strategy_stock.setFixedWidth(30)
        self.pbtn_minus_strategy_stock.clicked.connect(self.minus_combo_box_stock)

        self.pbtn_filter_stock = QPushButton("筛选股票")
        self.pbtn_filter_stock.clicked.connect(self.filter_stock_by_strategies)


        self.hlayout_2.addWidget(self.pbtn_add_strategy_stock)
        self.hlayout_2.addWidget(self.pbtn_minus_strategy_stock)
        self.hlayout_2.addWidget(self.pbtn_filter_stock)

        self.lw_stock = QListWidget()
        self.lw_stock.itemDoubleClicked.connect(self.select_single_result_stock)

        self.pbtn_show_stock_k_chart = QPushButton('查看股票K线图')
        self.pbtn_show_stock_k_chart.setStyleSheet("QPushButton{"
                             "text-align : center;"
                             "font-family:'Microsoft YaHei';"
                             "font-size:18px;"
                             "color:cyan;}")
        self.pbtn_show_stock_k_chart.clicked.connect(self.process_show_k_line_chart)

        self.vlayout_stock.addWidget(self.label_filter_stock)
        self.vlayout_stock.addWidget(self.cb_filter_stock_strategy)
        self.vlayout_stock.addLayout(self.hlayout_2)
        self.vlayout_stock.addWidget(self.lw_stock)
        self.vlayout_stock.addWidget(self.pbtn_show_stock_k_chart)

        # 4. 增加按钮
        arrow_right_icon = qta.icon('fa5s.angle-right',
                              options=[{'color': 'cyan', 'opacity': 0.7}])
        pbtn_3 = QPushButton(arrow_right_icon, '')
        pbtn_3.setIconSize(QSize(40, 40))
        pbtn_3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pbtn_3.setFixedSize(40, 40)
        pbtn_3.clicked.connect(self.select_single_result_stock)

        arrow_right_double_icon = qta.icon('fa5s.angle-double-right',
                                    options=[{'color': 'cyan', 'opacity': 0.7}])
        pbtn_4 = QPushButton(arrow_right_double_icon, '')
        pbtn_4.setIconSize(QSize(40, 40))
        pbtn_4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pbtn_4.setFixedSize(40, 40)
        pbtn_4.clicked.connect(self.select_all_result_stock)
        # pbtn_2.setStyleSheet("QPushButton{"
        #                      "text-align : left;"
        #                      "font-family:'Microsoft YaHei';"
        #                      "font-size:18px;"
        #                      "color:yellow;}")
        vlayout_pbtn2 = QVBoxLayout()
        vlayout_pbtn2.addWidget(pbtn_3)
        vlayout_pbtn2.addWidget(pbtn_4)

        # 5. 设置 自选股票 窗口
        self.vlayout_self_select_stock = QVBoxLayout()
        self.label_filter_self_select = QLabel('自选股票池：')
        self.label_filter_self_select.setStyleSheet("QLabel{"
                                                 "text-align : center;"
                                                 "font-family:'Microsoft YaHei';"
                                                 "font-size:18px;"
                                                 "color:yellow;}")

        self.lw_self_select = QListWidget()
        self.lw_self_select.itemDoubleClicked.connect(self.delete_single_stock)

        clear_icon = qta.icon('msc.clear-all',
                                           options=[{'color': 'red', 'opacity': 0.7}])
        self.pbtn_self_select_clear = QPushButton(clear_icon, '清空自选股票')
        self.pbtn_self_select_clear.setIconSize(QSize(28, 28))
        # self.pbtn_self_select_clear.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pbtn_self_select_clear.setStyleSheet("QPushButton{"
                                                         "text-align : center;"
                                                         "font-family:'Microsoft YaHei';"
                                                         "font-size:18px;"
                                                         "color:cyan;}")
        self.pbtn_self_select_clear.clicked.connect(self.lw_self_select.clear)

        self.pbtn_show_self_select_k_chart = QPushButton('查看自选股票K线图')
        self.pbtn_show_self_select_k_chart.setStyleSheet("QPushButton{"
                                            "text-align : center;"
                                            "font-family:'Microsoft YaHei';"
                                            "font-size:18px;"
                                            "color:cyan;}")
        self.pbtn_show_self_select_k_chart.clicked.connect(self.process_show_k_line_chart)

        self.vlayout_self_select_stock.addWidget(self.label_filter_self_select)
        self.vlayout_self_select_stock.addWidget(self.lw_self_select)
        self.vlayout_self_select_stock.addWidget(self.pbtn_self_select_clear)
        self.vlayout_self_select_stock.addWidget(self.pbtn_show_self_select_k_chart)

        # 6. 占位
        self.pbn = QPushButton('占位')

        # 设置窗口布局
        self.widget_left = QWidget()
        self.widget_left.setFixedWidth(600)
        self.hlayout_left = QHBoxLayout()
        self.hlayout_left.addLayout(self.vlayout_index)
        self.hlayout_left.addLayout(vlayout_pbtn1)
        self.hlayout_left.addLayout(self.vlayout_stock)
        self.hlayout_left.addLayout(vlayout_pbtn2)
        self.hlayout_left.addLayout(self.vlayout_self_select_stock)
        self.widget_left.setLayout(self.hlayout_left)

        self.hlayout_all = QHBoxLayout()
        self.hlayout_all.addWidget(self.widget_left)
        self.hlayout_all.addWidget(self.pbn)
        self.setLayout(self.hlayout_all)


    @Slot()
    def delete_single_stock(self):
        for item in self.lw_self_select.selectedItems():
            row = self.lw_self_select.row(item)
            self.lw_self_select.takeItem(row)

    @Slot()
    def select_single_result_stock(self):
        flag = True
        for item in self.lw_stock.selectedItems():
            i = MyListWidgetItem(item.get_data()['code_name'], item.get_data())

            for row in range(self.lw_self_select.count()):
                item = self.lw_self_select.item(row)
                if item.text() == i.text():
                    flag = False
                    break
            if flag:
                self.lw_self_select.addItem(i)

    @Slot()
    def select_all_result_stock(self):
        self.lw_self_select.clear()
        for row in range(self.lw_stock.count()):
            item = self.lw_stock.item(row)
            i = MyListWidgetItem(item.get_data()['code_name'], item.get_data())
            self.lw_self_select.addItem(i)

    @Slot()
    def load_stock_all(self):
        self.filter_engine.load_stock_all(self.lw_stock)

    @Slot()
    def filter_index_by_strategies(self):
        pass

    @Slot()
    def filter_stock_by_strategies(self):
        pass

    @Slot()
    def add_combo_box_index(self):
        # 创建一个新的ComboBox并添加到布局中
        combo_box = QComboBox()
        combo_box.addItems(self.index_strategys)
        self.vlayout_index.insertWidget(self.vlayout_index.count() - 3, combo_box)
        self.cb_index_list.append(combo_box)

    @Slot()
    def add_combo_box_stock(self):
        # 创建一个新的ComboBox并添加到布局中
        combo_box = QComboBox()
        combo_box.addItems(self.stock_strategys)
        self.vlayout_stock.insertWidget(self.vlayout_stock.count() - 3, combo_box)
        self.cb_stock_list.append(combo_box)

    @Slot()
    def minus_combo_box_index(self):
        # TODO: 减少布局中1个ComboBox
        pass

    @Slot()
    def minus_combo_box_stock(self):
        # TODO: 减少布局中1个ComboBox
        pass

    @Slot()
    def process_show_k_line_chart(self):
        # app = self.main_engine.apps['StockChartWizard']
        # ui_module: ModuleType = import_module(app.app_module + ".ui")
        # widget_class: QWidget = getattr(ui_module, app.widget_name)
        # self.window_chartwizard = widget_class(self.main_engine, self.event_engine)
        self.window_chartwizard = StockChartWizardWidget(self.main_engine, self.event_engine)

        button = self.sender()
        match button:
            case self.pbtn_show_index_k_chart:
                self.window_chartwizard.lw_chart_stock.clear()
                for row in range(self.lw_index.count()):
                    item = self.lw_index.item(row)
                    i = MyListWidgetItem(item.get_data()['code_name'], item.get_data())
                    i.setTextAlignment(Qt.AlignLeft)
                    self.window_chartwizard.lw_chart_stock.insertItem(row, i)

            case self.pbtn_show_stock_k_chart:
                self.window_chartwizard.lw_chart_stock.clear()
                for row in range(self.lw_stock.count()):
                    item = self.lw_stock.item(row)
                    i = MyListWidgetItem(item.get_data()['code_name'], item.get_data())
                    self.window_chartwizard.lw_chart_stock.insertItem(row, i)

            case self.pbtn_show_self_select_k_chart:
                self.window_chartwizard.lw_chart_stock.clear()
                for row in range(self.lw_self_select.count()):
                    item = self.lw_self_select.item(row)
                    i = MyListWidgetItem(item.get_data()['code_name'], item.get_data())
                    self.window_chartwizard.lw_chart_stock.insertItem(row, i)

            case '_':
                print('打开股票K线图出错！')

        self.window_chartwizard.show()
        if self.window_chartwizard.lw_chart_stock.count() > 0:
            self.window_chartwizard.lw_chart_stock.setCurrentRow(0)
            self.window_chartwizard.process_show_k_line_chart(self.window_chartwizard.lw_chart_stock.item(0).get_data()['code'])

    # @Slot()
    # def closeEvent(self, event: QCloseEvent) -> None:
    #     self.main_engine.close()


if __name__ == '__main__':
    app = QApplication()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))

    eng = EventEngine()
    main_eng = MainEngine(eng)

    win = StockFilterWidget(main_eng, eng)
    win.show()
    app.exec()

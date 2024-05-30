"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月21日
"""
import qdarkstyle
import pandas as pd
from threading import Thread

from PySide6.QtWidgets import QWidget, QApplication, QCheckBox, QVBoxLayout, \
    QPushButton, QHBoxLayout, QLabel, QFrame, QRadioButton, QGridLayout, QStackedWidget, \
    QHeaderView, QTableWidget, QTreeWidget, QTreeWidgetItem, QTextEdit, QLineEdit, \
    QComboBox, QDateEdit, QTableWidgetItem
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtCore import Slot, QDate, Qt
from pymongo.cursor import Cursor

from vnpy_datamanager_stock.engine_database_stock import ManagerEngineStock, download_data_scheduler
from vnpy.trader.engine import MainEngine, EventEngine, Event
from vnpy.trader.event import EVENT_UPDATE_DATABASE_FINISHED
from vnpy.trader import utility

import vnpy_baostock_stock.baostock_stock_datafeed


class ManagerWidgetStock(QWidget):
    """
    Main window of the Database manager.
    """
    def __init__(self, main_engine=None, event_engine=None) -> None:
        """"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        # 获取股票数据的引擎
        self.stock_engine = ManagerEngineStock(self.main_engine, self.event_engine)

        self.setWindowTitle("股票数据库管理")
        self.resize(1600, 800)
        # Set up icon
        icon = QIcon(utility.get_icon_path(__file__, "vnpy.ico"))
        self.setWindowIcon(icon)

        self.database_updating = False
        self.tablewidget: QTableWidget = QTableWidget()  # 右边输出表格

        self.init_ui()
        self.register_event()

    def init_ui(self):
        """初始化窗口"""
        # 设置左上的 更新数据 控件
        self.cbox_download_date_schuduler = QCheckBox('按计划更新数据')
        self.cbox_download_date_schuduler.stateChanged.connect(self.update_database_schudule)

        self.pbtn_update_database = QPushButton('立即更新数据')
        self.pbtn_update_database.clicked.connect(self.update_database)

        self.frame1 = QFrame()
        self.frame1.setFrameShape(QFrame.Box)  # 设置边框形状

        self.hlayout = QHBoxLayout(self.frame1)
        self.hlayout.addWidget(self.cbox_download_date_schuduler)
        self.hlayout.addWidget(self.pbtn_update_database)

        # 设置 baostock、ifind等数据源
        self.rb_baostock = QRadioButton("数据宝 BaoStock")
        self.rb_baostock.setChecked(True)
        self.rb_baostock.toggled.connect(lambda: self.change_stackwidget(0))
        self.rb_ifind = QRadioButton("同花顺 iFinD")
        self.rb_ifind.toggled.connect(lambda: self.change_stackwidget(1))
        self.rb_dtshare = QRadioButton("分布式 DTShare")
        self.rb_dtshare.toggled.connect(lambda: self.change_stackwidget(2))
        self.rb_tushare = QRadioButton("挖地兔 Tushare")
        self.rb_tushare.toggled.connect(lambda: self.change_stackwidget(3))

        self.glayout_database = QGridLayout()
        self.glayout_database.addWidget(self.rb_baostock, 0, 0)
        self.glayout_database.addWidget(self.rb_ifind, 0, 1)
        self.glayout_database.addWidget(self.rb_dtshare, 1, 0)
        self.glayout_database.addWidget(self.rb_tushare, 1, 1)


        self.frame2 = QFrame()
        self.frame2.setFrameShape(QFrame.Box)  # 设置边框形状
        self.frame2.setLayout(self.glayout_database)

        # 设置 stackwidget 控件
        self.stackwidget = QStackedWidget()
        self.stackwidget.setFrameShape(QFrame.Box)

        self.stackwidget.addWidget(StackBaostock(self.main_engine, self.event_engine, self.stock_engine, self.tablewidget))
        self.stackwidget.addWidget(QLabel('堆栈窗口2'))
        self.stackwidget.addWidget(QLabel('堆栈窗口3'))
        self.stackwidget.addWidget(QLabel('堆栈窗口4'))
        self.stackwidget.setCurrentIndex(0)


        # 左面板，控件加入布局
        self.vlayout_left = QVBoxLayout()
        self.vlayout_left.addWidget(self.frame1)
        self.vlayout_left.addWidget(self.frame2)
        self.vlayout_left.addWidget(self.stackwidget)

        self.wighet_left = QWidget()
        self.wighet_left.setFixedWidth(750)
        self.wighet_left.setLayout(self.vlayout_left)


        # 右面板 ==========================================
        # 设置右上的 导入数据、导出数据 控件
        self.pbtn_import = QPushButton('导入数据')
        self.pbtn_import.clicked.connect(self.import_data)

        self.pbtn_export = QPushButton('导出数据')
        self.pbtn_export.clicked.connect(self.export_data)


        self.frame3 = QFrame()
        self.frame3.setFrameShape(QFrame.Box)  # 设置边框形状

        self.hlayout_right = QHBoxLayout(self.frame3)
        self.hlayout_right.addStretch()
        self.hlayout_right.addWidget(self.pbtn_import)
        self.hlayout_right.addWidget(self.pbtn_export)
        self.frame3.setLayout(self.hlayout_right)

        # 设置右边布局
        self.vlayout_right = QVBoxLayout()
        self.vlayout_right.addWidget(self.frame3)
        self.vlayout_right.addWidget(self.tablewidget)

        self.wighet_right = QWidget()
        self.wighet_right.setLayout(self.vlayout_right)

        # 左、右面板，加入窗口布局 =========================
        self.hlayout_all = QHBoxLayout(self)
        self.hlayout_all.addWidget(self.wighet_left)
        self.hlayout_all.addWidget(self.wighet_right)

    def register_event(self):
        self.event_engine.register(EVENT_UPDATE_DATABASE_FINISHED, self.process_update_database_finished)
        print(f'目前共注册了 {len(self.event_engine._handlers.keys())} 个事件类型：')
        i=1
        for k, v in self.event_engine._handlers.items():
            print('{:<3}{:<24} : {}'.format(i, k, v))
            i += 1

        print(f'目前共注册了 {len(self.event_engine._general_handlers)} 个事件通用函数：')
        i = 1
        for v in self.event_engine._general_handlers:
            print('{:<3}{}'.format(i, v))
            i += 1

    @Slot()
    def import_data(self):
        pass

    @Slot()
    def export_data(self):
        pass

    @Slot()
    def change_stackwidget(self, n):
        self.stackwidget.setCurrentIndex(n)

    @Slot()
    def update_database_schudule(self):
        if self.cbox_download_date_schuduler.isChecked():
            print('按计划更新数据库')
        else:
            print('取消数据库更新计划')

    @Slot()
    def update_database(self):
        self.pbtn_update_database.setText('数据更新中...')
        self.pbtn_update_database.setEnabled(False)

        t = Thread(target=self.stock_engine.update_baostock_database)
        t.start()

        self.database_updating = True

    @Slot()
    def process_update_database_finished(self, event):
        self.pbtn_update_database.setText('立即更新数据')
        self.pbtn_update_database.setEnabled(True)
        print("数据库更新完毕。")
        self.database_updating = False

    @Slot()
    def closeEvent(self, event: QCloseEvent) -> None:
        if self.database_updating:
            print("数据库更新未完成，请重新更新！")
        self.main_engine.close()


class StackBaostock(QWidget):
    def __init__(self, main_engine, event_engine, stock_engine, tablewidget):
        super().__init__()
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.stock_engine = stock_engine
        self.tablewidget = tablewidget

        self.init_ui()

    def init_ui(self):
        labels: list = ["数据类别", "代码", "交易所", "数据量", "开始时间", "结束时间", ""]

        self.tree: QTreeWidget = QTreeWidget(self)
        self.tree.setColumnCount(len(labels))
        self.tree.setHeaderLabels(labels)
        self.tree.setStyleSheet("QTreeView::item { text-align: center; }")
        self.tree.itemClicked.connect(self.on_tree_item_clicked)

        self.industry_child: QTreeWidgetItem = QTreeWidgetItem()
        self.industry_child.setText(0, "板块行业")
        self.tree.addTopLevelItem(self.industry_child)

        self.stock_list_child: QTreeWidgetItem = QTreeWidgetItem()
        self.stock_list_child.setText(0, "个股名单")
        self.tree.addTopLevelItem(self.stock_list_child)

        self.daily_child: QTreeWidgetItem = QTreeWidgetItem()
        self.daily_child.setText(0, "日K线数据")
        self.tree.addTopLevelItem(self.daily_child)

        self.week_child: QTreeWidgetItem = QTreeWidgetItem(self.tree)
        self.week_child.setText(0, "周K线数据")
        self.tree.addTopLevelItem(self.week_child)

        self.month_child: QTreeWidgetItem = QTreeWidgetItem(self.tree)
        self.month_child.setText(0, "月K线数据")
        self.tree.addTopLevelItem(self.month_child)

        self.other_child: QTreeWidgetItem = QTreeWidgetItem(self.tree)
        self.other_child.setText(0, "其他")
        self.tree.addTopLevelItem(self.other_child)

        # ====向K线数据中加控件=================
        # 日K线
        symbol_daily = QLineEdit('600000')
        self.tree.setItemWidget(self.daily_child, 1, symbol_daily)

        exchange_daily = QComboBox()
        exchange_daily.addItems(['sh', 'sz'])
        self.tree.setItemWidget(self.daily_child, 2, exchange_daily)

        date_begin_daily = QDateEdit()
        date_begin_daily.setDate(QDate(2020, 1, 1))
        self.tree.setItemWidget(self.daily_child, 4, date_begin_daily)

        date_end_daily = QDateEdit()
        date_end_daily.setDate(QDate.currentDate())
        self.tree.setItemWidget(self.daily_child, 5, date_end_daily)

        show_button_daily: QPushButton = QPushButton("查看")
        self.tree.setItemWidget(self.daily_child, 6, show_button_daily)

        # 周K线
        symbol_week = QLineEdit('600000')
        self.tree.setItemWidget(self.week_child, 1, symbol_week)

        exchange_week = QComboBox()
        exchange_week.addItems(['sh', 'sz'])
        self.tree.setItemWidget(self.week_child, 2, exchange_week)

        date_begin_week = QDateEdit()
        date_begin_week.setDate(QDate(2020, 1, 1))
        self.tree.setItemWidget(self.week_child, 4, date_begin_week)

        date_end_week = QDateEdit()
        date_end_week.setDate(QDate.currentDate())
        self.tree.setItemWidget(self.week_child, 5, date_end_week)

        show_button_week: QPushButton = QPushButton("查看")
        self.tree.setItemWidget(self.week_child, 6, show_button_week)

        # 月K线
        symbol_month = QLineEdit('600000')
        self.tree.setItemWidget(self.month_child, 1, symbol_month)

        exchange_month = QComboBox()
        exchange_month.addItems(['sh', 'sz'])
        self.tree.setItemWidget(self.month_child, 2, exchange_month)

        date_begin_month = QDateEdit()
        date_begin_month.setDate(QDate(2020, 1, 1))
        self.tree.setItemWidget(self.month_child, 4, date_begin_month)

        date_end_month = QDateEdit()
        date_end_month.setDate(QDate.currentDate())
        self.tree.setItemWidget(self.month_child, 5, date_end_month)

        show_button_month: QPushButton = QPushButton("查看")
        self.tree.setItemWidget(self.month_child, 6, show_button_month)

        # =====字段说明=========================================
        self.tedit_specification = QTextEdit("字段说明")
        self.tedit_specification.setFixedHeight(150)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.tree)
        self.vlayout.addWidget(self.tedit_specification)

        self.setLayout(self.vlayout)

    def update_tablewidget(self, cursor):

        # 清空原 self.tablewidget 内容
        self.tablewidget.clear()

        # 将Cursor转换为列表
        results_list = list(cursor)

        # 将列表转换为Pandas DataFrame
        df = pd.DataFrame(results_list)
        # print(df)
        df.drop('_id', axis=1, inplace=True)

        # 设置右侧表格
        self.tablewidget.setColumnCount(len(df.columns))
        self.tablewidget.setHorizontalHeaderLabels(df.columns)
        self.tablewidget.verticalHeader().setVisible(False)
        self.tablewidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        data = df.values.tolist()
        self.tablewidget.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.tablewidget.setItem(i, j, DataCell(str(val)))

        # 显示QTableWidget
        self.tablewidget.show()

    @Slot()
    def on_tree_item_clicked(self, item, column):
        str_row = item.text(0)
        match str_row:
            case '板块行业':
                cursor: Cursor = self.stock_engine.database.classification_of_industry.find({})
                self.update_tablewidget(cursor)
                self.tedit_specification.setText("updateDate 更新日期; code 证券代码; code_name 证券名称; "
                                                 "industry 所属行业; industryClassification 所属行业类别")
            case '个股名单':
                print('个股名单行')
            case '其他':
                print('其他')
            case _:
                print('没有匹配的行。')


    def closeEvent(self, event: QCloseEvent) -> None:
        self.main_engine.close()


class DataCell(QTableWidgetItem):
    """"""

    def __init__(self, text: str = "") -> None:
        super().__init__(text)

        self.setTextAlignment(Qt.AlignCenter)

if __name__ == '__main__':
    app = QApplication()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))

    eng = EventEngine()
    main_eng = MainEngine(eng)

    win = ManagerWidgetStock(main_eng, eng)
    win.show()
    app.exec()

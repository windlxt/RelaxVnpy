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
    QComboBox, QDateEdit, QTableWidgetItem, QDialog, QFormLayout, QFileDialog, QMessageBox, QLayout, QAbstractItemView
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtCore import Slot, QDate, Qt, Signal
from pymongo.cursor import Cursor

from vnpy_datamanager_stock.stock_engine_database import StockManagerEngine, download_data_scheduler
from vnpy.trader.engine import MainEngine, EventEngine, Event
from vnpy.trader.event import EVENT_UPDATE_DATABASE_FINISHED
from vnpy.trader import utility

import vnpy_baostock_stock.baostock_stock_datafeed


class StockManagerWidget(QWidget):
    """
    Main window of the Database manager.
    """
    def __init__(self, main_engine=None, event_engine=None) -> None:
        """"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        # 获取股票数据的引擎
        self.stock_engine = StockManagerEngine(self.main_engine, self.event_engine)

        self.setWindowTitle("股票数据库管理")
        self.resize(1920, 1080)
        # Set up icon
        icon = QIcon("/home/lxt/pythonProjects_2024/RelaxVnpy/vnpy_datamanager_stock/ui/manager.ico")
        self.setWindowIcon(icon)

        self.database_updating = False          # 数据库是否正在更新中
        self.database_increment_update = True   # 数据库是否采取 增量更新的模式
        self.tablewidget: QTableWidget = QTableWidget()     # 右边输出表格
        self.tablewidget.setEditTriggers(self.tablewidget.NoEditTriggers)
        self.tablewidget.setAlternatingRowColors(True)
        self.tablewidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置选择行为

        self.tablewidget.tablewidget_data = pd.DataFrame()  # 右边输出表格展示的数据

        self.init_ui()
        self.register_event()

    def init_ui(self):
        """初始化窗口"""
        # 设置左上的 更新数据 控件
        self.cbox_download_date_schuduler = QCheckBox('  按计划更新数据库')
        self.cbox_download_date_schuduler.setChecked(True)
        self.cbox_download_date_schuduler.stateChanged.connect(self.update_database_schudule)

        self.pbtn_update_database = QPushButton('   立即更新数据库   ')
        self.pbtn_update_database.clicked.connect(lambda: self.update_database(self.database_increment_update))

        self.cbox_increment_update_database = QCheckBox('增量更新  ')
        self.cbox_increment_update_database.setChecked(True)
        self.cbox_increment_update_database.stateChanged.connect(self.set_database_increment_update)

        self.frame1 = QFrame()
        self.frame1.setFrameShape(QFrame.Box)  # 设置边框形状

        self.hlayout = QHBoxLayout(self.frame1)
        self.hlayout.addWidget(self.cbox_download_date_schuduler)
        self.hlayout.addStretch()
        self.hlayout.addWidget(self.pbtn_update_database)
        self.hlayout.addWidget(self.cbox_increment_update_database)

        # 设置 baostock、ifind等数据源
        self.rb_baostock = QRadioButton("  数据宝 BaoStock")
        self.rb_baostock.setChecked(True)
        self.rb_baostock.toggled.connect(lambda: self.change_stackwidget(0))
        self.rb_ifind = QRadioButton("  同花顺 iFinD")
        self.rb_ifind.toggled.connect(lambda: self.change_stackwidget(1))
        self.rb_dtshare = QRadioButton("  分布式 DTShare")
        self.rb_dtshare.toggled.connect(lambda: self.change_stackwidget(2))
        self.rb_tushare = QRadioButton("  挖地兔 Tushare")
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
        self.wighet_left.setFixedWidth(800)

        self.wighet_left.setLayout(self.vlayout_left)


        # 右面板 ==========================================
        # 设置右上的 导入数据、导出数据 控件
        self.pbtn_import = QPushButton('   导入数据   ')
        self.pbtn_import.clicked.connect(self.import_data)

        self.pbtn_export = QPushButton('   导出数据   ')
        self.pbtn_export.clicked.connect(self.export_data)

        self.pbtn_delete_database_error_data = QPushButton('   删除数据库出错数据   ')
        self.pbtn_delete_database_error_data.clicked.connect(self.delete_database_error_data)


        self.frame3 = QFrame()
        self.frame3.setFrameShape(QFrame.Box)  # 设置边框形状

        self.hlayout_right = QHBoxLayout(self.frame3)
        self.hlayout_right.addStretch()
        self.hlayout_right.addWidget(self.pbtn_import)
        self.hlayout_right.addWidget(self.pbtn_export)
        self.hlayout_right.addWidget(self.pbtn_delete_database_error_data)
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
    def delete_database_error_data(self):
        self.stock_engine.database.delete_error_data()

    @Slot()
    def set_database_increment_update(self):
        if self.cbox_increment_update_database.isChecked():
            self.database_increment_update = True
            print('self.database_increment_update:', self.database_increment_update)
        else:
            self.database_increment_update = False
            print('self.database_increment_update:', self.database_increment_update)

    @Slot()
    def import_data(self):
        import_dialog = ImportDialog()
        stat = import_dialog.exec()
        if stat:
            self.stock_engine.database.save_collection_from_csv(import_dialog.collection_combo.currentText(), import_dialog.file_edit.text())

    @Slot()
    def export_data(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # 强制使用 PySide6 提供的文件选择对话框而不是系统原生的对话框
        file_name, flag = QFileDialog.getSaveFileName(self, "选择文件", "", "All Files (*)", options=options)  # 返回文件名
        # file_name, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")    # 这个返回的是系统原生的文件选择对话框

        if not flag:
            return
        elif self.tablewidget.tablewidget_data.empty:
            QMessageBox.information(self, '提示', '请在左边树列表中选择要导出的数据！',  QMessageBox.Ok)
            return
        else:
            with open(file_name, 'w+') as f:
                self.tablewidget.tablewidget_data.to_csv(f, index=False)
                self.output('导出完成！')

    @Slot()
    def change_stackwidget(self, n):
        self.stackwidget.setCurrentIndex(n)

    @Slot()
    def update_database_schudule(self):
        if self.cbox_download_date_schuduler.isChecked():
            self.output('按计划更新数据库')
        else:
            self.output('取消数据库更新计划')

    @Slot()
    def update_database(self, is_increment):
        self.pbtn_update_database.setText('数据更新中...')
        self.pbtn_update_database.setEnabled(False)
        self.database_updating = True

        t = Thread(target=self.stock_engine.update_baostock_database, args=(is_increment,))
        t.start()

    @Slot()
    def process_update_database_finished(self, event):
        self.database_updating = False
        self.pbtn_update_database.setText('立即更新数据')
        self.pbtn_update_database.setEnabled(True)


    @Slot()
    def closeEvent(self, event: QCloseEvent) -> None:
        if self.database_updating:
            self.output("数据库更新未完成，请重新更新！")
        self.main_engine.close()

    def output(self, msg: str) -> None:
        """输出下载过程中的日志"""
        QMessageBox.warning(
            self,
            "数据导出",
            msg,
            QMessageBox.Ok,
            QMessageBox.Ok,
        )


class StackBaostock(QWidget):
    def __init__(self, main_engine, event_engine, stock_engine, tablewidget):
        super().__init__()
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.stock_engine = stock_engine
        self.tablewidget = tablewidget

        self.tablewidget_data = None    # 通过下载按钮，将 tablewidget 中的数据下载到本地

        self.init_ui()

    def init_ui(self):
        labels: list = ["数据类别", "代码", "交易所", "数据量", "开始时间", "结束时间", ""]

        self.tree: QTreeWidget = QTreeWidget(self)
        self.tree.setColumnCount(len(labels))
        self.tree.setHeaderLabels(labels)
        # self.tree.setStyleSheet("QTreeView::header{alignment: Center;}")
        # self.tree.setStyleSheet("QTreeView::item { text-align: center; }")
        self.tree.setColumnWidth(0, 120)
        self.tree.setColumnWidth(1, 90)
        self.tree.setColumnWidth(2, 90)
        self.tree.setColumnWidth(3, 90)
        self.tree.setColumnWidth(4, 120)
        self.tree.setColumnWidth(5, 120)
        self.tree.setColumnWidth(6, 120)
        self.tree.itemClicked.connect(self.on_tree_item_clicked)

        self.stock_list_child: QTreeWidgetItem = QTreeWidgetItem()
        self.stock_list_child.setText(0, "股票列表")
        self.tree.addTopLevelItem(self.stock_list_child)

        self.index_list_child: QTreeWidgetItem = QTreeWidgetItem()
        self.index_list_child.setText(0, "指数列表")
        self.tree.addTopLevelItem(self.index_list_child)

        self.daily_child: QTreeWidgetItem = QTreeWidgetItem()
        self.daily_child.setText(0, "日K线")
        self.tree.addTopLevelItem(self.daily_child)

        self.week_child: QTreeWidgetItem = QTreeWidgetItem(self.tree)
        self.week_child.setText(0, "周K线")
        self.tree.addTopLevelItem(self.week_child)

        self.month_child: QTreeWidgetItem = QTreeWidgetItem(self.tree)
        self.month_child.setText(0, "月K线")
        self.tree.addTopLevelItem(self.month_child)

        self.industry_child: QTreeWidgetItem = QTreeWidgetItem()
        self.industry_child.setText(0, "板块行业")
        self.tree.addTopLevelItem(self.industry_child)

        self.stock_st_list_child: QTreeWidgetItem = QTreeWidgetItem()
        self.stock_st_list_child.setText(0, "ST股票")
        self.tree.addTopLevelItem(self.stock_st_list_child)

        self.trade_dates_child: QTreeWidgetItem = QTreeWidgetItem(self.tree)
        self.trade_dates_child.setText(0, "交易日期")
        self.tree.addTopLevelItem(self.trade_dates_child)

        self.index_components_child: QTreeWidgetItem = QTreeWidgetItem(self.tree)
        self.index_components_child.setText(0, "成分股")
        self.tree.addTopLevelItem(self.index_components_child)
        self.index_components_child.setExpanded(True)

        self.shangzheng50_child: QTreeWidgetItem = QTreeWidgetItem(self.index_components_child)
        self.shangzheng50_child.setText(0, "上证50")
        self.tree.addTopLevelItem(self.shangzheng50_child)

        self.hushen300_child: QTreeWidgetItem = QTreeWidgetItem(self.index_components_child)
        self.hushen300_child.setText(0, "沪深300")
        self.tree.addTopLevelItem(self.hushen300_child)

        self.zhongzheng500_child: QTreeWidgetItem = QTreeWidgetItem(self.index_components_child)
        self.zhongzheng500_child.setText(0, "中证500")
        self.tree.addTopLevelItem(self.zhongzheng500_child)

        self.financial_analysis_child: QTreeWidgetItem = QTreeWidgetItem(self.tree)
        self.financial_analysis_child.setText(0, "财务分析")
        self.tree.addTopLevelItem(self.financial_analysis_child)
        self.financial_analysis_child.setExpanded(True)

        self.profitability_child: QTreeWidgetItem = QTreeWidgetItem(self.financial_analysis_child)
        self.profitability_child.setText(0, "盈利能力")
        self.tree.addTopLevelItem(self.profitability_child)

        self.growth_child: QTreeWidgetItem = QTreeWidgetItem(self.financial_analysis_child)
        self.growth_child.setText(0, "成长能力")
        self.tree.addTopLevelItem(self.growth_child)

        # ====向K线数据中加控件=================
        # 日K线
        self.symbol_daily = QLineEdit('600000')
        self.tree.setItemWidget(self.daily_child, 1, self.symbol_daily)

        self.exchange_daily = QComboBox()
        self.exchange_daily.addItems(['sh', 'sz'])
        self.tree.setItemWidget(self.daily_child, 2, self.exchange_daily)

        self.date_begin_daily = QDateEdit()
        self.date_begin_daily.setDate(QDate(2020, 1, 1))
        self.tree.setItemWidget(self.daily_child, 4, self.date_begin_daily)

        self.date_end_daily = QDateEdit()
        self.date_end_daily.setDate(QDate.currentDate())
        self.tree.setItemWidget(self.daily_child, 5, self.date_end_daily)

        self.show_button_daily: QPushButton = QPushButton("查看")
        self.tree.setItemWidget(self.daily_child, 6, self.show_button_daily)
        self.show_button_daily.clicked.connect(self.process_show_button_daily)

        # 周K线
        self.symbol_week = QLineEdit('600000')
        self.tree.setItemWidget(self.week_child, 1, self.symbol_week)

        self.exchange_week = QComboBox()
        self.exchange_week.addItems(['sh', 'sz'])
        self.tree.setItemWidget(self.week_child, 2, self.exchange_week)

        self.date_begin_week = QDateEdit()
        self.date_begin_week.setDate(QDate(2020, 1, 1))
        self.tree.setItemWidget(self.week_child, 4, self.date_begin_week)

        self.date_end_week = QDateEdit()
        self.date_end_week.setDate(QDate.currentDate())
        self.tree.setItemWidget(self.week_child, 5, self.date_end_week)

        self.show_button_week: QPushButton = QPushButton("查看")
        self.tree.setItemWidget(self.week_child, 6, self.show_button_week)
        self.show_button_week.clicked.connect(self.process_show_button_week)

        # 月K线
        self.symbol_month = QLineEdit('600000')
        self.tree.setItemWidget(self.month_child, 1, self.symbol_month)

        self.exchange_month = QComboBox()
        self.exchange_month.addItems(['sh', 'sz'])
        self.tree.setItemWidget(self.month_child, 2, self.exchange_month)

        self.date_begin_month = QDateEdit()
        self.date_begin_month.setDate(QDate(2020, 1, 1))
        self.tree.setItemWidget(self.month_child, 4, self.date_begin_month)

        self.date_end_month = QDateEdit()
        self.date_end_month.setDate(QDate.currentDate())
        self.tree.setItemWidget(self.month_child, 5, self.date_end_month)

        self.show_button_month: QPushButton = QPushButton("查看")
        self.tree.setItemWidget(self.month_child, 6, self.show_button_month)
        self.show_button_month.clicked.connect(self.process_show_button_month)

        # =====字段说明=========================================
        self.tedit_specification = QTextEdit("字段说明")
        self.tedit_specification.setFixedHeight(260)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.tree)
        self.vlayout.addWidget(self.tedit_specification)

        self.setLayout(self.vlayout)

    @Slot()
    def update_tablewidget(self, results):
        # 清空原 self.tablewidget 内容
        self.tablewidget.clear()

        # 将列表转换为Pandas DataFrame
        df = pd.DataFrame(results)
        df.drop('_id', axis=1, inplace=True)
        self.tablewidget.tablewidget_data = df  # 导出数据
        df = df.head(6000)

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
            case  '股票列表':
                results_list = list(self.stock_engine.database.all_stock_list.find({}))
                self.stock_list_child.setText(3, str(len(results_list))+'  ')
                self.stock_list_child.setTextAlignment(3, Qt.AlignRight)
                self.update_tablewidget(results_list)
                self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">code</font></b>         证券代码;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">tradeStatus</font></b>  交易状态(1：正常交易 0：停牌）; </pre>"
                                                 "<pre><b><font color=\"#FF0000\">code_name</font></b>    证券名称</pre>")

            case '指数列表':
                results_list = list(self.stock_engine.database.all_index_list.find({}))
                self.index_list_child.setText(3, str(len(results_list))+'  ')
                self.index_list_child.setTextAlignment(3, Qt.AlignRight)
                self.update_tablewidget(results_list)
                self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">code</font></b>         股指代码;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">tradeStatus</font></b>  交易状态(1：正常交易 0：停牌）;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">code_name</font></b>    证券名称</pre>")

            case '日K线':
                pass

            case '周K线':
                pass

            case '月K线':
                pass

            case '板块行业':
                results_list = list(self.stock_engine.database.classification_of_industry.find({}))
                industry = set(doc['industry'] for doc in results_list)
                print(industry)
                self.industry_child.setText(3, str(len(industry)-1)+'  ')
                self.industry_child.setTextAlignment(3, Qt.AlignRight)
                self.update_tablewidget(results_list)
                self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">updateDate</font></b>              更新日期;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">code</font></b>                    证券代码;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">code_name</font></b>               证券名称;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">industry</font></b>                所属行业;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">industryClassification</font></b>  所属行业类别</pre>"
                                                 "<pre>申万一级行业共 28 个：<b><font color=\"#30aacc\">轻工制造, 公用事业, 计算机, 采掘, 交通运输, 汽车, 传媒, 家用电器,\n"
                                                 "电子, 化工, 房地产, 通信, 医药生物, 食品饮料, 银行, 非银金融, 综合, 纺织服装, 建筑材料,\n"
                                                 "电气设备, 国防军工, 休闲服务, 商业贸易, 有色金属, 钢铁, 机械设备, 农林牧渔, 建筑装饰。</font></b></pre>")

            case 'ST股票':
                results_list = list(self.stock_engine.database.all_st_stock_list.find({}))
                self.stock_st_list_child.setText(3, str(len(results_list))+'  ')
                self.stock_st_list_child.setTextAlignment(3, Qt.AlignRight)
                self.update_tablewidget(results_list)
                self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">code</font></b>         证券代码;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">tradeStatus</font></b>  交易状态(1：正常交易 0：停牌）;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">code_name</font></b>    证券名称</pre>")

            case '交易日期':
                results_list = list(self.stock_engine.database.trade_dates.find({}))
                self.trade_dates_child.setText(3, str(len(results_list))+'  ')
                self.trade_dates_child.setTextAlignment(3, Qt.AlignRight)
                self.update_tablewidget(results_list)
                self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">calendar_date</font></b>   日期;</pre>  "
                                                 "<pre><b><font color=\"#FF0000\">is_trading_day</font></b>  是否交易日(0:非交易日;1:交易日)</pre>")

            case '上证50':
                cursor: Cursor = self.stock_engine.database.components_shangzheng50.find({})
                self.update_tablewidget(cursor)
                self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">updateDate</font></b>  更新日期;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">code</font></b>        证券代码;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">code_name</font></b>   证券名称</pre>")

            case '沪深300':
                cursor: Cursor = self.stock_engine.database.components_hushen300.find({})
                self.update_tablewidget(cursor)
                self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">updateDate</font></b>  更新日期;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">code</font></b>        证券代码;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">code_name</font></b>   证券名称</pre>")

            case '中证500':
                cursor: Cursor = self.stock_engine.database.components_zhongzheng500.find({})
                self.update_tablewidget(cursor)
                self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">updateDate</font></b>  更新日期;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">code</font></b>        证券代码;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">code_name</font></b>   证券名称</pre>")

            case '盈利能力':
                results_list = list(self.stock_engine.database.stock_profitability.find({}))
                self.profitability_child.setText(3, str(len(results_list))+'  ')
                self.profitability_child.setTextAlignment(3, Qt.AlignRight)
                self.update_tablewidget(results_list)
                self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">code</font></b>      证券代码;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">pubDate</font></b>   公司发布财报的日期;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">statDate</font></b>  财报统计的季度的最后一天, 比如2017-03-31, 2017-06-30;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">roeAvg</font></b>    净资产收益率(平均)(%) = 归属母公司股东净利润/[(期初归属母公司股东的权益+期末归属母公司股东的权益)/2]*100%;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">npMargin</font></b>  销售净利率(%) = 净利润/营业收入*100%; gpMargin 销售毛利率(%) 毛利/营业收入*100%=(营业收入-营业成本)/营业收入*100%;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">netProfit</font></b> 净利润(元); "
                                                 "<pre><b><font color=\"#FF0000\">epsTTM</font></b>    每股收益 = 归属母公司股东的净利润 <b>TTM</b>/最新总股本;</pre> "
                                                 "<pre><b><font color=\"#FF0000\">MBRevenue</font></b> 主营营业收入(元); totalShare 总股本; liqaShare 流通股本</pre>")

            case '成长能力':
                results_list = list(self.stock_engine.database.stock_growth.find({}))
                self.growth_child.setText(3, str(len(results_list))+'  ')
                self.growth_child.setTextAlignment(3, Qt.AlignRight)
                self.update_tablewidget(results_list)
                self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">code</font></b>        证券代码;</pre>"
                                                 "<pre><b><font color=\"#FF0000\">pubDate</font></b>     公司发布财报的日期;</pre>"
                                                 "<pre><b><font color=\"#FF0000\">statDate</font></b>    财报统计的季度的最后一天, 比如2017-03-31, 2017-06-30;</pre>"
                                                 "<pre><b><font color=\"#FF0000\">YOYEquity</font></b>   净资产同比增长率 (本期净资产-上年同期净资产)/上年同期净资产的绝对值*100%;</pre>"
                                                 "<pre><b><font color=\"#FF0000\">YOYAsset</font></b>    总资产同比增长率 (本期总资产-上年同期总资产)/上年同期总资产的绝对值*100%;</pre>"
                                                 "<pre><b><font color=\"#FF0000\">YOYNI</font></b>       净利润同比增长率 (本期净利润-上年同期净利润)/上年同期净利润的绝对值*100%;</pre>"
                                                 "<pre><b><font color=\"#FF0000\">YOYEPSBasic</font></b> 基本每股收益同比增长率 (本期基本每股收益-上年同期基本每股收益)/上年同期基本每股收益的绝对值*100%;</pre>"
                                                 "<pre><b><font color=\"#FF0000\">YOYPNI</font></b>      归属母公司股东净利润同比增长率 (本期归属母公司股东净利润-上年同期归属母公司股东净利润)/上年同期归属母公司股东净利润的绝对值*100%</pre>")

            case _:
                pass

    @Slot()
    def process_show_button_daily(self):
        bs_code = self.exchange_daily.currentText() + '.' + self.symbol_daily.text()
        # start_time = self.date_begin_daily.date()
        # end_time = self.date_end_daily.date()
        results_list = list(self.stock_engine.database.stock_history_daily_k_data.find({'code': bs_code}, {'date':1,'code':1,'open':1,'high':1,'low':1,'close':1,'preclose':1,'volume':1,'amount':1,'adjustflag':1,'turn':1,'tradestatus':1,'pctChg':1,'peTTM':1,'psTTM':1,'pcfNcfTTM':1,'pbMRQ':1,'isST':1}))
        self.daily_child.setText(3, str(len(results_list)) + '  ')
        self.daily_child.setTextAlignment(3, Qt.AlignRight)
        self.update_tablewidget(results_list)
        self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">preclose</font></b>       前收盘价</pre>"
                                         "<pre><b><font color=\"#FF0000\">volume</font></b>         成交量（累计 单位：股）</pre>"
                                         "<pre><b><font color=\"#FF0000\">amount</font></b>         成交额（单位：人民币元）</pre>"
                                         "<pre><b><font color=\"#FF0000\">adjustflag</font></b>     复权状态(1：后复权， 2：前复权，3：不复权）</pre>"
                                         "<pre><b><font color=\"#FF0000\">turn</font></b>           换手率 = [指定交易日的成交量(股)/指定交易日的股票的流通股总股数(股)]*100%</pre>"
                                         "<pre><b><font color=\"#FF0000\">pctChg</font></b>         日涨跌幅 = [(指定交易日的收盘价-指定交易日前收盘价)/指定交易日前收盘价]*100%</pre>"
                                         "<pre><b><font color=\"#FF0000\">peTTM</font></b>          滚动市盈率 = (指定交易日的股票收盘价/指定交易日的每股盈余TT M)=(指定交易日的股票收盘价*截至当日公司总股本)/归属母公司股东净利润TT M</pre>"
                                         "<pre><b><font color=\"#FF0000\">pbMRQ</font></b>          市净率 = (指定交易日的股票收盘价/指定交易日的每股净资产)=总市值/(最近披露的归属母公司股东的权益-其他权益工具)</pre>"
                                         "<pre><b><font color=\"#FF0000\">psTTM</font></b>          滚动市销率 = (指定交易日的股票收盘价/指定交易日的每股销售额)=(指定交易日的股票收盘价*截至当日公司总股本)/营业总收入TT M</pre>"
                                         "<pre><b><font color=\"#FF0000\">pcfNcfTTM</font></b>      滚动市现率 = (指定交易日的股票收盘价/指定交易日的每股现金流TT M)=(指定交易日的股票收盘价*截至当日公司总股本)/现金以及现金等价物净增加额TT M</pre>"
                                         "<pre><b><font color=\"#FF0000\">isST</font></b>           是否ST股，1是，0</pre>")

    @Slot()
    def process_show_button_week(self):
        bs_code = self.exchange_week.currentText() + '.' + self.symbol_week.text()
        results_list = list(self.stock_engine.database.stock_history_week_k_data.find({'code': bs_code},
                                                                                       {'date': 1, 'code': 1, 'open': 1, 'high': 1, 'low': 1, 'close': 1, 'volume': 1, 'amount': 1, 'adjustflag': 1, 'turn': 1, 'pctChg': 1}))
        self.week_child.setText(3, str(len(results_list)) + '  ')
        self.week_child.setTextAlignment(3, Qt.AlignRight)
        self.update_tablewidget(results_list)
        self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">volume</font></b>     成交数量</pre>"
                                         "<pre><b><font color=\"#FF0000\">amount</font></b>     成交金额</pre>"
                                         "<pre><b><font color=\"#FF0000\">adjustflag</font></b> 复权状态</pre>"
                                         "<pre><b><font color=\"#FF0000\">turn</font></b>       换手率</pre>"
                                         "<pre><b><font color=\"#FF0000\">pctChg</font></b>     涨跌幅（百分比）</pre>")

    @Slot()
    def process_show_button_month(self):
        bs_code = self.exchange_month.currentText() + '.' + self.symbol_month.text()
        results_list = list(self.stock_engine.database.stock_history_month_k_data.find({'code': bs_code},
                                                                                      {'date': 1, 'code': 1, 'open': 1, 'high': 1, 'low': 1, 'close': 1, 'volume': 1, 'amount': 1, 'adjustflag': 1, 'turn': 1, 'pctChg': 1}))
        self.month_child.setText(3, str(len(results_list)) + '  ')
        self.month_child.setTextAlignment(3, Qt.AlignRight)
        self.update_tablewidget(results_list)
        self.tedit_specification.setText("<pre><b><font color=\"#FF0000\">volume</font></b>     成交数量</pre>"
                                         "<pre><b><font color=\"#FF0000\">amount</font></b>     成交金额</pre>"
                                         "<pre><b><font color=\"#FF0000\">adjustflag</font></b> 复权状态</pre>"
                                         "<pre><b><font color=\"#FF0000\">turn</font></b>       换手率</pre>"
                                         "<pre><b><font color=\"#FF0000\">pctChg</font></b>     涨跌幅（百分比）</pre>")

    @Slot()
    def closeEvent(self, event: QCloseEvent) -> None:
        self.main_engine.close()


class DataCell(QTableWidgetItem):
    """"""

    def __init__(self, text: str = "") -> None:
        super().__init__(text)

        self.setTextAlignment(Qt.AlignCenter)


class ImportDialog(QDialog):
    """从CSV文件导入到数据中"""

    def __init__(self, parent=None) -> None:
        """"""
        super().__init__()

        self.setWindowTitle("从CSV文件导入数据")
        self.setFixedWidth(400)

        self.setWindowFlags(
            (self.windowFlags() | Qt.CustomizeWindowHint)
            & ~Qt.WindowMaximizeButtonHint)

        database_collections = ['日K线', '周K线', '月K线', '盈利能力', '成长能力']
        self.collection_combo = QComboBox()
        self.collection_combo.addItems(database_collections)

        self.file_edit: QLineEdit = QLineEdit()
        file_button: QPushButton = QPushButton("选择文件")
        file_button.clicked.connect(self.select_file)

        load_button: QPushButton = QPushButton("确定导入")
        load_button.clicked.connect(self.accept)

        form:QFormLayout = QFormLayout()
        form.addRow("目标集合 :", self.collection_combo)
        form.addRow("日K线   :", QLabel("选择 <b><font color=\"#FF0000\">stock_history_daily_k_data</font></b> 文件"))
        form.addRow("周K线   :", QLabel("选择 <b><font color=\"#FF0000\">stock_history_week_k_data</font></b> 文件"))
        form.addRow("月K线   :", QLabel("选择 <b><font color=\"#FF0000\">stock_history_month_k_data</font></b> 文件"))
        form.addRow("盈利能力 :", QLabel("选择 <b><font color=\"#FF0000\">stock_profitability</font></b> 文件"))
        form.addRow("成长能力 :", QLabel("选择 <b><font color=\"#FF0000\">stock_growth</font></b> 文件"))
        form.addRow(file_button, self.file_edit)
        form.addRow(load_button)

        self.setLayout(form)

    def select_file(self) -> None:
        """"""
        result: str = QFileDialog.getOpenFileName(
            self, filter="CSV (*.csv)")
        filename: str = result[0]
        if filename:
            self.file_edit.setText(filename)


if __name__ == '__main__':
    app = QApplication()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))

    eng = EventEngine()
    main_eng = MainEngine(eng)

    win = StockManagerWidget(main_eng, eng)
    win.show()
    app.exec()

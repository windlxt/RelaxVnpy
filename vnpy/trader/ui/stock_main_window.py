"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月07日
"""
from types import ModuleType
import webbrowser
from functools import partial
from importlib import import_module
from typing import Callable, Dict, List, Tuple

from PySide6.QtWidgets import QMainWindow, QWidget, QTableWidget, QCheckBox, QListWidget, \
    QMenuBar, QMenu, QToolBar, QDockWidget, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QIcon, QAction, QCloseEvent
from PySide6.QtCore import Qt, QSize, QSettings, QByteArray

import vnpy
from vnpy.event import EventEngine
from ..engine import MainEngine, BaseApp
from ..utility import get_icon_path, TRADER_DIR

from .stock_main_widget import BaseMonitor, StockHoldingPool, StockPrepareBuyPool, StockWatchPool, \
    StockKLineChart, AboutDialog, GlobalDialog, StockPrepareSellPool


class StockMainWindow(QMainWindow):
    """股票分析平台主窗口"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        self.window_title: str = '股票分析平台'
        icon = QIcon("/home/lxt/pythonProjects_2024/RelaxVnpy/vnpy/trader/ui/ico/vnpy.ico")
        self.setWindowIcon(icon)

        self.widgets: Dict[str, QWidget] = {}
        self.monitors: Dict[str, BaseMonitor] = {}

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle(self.window_title)
        self.init_window()
        self.init_toolbar()
        self.init_menu()
        self.load_window_setting("custom")

    def init_window(self):
        # 生成4个子窗口
        self.stock_k_line_chart_widget = StockKLineChart(self.main_engine, self.event_engine)
        self.stock_holding_pool_widget = StockHoldingPool(self.main_engine, self.event_engine, self.stock_k_line_chart_widget.chart)
        self.stock_prepare_sell_pool_widget = StockPrepareSellPool(self.main_engine, self.event_engine)
        self.stock_prepare_buy_pool_widget = StockPrepareBuyPool(self.main_engine, self.event_engine)

        # 设置子窗口宽度
        self.stock_k_line_chart_widget.setFixedWidth(680)
        # 设置双击响应函数
        self.stock_prepare_buy_pool_widget.itemDoubleClicked.connect(self.stock_prepare_buy_pool_widget.update_with_cell)
        self.stock_prepare_sell_pool_widget.itemDoubleClicked.connect(self.stock_prepare_buy_pool_widget.update_with_cell)

        vlayout_left = QVBoxLayout()
        vlayout_left.addWidget(self.stock_holding_pool_widget)
        vlayout_left.addWidget(self.stock_prepare_sell_pool_widget)
        vlayout_left.addWidget(self.stock_prepare_buy_pool_widget)

        hlayout_all = QHBoxLayout()
        hlayout_all.addLayout(vlayout_left)
        hlayout_all.addWidget(self.stock_k_line_chart_widget)

        widget_all = QWidget()
        widget_all.setLayout(hlayout_all)

        self.setCentralWidget(widget_all)

    def init_menu(self) -> None:
        """"""
        bar: QMenuBar = self.menuBar()
        bar.setNativeMenuBar(False)     # for mac and linux

        # System menu
        sys_menu: QMenu = bar.addMenu("系统")

        self.add_action(
            sys_menu,
            "退出",
            get_icon_path(__file__, "exit.ico"),
            self.close
        )

        # App menu
        app_menu: QMenu = bar.addMenu("功能")

        all_apps: List[BaseApp] = self.main_engine.get_all_apps()
        for app in all_apps:
            ui_module: ModuleType = import_module(app.app_module + ".ui")
            widget_class: QWidget = getattr(ui_module, app.widget_name)

            func: Callable = partial(self.open_widget, widget_class, app.app_name)

            self.add_action(app_menu, app.display_name, app.icon_name, func, True)

        # Global setting editor
        action: QAction = QAction("配置", self)
        action.triggered.connect(self.edit_global_setting)
        bar.addAction(action)

        # Help menu
        help_menu: QMenu = bar.addMenu("帮助")

        self.add_action(
            help_menu,
            "还原窗口",
            get_icon_path(__file__, "restore.ico"),
            self.restore_window_setting
        )

        self.add_action(
            help_menu,
            "测试邮件",
            get_icon_path(__file__, "email.ico"),
            self.send_test_email
        )

        self.add_action(
            help_menu,
            "社区论坛",
            get_icon_path(__file__, "forum.ico"),
            self.open_forum,
            True
        )

        self.add_action(
            help_menu,
            "关于",
            get_icon_path(__file__, "about.ico"),
            partial(self.open_widget, AboutDialog, "about"),
        )

    def init_toolbar(self) -> None:
        """"""
        self.toolbar: QToolBar = QToolBar(self)
        self.toolbar.setObjectName("工具栏")
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)

        # Set button size
        w: int = 40
        size = QSize(w, w)
        self.toolbar.setIconSize(size)

        # Set button spacing
        self.toolbar.layout().setSpacing(10)

        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

    def add_action(
        self,
        menu: QMenu,
        action_name: str,
        icon_name: str,
        func: Callable,
        toolbar: bool = False
    ) -> None:
        """"""
        icon: QIcon = QIcon(icon_name)

        action: QAction = QAction(action_name, self)
        action.triggered.connect(func)
        action.setIcon(icon)

        menu.addAction(action)

        if toolbar:
            self.toolbar.addAction(action)

    def create_dock(
        self,
        widget_class: QWidget,
        name: str,
        area: int
    ) -> Tuple[QWidget, QDockWidget]:
        """
        Initialize a dock widget.
        """
        widget: QWidget = widget_class(self.main_engine, self.event_engine)
        if isinstance(widget, BaseMonitor):
            self.monitors[name] = widget

        dock: QDockWidget = QDockWidget(name)
        dock.setWidget(widget)
        dock.setObjectName(name)
        dock.setFeatures(dock.DockWidgetFloatable | dock.DockWidgetMovable)
        self.addDockWidget(area, dock)
        return widget, dock

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Call main engine close function before exit.
        """
        # reply = QMessageBox.question(
        #     self,
        #     "退出",
        #     "确认退出？",
        #     QMessageBox.Yes | QMessageBox.No,
        #     QMessageBox.No,
        # )
        #
        # if reply == QMessageBox.Yes:
        for widget in self.widgets.values():
            widget.close()

        for monitor in self.monitors.values():
            monitor.save_setting()

        self.save_window_setting("custom")

        self.main_engine.close()

        event.accept()
        # else:
        #     event.ignore()

    def open_widget(self, widget_class: QWidget, name: str) -> None:
        """
        Open contract manager.
        """
        widget: QWidget = self.widgets.get(name, None)
        if not widget:
            widget = widget_class(self.main_engine, self.event_engine)
            self.widgets[name] = widget

        if isinstance(widget, QDialog):
            widget.exec()
        else:
            widget.show()

    def save_window_setting(self, name: str) -> None:
        """
        Save current window size and state by trader path and setting name.
        """
        settings: QSettings = QSettings(self.window_title, name)
        settings.setValue("state", self.saveState())
        settings.setValue("geometry", self.saveGeometry())

    def load_window_setting(self, name: str) -> None:
        """
        Load previous window size and state by trader path and setting name.
        """
        settings: QSettings = QSettings(self.window_title, name)
        state = settings.value("state")
        geometry = settings.value("geometry")

        if isinstance(state, QByteArray):
            self.restoreState(state)
            self.restoreGeometry(geometry)

    def restore_window_setting(self) -> None:
        """
        Restore window to default setting.
        """
        self.load_window_setting("default")
        self.showMaximized()

    def send_test_email(self) -> None:
        """
        Sending a test email.
        """
        self.main_engine.send_email("VeighNa Trader", "testing")

    def open_forum(self) -> None:
        """
        """
        webbrowser.open("https://www.vnpy.com/forum/")

    def edit_global_setting(self) -> None:
        """
        """
        dialog: GlobalDialog = GlobalDialog()
        dialog.exec()


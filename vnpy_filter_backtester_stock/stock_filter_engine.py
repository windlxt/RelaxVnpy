"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年06月22日
"""
import os
import importlib
import traceback
import pandas as pd

from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt

import vnpy_filter_backtester_stock

from pathlib import Path
from glob import glob
from types import ModuleType
from typing import Any, Dict, List
from vnpy_filter_strategy_stock import StockStrategyTemplate

from vnpy.trader.engine import BaseEngine, MainEngine, EventEngine
from vnpy.event import Event
from vnpy.trader.database import BaseDatabase, get_database
from vnpy.trader.setting import SETTINGS
APP_NAME = "StockFilter"


class MyListWidgetItem(QListWidgetItem):
    """
        General cell used in listwidgets.
    """
    def __init__(self, content: Any, data: Any) -> None:
        """"""
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.set_content(content, data)

    def set_content(self, content: Any, data: Any) -> None:
        """
        Set text content.
        """
        self.setText(str(content))
        self._data = data

    def get_data(self) -> Any:
        """
        Get data object.
        """
        return self._data


class StockFilterEngine(BaseEngine):
    """筛选股票引擎"""
    def __init__(self, main_engine=None, event_engine=None) -> None:
        """"""
        super().__init__(main_engine, event_engine, 'StockFilter')

        self.main_engine = main_engine
        self.event_engine = event_engine

        self.database = get_database()

        self.classes_index_strategies: dict = {}
        self.classes_stock_strategies: dict = {}

        self.reload_strategy_class()
        print('self.classes_index_strategies:', self.classes_index_strategies)
        print('self.classes_stock_strategies:', self.classes_stock_strategies)

    def load_index_all(self, lw):
        self.result_index = self.database.all_index_list.find({}, {'code': 1, 'code_name': 1, '_id': 0})
        # self.df_index = pd.DataFrame(result)
        # print(self.df_index)
        for item in self.result_index:
            # item 是字典，如：{'code': 'sz.399998', 'code_name': '中证煤炭指数'}
            i = MyListWidgetItem(item['code_name'], item)
            i.setTextAlignment(Qt.AlignLeft)
            lw.addItem(i)

    def load_stock_all(self, lw):
        lw.clear()
        self.result_stock = self.database.all_stock_list.find({}, {'code': 1, 'code_name': 1, '_id': 0})
        # self.df_index = pd.DataFrame(result)
        # print(self.df_index)
        for item in self.result_stock:
            # item 是字典，如：{'code': 'sh.600000', 'code_name': '浦发银行'}
            i = MyListWidgetItem(item['code_name'], item)
            lw.addItem(i)

    def get_all_index_strategies(self):
        result = self.get_index_strategy_class_names()
        return result

    def get_all_stock_strategies(self):
        result = self.get_stock_strategy_class_names()
        return result

    def load_strategy_class(self) -> None:
        """
        Load strategy class from source code.
        """
        app_path: Path = Path(vnpy_filter_backtester_stock.__file__).parent
        path1: Path = app_path.joinpath("strategies_index")
        self.load_strategy_class_from_folder(path1, "vnpy_filter_backtester_stock.strategies_index")

        path2: Path = app_path.joinpath("strategies_stock")
        self.load_strategy_class_from_folder(path2, "vnpy_filter_backtester_stock.strategies_stock")

        # path2: Path = Path.cwd().joinpath("strategies")
        # self.load_strategy_class_from_folder(path2, "strategies")

    def load_strategy_class_from_folder(self, path: Path, module_name: str = "") -> None:
        """
        Load strategy class from certain folder.
        """
        for suffix in ["py", "pyd", "so"]:
            pathname: str = str(path.joinpath(f"*.{suffix}"))
            for filepath in glob(pathname):
                filename: str = Path(filepath).stem
                name: str = f"{module_name}.{filename}"
                # 在 Combo Box 中加入文件名
                folder_name = os.path.basename(path)
                if folder_name == 'strategies_index':
                    self.load_index_strategy_class_from_module(name)
                elif folder_name == 'strategies_stock':
                    self.load_stock_strategy_class_from_module(name)

    def load_index_strategy_class_from_module(self, module_name: str) -> None:
        """
        Load strategy class from module file.
        """
        try:
            module: ModuleType = importlib.import_module(module_name)

            # 重载模块，确保如果策略文件中有任何修改，能够立即生效。
            # print(module)
            importlib.reload(module)

            for name in dir(module):
                value = getattr(module, name)
                # print(module)
                # print(value)
                if (isinstance(value, type) and issubclass(value, StockStrategyTemplate) and value is not StockStrategyTemplate):
                    self.classes_index_strategies[value.__name__] = value
                    # print('CtaTemplate')

        except:  # noqa
            msg: str = f"策略文件{module_name}加载失败，触发异常：\n{traceback.format_exc()}"
            # self.write_log(msg)
            print(msg)

    def load_stock_strategy_class_from_module(self, module_name: str) -> None:
        """
        Load strategy class from module file.
        """
        try:
            module: ModuleType = importlib.import_module(module_name)

            # 重载模块，确保如果策略文件中有任何修改，能够立即生效。
            # print(module)
            importlib.reload(module)

            for name in dir(module):
                value = getattr(module, name)
                # print(module)
                # print(value)
                if (isinstance(value, type) and issubclass(value, StockStrategyTemplate) and value is not StockStrategyTemplate):
                    self.classes_stock_strategies[value.__name__] = value
                    # print('CtaTemplate')

        except:  # noqa
            msg: str = f"策略文件{module_name}加载失败，触发异常：\n{traceback.format_exc()}"
            # self.write_log(msg)
            print(msg)

    def reload_strategy_class(self) -> None:
        """"""
        self.classes_index_strategies.clear()
        self.classes_stock_strategies.clear()
        self.load_strategy_class()
        # self.write_log("策略文件重载刷新完成")

    def get_index_strategy_class_names(self) -> list:
        """"""
        return list(self.classes_index_strategies.keys())

    def get_stock_strategy_class_names(self) -> list:
        """"""
        return list(self.classes_stock_strategies.keys())

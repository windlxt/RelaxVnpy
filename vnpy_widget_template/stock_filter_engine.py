"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年06月22日
"""
from vnpy.trader.engine import BaseEngine, MainEngine, EventEngine
from vnpy.event import Event
from vnpy.trader.database import BaseDatabase, get_database
from vnpy.trader.setting import SETTINGS
APP_NAME = "StockFilter"


class StockFilterEngine(BaseEngine):
    """筛选股票引擎"""
    def __init__(self, main_engine=None, event_engine=None) -> None:
        """"""
        super().__init__(main_engine, event_engine, 'StockFilter')

        self.main_engine = main_engine
        self.event_engine = event_engine

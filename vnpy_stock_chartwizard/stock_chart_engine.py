from datetime import datetime
from threading import Thread
from typing import List, Optional

from vnpy.event import Event, EventEngine
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.object import BarData, HistoryRequest, ContractData
from vnpy.trader.utility import printr, printb, printg, printy
from vnpy.trader.database import get_database, BaseDatabase
from vnpy.trader.datafeed import get_datafeed, BaseDatafeed

from pymongo.cursor import Cursor


APP_NAME = "StockChartWizard"

EVENT_STOCK_CHART_HISTORY = "eStockChartHistory"


class StockChartWizardEngine(BaseEngine):
    """
    For running chartWizard.
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

        self.datafeed: BaseDatafeed = get_datafeed()
        self.database: BaseDatabase = get_database()

    def query_history(
        self,
        vt_symbol: str,
        interval: str,
        start: datetime,
        end: datetime
    ) -> None:
        """"""
        thread: Thread = Thread(
            target=self._query_history,
            args=[vt_symbol, interval, start, end]
        )
        thread.start()

    def _query_history(
        self,
        vt_symbol: str,
        interval: str,
        start: datetime,
        end: datetime
    ) -> None:
        """"""
        history_daily = self.database.load_bar_data(vt_symbol, '', 'd', start, end)
        history_week = self.database.load_bar_data(vt_symbol, '', 'w', start, end)
        history_month = self.database.load_bar_data(vt_symbol, '', 'm', start, end)

        history: List = [history_daily, history_week, history_month]

        if not history_daily[0]:
            printr('数据库没有存储该股票数据！')

        event: Event = Event(EVENT_STOCK_CHART_HISTORY, history)
        self.event_engine.put(event)

    def get_code_name(self, stock_code):
        c_index: Cursor = self.database.all_index_list.find({'code': stock_code}, {'code_name': 1, '_id': 0})
        code_name = ''
        for item in c_index:
            code_name = item['code_name']
            if not code_name:
                break

        if not code_name:
            c_stock: Cursor = self.database.classification_of_industry.find({'code': stock_code}, {'code_name': 1, '_id': 0})
            for item in c_stock:
                code_name = item['code_name']
                if not code_name:
                    break

        return code_name

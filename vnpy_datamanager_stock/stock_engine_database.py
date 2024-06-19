"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月21日
"""
import qdarkstyle
from PySide6.QtGui import QCloseEvent
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time

from PySide6.QtCore import QTimer
from vnpy.trader import utility
from vnpy.trader.engine import BaseEngine, MainEngine, EventEngine
from vnpy.event import Event
from vnpy.trader.event import EVENT_UPDATE_DATABASE_FINISHED
from vnpy.trader.database import BaseDatabase, get_database, BarOverview, DB_TZ
from vnpy.trader.datafeed import BaseDatafeed, get_datafeed
from vnpy.trader.setting import SETTINGS
APP_NAME = "StockDataManager"

event_update_database_finished = Event(EVENT_UPDATE_DATABASE_FINISHED)


class StockManagerEngine(BaseEngine):
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        super().__init__(main_engine, event_engine, APP_NAME)

        self.database: BaseDatabase = get_database()
        self.datafeed: BaseDatafeed = get_datafeed()

    def update_baostock_database(self, is_increment):
        # 1. 更新 行业分类 数据
        result = self.datafeed.baostock_query_stock_industry()
        self.database.baostock_save_industry_data(result)

        # 2. 更新 指定交易日期所有股票列表、股指、ST股票
        result = self.datafeed.baostock_query_all_stock()
        self.database.baostock_save_all_stock_list(result)

        # 3.日K线、周K线、月K线 集合
        result = self.datafeed.baostock_query_history_daily_k_data(is_increment)
        self.database.baostock_save_history_daily_k_data(result, is_increment)

        result = self.datafeed.baostock_query_history_week_k_data(is_increment)
        self.database.baostock_save_history_week_k_data(result, is_increment)

        result = self.datafeed.baostock_query_history_month_k_data(is_increment)
        self.database.baostock_save_history_month_k_data(result, is_increment)

        # 3. 更新 交易日期
        result = self.datafeed.baostock_query_trade_dates()
        self.database.baostock_save_trade_dates(result)

        # 4. 更新 上证50、沪深300、中证500成分股
        result = self.datafeed.baostock_query_components_shangzheng50()
        self.database.baostock_save_components_shangzheng50(result)

        result = self.datafeed.baostock_query_components_hushen300()
        self.database.baostock_save_components_hushen300(result)

        result = self.datafeed.baostock_query_components_zhongzheng500()
        self.database.baostock_save_components_zhongzheng500(result)

        # 5. 更新 盈利能力、成长能力
        result = self.datafeed.baostock_query_stock_profitability(is_increment)
        self.database.baostock_save_stock_profitability(result, is_increment)

        result = self.datafeed.baostock_query_stock_growth(is_increment)
        self.database.baostock_save_stock_growth(result, is_increment)

        # 发出 数据库更新完毕 事件通知
        print('====发出 数据库更新完毕 事件通知====')
        self.event_engine.put(event_update_database_finished)


def download_data_scheduler(event_engine):
    print('开始更新数据库。。。')
    print("=" * 50)
    print("启动 scheduler")

    # 阻塞式调度
    # scheduler = BlockingScheduler()
    # intervalTrigger = IntervalTrigger(seconds=1)
    # scheduler.add_job(lambda: print('This is a test.'), intervalTrigger, jitter=2)  # 每3s运行1次
    # scheduler.start()

    # 后台式调度
    scheduler = BackgroundScheduler()
    intervalTrigger = IntervalTrigger(seconds=1)
    scheduler.add_job(lambda: print('This is a test.'), intervalTrigger, jitter=1)
    scheduler.start()

    def shutdown():
        scheduler.shutdown()
        print("关闭 scheduler")
        event_engine.put(event_update_database_finished)

    QTimer.singleShot(5000, shutdown)




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
APP_NAME = "DataManagerStock"

event_update_database_finished = Event(EVENT_UPDATE_DATABASE_FINISHED)


class ManagerEngineStock(BaseEngine):
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        super().__init__(main_engine, event_engine, APP_NAME)

        self.database: BaseDatabase = get_database()
        self.datafeed: BaseDatafeed = get_datafeed()

    def update_baostock_database(self):
        result = self.datafeed.baostock_query_stock_industry()
        self.database.baostock_save_industry_data(result)
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




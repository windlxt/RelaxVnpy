"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月21日
"""
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time


def download_data_scheduler():

    # 阻塞式调度
    # scheduler = BlockingScheduler()
    # intervalTrigger = IntervalTrigger(seconds=1)
    # scheduler.add_job(publicAcc.WriteNewArtical, intervalTrigger, jitter=2)  # 每3s运行1次
    # scheduler.start()

    # 后台式调度
    scheduler = BackgroundScheduler()
    intervalTrigger = IntervalTrigger(seconds=1)
    scheduler.add_job(lambda : print('This is a test.'), intervalTrigger, jitter=1)
    scheduler.start()

    print("="*50)
    flag = True

    time.sleep(5)

    if flag:
        print("关闭 scheduler")
        flag = scheduler.shutdown()


if __name__ == '__main__':
    download_data_scheduler()

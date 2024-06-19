"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年06月04日
"""
import concurrent.futures
import time


# 定义一个简单的函数，模拟耗时任务
def task(n):
    time.sleep(n)  # 休眠n秒
    return n


# 使用ThreadPoolExecutor
def use_thread_pool():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # 提交任务到线程池
        future_to_time = {executor.submit(task, time): time for time in [5, 1, 2, 4, 3]}
        print(future_to_time)
        print(type(future_to_time))

        # 等待所有任务完成
        for future in concurrent.futures.as_completed(future_to_time):
            print(future)
            time = future_to_time[future]
            try:
                data = future.result()  # 获取任务返回的结果
                print(f"Task with time {time} finished with result: {data}")
            except Exception as e:
                print(f"Task with time {time} raised an exception: {e}")


# 运行函数
use_thread_pool()

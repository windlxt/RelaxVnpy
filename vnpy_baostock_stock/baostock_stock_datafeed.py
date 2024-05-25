"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月23日
"""
from datetime import datetime
from typing import List, Optional

import baostock as bs
import pandas as pd

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.datafeed import BaseDatafeed
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.setting import SETTINGS
from vnpy.trader.utility import round_to

# 数据频率映射
INTERVAL_VT2TS = {
    Interval.MINUTE: "5",  # 只支持5分钟
    Interval.HOUR: "60",
    Interval.DAILY: "d",
    Interval.WEEKLY: "w",
}

# 股票支持列表
STOCK_LIST = [
    Exchange.SSE,
    Exchange.SZSE,
]


class BaoStockDatafeed(BaseDatafeed):
# class BaoStockDatafeed():
    """BaoStock数据服务接口"""

    def __init__(self):
        """初始化"""
        # self.username: str = SETTINGS["datafeed.username"]
        # self.password: str = SETTINGS["datafeed.password"]

        self.inited: bool = False

    def init(self) -> bool:
        """初始化"""
        if self.inited:
            return True

        bs.login()
        self.inited = True

        return True

    def __delete__(self):
        bs.logout()

    def query_bar_history(self, req: HistoryRequest) -> Optional[List[BarData]]:
        """查询k线数据"""
        if not self.inited:
            self.init()

        symbol = req.symbol
        exchange = req.exchange
        interval = req.interval
        start = req.start.strftime("%Y-%m-%d")
        end = req.end.strftime("%Y-%m-%d")
        bs_symbol = f"sz.{symbol}" if exchange == Exchange.SZSE else f"sh.{symbol}"

        bs_interval = INTERVAL_VT2TS.get(interval)
        if not bs_interval:
            return None

        if interval in (Interval.MINUTE, Interval.HOUR):
            fields = "time,code,open,high,low,close,volume,amount"
        else:
            fields = "date,code,open,high,low,close,volume,amount"
        try:
            rs = bs.query_history_k_data_plus(
                bs_symbol,
                fields,
                start_date=start,
                end_date=end,
                frequency=bs_interval,
                adjustflag="3",
            )
        except Exception as e:
            return []
        data: List[BarData] = []

        print(fields.split(','))
        while (rs.error_code == "0") & rs.next():
            item = rs.get_row_data()
            print(item)
            str_format = "%Y-%m-%d"
            if interval in (Interval.MINUTE, Interval.HOUR):
                str_format = "%Y%m%d%H%M%S%f"
            dt = datetime.strptime(item[0], str_format)
            bar: BarData = BarData(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                datetime=dt,
                open_price=round_to(item[2], 0.000001),
                high_price=round_to(item[3], 0.000001),
                low_price=round_to(item[4], 0.000001),
                close_price=round_to(item[5], 0.000001),
                volume=float(item[6]),
                turnover=float(item[7]),
                open_interest=0,
                gateway_name="BS",
            )
            data.append(bar)

        return data


if __name__ == "__main__":
    bsd = BaoStockDatafeed()
    r = HistoryRequest(
        symbol="600000",
        exchange=Exchange.SSE,
        start=datetime.strptime("2024-05-01", "%Y-%m-%d"),
        end=datetime.strptime("2024-12-31", "%Y-%m-%d"),
        interval=Interval.DAILY,
    )
    data = bsd.query_bar_history(r)
    df = pd.DataFrame(data)

    # ===================================================
    # 忽略警告
    import warnings

    warnings.filterwarnings("ignore")
    # 设置 DataFrame 输出格式
    pd.set_option('display.max_columns', None)  # 显示完整的列
    # pd.set_option('display.max_rows', None)  # 显示完整的行
    pd.set_option('display.expand_frame_repr', False)  # 设置不折叠数据
    pd.set_option('display.max_colwidth', 100)  # 设置每列宽度
    pd.set_option('display.float_format', '{:.2f}'.format)  # 设置显示2位小数
    # pd.reset_option('display.float_format')  # 恢复小数原始设置
    # ===================================================
    print(df.head())

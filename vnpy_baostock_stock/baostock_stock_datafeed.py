"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月23日
"""
print('Enter vnpy_baostock_stock 模块')
from datetime import datetime, date, timedelta
from typing import List, Optional
from time import sleep

import baostock as bs
import pandas as pd

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.datafeed import BaseDatafeed
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.setting import SETTINGS
from vnpy.trader.utility import round_to
from vnpy.trader.database import BaseDatabase, get_database

CODE_REFERENCE = 'sz.300776'        # 以该股票日期为准，更新数据库

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
        self.startdate: str = SETTINGS["database.startdate"]
        self.update: str = SETTINGS["database.update"]

        self.database: BaseDatabase = get_database()
        self.all_stocks = []
        self.all_index = []
        self.all_stocks_index = []

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

    def baostock_query_stock_industry(self):
        """
        查询 行业分类 数据
        :return: 字典
        """
        if not self.inited:
            self.init()

        # 获取行业分类数据
        rs = bs.query_stock_industry()
        print('====获取 行业分类 数据====')
        print('query_stock_industry error_code:' + rs.error_code)
        print('query_stock_industry respond  error_msg:' + rs.error_msg)

        # 打印结果集
        industry_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            industry_list.append(rs.get_row_data())
        result = pd.DataFrame(industry_list, columns=rs.fields)

        # 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
        # 调用格式为data_records[index][key1]
        data_dict = result.to_dict('records')

        return data_dict

    def baostock_query_all_stock(self):
        """
        获取指定交易日期所有股票列表。通过API接口获取证券代码及股票交易状态信息，与日K线数据同时更新。
        可以通过参数‘某交易日’获取数据（包括：A股、指数），数据范围同接口query_history_k_data_plus()
        :return: 字典，去除以 bj 开头的 code
        """
        if not self.inited:
            self.init()

        #### 获取证券信息 ####
        rs = bs.query_all_stock(day=str(get_previous_workday()))
        print('====获取指定交易日期所有股票列表====')
        print('query_all_stock respond error_code:' + rs.error_code)
        print('query_all_stock respond  error_msg:' + rs.error_msg)

        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)

        # 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
        # 调用格式为data_records[index][key1]
        data_dict = result.to_dict('records')

        return data_dict

    def baostock_query_trade_dates(self):
        """
        获取股票交易日信息
        :return: 字典
        """
        if not self.inited:
            self.init()

        #### 获取交易日信息 ####
        print('====获取交易日信息====')
        rs = bs.query_trade_dates(start_date="2020-01-01", end_date=datetime.today())
        print('query_trade_dates respond error_code:' + rs.error_code)
        print('query_trade_dates respond  error_msg:' + rs.error_msg)

        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)

        # 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
        # 调用格式为data_records[index][key1]
        data_dict = result.to_dict('records')

        return data_dict

    def baostock_query_components_shangzheng50(self):
        """
        获取上证50成分股
        :return: 字典
        """
        if not self.inited:
            self.init()

        # 获取上证50成分股
        rs = bs.query_sz50_stocks()
        print('====获取上证50成分股====')
        print('query_sz50 error_code:' + rs.error_code)
        print('query_sz50  error_msg:' + rs.error_msg)

        # 打印结果集
        sz50_stocks = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            sz50_stocks.append(rs.get_row_data())
        result = pd.DataFrame(sz50_stocks, columns=rs.fields)

        # 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
        # 调用格式为data_records[index][key1]
        data_dict = result.to_dict('records')

        return data_dict

    def baostock_query_components_hushen300(self):
        """
        获取沪深300成分股
        :return: 字典
        """
        if not self.inited:
            self.init()

        # 获取沪深300成分股
        rs = bs.query_hs300_stocks()
        print('====获取沪深300成分股====')
        print('query_hs300 error_code:' + rs.error_code)
        print('query_hs300  error_msg:' + rs.error_msg)

        # 打印结果集
        hs300_stocks = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            hs300_stocks.append(rs.get_row_data())
        result = pd.DataFrame(hs300_stocks, columns=rs.fields)

        # 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
        # 调用格式为data_records[index][key1]
        data_dict = result.to_dict('records')

        return data_dict

    def baostock_query_components_zhongzheng500(self):
        """
        获取中证500成分股
        :return: 字典
        """
        if not self.inited:
            self.init()

        # 获取中证500成分股
        rs = bs.query_zz500_stocks()
        print('====获取中证500成分股====')
        print('query_zz500 error_code:' + rs.error_code)
        print('query_zz500  error_msg:' + rs.error_msg)

        # 打印结果集
        zz500_stocks = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            zz500_stocks.append(rs.get_row_data())
        result = pd.DataFrame(zz500_stocks, columns=rs.fields)

        # 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
        # 调用格式为data_records[index][key1]
        data_dict = result.to_dict('records')

        return data_dict

    def baostock_query_stock_profitability(self, is_increment):
        """
        查询季频估值指标盈利能力。两种模式：1. 全部更新； 2. 增量更新（常用）。
        :return: 字典
        """
        if not self.inited:
            self.init()

        print('=====获取 盈利能力 季频数据====')

        # 数据库集合为空，全部更新
        if len(list(self.database.stock_profitability.find({}))) == 0:
            print('数据库中 盈利能力 集合为空，需要全部更新！')
            result = self.update_all_quarter_data(bs.query_profit_data)
            return result

        # 增量更新
        if is_increment:
            result = self.update_increment_quarter_data(bs.query_profit_data)
            return result

        # 全部更新
        if not is_increment:
            result = self.update_all_quarter_data(bs.query_growth_data)
            return result

    def baostock_query_stock_growth(self, is_increment):
        """
        获取季频成长能力数据。两种模式：1. 全部更新； 2. 增量更新（常用）。
        :return: 字典
        """
        if not self.inited:
            self.init()

        print('====获取 成长能力 季频数据====')

        # 数据库集合为空，全部更新
        if len(list(self.database.stock_growth.find({}))) == 0:
            print('数据库中 成长能力 集合为空，需要全部更新！')
            result = self.update_all_quarter_data(bs.query_growth_data)
            return result

        # 增量更新
        if is_increment:
            result = self.update_increment_quarter_data(bs.query_growth_data)
            return result

        # 全部更新
        if not is_increment:
            result = self.update_all_quarter_data(bs.query_growth_data)
            return result

    def update_all_quarter_data(self, bs_query_func):
        """
        更新全部数据
        :param bs_query_func: 需要调用查询的函数，如 bs.query_growth_data
        :return: 数据字典列表 [{},{},{}...]
        """
        print('开始更新 该项数据库 全部数据。。。。。。')
        # 1. 获取 baostock网站的数据 的最新日期 datafeed_date
        date_now = datetime.now()
        year, quarter = get_previous_year_quarter(date_now)
        while True:
            rs_query = bs_query_func(code=CODE_REFERENCE, year=year, quarter=quarter)
            if (rs_query.error_code == '0') & rs_query.next():
                datafeed_date = rs_query.get_row_data()[2]     # datafeed 数据时间点 statDate
                break
            else:
                year, quarter = get_previous_year_quarter(date_now - timedelta(days=90))

        # 2. 获取所有股票列表
        if not self.all_stocks:
            self.all_stocks = [doc['code'] for doc in self.database.all_stock_list.find({}, {'code': 1, '_id': 0})]

        # 3. 获取查询开始年份，和 datafeed 最新数据的年、季度
        start_year = datetime.strptime(self.startdate, '%Y-%m-%d').year
        datafeed_date = datetime.strptime(datafeed_date, '%Y-%m-%d')
        end_year = datafeed_date.year
        end_quarter = month_to_quarter(datafeed_date.month)

        # 4. 获取全部季频数据
        rs_query_list = []
        # 三层循环取数
        # 初始年 到 去年 的数据
        for stock in self.all_stocks:
            # 从 start_year 到 end_year-1 数据
            for year in range(start_year, end_year):
                for quarter in [1, 2, 3, 4]:
                    rs_query = bs_query_func(code=stock, year=year, quarter=quarter)
                    while (rs_query.error_code == '0') & rs_query.next():
                        rs_query_list.append(rs_query.get_row_data())
                        print(rs_query_list[-1])
            # end_year 数据
            for quarter in range(1, end_quarter+1):
                rs_query = bs_query_func(code=stock, year=end_year, quarter=quarter)
                while (rs_query.error_code == '0') & rs_query.next():
                    rs_query_list.append(rs_query.get_row_data())
                    print(rs_query_list[-1])

        # 列表 转换成 DataFrame
        result = pd.DataFrame(rs_query_list, columns=rs_query.fields)

        # 5. 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
        # 调用格式为data_records[index][key1]
        data_dict = result.to_dict('records')
        return data_dict

    def update_increment_quarter_data(self, bs_query_func):
        """
        更新全部数据
        :param bs_query_func: 需要调用查询的函数，如 bs.query_growth_data
        :return: 数据字典列表 [{},{},{}...]
        """
        print('开始更新 该项数据库 增量数据。。。。。。')
        # 1. 获取 baostock网站的数据 的最新日期 datafeed_date
        date_now = datetime.now()
        year, quarter = get_previous_year_quarter(date_now)
        while True:
            rs_query = bs_query_func(code=CODE_REFERENCE, year=year, quarter=quarter)
            if (rs_query.error_code == '0') & rs_query.next():
                datafeed_date = rs_query.get_row_data()[2]     # datafeed 数据时间点 statDate
                break
            else:
                year, quarter = get_previous_year_quarter(date_now - timedelta(days=90))

        # 2. 获取 database 数据最新年、季度，和 datafeed 最新数据的年、季度
        database_date = self.database.stock_growth.find({}, {'statDate': 1, '_id': 0})
        database_date_max = pd.DataFrame(database_date)['statDate'].max()
        print('数据库最新日期为：', database_date_max)

        # 判断数据库中，是否已经是最新数据（两字符串比较）
        if database_date_max == datafeed_date:
            print('数据库已经是最新，无需更新！', bs_query_func)
            return

        # 需要更新，继续。获取数据库时间的下一个季频时间（年，第几季度）
        database_date_max = datetime.strptime(database_date_max, "%Y-%m-%d")
        start_year, start_quarter = get_next_year_quarter(database_date_max)

        # 获取 datafeed 网上数据时间（年，第几季度）
        datafeed_date = datetime.strptime(datafeed_date, '%Y-%m-%d')
        print('datafeed 数据最新日期为：', datafeed_date)
        end_year = datafeed_date.year
        end_quarter = month_to_quarter(datafeed_date.month)

        # 3. 获取所有股票列表
        if not self.all_stocks:
            self.all_stocks = [doc['code'] for doc in self.database.all_stock_list.find({}, {'code': 1, '_id': 0})]
        # 调试用
        # self.all_stocks = ['sh.600000', 'sh.600004', 'sh.600006']
        # 4. 获取季频增量数据
        rs_query_list = []
        # ===================================================================================
        # 同一年内更新
        if start_year == end_year and start_quarter != 1:
            for stock in self.all_stocks:
                for quarter in range(start_quarter, end_quarter+1):
                    rs_query = bs_query_func(code=stock, year=end_year, quarter=quarter)
                    while (rs_query.error_code == '0') & rs_query.next():
                        rs_query_list.append(rs_query.get_row_data())
                        print("1 >", rs_query_list[-1])
            # 列表 转换成 DataFrame
            result = pd.DataFrame(rs_query_list, columns=rs_query.fields)
            # 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
            # 调用格式为data_records[index][key1]
            data_dict = result.to_dict('records')
            return data_dict

        # 数据库日期是 前一年 12月31日
        if start_year == end_year and start_quarter == 1:
            for stock in self.all_stocks:
                for quarter in range(1, end_quarter+1):
                    # print(stock, end_year, quarter)
                    rs_query = bs_query_func(code=stock, year=end_year, quarter=quarter)
                    while (rs_query.error_code == '0') & rs_query.next():
                        rs_query_list.append(rs_query.get_row_data())
                        print("2 >", rs_query_list[-1])
            # 列表 转换成 DataFrame
            result = pd.DataFrame(rs_query_list, columns=rs_query.fields)
            # print(result)
            # 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
            # 调用格式为data_records[index][key1]
            data_dict = result.to_dict('records')
            # print(data_dict)
            return data_dict
        # ==================================================================================
        # 下面是已经跨年的情形，且数据库日期，至少是 前1年的9月30日
        # 首先，更新 数据库 start_year 的数据
        for stock in self.all_stocks:
            for quarter in range(start_quarter, 5):
                rs_query = bs_query_func(code=stock, year=start_year, quarter=quarter)
                while (rs_query.error_code == '0') & rs_query.next():
                    rs_query_list.append(rs_query.get_row_data())
                    print("3 >", rs_query_list[-1])

        # 其次，更新 datafeed年的数据
        for stock in self.all_stocks:
            for quarter in range(1, end_quarter + 1):
                rs_query = bs_query_func(code=stock, year=end_year, quarter=quarter)
                while (rs_query.error_code == '0') & rs_query.next():
                    rs_query_list.append(rs_query.get_row_data())
                    print("4 >", rs_query_list[-1])

        # 数据库当年 与 datafeed年 相差1年以上
        if (end_year - start_year) > 1:
            # 更新数据库当年 与 datafeed年 之间的数据
            for stock in self.all_stocks:
                for year in range(start_year + 1, end_year):
                    for quarter in [1, 2, 3, 4]:
                        rs_query = bs_query_func(code=stock, year=year, quarter=quarter)
                        while (rs_query.error_code == '0') & rs_query.next():
                            rs_query_list.append(rs_query.get_row_data())
                            print("5 >", rs_query_list[-1])

        # 列表 转换成 DataFrame
        result = pd.DataFrame(rs_query_list, columns=rs_query.fields)

        # 5. 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
        # 调用格式为data_records[index][key1]
        data_dict = result.to_dict('records')
        return data_dict

    def baostock_query_history_daily_k_data(self, is_increment):
        """
        获取 日K线 数据。两种模式：1. 全部更新； 2. 增量更新（常用）。
        :return: 字典
        """
        # return
        if not self.inited:
            self.init()

        print('====获取 日K线 数据====')

        # 数据库集合为空，全部更新
        if len(list(self.database.stock_history_daily_k_data.find({'code': 'sz.300776', 'date': '2024-05-31'}, {'date': 1, '_id': 0}))) == 0:
            print('数据库中 成长能力 集合为空，需要全部更新！')
            result = self.update_all_history_k_data('d')
            return result

        # 增量更新
        if is_increment:
            result = self.update_increment_history_k_data('d')
            # result = self.update_all_history_k_data('d')
            return result

        # 全部更新
        if not is_increment:
            result = self.update_all_history_k_data('d')
            return result

    def baostock_query_history_week_k_data(self, is_increment):
        """
        获取 周K线 数据。两种模式：1. 全部更新； 2. 增量更新（常用）。
        :return: 字典
        """
        # return
        if not self.inited:
            self.init()

        print('====获取 周K线 数据====')

        # 数据库集合为空，全部更新
        if len(list(self.database.stock_history_week_k_data.find({'code': 'sz.300776', 'date': '2024-05-31'}, {'date': 1, '_id': 0}))) == 0:
            print('数据库中 成长能力 集合为空，需要全部更新！')
            result = self.update_all_history_k_data('w')
            return result

        # 增量更新
        if is_increment:
            result = self.update_increment_history_k_data('w')
            # result = self.update_all_history_k_data('w')
            return result

        # 全部更新
        if not is_increment:
            result = self.update_all_history_k_data('w')
            return result

    def baostock_query_history_month_k_data(self, is_increment):
        """
        获取 月K线 数据。两种模式：1. 全部更新； 2. 增量更新（常用）。
        :return: 字典
        """
        if not self.inited:
            self.init()

        print('====获取 月K线 数据====')

        # 数据库集合为空，全部更新
        if len(list(self.database.stock_history_month_k_data.find({'code': 'sz.300776', 'date': '2024-05-31'}, {'date': 1, '_id': 0}))) == 0:
            print('数据库中 成长能力 集合为空，需要全部更新！')
            result = self.update_all_history_k_data('m')
            return result

        # 增量更新
        if is_increment:
            result = self.update_increment_history_k_data('m')
            # result = self.update_all_history_k_data('m')
            return result

        # 全部更新
        if not is_increment:
            result = self.update_all_history_k_data('m')
            return result

    def update_all_history_k_data(self, frequency):
        """
        更新全部数据
        :param frequency: 数据频率 ‘d’, 'w', 'm'
        :return: 数据字典列表 [{},{},{}...]
        """
        dict_frequency = {'d': '日', 'w': '周', 'm': '月'}
        print(f'开始更新 {dict_frequency[frequency]}K线 全部数据。。。。。。')

        # 1. 设置数据的 起始日期(self.startdate) 和 最新日期
        end_date = datetime.now().strftime('%Y-%m-%d')

        # 2. 获取所有股票列表、所有指数列表，并合并
        if not self.all_stocks:
            self.all_stocks = [doc['code'] for doc in self.database.all_stock_list.find({}, {'code': 1, '_id': 0})]
        if not self.all_index:
            self.all_index = [doc['code'] for doc in self.database.all_index_list.find({}, {'code': 1, '_id': 0})]
            print('1 > ', self.all_index)
        self.all_stocks_index.extend(self.all_stocks)
        self.all_stocks_index.extend(self.all_index)
        print(self.all_stocks_index)

        # self.all_stocks = ['sh.600000', 'sh.600004', 'sh.600006']
        # STOCKS_SLICE_NUM = 500     # 设置 股票切片数量
        # stocks_num = len(self.all_stocks)

        # 3. 设置 数据列
        match frequency:
            case 'd':
                fields = 'date,code,open,high,low,close,preclose,volume,amount,' \
                         'adjustflag,turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST'
            case 'w' | 'm':
                fields = 'date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg'
            case '_':
                print('frequency is error. Only d、w、m')
                return

        # 4. 初始日期 到 现在日期 的数据
        rs_query_list = []
        for stock in self.all_stocks_index:
            rs_query = bs.query_history_k_data_plus(code=stock, fields=fields,
                                                    start_date=self.startdate, end_date=end_date,
                                                    frequency=frequency, adjustflag="2")
            while (rs_query.error_code == '0') & rs_query.next():
                rs_query_list.append(rs_query.get_row_data())
                print(rs_query_list[-1])

        # 列表 转换成 DataFrame
        result = pd.DataFrame(rs_query_list, columns=rs_query.fields)

        # 5. 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
        # 调用格式为data_records[index][key1]
        data_dict = result.to_dict('records')
        return data_dict

    def update_increment_history_k_data(self, frequency):
        """
        增量更新数据
        :param frequency: 数据频率 ‘d’, 'w', 'm'
        :return: 数据字典列表 [{},{},{}...]
        """
        dict_frequency = {'d': '日', 'w': '周', 'm': '月'}
        print(f'开始更新 {dict_frequency[frequency]}K线 增量数据。。。。。。')
        collection = None   # 操作的集合对象

        # 1. 设置数据的 最新日期
        # 数据库更新时间设置为当天的18:00:00
        database_daily_k_update_time = datetime.combine(datetime.now().date(), datetime.min.time()) + timedelta(hours=18)
        # 时间晚于18：00，更新今天的 日K线 数据
        if datetime.now() > database_daily_k_update_time:
            today_date = datetime.now().strftime('%Y-%m-%d')
        # 时间早于18：00，更新昨天的 日K线 数据
        else:
            today_date = (datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')

        #  2. 获取 database 数据最新日期，设置 数据列 信息
        match frequency:
            case 'd':
                fields = 'date,code,open,high,low,close,preclose,volume,amount,' \
                         'adjustflag,turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST'
                database_date = self.database.stock_history_daily_k_data.find({'code': CODE_REFERENCE}, {'date': 1, '_id': 0})
                # print('1 >', database_date)
                # print('2 >', pd.DataFrame(database_date))
                # print('3 >', pd.DataFrame(database_date)['date'])
                # print('4 >', pd.to_datetime(pd.DataFrame(database_date)['date']))
                # print('5 >', pd.to_datetime(pd.DataFrame(database_date)['date']).max())
                # return
                database_date_max = pd.to_datetime(pd.DataFrame(database_date)['date']).max()
                self.database_date_max_next = database_date_max + timedelta(days=1)
                self.database_date_max = database_date_max.strftime('%Y-%m-%d')
                self.database_date_max_next = self.database_date_max_next.strftime('%Y-%m-%d')
                print('日K线 数据库最新日期为：', self.database_date_max)
            case 'w':
                fields = 'date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg'
                database_date = self.database.stock_history_week_k_data.find({'code': CODE_REFERENCE}, {'date': 1, '_id': 0})
                database_date_max = pd.to_datetime(pd.DataFrame(database_date)['date']).max()
                self.database_date_max_next = database_date_max + timedelta(days=1)
                self.database_date_max = database_date_max.strftime('%Y-%m-%d')
                self.database_date_max_next = self.database_date_max_next.strftime('%Y-%m-%d')
                print('周K线 数据库最新日期为：', self.database_date_max)
            case 'm':
                fields = 'date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg'
                database_date = self.database.stock_history_month_k_data.find({'code': CODE_REFERENCE}, {'date': 1, '_id': 0})
                database_date_max = pd.to_datetime(pd.DataFrame(database_date)['date']).max()
                self.database_date_max_next = database_date_max + timedelta(days=1)
                self.database_date_max = database_date_max.strftime('%Y-%m-%d')
                self.database_date_max_next = self.database_date_max_next.strftime('%Y-%m-%d')
                print('月K线 数据库最新日期为：', self.database_date_max)
            case '_':
                print('frequency is error. Only d、w、m')
                return

        # 3. 比较 数据库日期 是不是最新日期
        # 是，就返回；不是同一天，说明需要从数据库日期第二天开始更新
        if self.database_date_max == today_date:
            print('数据库已经是最新数据，无需更新！')
            return

        # 4. 获取所有股票列表、所有指数列表，并合并
        if not self.all_stocks:
            self.all_stocks = [doc['code'] for doc in self.database.all_stock_list.find({}, {'code': 1, '_id': 0})]
        if not self.all_index:
            self.all_index = [doc['code'] for doc in self.database.all_index_list.find({}, {'code': 1, '_id': 0})]
            # print('1 > ', self.all_index)
        self.all_stocks_index.extend(self.all_stocks)
        self.all_stocks_index.extend(self.all_index)

        # 5. 增量更新数据
        rs_query_list = []
        for stock in self.all_stocks_index:
            rs_query = bs.query_history_k_data_plus(code=stock, fields=fields,
                                                    start_date=self.database_date_max_next, end_date=today_date,
                                                    frequency=frequency, adjustflag="2")
            while (rs_query.error_code == '0') & rs_query.next():
                rs_query_list.append(rs_query.get_row_data())
                print(rs_query_list[-1])
            # 取出数据为空，说明新的数据还没有
            if not rs_query_list:
                break
        if not rs_query_list:
            return

        # 列表 转换成 DataFrame
        result = pd.DataFrame(rs_query_list, columns=rs_query.fields)

        # 5. 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
        # 调用格式为data_records[index][key1]
        data_dict = result.to_dict('records')
        return data_dict


def month_to_quarter(month):
    """月份转换成第几季度"""
    match month:
        case 1 | 2 | 3:
            quarter = 1
            return quarter
        case 4 | 5 | 6:
            quarter = 2
            return quarter
        case 7 | 8 | 9:
            quarter = 3
            return quarter
        case 10 | 11 | 12:
            quarter = 4
            return quarter


def get_next_year_quarter(database_date_max):
    """
    获取下一个季频时间（年，第几季度）
    :param database_date_max: datetime值
    :return: 前一个季度的（年， 季度值）
    """
    month = database_date_max.month
    if month == 3:
        return database_date_max.year, 2
    elif month == 6:
        return database_date_max.year, 3
    elif month == 9:
        return database_date_max.year, 4
    else:
        return database_date_max.year+1, 1


def get_previous_year_quarter(date_now):
    """
    获得前一个季度 年、季度
    :param date_now: datetime值
    :return: 前一个季度的（年， 季度值）
    """
    match date_now.month:
        case 1 | 2 | 3:
            return date_now.year-1, 4
        case 4 | 5 | 6:
            return date_now.year, 1
        case 7 | 8 | 9:
            return date_now.year, 2
        case 10 | 11 | 12:
            return date_now.year, 3


def get_previous_workday():
    current_date = datetime.now().date()
    while True:
        current_date -= timedelta(days=1)
        weekday = current_date.weekday()
        if weekday > 4 or weekday == 0:  # 周六和周日为非工作日
            continue
        else:
            return current_date.strftime('%Y-%m-%d')



    # def query_bar_history(self, req: HistoryRequest) -> Optional[List[BarData]]:
    #     """查询k线数据"""
    #     if not self.inited:
    #         self.init()
    #
    #     symbol = req.symbol
    #     exchange = req.exchange
    #     interval = req.interval
    #     start = req.start.strftime("%Y-%m-%d")
    #     end = req.end.strftime("%Y-%m-%d")
    #     bs_symbol = f"sz.{symbol}" if exchange == Exchange.SZSE else f"sh.{symbol}"
    #
    #     bs_interval = INTERVAL_VT2TS.get(interval)
    #     if not bs_interval:
    #         return None
    #
    #     if interval in (Interval.MINUTE, Interval.HOUR):
    #         fields = "time,code,open,high,low,close,volume,amount"
    #     else:
    #         fields = "date,code,open,high,low,close,volume,amount"
    #     try:
    #         rs = bs.query_history_k_data_plus(
    #             bs_symbol,
    #             fields,
    #             start_date=start,
    #             end_date=end,
    #             frequency=bs_interval,
    #             adjustflag="3",
    #         )
    #     except Exception as e:
    #         return []
    #     data: List[BarData] = []
    #
    #     print(fields.split(','))
    #     while (rs.error_code == "0") & rs.next():
    #         item = rs.get_row_data()
    #         print(item)
    #         str_format = "%Y-%m-%d"
    #         if interval in (Interval.MINUTE, Interval.HOUR):
    #             str_format = "%Y%m%d%H%M%S%f"
    #         dt = datetime.strptime(item[0], str_format)
    #         bar: BarData = BarData(
    #             symbol=symbol,
    #             exchange=exchange,
    #             interval=interval,
    #             datetime=dt,
    #             open_price=round_to(item[2], 0.000001),
    #             high_price=round_to(item[3], 0.000001),
    #             low_price=round_to(item[4], 0.000001),
    #             close_price=round_to(item[5], 0.000001),
    #             volume=float(item[6]),
    #             turnover=float(item[7]),
    #             open_interest=0,
    #             gateway_name="BS",
    #         )
    #         data.append(bar)
    #
    #     return data


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


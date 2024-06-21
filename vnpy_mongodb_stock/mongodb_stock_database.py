""""""
import pandas as pd

print('Enter vnpy_mongodb_stock 模块')
from datetime import datetime
from typing import List
from pathlib import Path

from pymongo import ASCENDING, MongoClient, ReplaceOne
from pymongo.database import Database
from pymongo.cursor import Cursor
from pymongo.collection import Collection
from pymongo.results import DeleteResult
from pymongo.errors import BulkWriteError

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import TickData
from vnpy.trader.object_stock import BarData
from vnpy.trader.database import BaseDatabase, BarOverview, TickOverview, DB_TZ
from vnpy.trader.setting import SETTINGS


class StockMongodbDatabase(BaseDatabase):
    """MongoDB数据库接口"""

    def __init__(self) -> None:
        """"""
        # 读取配置
        self.database: str = SETTINGS["database.database"]
        self.host: str = SETTINGS["database.host"]
        self.port: int = SETTINGS["database.port"]
        self.username: str = SETTINGS["database.user"]
        self.password: str = SETTINGS["database.password"]

        # 创建客户端
        if self.username and self.password:
            self.client: MongoClient = MongoClient(
                host=self.host,
                port=self.port,
                tz_aware=True,
                username=self.username,
                password=self.password,
                tzinfo=DB_TZ
            )
        else:
            self.client: MongoClient = MongoClient(
                host=self.host,
                port=self.port,
                tz_aware=True,
                tzinfo=DB_TZ
            )

        # 初始化数据库
        self.db: Database = self.client[self.database]

        # ==== 基础数据 数据库 =======================================
        # 1. 初始化 行业分类 集合
        self.classification_of_industry: Collection = self.db["classification_of_industry"]
        self.classification_of_industry.create_index([("code", ASCENDING)], unique=True)

        # 2. 初始化 所有股票指数、所有股票、所有ST股票 集合
        self.all_stock_list: Collection = self.db["all_stock_list"]
        self.all_stock_list.create_index([("code", ASCENDING)], unique=True)

        self.all_index_list: Collection = self.db["all_index_list"]
        self.all_index_list.create_index([("code", ASCENDING)], unique=True)

        self.all_st_stock_list: Collection = self.db["all_st_stock_list"]
        self.all_st_stock_list.create_index([("code", ASCENDING)], unique=True)

        # 3. 初始化 日K线、周K线、月K线 集合
        self.stock_history_daily_k_data: Collection = self.db["stock_history_daily_k_data"]
        self.stock_history_daily_k_data.create_index([("code", ASCENDING), ("date", ASCENDING)], unique=True)

        self.stock_history_week_k_data: Collection = self.db["stock_history_week_k_data"]
        self.stock_history_week_k_data.create_index([("code", ASCENDING), ("date", ASCENDING)], unique=True)

        self.stock_history_month_k_data: Collection = self.db["stock_history_month_k_data"]
        self.stock_history_month_k_data.create_index([("code", ASCENDING), ("date", ASCENDING)], unique=True)

        # 4. 初始化 交易日期 集合
        self.trade_dates: Collection = self.db["trade_dates"]
        self.trade_dates.create_index([("calendar_date", ASCENDING)], unique=True)

        # 5. 初始化 上证50、沪深300、中证500成分股 集合
        self.components_shangzheng50: Collection = self.db["components_shangzheng50"]
        self.components_shangzheng50.create_index([("code", ASCENDING)], unique=True)

        self.components_hushen300: Collection = self.db["components_hushen300"]
        self.components_hushen300.create_index([("code", ASCENDING)], unique=True)

        self.components_zhongzheng500: Collection = self.db["components_zhongzheng500"]
        self.components_zhongzheng500.create_index([("code", ASCENDING)], unique=True)

        # 6. 初始化 盈利能力、成长能力 集合
        self.stock_profitability: Collection = self.db["stock_profitability"]
        self.stock_profitability.create_index([("code", ASCENDING), ("statDate", ASCENDING)], unique=True)

        self.stock_growth: Collection = self.db["stock_growth"]
        self.stock_growth.create_index([("code", ASCENDING), ("statDate", ASCENDING)], unique=True)

        # ==== 股票分析 数据库===============================
        # 7. 持有股票数据库
        self.stock_holding: Collection = self.db["stock_holding"]
        self.stock_holding.create_index([("code", ASCENDING), ("date_buy", ASCENDING)], unique=True)


        """
        # 初始化K线数据表
        self.bar_collection: Collection = self.db["bar_data"]
        self.bar_collection.create_index(
            [
                ("exchange", ASCENDING),
                ("symbol", ASCENDING),
                ("interval", ASCENDING),
                ("datetime", ASCENDING),
            ],
            unique=True
        )

        # 初始化K线概览表
        self.bar_overview_collection: Collection = self.db["bar_overview"]
        self.bar_overview_collection.create_index(
            [
                ("exchange", ASCENDING),
                ("symbol", ASCENDING),
                ("interval", ASCENDING),
            ],
            unique=True
        )
        """

    def baostock_save_industry_data(self, result):
        """保存 industry 数据"""
        self.classification_of_industry.drop()      # 清空表
        self.classification_of_industry.insert_many(result)
        return True

    def baostock_save_all_stock_list(self, result):
        """保存 所有股票、所有指数、所有ST股票 数据"""
        # 1. 数据处理
        # 去除 北京科创板，以ST、*ST、S开头的股票，使用str.startswith()配合~（not）去除特定开头的行
        res = result.copy()
        all_st_stocks = []  # 所有 ST股票 列表
        for item in result:
            if item['code'].startswith('bj'):
                res.remove(item)
            if item['code_name'].startswith('S') or item['code_name'].startswith('ST') or item['code_name'].startswith('*ST'):
                all_st_stocks.append(item)
                res.remove(item)

        all_index = []      # 所有 股票指数 列表
        all_stocks = []     # 所有 股票 列表
        for item in res:
            if item['code'].startswith('sh.000') or item['code'].startswith('sz.399'):
                all_index.append(item)
            else:
                all_stocks.append(item)


        # 2. 数据存储
        self.all_stock_list.drop()      # 清空表
        self.all_stock_list.insert_many(all_stocks)

        self.all_index_list.drop()      # 清空表
        self.all_index_list.insert_many(all_index)

        self.all_st_stock_list.drop()      # 清空表
        self.all_st_stock_list.insert_many(all_st_stocks)

        return True

    def baostock_save_trade_dates(self, result):
        """保存 交易日期 数据"""
        self.trade_dates.drop()      # 清空表
        self.trade_dates.insert_many(result)
        return True

    def baostock_save_components_shangzheng50(self, result):
        """保存 上证50 数据"""
        self.components_shangzheng50.drop()      # 清空表
        self.components_shangzheng50.insert_many(result)
        return True

    def baostock_save_components_hushen300(self, result):
        """保存 沪深300 数据"""
        self.components_hushen300.drop()      # 清空表
        self.components_hushen300.insert_many(result)
        return True

    def baostock_save_components_zhongzheng500(self, result):
        """保存 中证500 数据"""
        self.components_zhongzheng500.drop()      # 清空表
        self.components_zhongzheng500.insert_many(result)
        return True

    def baostock_save_stock_profitability(self, result, is_increment):
        """保存 盈利能力 数据"""
        if not result:
            return

        # 增量更新
        if is_increment:
            print('enter profitability increment.')
            self.stock_profitability.insert_many(result)
            return

        # 全部更新
        if not is_increment:
            print('enter profitability not increment.')
            if len(list(self.stock_profitability.find({}))) == 0:
                self.stock_profitability.insert_many(result)
            else:
                self.stock_profitability.drop()      # 清空表
                self.stock_profitability.insert_many(result)
            return True

    def baostock_save_stock_growth(self, result, is_increment):
        """保存 成长能力 数据"""
        if not result:
            return

        # 增量更新
        if is_increment:
            print('enter stock_growth increment.')
            self.stock_growth.insert_many(result)
            return

        # 全部更新
        if not is_increment:
            print('enter stock_growth not increment.')
            if len(list(self.stock_growth.find({}))) == 0:
                self.stock_growth.insert_many(result)
            else:
                self.stock_growth.drop()  # 清空表
                self.stock_growth.insert_many(result)
            return True

    def baostock_save_history_daily_k_data(self, result, is_increment):
        """保存 日K线 数据"""
        if not result:
            print('保存 日K线 数据，result 为空。')
            return

        # 增量更新, 第一次也算增量更新
        if is_increment:
            print('enter stock_history_daily_k_data increment.')
            self.stock_history_daily_k_data.insert_many(result)
            return

        # 全部更新
        if not is_increment:
            print('enter stock_history_daily_k_data not increment.')
            if len(list(self.stock_history_daily_k_data.find({}))) == 0:
                self.stock_history_daily_k_data.insert_many(result)
            else:
                self.stock_history_daily_k_data.drop()  # 清空表
                self.stock_history_daily_k_data.insert_many(result)
            return True

    def baostock_save_history_week_k_data(self, result, is_increment):
        """保存 周K线 数据"""
        if not result:
            print('保存 周K线 数据，result 为空。')
            return

        # 增量更新, 第一次也算增量更新
        if is_increment:
            print('enter stock_history_week_k_data increment.')
            try:
                self.stock_history_week_k_data.insert_many(result)
            except BulkWriteError:
                print("pymongo.errors.BulkWriteError: batch op errors occurred, full error: {'writeErrors': "
                      "[{'index': 5504, 'code': 11000, 'errmsg': 'E11000 duplicate key error collection: vnpy_stock.stock_history_week_k_data index: code_1_date_1 dup key: { code: \"sh.600000\", date: \"2024-06-14\" }', 'keyPattern': {'code': 1, 'date': 1}, 'keyValue': {'code': 'sh.600000', 'date': '2024-06-14'}, 'op': {'date': '2024-06-14', 'code': 'sh.600000', 'open': '8.3400000000', 'high': '8.3600000000', 'low': '7.9900000000', 'close': '8.1400000000', 'volume': '164646855', 'amount': '1339188141.4600', 'adjustflag': '2', 'turn': '0.561000', 'pctChg': '-2.045700', '_id': ObjectId('666cedd0f019c6b9c103224d')}}], "
                      "'writeConcernErrors': [], 'nInserted': 5504, 'nUpserted': 0, 'nMatched': 0, 'nModified': 0, 'nRemoved': 0, 'upserted': []}")
                pass

            return

        # 全部更新
        if not is_increment:
            print('enter stock_history_week_k_data not increment.')
            if len(list(self.stock_history_week_k_data.find({}))) == 0:
                self.stock_history_week_k_data.insert_many(result)
            else:
                self.stock_history_week_k_data.drop()  # 清空表
                self.stock_history_week_k_data.insert_many(result)
            return True

    def baostock_save_history_month_k_data(self, result, is_increment):
        """保存 月K线 数据"""
        if not result:
            print('保存 月K线 数据，result 为空。' )
            return

        # 增量更新, 第一次也算增量更新
        if is_increment:
            print('enter stock_history_month_k_data increment.')
            self.stock_history_month_k_data.insert_many(result)
            return

        # 全部更新
        if not is_increment:
            print('enter stock_history_month_k_data not increment.')
            if len(list(self.stock_history_month_k_data.find({}))) == 0:
                self.stock_history_month_k_data.insert_many(result)
            else:
                self.stock_history_month_k_data.drop()  # 清空表
                self.stock_history_month_k_data.insert_many(result)
            return True

    def save_collection_from_csv(self, collection, file):
        # print(collection, filename)
        filename = Path(file).stem
        print(filename)
        match collection:
            case '日K线':
                if filename == 'stock_history_daily_k_data':
                    df = pd.read_csv(file)
                    result = df.to_dict('records')
                    # self.stock_growth.drop()
                    self.stock_history_week_k_data.insert_many(result)
                    print('导入 stock_history_daily_k_data 完毕！')
                else:
                    print('导入的文件不匹配!')

            case '周K线':
                if filename == 'stock_history_week_k_data':
                    df = pd.read_csv(file)
                    result = df.to_dict('records')
                    # self.stock_growth.drop()
                    self.stock_history_week_k_data.insert_many(result)
                    print('导入 stock_history_week_k_data 完毕！')
                else:
                    print('导入的文件不匹配!')

            case '月K线':
                if filename == 'stock_history_month_k_data':
                    df = pd.read_csv(file)
                    result = df.to_dict('records')
                    # self.stock_growth.drop()
                    self.stock_history_week_k_data.insert_many(result)
                    print('导入 stock_history_month_k_data 完毕！')
                else:
                    print('导入的文件不匹配!')

            case '盈利能力':
                if filename == 'stock_profitability':
                    df = pd.read_csv(file)
                    result = df.to_dict('records')
                    self.stock_growth.drop()
                    self.stock_growth.insert_many(result)
                    print('导入 stock_profitability 完毕！')
                else:
                    print('导入的文件不匹配!')

            case '成长能力':
                if filename == 'stock_growth':
                    df = pd.read_csv(file)
                    result = df.to_dict('records')
                    self.stock_growth.drop()
                    self.stock_growth.insert_many(result)
                    print('导入 stock_growth 完毕！')
                else:
                    print('导入的文件不匹配!')

            case '_':
                print('无法导入')

    def delete_error_data(self):
        """删除数据库出错数据"""
        print('删除数据库出错数据，需要编辑函数内容！')
        # ==============================================
        # database_date = self.stock_history_daily_k_data.find({'code': 'sz.300776'}, {'date': 1, '_id': 0})
        # # print(pd.DataFrame(database_date)['date'])
        # self.database_date_max = pd.to_datetime(pd.DataFrame(database_date)['date']).max()
        # print('数据库最新日期为：', self.database_date_max)

        # ==========================================
        import baostock as bs
        bs.login()
        rs_query_list = []
        fields = 'date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg'
        rs_query = bs.query_history_k_data_plus(code='sh.600000', fields=fields,
                                                start_date='2024-06-01', end_date='2024-06-06',
                                                frequency='w', adjustflag="2")
        while (rs_query.error_code == '0') & rs_query.next():
            rs_query_list.append(rs_query.get_row_data())
            print(rs_query_list[-1])
        bs.logout()
        # ================================================
        return

        # 设置你想要删除的条件
        query = {"code": "sz.399359"}  # 替换为你的查询条件

        # 批量删除
        self.stock_history_week_k_data.delete_many(query)

    # =====以下是原函数==========================================================================
    """"""
    def save_bar_data(self, bars: List[BarData], stream: bool = False) -> bool:
        """保存K线数据"""
        requests: List[ReplaceOne] = []

        for bar in bars:
            # 逐个插入
            filter: dict = {
                "symbol": bar.symbol,
                "exchange": bar.exchange.value,
                "datetime": bar.datetime,
                "interval": bar.interval.value,
            }

            d: dict = {
                "symbol": bar.symbol,
                "exchange": bar.exchange.value,
                "datetime": bar.datetime,
                "interval": bar.interval.value,
                "volume": bar.volume,
                "turnover": bar.turnover,
                "open_interest": bar.open_interest,
                "open_price": bar.open_price,
                "high_price": bar.high_price,
                "low_price": bar.low_price,
                "close_price": bar.close_price,
            }

            requests.append(ReplaceOne(filter, d, upsert=True))

        self.bar_collection.bulk_write(requests, ordered=False)

        # 更新汇总
        filter: dict = {
            "symbol": bar.symbol,
            "exchange": bar.exchange.value,
            "interval": bar.interval.value
        }

        overview: dict = self.bar_overview_collection.find_one(filter)

        if not overview:
            overview = {
                "symbol": bar.symbol,
                "exchange": bar.exchange.value,
                "interval": bar.interval.value,
                "count": len(bars),
                "start": bars[0].datetime,
                "end": bars[-1].datetime
            }
        elif stream:
            overview["end"] = bars[-1].datetime
            overview["count"] += len(bars)
        else:
            overview["start"] = min(bars[0].datetime, overview["start"])
            overview["end"] = max(bars[-1].datetime, overview["end"])
            overview["count"] = self.bar_collection.count_documents(filter)

        self.bar_overview_collection.update_one(filter, {"$set": overview}, upsert=True)

        return True

    def save_tick_data(self, ticks: List[TickData], stream: bool = False) -> bool:
        """保存TICK数据"""
        pass

    def load_bar_data(
        self,
        code: str,
        exchange: str,
        interval: str,
        start: datetime,
        end: datetime
    ) -> List[BarData]:
        """读取K线数据"""
        filter: dict = {
            "code": code
        }

        c: Cursor = self.stock_history_daily_k_data.find(filter)

        bars: List[BarData] = []
        bar_temp = {}
        for d in c:
            bar_temp["gateway_name"] = "MongoDB"
            bar_temp['symbol'] = d['code']
            bar_temp['exchange'] = 'sh | sz'
            bar_temp['datetime'] = datetime.strptime(d['date'], '%Y-%m-%d')
            bar_temp["interval"] = 'd'

            bar_temp['volume'] = int(d['volume'])
            bar_temp['open_price'] = float(d['open'])
            bar_temp['high_price'] = float(d['high'])
            bar_temp['low_price'] = float(d['low'])
            bar_temp['close_price'] = float(d['close'])

            bar = BarData(**bar_temp)
            bars.append(bar)

        return bars

    def load_tick_data(
        self,
        symbol: str,
        exchange: Exchange,
        start: datetime,
        end: datetime
    ) -> List[TickData]:
        """读取TICK数据"""
        pass

    def delete_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval
    ) -> int:
        """删除K线数据"""
        filter: dict = {
            "symbol": symbol,
            "exchange": exchange.value,
            "interval": interval.value,
        }

        result: DeleteResult = self.bar_collection.delete_many(filter)
        self.bar_overview_collection.delete_one(filter)

        return result.deleted_count

    def delete_tick_data(
        self,
        symbol: str,
        exchange: Exchange
    ) -> int:
        """删除TICK数据"""
        pass

    def get_bar_overview(self) -> List[BarOverview]:
        """查询数据库中的K线汇总信息"""
        c: Cursor = self.bar_overview_collection.find()

        overviews: List[BarOverview] = []
        for d in c:
            d["exchange"] = Exchange(d["exchange"])
            d["interval"] = Interval(d["interval"])
            d.pop("_id")

            overview: BarOverview = BarOverview(**d)
            overviews.append(overview)

        return overviews

    def get_tick_overview(self) -> List[TickOverview]:
        """查询数据库中的Tick汇总信息"""
        pass

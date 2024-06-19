from datetime import datetime, date, timedelta
from typing import List, Optional

import baostock as bs
import pandas as pd

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.datafeed import BaseDatafeed
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.setting import SETTINGS
from vnpy.trader.utility import round_to
from vnpy.trader.database import BaseDatabase, get_database
from vnpy_baostock_stock.baostock_stock_datafeed import get_previous_year_quarter, get_next_year_quarter, \
    get_previous_workday, month_to_quarter
database: BaseDatabase = get_database()
bs_query_func = bs.query_growth_data

CODE_REFERENCE = 'sz.300776'        # 以该股票日期为准，更新数据库

# 登陆系统
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

# 1. 获取 baostock网站的数据 的最新日期 datafeed_date
date_now = datetime.now()
year, quarter = get_previous_year_quarter(date_now)
while True:
    rs_growth = bs_query_func(code=CODE_REFERENCE, year=year, quarter=quarter)
    if (rs_growth.error_code == '0') & rs_growth.next():
        datafeed_date = rs_growth.get_row_data()[2]  # datafeed 数据时间点 statDate
        break
    else:
        year, quarter = get_previous_year_quarter(date_now - timedelta(days=90))

# 2. 获取 database 数据最新年、季度，和 datafeed 最新数据的年、季度
database_date = database.stock_growth.find({}, {'statDate': 1, '_id': 0})
database_date_max = pd.DataFrame(database_date)['statDate'].max()
print('数据库最新日期为：', database_date_max)

# 判断数据库中，是否已经是最新数据（两字符串比较）
if database_date_max == datafeed_date:
    print('数据库已经是最新，无需更新！', bs_query_func)


# 需要更新，继续。获取数据库时间的下一个季频时间（年，第几季度）
database_date_max = datetime.strptime(database_date_max, "%Y-%m-%d")
start_year, start_quarter = get_next_year_quarter(database_date_max)

# 获取 datafeed 网上数据时间（年，第几季度）
datafeed_date = datetime.strptime(datafeed_date, '%Y-%m-%d')
print('datafeed 数据最新日期为：', datafeed_date)
end_year = datafeed_date.year
end_quarter = month_to_quarter(datafeed_date.month)

# 3. 获取所有股票列表
all_stocks = ['sh.600000', 'sh.600004', 'sh.600006']

# 4. 获取季频增量数据
growth_list = []
# ===================================================================================
# 同一年内更新
if start_year == end_year and start_quarter != 1:
    for stock in all_stocks:
        for quarter in range(start_quarter, end_quarter + 1):
            rs_growth = bs_query_func(code=stock, year=end_year, quarter=quarter)
            while (rs_growth.error_code == '0') & rs_growth.next():
                growth_list.append(rs_growth.get_row_data())
                print("1 >", growth_list[-1])
    # 列表 转换成 DataFrame
    result = pd.DataFrame(growth_list, columns=rs_growth.fields)

    result.to_csv("growth_data_increment.csv", encoding="utf-8", index=False)
    print("1 >", result)
    # 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
    # 调用格式为data_records[index][key1]
    data_dict = result.to_dict('records')
    print("1 >", data_dict)


# 数据库日期是 前一年 12月31日
if start_year == end_year and start_quarter == 1:
    for stock in all_stocks:
        for quarter in range(1, end_quarter + 1):
            print(stock, end_year, quarter)
            rs_growth = bs_query_func(code=stock, year=end_year, quarter=quarter)
            while (rs_growth.error_code == '0') & rs_growth.next():
                growth_list.append(rs_growth.get_row_data())
                print("2 >", growth_list[-1])

    # 列表 转换成 DataFrame
    result = pd.DataFrame(growth_list, columns=rs_growth.fields)
    result.to_csv("growth_data_increment.csv", encoding="utf-8", index=False)
    print("2 >", result)
    # 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
    # 调用格式为data_records[index][key1]
    data_dict = result.to_dict('records')
    print("2 >", data_dict)

# ==================================================================================
# 下面是已经跨年的情形，且数据库日期，至少是 前1年的9月30日
# 首先，更新 数据库 start_year 的数据
for stock in all_stocks:
    for quarter in range(start_quarter, 5):
        rs_growth = bs_query_func(code=stock, year=start_year, quarter=quarter)
        while (rs_growth.error_code == '0') & rs_growth.next():
            growth_list.append(rs_growth.get_row_data())
            print("3 >", growth_list[-1])

# 其次，更新 datafeed年的数据
for stock in all_stocks:
    for quarter in range(1, end_quarter + 1):
        print('stock:', stock, 'end_year:', end_year, 'quarter:', quarter)
        rs_growth = bs_query_func(code=stock, year=end_year, quarter=quarter)
        while (rs_growth.error_code == '0') & rs_growth.next():
            growth_list.append(rs_growth.get_row_data())
            print("4 >", growth_list[-1])

# 数据库当年 与 datafeed年 相差1年以上
if (end_year - start_year) > 1:
    # 数据库当年 与 datafeed年 之间的数据
    for stock in all_stocks:
        for year in range(start_year + 1, end_year):
            for quarter in [1, 2, 3, 4]:
                rs_growth = bs_query_func(code=stock, year=year, quarter=quarter)
                while (rs_growth.error_code == '0') & rs_growth.next():
                    growth_list.append(rs_growth.get_row_data())
                    print("5 >", growth_list[-1])

# 列表 转换成 DataFrame
result = pd.DataFrame(growth_list, columns=rs_growth.fields)
result.to_csv("growth_data_increment.csv", encoding="utf-8", index=False)
print("5 >", result)

# 5. 将DataFrame转换为字典，整体构成一个列表，内层是将原始数据的每行提取出来形成字典
# 调用格式为data_records[index][key1]
data_dict = result.to_dict('records')
print("5 >", data_dict)


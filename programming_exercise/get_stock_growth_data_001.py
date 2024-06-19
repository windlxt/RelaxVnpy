"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月30日
"""
import baostock as bs
import pandas as pd

import baostock as bs
import pandas as pd
from datetime import datetime, date, timedelta

from vnpy.trader.setting import SETTINGS
from vnpy.trader.database import BaseDatabase, get_database

startdate: str = SETTINGS["database.startdate"]
update: str = SETTINGS["database.update"]

database: BaseDatabase = get_database()

# 登陆系统
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

# 1. 获取所有股票列表

rs = database.all_stock_list.find({}, {'code': 1, '_id': 0})
all_stocks = list(rs)
all_stocks = pd.DataFrame(all_stocks)
all_stocks = list(all_stocks['code'])
print(all_stocks)
print(type(all_stocks))

# 2. 获取查询的时间点，季频
start_year = datetime.strptime(startdate, '%Y-%m-%d').year
end_year = datetime.now().year
print(start_year, type(start_year))
print(end_year, type(end_year))

# 3. 获取季频成长能力数据
growth_list = []
# 三层循环取数
for stock in all_stocks:
    for year in range(start_year, end_year+1):
        for quarter in [1, 2, 3, 4]:
            rs_growth = bs.query_growth_data(code=stock, year=year, quarter=quarter)
            while (rs_growth.error_code == '0') & rs_growth.next():
                m = rs_growth.get_row_data()
                print(m)
                growth_list.append(m)

result = pd.DataFrame(growth_list, columns=rs_growth.fields)
print(result)
# 结果集输出到csv文件
result.to_csv("growth_data_600000.csv", encoding="utf-8", index=False)

# 登出系统
bs.logout()

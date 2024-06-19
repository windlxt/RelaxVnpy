"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月22日
"""
import baostock as bs
import pandas as pd
from datetime import datetime


# 设置 DataFrame 输出格式=====================================
pd.set_option('display.max_columns', None)  # 显示完整的列
pd.set_option('display.max_rows', None)  # 显示完整的行
pd.set_option('display.expand_frame_repr', False)  # 设置不折叠数据
pd.set_option('display.max_colwidth', 100)  # 设置每列宽度
pd.set_option('display.float_format', '{:.2f}'.format)  # 设置显示2位小数
# pd.reset_option('display.float_format')  # 恢复小数原始设置
# ===================================================

bs_query_func = bs.query_growth_data
# 登陆系统
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

# 1. 设置数据的 起始日期(self.startdate) 和 最新日期
end_date = datetime.now().strftime('%Y-%m-%d')

fields= 'date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg'

rs_query_list = []
all_stocks_index = ['sz.399359']
all_stocks_index = pd.read_csv('/home/lxt/data/all_index_list.csv')
all_stocks_index = all_stocks_index['code'][286:]
# print(all_stocks_index)
# all_stocks_index.to_csv('/home/lxt/data/week_index_359_after.csv')
# 打印结果集
# 初始年 到 去年 的数据
for stock in all_stocks_index:
    rs_query = bs.query_history_k_data_plus(code=stock, fields=fields,
                                            start_date='2020-01-01', end_date=end_date,
                                            frequency='w', adjustflag="2")
    while (rs_query.error_code == '0') & rs_query.next():
        rs_query_list.append(rs_query.get_row_data())


# 列表 转换成 DataFrame
result = pd.DataFrame(rs_query_list, columns=rs_query.fields)
result.to_csv("index_week_k_data.csv", encoding="utf-8", index=False)


# 登出系统
bs.logout()

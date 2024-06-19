"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月20日
"""
import baostock as bs
import pandas as pd
# ===================================================
# 忽略警告
import warnings
warnings.filterwarnings("ignore")
# 设置 DataFrame 输出格式
pd.set_option('display.max_columns', None)   # 显示完整的列
pd.set_option('display.max_rows', None)  # 显示完整的行
pd.set_option('display.expand_frame_repr', False)  # 设置不折叠数据
pd.set_option('display.max_colwidth', 100)  # 设置每列宽度
pd.set_option('display.float_format', '{:.2f}'.format)  # 设置显示2位小数
pd.reset_option('display.float_format')  # 恢复小数原始设置
# ===================================================
# np.set_printoptions(precision=5, linewidth=200, suppress=True)  # numpy 输出设置
# ===================================================
#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 获取历史K线数据 ####
# 详细指标参数，参见“历史行情指标参数”章节
rs = bs.query_history_k_data_plus("sh.000001",
    "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
    start_date='2020-01-01', end_date='2024-05-22',
    frequency="d", adjustflag="3") #frequency="d"取日k线，adjustflag="3"默认不复权
print('query_history_k_data_plus respond error_code:'+rs.error_code)
print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

#### 打印结果集 ####
data_list = []
while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)
#### 结果集输出到csv文件 ####
result.to_csv("history_k_data.csv", encoding="gbk", index=False)
print(result)

#### 登出系统 ####
bs.logout()






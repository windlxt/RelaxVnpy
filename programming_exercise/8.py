"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月29日
"""
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMessageBox
from vnpy_baostock_stock.baostock_stock_datafeed import BaoStockDatafeed, get_previous_year_quarter

date_now = datetime.now()
year, quarter = get_previous_year_quarter(date_now)
print(year, quarter)

# BaoStockDatafeed().baostock_query_stock_growth()
# BaoStockDatafeed().update_increment_quarter_data()






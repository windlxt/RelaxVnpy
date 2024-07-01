"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年06月22日
"""
from pathlib import Path

from vnpy.trader.app import BaseApp

from .stock_filter_engine import APP_NAME, StockFilterEngine


class StockFilterApp(BaseApp):
    """"""

    app_name: str = APP_NAME
    app_module: str = __module__
    app_path: Path = Path(__file__).parent
    display_name: str = "筛选股票"
    engine_class: StockFilterEngine = StockFilterEngine
    widget_name: str = "StockFilterWidget"
    icon_name: str = str(app_path.joinpath("ui", "filter.ico"))


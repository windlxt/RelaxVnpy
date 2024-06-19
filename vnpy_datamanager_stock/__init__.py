"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月28日
"""
from pathlib import Path

from vnpy.trader.app import BaseApp

from .stock_engine_database import APP_NAME, StockManagerEngine


class StockDataManagerApp(BaseApp):
    """"""

    app_name: str = APP_NAME
    app_module: str = __module__
    app_path: Path = Path(__file__).parent
    display_name: str = "数据管理"
    engine_class: StockManagerEngine = StockManagerEngine
    widget_name: str = "StockManagerWidget"
    icon_name: str = str(app_path.joinpath("ui", "manager.ico"))


if __name__ == '__main__':
    a = StockDataManagerApp()
    # __module__是一个内置属性，它表示对象所属的模块。对于PySide6中的QWidget对象，你可以通过访问它的__module__属性来查看它属于哪个模块。
    print(a.app_module)
    
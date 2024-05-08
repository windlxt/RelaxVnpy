"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月07日
"""
import vnpy
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine

from vnpy.trader.ui import TradingPlatformWindow, create_qapp


print(vnpy.__version__)

def main_ui():
    """有图形窗口界面的平台"""
    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)

    trading_platform_window = TradingPlatformWindow(main_engine, event_engine)
    trading_platform_window.show()
    qapp.exec()

def main_no_ui():
    """无窗口"""
    pass


if __name__ == '__main__':
    main_ui()
    # main_no_ui()



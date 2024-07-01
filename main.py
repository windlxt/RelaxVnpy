"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月07日
"""
import os
import subprocess

import vnpy
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui.main_trading_platform_window import TradingPlatformWindow
from vnpy.trader.ui.qt import create_qapp


# from vnpy_paperaccount import PaperAccountApp
from vnpy_ctastrategy import CtaStrategyApp
from vnpy_ctabacktester import CtaBacktesterApp
# from vnpy_spreadtrading import SpreadTradingApp
# from vnpy_algotrading import AlgoTradingApp
# from vnpy_optionmaster import OptionMasterApp
# from vnpy_portfoliostrategy import PortfolioStrategyApp
# from vnpy_scripttrader import ScriptTraderApp
# from vnpy_chartwizard import ChartWizardApp
# from vnpy_rpcservice import RpcServiceApp
# from vnpy_excelrtd import ExcelRtdApp
from vnpy_datamanager import DataManagerApp
# from vnpy_datarecorder import DataRecorderApp
# from vnpy_riskmanager import RiskManagerApp
# from vnpy_webtrader import WebTraderApp
# from vnpy_portfoliomanager import PortfolioManagerApp

from vnpy_datamanager_stock import StockDataManagerApp
from vnpy_filter_backtester_stock import StockFilterApp
from vnpy_stock_chartwizard import StockChartWizardApp


print(vnpy.__version__)
# from pathlib import Path
# print(Path.cwd())


def main_ui():
    """有图形窗口界面的平台"""
    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)

    # main_engine.add_app(PaperAccountApp)
    # main_engine.add_app(CtaStrategyApp)
    # main_engine.add_app(CtaBacktesterApp)
    # main_engine.add_app(SpreadTradingApp)
    # main_engine.add_app(AlgoTradingApp)
    # main_engine.add_app(OptionMasterApp)
    # main_engine.add_app(PortfolioStrategyApp)
    # main_engine.add_app(ScriptTraderApp)
    # main_engine.add_app(ChartWizardApp)
    # main_engine.add_app(RpcServiceApp)
    # main_engine.add_app(ExcelRtdApp)
    # main_engine.add_app(DataManagerApp)
    # main_engine.add_app(DataRecorderApp)
    # main_engine.add_app(RiskManagerApp)
    # main_engine.add_app(WebTraderApp)
    # main_engine.add_app(PortfolioManagerApp)

    # ====以下是股票分析界面 APP =======================================
    main_engine.add_app(StockFilterApp)
    main_engine.add_app(StockChartWizardApp)
    main_engine.add_app(StockDataManagerApp)

    trading_platform_window = TradingPlatformWindow(main_engine, event_engine)
    trading_platform_window.show()

    qapp.exec()


def main_no_ui():
    """无窗口"""
    pass


if __name__ == '__main__':
    # 启动 MongoDB
    p = subprocess.Popen("sh ./start_mongod.sh".split())
    p.wait()
    # 启动主界面
    main_ui()
    # main_no_ui()



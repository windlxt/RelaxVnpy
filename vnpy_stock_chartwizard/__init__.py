
from pathlib import Path

from vnpy.trader.app import BaseApp

from .stock_chart_engine import StockChartWizardEngine, APP_NAME


class StockChartWizardApp(BaseApp):
    """"""
    
    app_name: str = APP_NAME
    app_module: str = __module__
    app_path: Path = Path(__file__).parent
    display_name: str = "股票K线图表"
    engine_class: StockChartWizardEngine = StockChartWizardEngine
    widget_name: str = "StockChartWizardWidget"
    icon_name: str = str(app_path.joinpath("ui", "cw.ico"))

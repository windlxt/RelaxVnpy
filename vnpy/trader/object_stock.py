"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年06月17日
"""
from dataclasses import dataclass, field
from datetime import datetime
from .object import BaseData


@dataclass
class StockHoldingData(BaseData):
    """持有股票数据"""
    date_buy: datetime
    code: str
    exchange: str
    stock_name: str
    logic_buy: str

    price_cost: float = 0
    volume_holding: float = 0
    days_holding: int = 0
    price_current: float = 0
    cost: float = 0
    market_value: float = 0
    profit_loss: float = 0

    def __post_init__(self) -> None:
        """"""
        self.vt_code: str = f"{self.exchange}.{self.code}"

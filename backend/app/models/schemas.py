from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AlertType(str, Enum):
    PRICE_THRESHOLD = "price_threshold"
    PCT_MOVE = "pct_move"


class WSMessageType(str, Enum):
    QUOTE = "quote"
    ALERT = "alert"


class StockQuote(BaseModel):
    ticker: str
    price: float
    open: float
    high: float
    low: float
    volume: int
    change_pct: float = Field(description="Percentage change from daily open")
    market_cap: float | None = None
    pe_ratio: float | None = None
    timestamp: datetime


class HistoryPoint(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockHistory(BaseModel):
    ticker: str
    interval: str
    points: list[HistoryPoint]


class AlertEvent(BaseModel):
    alert_type: AlertType
    message: str
    price: float
    ticker: str
    triggered_at: datetime = Field(default_factory=datetime.now)


class WSMessage(BaseModel):
    type: WSMessageType
    payload: StockQuote | AlertEvent

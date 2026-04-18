import logging

from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.models.schemas import StockHistory, StockQuote
from app.services import stock

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/metrics", response_model=StockQuote)
async def get_metrics(ticker: str = Query(default=None)):
    ticker = ticker or settings.ticker
    try:
        return await stock.fetch_quote(ticker)
    except Exception as exc:
        logger.exception("Failed to fetch metrics for %s", ticker)
        raise HTTPException(status_code=502, detail=f"Upstream data error: {exc}") from exc


@router.get("/history", response_model=StockHistory)
async def get_history(
    ticker: str = Query(default=None),
    interval: str = Query(default=None),
    period: str = Query(default="1d"),
):
    ticker = ticker or settings.ticker
    interval = interval or settings.data_interval
    try:
        return await stock.fetch_history(ticker, interval=interval, period=period)
    except Exception as exc:
        logger.exception("Failed to fetch history for %s", ticker)
        raise HTTPException(status_code=502, detail=f"Upstream data error: {exc}") from exc

import asyncio
import logging
from datetime import datetime, timezone

import yfinance as yf
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

from app.models.schemas import HistoryPoint, StockHistory, StockQuote

logger = logging.getLogger(__name__)

# yfinance raises this on Yahoo rate limits (common on cloud IPs)
_YF_RATE_LIMIT = getattr(yf.exceptions, "YFRateLimitError", Exception)

_RETRY_POLICY = dict(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    retry=(
        retry_if_exception_type(_YF_RATE_LIMIT)
        | retry_if_result(lambda r: r is None)
    ),
    reraise=True,
    before_sleep=lambda rs: logger.warning(
        "yfinance retry #%d after %s", rs.attempt_number, rs.outcome
    ),
)


@retry(**_RETRY_POLICY)
def _fetch_ticker_info(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    info = t.info
    if not info or info.get("regularMarketPrice") is None:
        return None  # type: ignore[return-value]
    return info


@retry(**_RETRY_POLICY)
def _fetch_ticker_history(ticker: str, interval: str, period: str):
    t = yf.Ticker(ticker)
    df = t.history(interval=interval, period=period)
    return df


def _build_quote(ticker: str, info: dict) -> StockQuote:
    price = info.get("regularMarketPrice", 0.0)
    open_price = info.get("regularMarketOpen", price)
    change_pct = ((price - open_price) / open_price * 100) if open_price else 0.0

    return StockQuote(
        ticker=ticker,
        price=price,
        open=open_price,
        high=info.get("regularMarketDayHigh", price),
        low=info.get("regularMarketDayLow", price),
        volume=int(info.get("regularMarketVolume", 0)),
        change_pct=round(change_pct, 4),
        market_cap=info.get("marketCap"),
        pe_ratio=info.get("trailingPE"),
        timestamp=datetime.now(timezone.utc),
    )


async def fetch_quote(ticker: str) -> StockQuote:
    logger.info("Fetching quote for %s", ticker)
    info = await asyncio.to_thread(_fetch_ticker_info, ticker)
    return _build_quote(ticker, info)


async def fetch_history(
    ticker: str, interval: str = "5m", period: str = "1d"
) -> StockHistory:
    logger.info("Fetching history for %s interval=%s period=%s", ticker, interval, period)
    df = await asyncio.to_thread(_fetch_ticker_history, ticker, interval, period)

    # If no data for the requested period (e.g. weekend), widen to 5d
    # and take only the last trading day's data.
    if df is None or df.empty:
        logger.info("No data for period=%s, falling back to 5d", period)
        df = await asyncio.to_thread(_fetch_ticker_history, ticker, interval, "5d")
        if df is not None and not df.empty:
            last_date = df.index[-1].date()
            df = df[df.index.date == last_date]

    points: list[HistoryPoint] = []
    if df is not None:
        for ts, row in df.iterrows():
            points.append(
                HistoryPoint(
                    timestamp=ts.to_pydatetime(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                )
            )

    return StockHistory(ticker=ticker, interval=interval, points=points)

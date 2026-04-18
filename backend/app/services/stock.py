import asyncio
import logging
from datetime import datetime, timezone

import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result

from app.models.schemas import HistoryPoint, StockHistory, StockQuote

logger = logging.getLogger(__name__)


def _is_empty_or_none(result: object) -> bool:
    """Retry predicate: yfinance silently returns empty DataFrames on rate limits."""
    if result is None:
        return True
    if hasattr(result, "empty") and result.empty:
        return True
    return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_result(_is_empty_or_none),
    reraise=True,
)
def _fetch_ticker_info(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    info = t.info
    if not info or info.get("regularMarketPrice") is None:
        return None  # type: ignore[return-value]
    return info


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_result(lambda r: r is None),
    reraise=True,
)
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

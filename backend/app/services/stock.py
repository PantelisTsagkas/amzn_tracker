import asyncio
import logging
from datetime import UTC, datetime

import yfinance as yf
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)
from yfinance.exceptions import YFRateLimitError

from app.models.schemas import HistoryPoint, StockHistory, StockQuote

logger = logging.getLogger(__name__)

_HISTORY_RETRY = dict(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=3, max=25),
    retry=(
        retry_if_exception_type(YFRateLimitError)
        | retry_if_result(lambda r: r is None or (hasattr(r, "empty") and r.empty))
    ),
    reraise=True,
    before_sleep=lambda rs: logger.warning(
        "yfinance history retry #%d after %s", rs.attempt_number, rs.outcome
    ),
)


@retry(**_HISTORY_RETRY)
def _fetch_history_df(ticker: str, interval: str, period: str):
    t = yf.Ticker(ticker)
    return t.history(interval=interval, period=period)


def _try_fetch_info_dict(ticker: str) -> dict | None:
    """Full quote summary from Yahoo. Often rate-limited on cloud/datacenter IPs."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if info and info.get("regularMarketPrice") is not None:
            return info
    except YFRateLimitError as exc:
        logger.warning("yfinance .info rate limited for %s: %s", ticker, exc)
    except Exception:
        logger.exception("yfinance .info failed for %s", ticker)
    return None


def _build_quote_from_info(ticker: str, info: dict) -> StockQuote:
    price = float(info.get("regularMarketPrice", 0.0))
    open_price = float(info.get("regularMarketOpen", price))
    change_pct = ((price - open_price) / open_price * 100) if open_price else 0.0

    return StockQuote(
        ticker=ticker,
        price=price,
        open=open_price,
        high=float(info.get("regularMarketDayHigh", price)),
        low=float(info.get("regularMarketDayLow", price)),
        volume=int(info.get("regularMarketVolume", 0)),
        change_pct=round(change_pct, 4),
        market_cap=info.get("marketCap"),
        pe_ratio=info.get("trailingPE"),
        timestamp=datetime.now(UTC),
    )


def _build_quote_from_intraday_df(ticker: str, df) -> StockQuote:
    """Build quote from OHLCV bars when .info is unavailable (rate limits)."""
    if df is None or df.empty:
        raise ValueError("empty history dataframe")

    last_date = df.index[-1].date()
    day = df[df.index.date == last_date]
    if day.empty:
        day = df

    last = day.iloc[-1]
    first = day.iloc[0]
    price = float(last["Close"])
    open_price = float(first["Open"])
    high = float(day["High"].max())
    low = float(day["Low"].min())
    vol = int(day["Volume"].sum())
    change_pct = ((price - open_price) / open_price * 100) if open_price else 0.0

    return StockQuote(
        ticker=ticker,
        price=price,
        open=open_price,
        high=high,
        low=low,
        volume=vol,
        change_pct=round(change_pct, 4),
        market_cap=None,
        pe_ratio=None,
        timestamp=datetime.now(UTC),
    )


def _fetch_quote_via_history(ticker: str) -> StockQuote:
    """Fallback from OHLCV when .info is blocked (often same path as /history)."""
    df = _fetch_history_df(ticker, "5m", "5d")
    if df is None or df.empty:
        logger.info("No 5m data, trying daily history for %s", ticker)
        df = _fetch_history_df(ticker, "1d", "1mo")
        if df is None or df.empty:
            raise ValueError("no price history from yfinance")
        last = df.iloc[-1]
        o = float(last["Open"])
        c = float(last["Close"])
        return StockQuote(
            ticker=ticker,
            price=c,
            open=o,
            high=float(last["High"]),
            low=float(last["Low"]),
            volume=int(last["Volume"]),
            change_pct=round(((c - o) / o * 100) if o else 0.0, 4),
            market_cap=None,
            pe_ratio=None,
            timestamp=datetime.now(UTC),
        )
    return _build_quote_from_intraday_df(ticker, df)


async def fetch_quote(ticker: str) -> StockQuote:
    logger.info("Fetching quote for %s", ticker)
    info = await asyncio.to_thread(_try_fetch_info_dict, ticker)
    if info:
        return _build_quote_from_info(ticker, info)

    logger.info("Using history-based quote fallback for %s", ticker)
    return await asyncio.to_thread(_fetch_quote_via_history, ticker)


async def fetch_history(
    ticker: str, interval: str = "5m", period: str = "1d"
) -> StockHistory:
    logger.info("Fetching history for %s interval=%s period=%s", ticker, interval, period)
    df = await asyncio.to_thread(_fetch_history_df, ticker, interval, period)

    if df is None or df.empty:
        logger.info("No data for period=%s, falling back to 5d", period)
        df = await asyncio.to_thread(_fetch_history_df, ticker, interval, "5d")
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

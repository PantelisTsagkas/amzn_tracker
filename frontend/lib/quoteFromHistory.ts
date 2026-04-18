import type { HistoryPoint, StockQuote } from "./types";

/**
 * When GET /metrics fails (e.g. yfinance quote path on cloud IPs) but /history succeeds,
 * approximate a quote from the same intraday series so the UI is not stuck on skeletons.
 */
export function quoteFromHistoryPoints(
  ticker: string,
  points: HistoryPoint[],
): StockQuote | null {
  if (points.length === 0) return null;

  const byTime = [...points].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
  );

  const last = byTime[byTime.length - 1];
  const lastDay = new Date(last.timestamp).toDateString();
  const dayPoints = byTime.filter(
    (p) => new Date(p.timestamp).toDateString() === lastDay,
  );
  const day = dayPoints.length > 0 ? dayPoints : byTime;
  const first = day[0];

  const price = last.close;
  const open = first.open;
  const changePct = open ? ((price - open) / open) * 100 : 0;

  let high = -Infinity;
  let low = Infinity;
  let volume = 0;
  for (const p of day) {
    high = Math.max(high, p.high);
    low = Math.min(low, p.low);
    volume += p.volume;
  }

  return {
    ticker,
    price,
    open,
    high,
    low,
    volume,
    change_pct: Math.round(changePct * 10000) / 10000,
    market_cap: null,
    pe_ratio: null,
    timestamp: last.timestamp,
  };
}

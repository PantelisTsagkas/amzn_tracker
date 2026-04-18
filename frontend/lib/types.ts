export interface StockQuote {
  ticker: string;
  price: number;
  open: number;
  high: number;
  low: number;
  volume: number;
  change_pct: number;
  market_cap: number | null;
  pe_ratio: number | null;
  timestamp: string;
}

export interface HistoryPoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StockHistory {
  ticker: string;
  interval: string;
  points: HistoryPoint[];
}

export type AlertType = "price_threshold" | "pct_move";

export interface AlertEvent {
  alert_type: AlertType;
  message: string;
  price: number;
  ticker: string;
  triggered_at: string;
}

export type WSMessageType = "quote" | "alert";

export interface WSMessage {
  type: WSMessageType;
  payload: StockQuote | AlertEvent;
}

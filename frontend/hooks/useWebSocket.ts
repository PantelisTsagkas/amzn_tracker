"use client";

import { useEffect, useRef, useCallback } from "react";
import { useStockStore } from "@/lib/store";
import type { WSMessage, StockQuote } from "@/lib/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";
const BASE_DELAY = 1000;
const MAX_DELAY = 30000;

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const retryCount = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const setQuote = useStockStore((s) => s.setQuote);
  const addHistoryPoint = useStockStore((s) => s.addHistoryPoint);
  const addAlert = useStockStore((s) => s.addAlert);
  const setConnected = useStockStore((s) => s.setConnected);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      retryCount.current = 0;
      setConnected(true);
    };

    ws.onclose = () => {
      setConnected(false);
      const delay = Math.min(BASE_DELAY * 2 ** retryCount.current, MAX_DELAY);
      retryCount.current += 1;
      timerRef.current = setTimeout(connect, delay);
    };

    ws.onerror = () => {
      ws.close();
    };

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);

        if (msg.type === "quote") {
          const quote = msg.payload as StockQuote;
          setQuote(quote);
          addHistoryPoint({
            timestamp: quote.timestamp,
            open: quote.open,
            high: quote.high,
            low: quote.low,
            close: quote.price,
            volume: quote.volume,
          });
        } else if (msg.type === "alert") {
          addAlert(msg.payload as import("@/lib/types").AlertEvent);
        }
      } catch {
        // ignore malformed messages
      }
    };
  }, [setQuote, addHistoryPoint, addAlert, setConnected]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(timerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);
}

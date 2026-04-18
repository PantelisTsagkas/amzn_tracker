"use client";

import { useEffect } from "react";
import { useStockStore } from "@/lib/store";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { StockQuote, StockHistory } from "@/lib/types";

import Header from "@/components/Header";
import MetricsPanel from "@/components/MetricsPanel";
import LiveChart from "@/components/LiveChart";
import AlertBanner from "@/components/AlertBanner";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Dashboard() {
  const setQuote = useStockStore((s) => s.setQuote);
  const setHistory = useStockStore((s) => s.setHistory);

  useWebSocket();

  useEffect(() => {
    async function loadInitial() {
      try {
        const [metricsRes, historyRes] = await Promise.all([
          fetch(`${API_URL}/metrics`),
          fetch(`${API_URL}/history`),
        ]);

        if (metricsRes.ok) {
          const quote: StockQuote = await metricsRes.json();
          setQuote(quote);
        }

        if (historyRes.ok) {
          const history: StockHistory = await historyRes.json();
          setHistory(history.points);
        }
      } catch {
        // backend not yet available — WebSocket will hydrate once connected
      }
    }

    loadInitial();
  }, [setQuote, setHistory]);

  return (
    <div className="flex min-h-screen flex-col bg-zinc-50 dark:bg-zinc-950">
      <Header />
      <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-4 p-4 sm:p-6">
        <AlertBanner />
        <MetricsPanel />
        <LiveChart />
      </main>
      <footer className="border-t border-zinc-200 py-3 text-center text-xs text-zinc-400 dark:border-zinc-800 dark:text-zinc-600">
        AMZN Stock Tracker &middot; Data via yfinance &middot; Not financial advice
      </footer>
    </div>
  );
}

import { create } from "zustand";
import type { AlertEvent, HistoryPoint, StockQuote } from "./types";

const MAX_HISTORY_POINTS = 390;

interface StockState {
  quote: StockQuote | null;
  history: HistoryPoint[];
  alerts: AlertEvent[];
  connected: boolean;

  setQuote: (quote: StockQuote) => void;
  setHistory: (points: HistoryPoint[]) => void;
  addHistoryPoint: (point: HistoryPoint) => void;
  addAlert: (alert: AlertEvent) => void;
  dismissAlert: (index: number) => void;
  setConnected: (connected: boolean) => void;
}

export const useStockStore = create<StockState>((set) => ({
  quote: null,
  history: [],
  alerts: [],
  connected: false,

  setQuote: (quote) => set({ quote }),

  setHistory: (points) =>
    set({ history: points.slice(-MAX_HISTORY_POINTS) }),

  addHistoryPoint: (point) =>
    set((state) => ({
      history: [...state.history, point].slice(-MAX_HISTORY_POINTS),
    })),

  addAlert: (alert) =>
    set((state) => ({ alerts: [alert, ...state.alerts] })),

  dismissAlert: (index) =>
    set((state) => ({
      alerts: state.alerts.filter((_, i) => i !== index),
    })),

  setConnected: (connected) => set({ connected }),
}));

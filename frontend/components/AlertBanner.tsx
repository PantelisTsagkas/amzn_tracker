"use client";

import { useStockStore } from "@/lib/store";
import clsx from "clsx";

export default function AlertBanner() {
  const alerts = useStockStore((s) => s.alerts);
  const dismissAlert = useStockStore((s) => s.dismissAlert);

  if (alerts.length === 0) return null;

  return (
    <div className="flex flex-col gap-2">
      {alerts.map((alert, i) => (
        <div
          key={`${alert.alert_type}-${alert.triggered_at}`}
          className={clsx(
            "flex items-center justify-between rounded-lg border px-4 py-3 text-sm",
            alert.alert_type === "price_threshold"
              ? "border-amber-300 bg-amber-50 text-amber-900 dark:border-amber-700 dark:bg-amber-950/50 dark:text-amber-200"
              : "border-red-300 bg-red-50 text-red-900 dark:border-red-700 dark:bg-red-950/50 dark:text-red-200",
          )}
        >
          <div className="flex items-center gap-2">
            <span className="text-base">
              {alert.alert_type === "price_threshold" ? "⚠" : "📉"}
            </span>
            <span>{alert.message}</span>
          </div>
          <button
            onClick={() => dismissAlert(i)}
            className="ml-4 rounded p-1 opacity-60 transition-opacity hover:opacity-100"
            aria-label="Dismiss alert"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}

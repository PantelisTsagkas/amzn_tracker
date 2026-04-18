"use client";

import { useStockStore } from "@/lib/store";
import clsx from "clsx";

export default function Header() {
  const quote = useStockStore((s) => s.quote);
  const connected = useStockStore((s) => s.connected);

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-zinc-200 dark:border-zinc-800">
      <div className="flex items-center gap-4">
        <span className="inline-flex items-center gap-2 rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-semibold text-white dark:bg-zinc-100 dark:text-zinc-900">
          {quote?.ticker ?? "AMZN"}
        </span>

        {quote && (
          <>
            <span className="text-2xl font-bold tabular-nums tracking-tight">
              ${quote.price.toFixed(2)}
            </span>
            <span
              className={clsx(
                "inline-flex items-center rounded-full px-2.5 py-0.5 text-sm font-medium tabular-nums",
                quote.change_pct >= 0
                  ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-400"
                  : "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-400",
              )}
            >
              {quote.change_pct >= 0 ? "+" : ""}
              {quote.change_pct.toFixed(2)}%
            </span>
          </>
        )}
      </div>

      <div className="flex items-center gap-2 text-sm text-zinc-500 dark:text-zinc-400">
        <span
          className={clsx(
            "inline-block h-2 w-2 rounded-full",
            connected ? "bg-emerald-500" : "bg-red-500",
          )}
        />
        {connected ? "Live" : "Disconnected"}
      </div>
    </header>
  );
}

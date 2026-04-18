"use client";

import { useStockStore } from "@/lib/store";
import clsx from "clsx";

function fmt(n: number | null | undefined, opts?: { currency?: boolean; compact?: boolean }) {
  if (n == null) return "—";
  if (opts?.compact) {
    return Intl.NumberFormat("en-US", {
      notation: "compact",
      maximumFractionDigits: 2,
      ...(opts.currency && { style: "currency", currency: "USD" }),
    }).format(n);
  }
  if (opts?.currency) {
    return Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(n);
  }
  return Intl.NumberFormat("en-US").format(n);
}

interface MetricCardProps {
  label: string;
  value: string;
  accent?: "green" | "red" | "neutral";
}

function MetricCard({ label, value, accent = "neutral" }: MetricCardProps) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
      <p className="text-xs font-medium uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
        {label}
      </p>
      <p
        className={clsx(
          "mt-1 text-xl font-semibold tabular-nums",
          accent === "green" && "text-emerald-600 dark:text-emerald-400",
          accent === "red" && "text-red-600 dark:text-red-400",
          accent === "neutral" && "text-zinc-900 dark:text-zinc-100",
        )}
      >
        {value}
      </p>
    </div>
  );
}

export default function MetricsPanel() {
  const quote = useStockStore((s) => s.quote);

  if (!quote) {
    return (
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="h-20 animate-pulse rounded-xl border border-zinc-200 bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900"
          />
        ))}
      </div>
    );
  }

  const accent = quote.change_pct >= 0 ? "green" : "red";

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      <MetricCard label="Price" value={fmt(quote.price, { currency: true })!} />
      <MetricCard label="Open" value={fmt(quote.open, { currency: true })!} />
      <MetricCard
        label="Change"
        value={`${quote.change_pct >= 0 ? "+" : ""}${quote.change_pct.toFixed(2)}%`}
        accent={accent}
      />
      <MetricCard label="Market Cap" value={fmt(quote.market_cap, { currency: true, compact: true })!} />
      <MetricCard label="P/E Ratio" value={quote.pe_ratio != null ? quote.pe_ratio.toFixed(2) : "—"} />
      <MetricCard label="Volume" value={fmt(quote.volume, { compact: true })!} />
    </div>
  );
}

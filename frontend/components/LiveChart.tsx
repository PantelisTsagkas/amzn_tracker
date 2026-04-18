"use client";

import { useStockStore } from "@/lib/store";
import { format } from "date-fns";
import { useMemo } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function formatPrice(v: number) {
  return `$${v.toFixed(2)}`;
}

export default function LiveChart() {
  const history = useStockStore((s) => s.history);
  const quote = useStockStore((s) => s.quote);

  const data = useMemo(
    () =>
      history.map((p) => ({
        time: new Date(p.timestamp).getTime(),
        price: p.close,
      })),
    [history],
  );

  const isPositive = (quote?.change_pct ?? 0) >= 0;
  const strokeColor = isPositive ? "#10b981" : "#ef4444";
  const fillColor = isPositive ? "#10b98133" : "#ef444433";

  if (data.length === 0) {
    return (
      <div className="flex h-72 items-center justify-center rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
        <p className="text-sm text-zinc-400">Waiting for data...</p>
      </div>
    );
  }

  const prices = data.map((d) => d.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const padding = (maxPrice - minPrice) * 0.1 || 1;

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="mb-3 text-sm font-medium text-zinc-500 dark:text-zinc-400">
        Intraday Price
      </h2>
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={strokeColor} stopOpacity={0.3} />
              <stop offset="100%" stopColor={strokeColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="currentColor"
            className="text-zinc-200 dark:text-zinc-800"
          />
          <XAxis
            dataKey="time"
            type="number"
            domain={["dataMin", "dataMax"]}
            scale="time"
            tickFormatter={(v: number) => format(new Date(v), "HH:mm")}
            tick={{ fontSize: 11 }}
            stroke="currentColor"
            className="text-zinc-400"
          />
          <YAxis
            domain={[minPrice - padding, maxPrice + padding]}
            tickFormatter={formatPrice}
            tick={{ fontSize: 11 }}
            width={72}
            stroke="currentColor"
            className="text-zinc-400"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--background)",
              border: "1px solid var(--foreground, #e4e4e7)",
              borderRadius: 8,
              fontSize: 13,
            }}
            labelFormatter={(v) =>
              format(new Date(v as number), "MMM d, HH:mm:ss")
            }
            formatter={(value) => [formatPrice(value as number), "Price"]}
          />
          <Area
            type="monotone"
            dataKey="price"
            stroke={strokeColor}
            strokeWidth={2}
            fill="url(#priceGrad)"
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

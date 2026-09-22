import React, { useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { TrendingUp } from 'lucide-react';
import type { SalesTrendPoint } from '../../types/sales';

export interface SalesTrendChartProps {
  data: SalesTrendPoint[];
}

function formatYAxisValue(val: number, mode: 'value' | 'count'): string {
  if (mode === 'count') return val.toString();
  if (val === 0) return '0';
  if (val >= 10000000) return `${(val / 10000000).toFixed(1)}Cr`;
  if (val >= 100000) return `${(val / 100000).toFixed(val % 100000 === 0 ? 0 : 1)}L`;
  if (val >= 1000) return `${(val / 1000).toFixed(0)}K`;
  return val.toString();
}

function formatTooltipCurrency(val: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val);
}

export const SalesTrendChart: React.FC<SalesTrendChartProps> = ({ data }) => {
  const [toggleMode, setToggleMode] = useState<'value' | 'count'>('value');

  const chartData = data.map((d) => ({
    label: d.label,
    value: toggleMode === 'value' ? d.sales_value : d.order_count,
    date: d.date,
  }));

  const hasData = data.length > 0 && data.some((d) => (toggleMode === 'value' ? d.sales_value > 0 : d.order_count > 0));

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-xs border border-slate-200/80 dark:border-slate-800 transition-colors flex flex-col justify-between">
      {/* Card Header */}
      <div className="flex items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">Sales Trend</h2>
        </div>

        {/* Toggle Dropdown */}
        <div className="relative">
          <select
            id="sales-trend-toggle"
            aria-label="Sales Trend View Toggle"
            value={toggleMode}
            onChange={(e) => setToggleMode(e.target.value as 'value' | 'count')}
            className="h-8 pl-3 pr-7 text-xs font-semibold bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer"
          >
            <option value="value">Sales Value</option>
            <option value="count">Order Count</option>
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
            <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Recharts Area */}
      <div className="w-full h-56 min-h-[224px]">
        {hasData ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
              <defs>
                <linearGradient id="salesTrendGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" strokeOpacity={0.6} />
              <XAxis
                dataKey="label"
                tickLine={false}
                axisLine={false}
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                interval="preserveStartEnd"
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                tickFormatter={(val) => formatYAxisValue(val, toggleMode)}
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const pointVal = payload[0].value as number;
                    return (
                      <div className="bg-white dark:bg-slate-800 p-2.5 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 text-xs">
                        <div className="font-semibold text-slate-500 dark:text-slate-400 mb-1">{label}</div>
                        <div className="font-bold text-blue-600 dark:text-blue-400 text-sm">
                          {toggleMode === 'value'
                            ? formatTooltipCurrency(pointVal)
                            : `${pointVal} ${pointVal === 1 ? 'Order' : 'Orders'}`}
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#2563eb"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#salesTrendGrad)"
                activeDot={{ r: 5, fill: '#2563eb', stroke: '#ffffff', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 text-xs">
            <span>No sales trend data in this period</span>
          </div>
        )}
      </div>
    </div>
  );
};

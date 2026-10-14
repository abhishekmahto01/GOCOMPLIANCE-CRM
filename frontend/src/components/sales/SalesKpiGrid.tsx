import React from 'react';
import {
  BarChart3,
  ClipboardCheck,
  IndianRupee,
  Clock,
  TrendingUp,
  Users,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import type { SalesKpiSummary, KpiMetric } from '../../types/sales';

export interface SalesKpiGridProps {
  kpis: SalesKpiSummary;
}

interface KpiCardProps {
  title: string;
  metric: KpiMetric;
  icon: React.ReactNode;
  iconBgClass: string;
  isInverseTrend?: boolean; // For outstanding, increase is negative
}

const getValueFontSize = (val: string) => {
  const len = val?.length || 0;
  if (len > 13) return 'text-base sm:text-lg xl:text-lg 2xl:text-xl';
  if (len > 10) return 'text-lg sm:text-xl xl:text-xl 2xl:text-2xl';
  if (len > 7) return 'text-xl sm:text-2xl xl:text-2xl 2xl:text-[26px]';
  return 'text-2xl sm:text-3xl xl:text-[26px] 2xl:text-3xl';
};

const KpiCard: React.FC<KpiCardProps> = ({
  title,
  metric,
  icon,
  iconBgClass,
  isInverseTrend = false,
}) => {
  const isPositive = isInverseTrend ? metric.percentage_change <= 0 : metric.percentage_change >= 0;
  const trendArrow = metric.percentage_change >= 0 ? (
    <ArrowUpRight className="w-3.5 h-3.5 shrink-0" />
  ) : (
    <ArrowDownRight className="w-3.5 h-3.5 shrink-0" />
  );

  const displayValue = metric.formatted_value || '0';

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-4 sm:p-4.5 shadow-xs border border-slate-200/80 dark:border-slate-800 transition-all hover:shadow-md flex flex-col justify-between min-w-0 overflow-hidden">
      <div className="flex items-start justify-between gap-2">
        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 truncate" title={title}>
          {title}
        </span>
        <div className={`p-2 sm:p-2.5 rounded-xl shrink-0 ${iconBgClass}`}>{icon}</div>
      </div>

      <div className="mt-3 min-w-0">
        <div
          className={`font-bold text-slate-900 dark:text-white tracking-tight truncate ${getValueFontSize(displayValue)}`}
          title={displayValue}
        >
          {displayValue}
        </div>

        <div className="mt-2.5 flex items-center gap-1.5 text-xs min-w-0">
          <span
            className={`inline-flex items-center gap-0.5 font-semibold shrink-0 ${
              isPositive
                ? 'text-emerald-600 dark:text-emerald-400'
                : 'text-rose-600 dark:text-rose-400'
            }`}
          >
            {trendArrow}
            {Math.abs(metric.percentage_change)}%
          </span>
          <span
            className="text-slate-400 dark:text-slate-500 font-medium truncate"
            title={metric.comparison_label || 'vs last month'}
          >
            {metric.comparison_label || 'vs last month'}
          </span>
        </div>
      </div>
    </div>
  );
};

export const SalesKpiGrid: React.FC<SalesKpiGridProps> = ({ kpis }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {/* 1. Total Sales */}
      <KpiCard
        title="Total Sales"
        metric={kpis.total_sales}
        icon={<BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />}
        iconBgClass="bg-blue-50 dark:bg-blue-950/50"
      />

      {/* 2. Confirmed Orders */}
      <KpiCard
        title="Confirmed Orders"
        metric={kpis.confirmed_orders}
        icon={<ClipboardCheck className="w-5 h-5 text-purple-600 dark:text-purple-400" />}
        iconBgClass="bg-purple-50 dark:bg-purple-950/50"
      />

      {/* 3. Amount Received */}
      <KpiCard
        title="Amount Received"
        metric={kpis.amount_received}
        icon={<IndianRupee className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />}
        iconBgClass="bg-emerald-50 dark:bg-emerald-950/50"
      />

      {/* 4. Outstanding */}
      <KpiCard
        title="Outstanding"
        metric={kpis.outstanding}
        icon={<Clock className="w-5 h-5 text-amber-600 dark:text-amber-400" />}
        iconBgClass="bg-amber-50 dark:bg-amber-950/50"
        isInverseTrend={true}
      />

      {/* 5. Avg. Order Value */}
      <KpiCard
        title="Avg. Order Value"
        metric={kpis.avg_order_value}
        icon={<TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />}
        iconBgClass="bg-blue-50 dark:bg-blue-950/50"
      />

      {/* 6. Total Clients */}
      <KpiCard
        title="Total Clients"
        metric={kpis.total_clients}
        icon={<Users className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />}
        iconBgClass="bg-indigo-50 dark:bg-indigo-950/50"
      />
    </div>
  );
};

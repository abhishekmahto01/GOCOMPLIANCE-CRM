import React from 'react';
import { BarChart3 } from 'lucide-react';
import type { ServiceSalesItem } from '../../types/sales';

export interface SalesLicenceBarChartProps {
  data: ServiceSalesItem[];
}

function formatInr(val: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val);
}

export const SalesLicenceBarChart: React.FC<SalesLicenceBarChartProps> = ({ data }) => {
  const maxVal = data.reduce((acc, curr) => Math.max(acc, curr.total_sales), 0);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-xs border border-slate-200/80 dark:border-slate-800 transition-colors flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">License-wise Sales</h2>
      </div>

      <div className="flex-1 flex flex-col justify-center space-y-3.5 h-56 min-h-[224px]">
        {data.length > 0 ? (
          data.slice(0, 5).map((item) => {
            const pct = maxVal > 0 ? Math.round((item.total_sales / maxVal) * 100) : 0;
            return (
              <div key={item.service_id} className="flex items-center gap-3 text-xs">
                {/* Service Name Label */}
                <div className="w-28 sm:w-32 font-medium text-slate-700 dark:text-slate-300 truncate" title={item.service_name}>
                  {item.service_name}
                </div>

                {/* Progress Bar Container */}
                <div className="flex-1 h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden relative">
                  <div
                    className="h-full bg-blue-600 dark:bg-blue-500 rounded-full transition-all duration-500"
                    style={{ width: `${Math.max(pct, item.total_sales > 0 ? 6 : 0)}%` }}
                  />
                </div>

                {/* Amount */}
                <div className="w-20 text-right font-semibold text-slate-800 dark:text-slate-200 shrink-0">
                  {formatInr(item.total_sales)}
                </div>
              </div>
            );
          })
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 text-xs">
            <span>No service sales in this period</span>
          </div>
        )}
      </div>
    </div>
  );
};

import React from 'react';
import { Users } from 'lucide-react';
import type { TeamPerformanceRow } from '../../types/sales';

export interface SalesTeamTableProps {
  rows: TeamPerformanceRow[];
}

function formatInr(val: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val);
}

export const SalesTeamTable: React.FC<SalesTeamTableProps> = ({ rows }) => {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-xs border border-slate-200/80 dark:border-slate-800 transition-colors">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">
          Sales Team Performance
        </h2>
      </div>

      {/* Table with horizontal scroll support */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs sm:text-sm">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              <th scope="col" className="py-3 px-3">SALESPERSON</th>
              <th scope="col" className="py-3 px-3 text-center">ORDERS</th>
              <th scope="col" className="py-3 px-3 text-right">TOTAL SALES</th>
              <th scope="col" className="py-3 px-3 text-right">RECEIVED</th>
              <th scope="col" className="py-3 px-3 text-right">OUTSTANDING</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
            {rows.length > 0 ? (
              rows.map((row) => (
                <tr
                  key={row.salesperson_id}
                  className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors"
                >
                  <td className="py-3.5 px-3 font-semibold text-slate-800 dark:text-slate-200">
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-950/70 text-blue-600 dark:text-blue-400 font-bold text-xs flex items-center justify-center shrink-0">
                        {row.salesperson_name.charAt(0).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <div className="truncate font-semibold">{row.salesperson_name}</div>
                        <div className="text-[11px] text-slate-400 font-normal">{row.employee_code}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 px-3 text-center font-semibold text-slate-700 dark:text-slate-300">
                    {row.orders_count}
                  </td>
                  <td className="py-3.5 px-3 text-right font-bold text-slate-900 dark:text-white">
                    {formatInr(row.total_sales)}
                  </td>
                  <td className="py-3.5 px-3 text-right font-semibold text-emerald-600 dark:text-emerald-400">
                    {formatInr(row.amount_received)}
                  </td>
                  <td className="py-3.5 px-3 text-right font-semibold text-amber-600 dark:text-amber-400">
                    {formatInr(row.outstanding)}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="py-8 text-center text-slate-400 dark:text-slate-500 text-xs">
                  No sales team performance recorded in this period
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

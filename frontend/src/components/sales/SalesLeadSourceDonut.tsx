import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { Megaphone } from 'lucide-react';
import type { LeadSourcesBreakdown } from '../../types/sales';

export interface SalesLeadSourceDonutProps {
  data: LeadSourcesBreakdown;
}

const COLOR_MAP: Record<string, string> = {
  WEBSITE: '#1e3a8a', // dark blue
  REFERRAL: '#38bdf8', // sky blue
  DIRECT: '#f97316', // orange
  OTHERS: '#a855f7', // purple
};

export const SalesLeadSourceDonut: React.FC<SalesLeadSourceDonutProps> = ({ data }) => {
  const { total_leads, items } = data;
  const hasLeads = total_leads > 0;

  const chartSlices = hasLeads
    ? items.filter((it) => it.count > 0).map((it) => ({
        name: it.label,
        value: it.count,
        color: COLOR_MAP[it.source] || '#94a3b8',
        percentage: it.percentage,
      }))
    : [{ name: 'No Leads', value: 1, color: '#e2e8f0', percentage: 0 }];

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-xs border border-slate-200/80 dark:border-slate-800 transition-colors flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <Megaphone className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">Lead Sources</h2>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 h-56 min-h-[224px]">
        {/* Donut Chart with Centered Metric */}
        <div className="relative w-44 h-44 shrink-0 flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartSlices}
                cx="50%"
                cy="50%"
                innerRadius={48}
                outerRadius={68}
                paddingAngle={hasLeads ? 3 : 0}
                dataKey="value"
                stroke="none"
              >
                {chartSlices.map((entry, index) => (
                  <Cell key={`cell-lead-${index}`} fill={entry.color} />
                ))}
              </Pie>
              {hasLeads && (
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-white dark:bg-slate-800 p-2 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-800 dark:text-slate-100">
                          <div>{d.name}</div>
                          <div className="text-blue-600 dark:text-blue-400">
                            {d.value} leads ({d.percentage}%)
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              )}
            </PieChart>
          </ResponsiveContainer>

          {/* Centered Total Count */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center">
            <span className="text-xl font-extrabold text-slate-900 dark:text-white leading-tight">
              {total_leads}
            </span>
            <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
              Leads
            </span>
          </div>
        </div>

        {/* Legend List on Right */}
        <div className="flex-1 w-full space-y-2 text-xs">
          {items.map((item) => {
            const dotColor = COLOR_MAP[item.source] || '#94a3b8';
            return (
              <div key={item.source} className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: dotColor }}
                  />
                  <span className="font-medium text-slate-700 dark:text-slate-300 truncate">
                    {item.label}
                  </span>
                </div>
                <div className="font-semibold text-slate-800 dark:text-slate-200 shrink-0">
                  {item.count} <span className="text-slate-400 font-normal">({item.percentage}%)</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

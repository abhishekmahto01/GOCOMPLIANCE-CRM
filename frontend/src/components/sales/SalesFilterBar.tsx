import { RotateCcw, Download, Calendar } from 'lucide-react';
import type { SalesFilterOptions, SalesDashboardFilterParams } from '../../types/sales';

export interface SalesFilterBarProps {
  filters: SalesDashboardFilterParams;
  filterOptions: SalesFilterOptions;
  dateDisplay: {
    formatted_from: string;
    formatted_to: string;
    from_date?: string;
    to_date?: string;
  };
  onFilterChange: (newFilters: Partial<SalesDashboardFilterParams>) => void;
  onReset: () => void;
  onExport: () => void;
  isExporting?: boolean;
}

const PRESET_OPTIONS = [
  { id: 'today', label: 'Today' },
  { id: 'this_week', label: 'This Week' },
  { id: 'this_month', label: 'This Month' },
  { id: 'this_quarter', label: 'This Quarter' },
  { id: 'this_year', label: 'This Year' },
  { id: 'custom', label: 'Custom' },
];

export const SalesFilterBar: React.FC<SalesFilterBarProps> = ({
  filters,
  filterOptions,
  dateDisplay,
  onFilterChange,
  onReset,
  onExport,
  isExporting = false,
}) => {
  const currentPreset = filters.preset || 'this_month';

  return (
    <div className="w-full bg-white dark:bg-slate-900 rounded-2xl p-4 shadow-sm border border-slate-200/80 dark:border-slate-800 transition-colors">
      <div className="flex flex-wrap items-center gap-3">
        {/* Preset Selector */}
        <div className="relative min-w-[140px]">
          <select
            id="preset-selector"
            aria-label="Preset Date Selector"
            value={currentPreset}
            onChange={(e) => {
              const val = e.target.value;
              if (val === 'custom') {
                onFilterChange({
                  preset: 'custom',
                  from_date: filters.from_date || dateDisplay.from_date,
                  to_date: filters.to_date || dateDisplay.to_date,
                });
              } else {
                onFilterChange({
                  preset: val,
                  from_date: undefined,
                  to_date: undefined,
                });
              }
            }}
            className="w-full h-10 pl-3 pr-8 text-xs sm:text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer"
          >
            {PRESET_OPTIONS.map((opt) => (
              <option key={opt.id} value={opt.id}>
                {opt.label}
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-400">
            <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
            </svg>
          </div>
        </div>

        {/* From Date */}
        <div className="relative min-w-[140px] flex-1 sm:flex-initial">
          <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-0.5 sm:hidden">From Date</div>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 flex items-center pl-2.5 pointer-events-none text-slate-400">
              <Calendar className="w-3.5 h-3.5" />
            </span>
            <input
              type="date"
              id="from-date-input"
              aria-label="From Date"
              value={filters.from_date || dateDisplay.from_date || ''}
              onChange={(e) => onFilterChange({ preset: 'custom', from_date: e.target.value })}
              onClick={(e) => {
                try {
                  (e.currentTarget as HTMLInputElement).showPicker?.();
                } catch (_) {}
              }}
              className="w-full h-10 pl-8 pr-2 text-xs sm:text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            />
          </div>
        </div>

        {/* To Date */}
        <div className="relative min-w-[140px] flex-1 sm:flex-initial">
          <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-0.5 sm:hidden">To Date</div>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 flex items-center pl-2.5 pointer-events-none text-slate-400">
              <Calendar className="w-3.5 h-3.5" />
            </span>
            <input
              type="date"
              id="to-date-input"
              aria-label="To Date"
              value={filters.to_date || dateDisplay.to_date || ''}
              onChange={(e) => onFilterChange({ preset: 'custom', to_date: e.target.value })}
              onClick={(e) => {
                try {
                  (e.currentTarget as HTMLInputElement).showPicker?.();
                } catch (_) {}
              }}
              className="w-full h-10 pl-8 pr-2 text-xs sm:text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            />
          </div>
        </div>

        {/* Employee Filter */}
        <div className="relative min-w-[150px] flex-1 sm:flex-initial">
          <select
            id="employee-filter"
            aria-label="Sales Employee Filter"
            disabled={!filterOptions.can_filter_employees}
            value={filters.employee_id || 'ALL'}
            onChange={(e) => onFilterChange({ employee_id: e.target.value })}
            className={`w-full h-10 pl-3 pr-8 text-xs sm:text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none ${
              !filterOptions.can_filter_employees ? 'opacity-75 cursor-not-allowed bg-slate-100 dark:bg-slate-800/50' : 'cursor-pointer'
            }`}
          >
            {filterOptions.can_filter_employees && (
              <option value="ALL">All Salespersons</option>
            )}
            {filterOptions.employees.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.label}
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-400">
            <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
            </svg>
          </div>
        </div>

        {/* Service Filter */}
        <div className="relative min-w-[140px] flex-1 sm:flex-initial">
          <select
            id="service-filter"
            aria-label="Service Filter"
            value={filters.service_id || 'ALL'}
            onChange={(e) => onFilterChange({ service_id: e.target.value })}
            className="w-full h-10 pl-3 pr-8 text-xs sm:text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer"
          >
            <option value="ALL">All Licences</option>
            {filterOptions.services.map((srv) => (
              <option key={srv.id} value={srv.id}>
                {srv.label}
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-400">
            <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
            </svg>
          </div>
        </div>

        {/* Lead Source Filter */}
        <div className="relative min-w-[130px] flex-1 sm:flex-initial">
          <select
            id="lead-source-filter"
            aria-label="Lead Source Filter"
            value={filters.lead_source || 'ALL'}
            onChange={(e) => onFilterChange({ lead_source: e.target.value })}
            className="w-full h-10 pl-3 pr-8 text-xs sm:text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer"
          >
            <option value="ALL">All Lead Sources</option>
            {filterOptions.lead_sources.map((ls) => (
              <option key={ls.id} value={ls.id}>
                {ls.label}
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-400">
            <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
            </svg>
          </div>
        </div>

        {/* Payment Status Filter */}
        <div className="relative min-w-[130px] flex-1 sm:flex-initial">
          <select
            id="payment-status-filter"
            aria-label="Payment Status Filter"
            value={filters.payment_status || 'ALL'}
            onChange={(e) => onFilterChange({ payment_status: e.target.value })}
            className="w-full h-10 pl-3 pr-8 text-xs sm:text-sm font-medium bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer"
          >
            <option value="ALL">All Payment Statuses</option>
            {filterOptions.payment_statuses.map((ps) => (
              <option key={ps.id} value={ps.id}>
                {ps.label}
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-400">
            <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
            </svg>
          </div>
        </div>

        {/* Action Buttons: Reset & Export */}
        <div className="flex items-center gap-2 ml-auto">
          <button
            type="button"
            id="sales-reset-filters-btn"
            onClick={onReset}
            className="h-10 px-3.5 flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition border border-slate-200/80 dark:border-slate-700"
            title="Reset Filters"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>

          <button
            type="button"
            id="sales-export-btn"
            disabled={isExporting}
            onClick={onExport}
            className="h-10 px-4 flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 active:scale-98 rounded-xl shadow-sm hover:shadow transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isExporting ? 'Exporting...' : 'Export'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

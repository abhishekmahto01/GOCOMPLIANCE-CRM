import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Receipt,
  CreditCard,
  Building2,
  Clock,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  FileSpreadsheet,
  PlusCircle,
  Filter,
  CheckCircle2,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { getAccountsDashboardApi } from '../../api/accounts';
import type { AccountsDashboardResponse } from '../../types/accounts';
import { Button } from '../../components/ui/button';

export const AccountsDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<AccountsDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [preset, setPreset] = useState<string>('this_month');
  const [fromDate, setFromDate] = useState<string>('');
  const [toDate, setToDate] = useState<string>('');
  const [companyId, setCompanyId] = useState<string>('ALL');
  const [employeeId, setEmployeeId] = useState<string>('ALL');

  const fetchDashboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getAccountsDashboardApi({
        preset,
        from_date: preset === 'custom' && fromDate ? fromDate : undefined,
        to_date: preset === 'custom' && toDate ? toDate : undefined,
        company_id: companyId,
        employee_id: employeeId,
      });
      setData(res);
    } catch (err: any) {
      console.error('Failed to load accounts dashboard:', err);
      setError(err?.response?.data?.detail || 'Failed to load financial dashboard. Please check permissions.');
    } finally {
      setIsLoading(false);
    }
  }, [preset, fromDate, toDate, companyId, employeeId]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const kpis = data?.kpis;
  const filterOptions = data?.filter_options;

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Top Banner Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-[#0a2569] via-indigo-900 to-blue-900 text-white shadow-xl relative overflow-hidden">
        {/* Ambient shapes */}
        <div className="absolute -right-10 -bottom-10 w-72 h-72 rounded-full bg-white/5 blur-3xl pointer-events-none" />
        <div className="absolute top-0 right-1/4 w-48 h-48 rounded-full bg-indigo-500/10 blur-2xl pointer-events-none" />

        <div className="relative z-10 space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-bold text-indigo-200 border border-white/10">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>Accounts & Financial Control Center</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Financial Health & Collections
          </h1>
          <p className="text-xs sm:text-sm text-indigo-200 max-w-2xl leading-relaxed">
            Real-time audit-safe tracking of confirmed order liabilities, verified collections, debtor ageing, and direct operational outlays.
          </p>
        </div>

        <div className="relative z-10 flex flex-wrap items-center gap-2.5">
          <Link to="/accounts/payments">
            <Button
              variant="primary"
              size="sm"
              className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-xs shadow-md flex items-center gap-1.5"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Record Payment</span>
            </Button>
          </Link>

          <Link to="/accounts/outstanding">
            <Button
              variant="outline"
              size="sm"
              className="bg-white/10 hover:bg-white/20 text-white border-white/20 backdrop-blur-md rounded-xl text-xs font-semibold flex items-center gap-1.5"
            >
              <Clock className="w-4 h-4" />
              <span>Debtors Ageing</span>
            </Button>
          </Link>
          <Link to="/accounts/reports">
            <Button
              variant="outline"
              size="sm"
              className="bg-white/10 hover:bg-white/20 text-white border-white/20 backdrop-blur-md rounded-xl text-xs font-semibold flex items-center gap-1.5"
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>Reports</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 dark:text-slate-400 mr-1">
            <Filter className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <span>Scope:</span>
          </div>

          {/* Preset Range */}
          <select
            aria-label="Filter Preset"
            value={preset}
            onChange={(e) => setPreset(e.target.value)}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
          >
            <option value="today">Today</option>
            <option value="this_week">This Week</option>
            <option value="this_month">This Month</option>
            <option value="this_quarter">This Quarter</option>
            <option value="this_year">This Financial Year</option>
            <option value="all_time">All Time</option>
            <option value="custom">Custom Date Range</option>
          </select>

          {/* Custom Date Pickers */}
          {preset === 'custom' && (
            <div className="flex items-center gap-1.5">
              <input
                type="date"
                aria-label="From Date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                className="px-2.5 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200"
              />
              <span className="text-slate-400 text-xs font-semibold">to</span>
              <input
                type="date"
                aria-label="To Date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                className="px-2.5 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200"
              />
            </div>
          )}

          {/* Company Filter */}
          {filterOptions && filterOptions.companies.length > 0 && (
            <select
              aria-label="Company Filter"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 max-w-[180px] truncate"
            >
              <option value="ALL">All Companies</option>
              {filterOptions.companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                </option>
              ))}
            </select>
          )}

          {/* Salesperson Filter */}
          {filterOptions && filterOptions.salespersons.length > 0 && (
            <select
              aria-label="Salesperson Filter"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 max-w-[180px] truncate"
            >
              <option value="ALL">All Salespersons</option>
              {filterOptions.salespersons.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          )}
        </div>

        <button
          onClick={fetchDashboard}
          disabled={isLoading}
          className="p-2 text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors disabled:opacity-50"
          title="Refresh Data"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 flex items-center gap-3 text-xs sm:text-sm">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Main KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Confirmed Order Value */}
        <div
          onClick={() => navigate('/accounts/payments')}
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-indigo-300 dark:hover:border-indigo-700 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Confirmed Order Value
            </span>
            <div className="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform">
              <Receipt className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2">
            {kpis ? kpis.formatted_confirmed_order_value : '₹0.00'}
          </div>
          <div className="flex items-center justify-between text-[11px] mt-2 text-slate-500 dark:text-slate-400">
            <span>{kpis ? `${kpis.confirmed_order_count} orders` : '0 orders'}</span>
            <span className="text-[10px] bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full font-semibold text-slate-500">
              📅 By Order Date
            </span>
          </div>
        </div>

        {/* KPI 2: Verified Collections */}
        <div
          onClick={() => navigate('/accounts/payments')}
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-emerald-300 dark:hover:border-emerald-700 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Verified Collections
            </span>
            <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 group-hover:scale-110 transition-transform">
              <CreditCard className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-2">
            {kpis ? kpis.formatted_verified_collections : '₹0.00'}
          </div>
          <div className="flex items-center justify-between text-[11px] mt-2 text-slate-500 dark:text-slate-400">
            <span className="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-0.5">
              <CheckCircle2 className="w-3 h-3" /> {kpis ? `${kpis.verified_collections_count} receipts` : '0 receipts'}
            </span>
            <span className="text-[10px] bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 px-2 py-0.5 rounded-full font-semibold border border-emerald-200 dark:border-emerald-800">
              💳 By Payment Date
            </span>
          </div>
        </div>

        {/* KPI 3: Current Outstanding */}
        <div
          onClick={() => navigate('/accounts/outstanding')}
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-amber-300 dark:hover:border-amber-700 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Current Outstanding
            </span>
            <div className="p-2.5 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-2">
            {kpis ? kpis.formatted_current_outstanding : '₹0.00'}
          </div>
          <div className="flex items-center justify-between text-[11px] mt-2 text-slate-500 dark:text-slate-400">
            <span>{kpis ? `${kpis.outstanding_orders_count} pending orders` : '0 orders'}</span>
            <span className="text-[10px] bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 px-2 py-0.5 rounded-full font-semibold border border-amber-200 dark:border-amber-800">
              ⏳ As of Today
            </span>
          </div>
        </div>

        {/* KPI 4: Overdue Receivables */}
        <div
          onClick={() => navigate('/accounts/outstanding?ageing_bucket=1_30_DAYS')}
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-rose-300 dark:hover:border-rose-700 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Overdue Receivables
            </span>
            <div className="p-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 group-hover:scale-110 transition-transform">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-rose-600 dark:text-rose-400 mt-2">
            {kpis ? kpis.formatted_current_overdue : '₹0.00'}
          </div>
          <div className="flex items-center justify-between text-[11px] mt-2 text-slate-500 dark:text-slate-400">
            <span className="text-rose-600 font-semibold">{kpis ? `${kpis.overdue_orders_count} overdue orders` : '0 orders'}</span>
            <span className="text-[10px] bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 px-2 py-0.5 rounded-full font-semibold border border-rose-200 dark:border-rose-800">
              🚨 Past Due Date
            </span>
          </div>
        </div>
      </div>

      {/* Secondary Metrics Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Unverified Submissions */}
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Unverified Payments</div>
            <div className="text-lg font-extrabold text-blue-600 dark:text-blue-400 mt-0.5">
              {kpis ? kpis.formatted_unverified_collections : '₹0.00'}
            </div>
            <div className="text-[11px] text-slate-500">
              {kpis?.unverified_collections_count || 0} collections awaiting approval
            </div>
          </div>
          <Link to="/accounts/payments">
            <Button size="sm" variant="ghost" className="text-xs text-blue-600 hover:bg-blue-50 font-semibold rounded-xl">
              Verify
            </Button>
          </Link>
        </div>

        {/* Direct Expenses */}
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Direct Operational Costs</div>
            <div className="text-lg font-extrabold text-purple-600 dark:text-purple-400 mt-0.5">
              {kpis ? kpis.formatted_recorded_direct_costs : '₹0.00'}
            </div>
            <div className="text-[11px] text-slate-500">
              Govt fees, vendor & incidentals
            </div>
          </div>
          <Link to="/accounts/expenses">
            <Button size="sm" variant="ghost" className="text-xs text-purple-600 hover:bg-purple-50 font-semibold rounded-xl">
              View
            </Button>
          </Link>
        </div>

        {/* Estimated Order Margin */}
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Estimated Order Margin</div>
            <div className="text-lg font-extrabold text-slate-800 dark:text-slate-100 mt-0.5">
              {kpis ? kpis.formatted_estimated_order_margin : '₹0.00'}
            </div>
            <div className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold">
              {kpis ? `${kpis.margin_percentage.toFixed(1)}% estimated margin` : '0%'}
            </div>
          </div>
          <span className="text-[10px] bg-slate-200/80 dark:bg-slate-800 px-2 py-1 rounded-lg text-slate-600 font-mono">
            Commercial Est.
          </span>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Collections Over Time Trend Chart */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-xs border border-slate-200/80 dark:border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">Verified Collections Over Time</h2>
            </div>
            <span className="text-xs font-semibold text-slate-400">
              {data?.date_range ? `${data.date_range.from_date} to ${data.date_range.to_date}` : ''}
            </span>
          </div>

          <div className="h-64 w-full">
            {data && data.collections_trend.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.collections_trend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorAccountsCollections" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#4f46e5" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="label" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis
                    stroke="#94a3b8"
                    fontSize={11}
                    tickLine={false}
                    tickFormatter={(val) => (val >= 100000 ? `${(val / 100000).toFixed(0)}L` : val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val)}
                  />
                  <Tooltip
                    formatter={(val: any) => [`₹${Number(val || 0).toLocaleString('en-IN')}`, 'Verified Collections']}
                    labelFormatter={(label) => `Date: ${label}`}
                  />

                  <Area
                    type="monotone"
                    dataKey="verified_amount"
                    stroke="#4f46e5"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#colorAccountsCollections)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs">
                <Receipt className="w-8 h-8 mb-2 opacity-40" />
                No collections recorded in this date range.
              </div>
            )}
          </div>
        </div>

        {/* Outstanding Ageing Distribution */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-xs border border-slate-200/80 dark:border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-amber-600 dark:text-amber-400" />
              <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">Receivables Ageing</h2>
            </div>
            <Link to="/accounts/outstanding" className="text-xs font-semibold text-indigo-600 hover:underline">
              View All
            </Link>
          </div>

          <div className="space-y-3 my-auto">
            {data && data.ageing_breakdown.map((item) => (
              <div key={item.bucket} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-medium">
                  <span className="text-slate-600 dark:text-slate-300 font-semibold">{item.label}</span>
                  <div className="text-right">
                    <span className="font-bold text-slate-900 dark:text-white">₹{item.amount.toLocaleString('en-IN')}</span>
                    <span className="text-[10px] text-slate-400 ml-1.5">({item.count} orders)</span>
                  </div>
                </div>
                <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.max(item.percentage, item.amount > 0 ? 4 : 0)}%`,
                      backgroundColor: item.color,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tables Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Company Financial Summary */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-xs border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">Company-wise Financials</h2>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
                  <th className="pb-2">Company</th>
                  <th className="pb-2 text-right">Orders Value</th>
                  <th className="pb-2 text-right">Collected</th>
                  <th className="pb-2 text-right">Pending</th>
                  <th className="pb-2 text-right">Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {data && data.company_breakdown.length > 0 ? (
                  data.company_breakdown.map((comp) => (
                    <tr key={comp.company_id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                      <td className="py-2.5 font-bold text-slate-800 dark:text-slate-200">{comp.company_name}</td>
                      <td className="py-2.5 text-right font-mono font-medium text-slate-700 dark:text-slate-300">
                        ₹{comp.order_value.toLocaleString('en-IN')}
                      </td>
                      <td className="py-2.5 text-right font-mono font-bold text-emerald-600 dark:text-emerald-400">
                        ₹{comp.verified_received.toLocaleString('en-IN')}
                      </td>
                      <td className="py-2.5 text-right font-mono font-bold text-amber-600 dark:text-amber-400">
                        ₹{comp.outstanding.toLocaleString('en-IN')}
                      </td>
                      <td className="py-2.5 text-right font-semibold">
                        <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                          {comp.collection_rate.toFixed(0)}%
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-6 text-center text-slate-400">
                      No company records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Outstanding Debtors Widget */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-xs border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-600 dark:text-rose-400" />
              <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">Top Outstanding Debtors</h2>
            </div>
            <Link to="/accounts/outstanding" className="text-xs font-semibold text-indigo-600 hover:underline">
              All Debtors &rarr;
            </Link>
          </div>

          <div className="space-y-2.5">
            {data && data.top_outstanding.length > 0 ? (
              data.top_outstanding.map((debtor) => (
                <div
                  key={debtor.sales_order_id}
                  onClick={() => navigate('/accounts/outstanding')}
                  className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-800 flex items-center justify-between hover:bg-slate-100/80 transition-colors cursor-pointer"
                >
                  <div className="space-y-0.5">
                    <div className="text-xs font-bold text-slate-800 dark:text-slate-100 flex items-center gap-1.5">
                      <span>{debtor.client_name}</span>
                      <span className="text-[10px] font-mono text-slate-400">({debtor.order_number})</span>
                    </div>
                    <div className="text-[11px] text-slate-500">
                      {debtor.service_name} &bull; Sales: {debtor.salesperson_name}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-extrabold text-rose-600 dark:text-rose-400">
                      {debtor.formatted_pending_amount}
                    </div>
                    <div className="text-[10px] font-bold text-slate-400">
                      {debtor.days_overdue > 0 ? `${debtor.days_overdue} days overdue` : 'Due soon'}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="py-8 text-center text-slate-400 text-xs">
                No outstanding debtors currently pending.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

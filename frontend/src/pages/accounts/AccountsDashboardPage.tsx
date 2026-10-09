import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  FileSpreadsheet,
  Filter,
  RefreshCw,
  AlertCircle,
  TrendingUp,
  Receipt,
  CreditCard,
  Clock,
  Landmark,
  Coins,
  ArrowRight,
  CheckCircle2,
  ListTodo,
  MapPin,
} from 'lucide-react';
import { getAccountsDashboardApi } from '../../api/accounts';
import type { AccountsDashboardResponse } from '../../types/accounts';
import { Button } from '../../components/ui/button';
import { CompanyFilterTabs } from '../../components/common/CompanyFilterTabs';
import { CompanyBadge } from '../../components/common/CompanyBadge';

export const AccountsDashboardPage: React.FC = () => {
  const [data, setData] = useState<AccountsDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Date & Company Filters using Sales Entry Date
  const [fromDate, setFromDate] = useState<string>('');
  const [toDate, setToDate] = useState<string>('');
  const [companyId, setCompanyId] = useState<string>('ALL');

  const fetchDashboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getAccountsDashboardApi({
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
        company_id: companyId !== 'ALL' ? companyId : undefined,
      });
      setData(res);
    } catch (err: any) {
      console.error('Failed to load accounts dashboard:', err);
      setError(err?.response?.data?.detail || 'Failed to load financial dashboard. Please check permissions.');
    } finally {
      setIsLoading(false);
    }
  }, [fromDate, toDate, companyId]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const buildEntriesUrl = (taskStatus?: string) => {
    const params = new URLSearchParams();
    if (taskStatus && taskStatus !== 'ALL') {
      params.set('task_status', taskStatus);
    }
    if (companyId && companyId !== 'ALL') {
      params.set('company_id', companyId);
    }
    if (fromDate) {
      params.set('from_date', fromDate);
    }
    if (toDate) {
      params.set('to_date', toDate);
    }
    const qs = params.toString();
    return `/accounts/entries${qs ? `?${qs}` : ''}`;
  };

  const kpis = data?.kpis;
  const taskSummary = data?.task_summary;
  const paymentBreakdown = data?.payment_status_breakdown || [];
  const recentEntries = data?.recent_entries || [];

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12 font-sans">
      {/* Top Banner Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-[#0a2569] via-indigo-900 to-blue-900 text-white shadow-xl relative overflow-hidden">
        {/* Ambient glow effects */}
        <div className="absolute -right-10 -bottom-10 w-72 h-72 rounded-full bg-white/5 blur-3xl pointer-events-none" />
        <div className="absolute top-0 right-1/4 w-48 h-48 rounded-full bg-indigo-500/10 blur-2xl pointer-events-none" />

        <div className="relative z-10 space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-bold text-indigo-200 border border-white/10">
            <Receipt className="w-3.5 h-3.5 text-amber-300" />
            <span>Accounts Management</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Accounts Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-indigo-200 max-w-2xl leading-relaxed">
            Live task lifecycle metrics, financial totals, advance collections, and estimated profits based on authorized Sales records.
          </p>
        </div>

        <div className="relative z-10 flex items-center gap-3">
          <Link to="/accounts/entries">
            <Button
              variant="primary"
              size="lg"
              className="bg-indigo-500 hover:bg-indigo-600 text-white font-bold rounded-2xl text-sm shadow-lg shadow-indigo-950/40 flex items-center gap-2 px-5 py-3 border border-indigo-400/30 transition-all hover:scale-[1.02]"
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>View Entries</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 dark:text-slate-400 mr-1">
            <Filter className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <span>Date Range (Sales Date):</span>
          </div>

          {/* From Date */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-slate-500 font-medium">From</span>
            <input
              type="date"
              aria-label="From Date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="px-3 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* To Date */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-slate-500 font-medium">To</span>
            <input
              type="date"
              aria-label="To Date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="px-3 py-1.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {(fromDate || toDate) && (
            <button
              onClick={() => {
                setFromDate('');
                setToDate('');
              }}
              className="text-xs text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 font-semibold px-2 py-1 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-950/40"
            >
              Reset Dates
            </button>
          )}

          {/* Company Filter Tabs */}
          <div className="flex items-center gap-2 ml-auto sm:ml-2">
            <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Company:</span>
            <CompanyFilterTabs
              selectedCompanyId={companyId}
              onCompanyChange={(newCompId) => setCompanyId(newCompId)}
              size="sm"
            />
          </div>
        </div>

        <button
          onClick={fetchDashboard}
          disabled={isLoading}
          className="p-2 text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors disabled:opacity-50 flex items-center gap-1.5 text-xs font-semibold"
          title="Refresh Dashboard"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 flex items-center gap-3 text-xs sm:text-sm">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* 3 Interactive Accounts Task Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Total Tasks Card */}
        <Link
          to={buildEntriesUrl('ALL')}
          aria-label="Filter Total Tasks"
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-indigo-400 dark:hover:border-indigo-600 transition-all hover:scale-[1.01] group cursor-pointer relative overflow-hidden flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                  <ListTodo className="w-5 h-5" />
                </div>
                <span className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">
                  Total Tasks
                </span>
              </div>
              <span className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400 flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                <span>View all</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </span>
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <div className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">
                {taskSummary ? taskSummary.total_tasks : (kpis ? kpis.total_entries : 0)}
              </div>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                Authorized Scope
              </span>
            </div>
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            All actionable Accounts workflows in current scope
          </div>
        </Link>

        {/* Completed Tasks Card */}
        <Link
          to={buildEntriesUrl('COMPLETED')}
          aria-label="Filter Completed Tasks"
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-emerald-400 dark:hover:border-emerald-600 transition-all hover:scale-[1.01] group cursor-pointer relative overflow-hidden flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <span className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">
                  Completed Tasks
                </span>
              </div>
              <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Filter list</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </span>
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <div className="text-3xl font-black text-emerald-600 dark:text-emerald-400 tracking-tight">
                {taskSummary ? taskSummary.completed_tasks : 0}
              </div>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                Tax Invoice Issued
              </span>
            </div>
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            Tasks with completed Accounts workflow
          </div>
        </Link>

        {/* Pending Tasks Card */}
        <Link
          to={buildEntriesUrl('PENDING')}
          aria-label="Filter Pending Tasks"
          className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-amber-400 dark:hover:border-amber-600 transition-all hover:scale-[1.01] group cursor-pointer relative overflow-hidden flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 group-hover:bg-amber-600 group-hover:text-white transition-colors">
                  <Clock className="w-5 h-5" />
                </div>
                <span className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">
                  Pending Tasks
                </span>
              </div>
              <span className="text-[11px] font-semibold text-amber-600 dark:text-amber-400 flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Filter list</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </span>
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <div className="text-3xl font-black text-amber-600 dark:text-amber-400 tracking-tight">
                {taskSummary ? taskSummary.pending_tasks : 0}
              </div>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300">
                Action Required
              </span>
            </div>
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            Pending / in-progress Tax Invoicing & closure
          </div>
        </Link>
      </div>

      {/* 7 Canonical Financial KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Total Entries */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-indigo-300 dark:hover:border-indigo-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Total Entries
            </span>
            <div className="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2">
            {kpis ? kpis.total_entries : 0}
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2 flex items-center justify-between">
            <span>Filtered Sales Orders</span>
            <span className="text-[10px] bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full font-semibold">
              Full Dataset
            </span>
          </div>
        </div>

        {/* KPI 2: Total Amount */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-blue-300 dark:hover:border-blue-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Total Amount
            </span>
            <div className="p-2.5 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
              <Receipt className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-blue-600 dark:text-blue-400 mt-2">
            {kpis ? kpis.formatted_total_amount : '₹0.00'}
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            Aggregate Order Value (Contractual)
          </div>
        </div>

        {/* KPI 3: Advance Amount */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-emerald-300 dark:hover:border-emerald-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Advance Amount
            </span>
            <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
              <CreditCard className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-2">
            {kpis ? kpis.formatted_advance_amount : '₹0.00'}
          </div>
          <div className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Total Received / Advance</span>
          </div>
        </div>

        {/* KPI 4: Pending Amount */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-amber-300 dark:hover:border-amber-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Pending Amount
            </span>
            <div className="p-2.5 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-2">
            {kpis ? kpis.formatted_pending_amount : '₹0.00'}
          </div>
          <div className="text-[11px] text-amber-700 dark:text-amber-300 font-medium mt-2">
            Outstanding Balance Amount
          </div>
        </div>

        {/* KPI 5: Govt Fees */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-purple-300 dark:hover:border-purple-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Govt Fees
            </span>
            <div className="p-2.5 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400">
              <Landmark className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-purple-600 dark:text-purple-400 mt-2">
            {kpis ? kpis.formatted_govt_fees : '₹0.00'}
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            Statutory & Filing Fees
          </div>
        </div>

        {/* KPI 6: Incidental Cost */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-orange-300 dark:hover:border-orange-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Incidental Cost
            </span>
            <div className="p-2.5 rounded-xl bg-orange-50 dark:bg-orange-950/60 text-orange-600 dark:text-orange-400">
              <Coins className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-orange-600 dark:text-orange-400 mt-2">
            {kpis ? kpis.formatted_incidental_cost : '₹0.00'}
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            Direct Operational Costs
          </div>
        </div>

        {/* KPI 7: Estimated Profit */}
        <div className="sm:col-span-2 p-5 rounded-2xl bg-gradient-to-br from-emerald-50 via-teal-50 to-emerald-100/50 dark:from-slate-900 dark:via-emerald-950/30 dark:to-slate-900 border border-emerald-200 dark:border-emerald-800 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-emerald-800 dark:text-emerald-300 text-[11px] font-bold uppercase tracking-wider">
              Estimated Profit
            </span>
            <div className="p-2.5 rounded-xl bg-emerald-600 text-white shadow-md">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-emerald-700 dark:text-emerald-400 mt-2">
            {kpis ? kpis.formatted_estimated_profit : '₹0.00'}
          </div>
          <div className="text-xs text-emerald-800/80 dark:text-emerald-300/80 font-medium mt-2 flex items-center justify-between">
            <span>Server Formula: Total Amount − Govt Fees − Incidental Cost</span>
            <span className="text-[10px] bg-emerald-200/60 dark:bg-emerald-900/60 px-2 py-0.5 rounded-full font-bold text-emerald-900 dark:text-emerald-200">
              Estimate
            </span>
          </div>
        </div>
      </div>

      {/* Payment Status Breakdown */}
      <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white">Payment Status Breakdown</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Distribution of confirmed orders across collection statuses
            </p>
          </div>
          <Link
            to="/accounts/entries"
            className="text-xs font-bold text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 flex items-center gap-1"
          >
            <span>View All in Entries</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
          {paymentBreakdown.map((item) => {
            let bgLight = 'bg-slate-50 border-slate-200 text-slate-800';
            let badgeBg = 'bg-slate-200 text-slate-700';

            if (item.status === 'FULLY_PAID') {
              bgLight = 'bg-emerald-50/70 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200';
              badgeBg = 'bg-emerald-200/80 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200';
            } else if (item.status === 'PARTIALLY_PAID') {
              bgLight = 'bg-blue-50/70 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800 text-blue-900 dark:text-blue-200';
              badgeBg = 'bg-blue-200/80 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
            } else if (item.status === 'PENDING') {
              bgLight = 'bg-amber-50/70 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200';
              badgeBg = 'bg-amber-200/80 text-amber-800 dark:bg-amber-900 dark:text-amber-200';
            } else if (item.status === 'OVERDUE') {
              bgLight = 'bg-rose-50/70 dark:bg-rose-950/30 border-rose-200 dark:border-rose-800 text-rose-900 dark:text-rose-200';
              badgeBg = 'bg-rose-200/80 text-rose-800 dark:bg-rose-900 dark:text-rose-200';
            }

            return (
              <div
                key={item.status}
                className={`p-4 rounded-2xl border ${bgLight} flex flex-col justify-between space-y-3 transition-transform hover:scale-[1.01]`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs">{item.label}</span>
                  <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full ${badgeBg}`}>
                    {item.percentage.toFixed(1)}%
                  </span>
                </div>
                <div>
                  <div className="text-xl font-extrabold font-mono">{item.formatted_amount}</div>
                  <div className="text-[11px] opacity-80 mt-0.5 font-medium">{item.count} orders</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Entries Preview */}
      <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white">Recent Accounts Entries</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Latest shared sales records in the Accounts module
            </p>
          </div>
          <Link to="/accounts/entries">
            <Button
              variant="outline"
              size="sm"
              className="text-xs font-semibold rounded-xl flex items-center gap-1.5"
            >
              <span>View All Entries</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
                <th className="pb-3 pl-2">S.No</th>
                <th className="pb-3">Company</th>
                <th className="pb-3">Date</th>
                <th className="pb-3">Client Name</th>
                <th className="pb-3">Location</th>
                <th className="pb-3">Work</th>
                <th className="pb-3">Converted By</th>
                <th className="pb-3 text-right">Total Amount</th>
                <th className="pb-3 text-right">Advance Amount</th>
                <th className="pb-3 text-right">Pending Amount</th>
                <th className="pb-3 text-center">Payment Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {recentEntries.length > 0 ? (
                recentEntries.map((entry) => (
                  <tr key={entry.order_id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 pl-2 font-mono text-slate-500 font-semibold">{entry.s_no}</td>
                    <td className="py-3">
                      <CompanyBadge companyName={entry.company_name} companyCode={entry.company_code} />
                    </td>
                    <td className="py-3 whitespace-nowrap text-slate-600 dark:text-slate-400 font-medium">
                      {entry.formatted_date}
                    </td>
                    <td className="py-3 font-bold text-slate-800 dark:text-slate-200">
                      {entry.client_name}
                    </td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">
                      {entry.location ? (
                        <span className="inline-flex items-center gap-1 font-medium text-slate-700 dark:text-slate-300">
                          <MapPin className="w-3 h-3 text-indigo-500 shrink-0" />
                          <span>{entry.location}</span>
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="py-3 text-slate-600 dark:text-slate-400 font-medium">
                      {entry.service_name}
                    </td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">
                      {entry.salesperson_name}
                    </td>
                    <td className="py-3 text-right font-mono font-medium text-slate-800 dark:text-slate-200">
                      {entry.formatted_order_value}
                    </td>
                    <td className="py-3 text-right font-mono font-bold text-emerald-600 dark:text-emerald-400">
                      {entry.formatted_amount_received}
                    </td>
                    <td className="py-3 text-right font-mono font-bold text-amber-600 dark:text-amber-400">
                      {entry.formatted_balance_amount}
                    </td>
                    <td className="py-3 text-center">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          entry.payment_status === 'FULLY_PAID'
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                            : entry.payment_status === 'PARTIALLY_PAID'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                            : entry.payment_status === 'OVERDUE'
                            ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                            : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                        }`}
                      >
                        {entry.payment_status.replace('_', ' ')}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={11} className="py-8 text-center text-slate-400 text-xs">
                    No sales orders found for the selected filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

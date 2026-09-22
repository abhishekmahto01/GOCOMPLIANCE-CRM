import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate, useOutletContext } from 'react-router-dom';
import {
  Users,
  AlertTriangle,
  RotateCcw,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getSalesDashboardApi, exportSalesDashboardCsvApi } from '../api/sales';
import { extractErrorMessage } from '../api/client';
import type {
  SalesDashboardResponse,
  SalesDashboardFilterParams,
} from '../types/sales';
import { SalesFilterBar } from '../components/sales/SalesFilterBar';
import { SalesKpiGrid } from '../components/sales/SalesKpiGrid';
import { SalesTrendChart } from '../components/sales/SalesTrendChart';
import { SalesPaymentDonut } from '../components/sales/SalesPaymentDonut';
import { SalesLicenceBarChart } from '../components/sales/SalesLicenceBarChart';
import { SalesLeadSourceDonut } from '../components/sales/SalesLeadSourceDonut';
import { SalesTeamTable } from '../components/sales/SalesTeamTable';
import { RecentSalesOrdersTable } from '../components/sales/RecentSalesOrdersTable';

interface OutletContextType {
  addToast?: (type: 'success' | 'error' | 'info', title: string, message: string) => void;
}

export const SalesDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const outletCtx = useOutletContext<OutletContextType>();
  const [searchParams, setSearchParams] = useSearchParams();

  // Filters State from URL or defaults
  const [filters, setFilters] = useState<SalesDashboardFilterParams>(() => {
    return {
      preset: searchParams.get('preset') || 'this_month',
      from_date: searchParams.get('from_date') || undefined,
      to_date: searchParams.get('to_date') || undefined,
      employee_id: searchParams.get('employee_id') || undefined,
      service_id: searchParams.get('service_id') || undefined,
      lead_source: searchParams.get('lead_source') || undefined,
      payment_status: searchParams.get('payment_status') || undefined,
    };
  });

  const [dashboardData, setDashboardData] = useState<SalesDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  const addToastRef = React.useRef(outletCtx?.addToast);
  useEffect(() => {
    addToastRef.current = outletCtx?.addToast;
  }, [outletCtx]);

  // Sync state to URL query params
  const updateUrlParams = useCallback((newFilters: SalesDashboardFilterParams) => {
    const params: Record<string, string> = {};
    if (newFilters.preset) params.preset = newFilters.preset;
    if (newFilters.from_date) params.from_date = newFilters.from_date;
    if (newFilters.to_date) params.to_date = newFilters.to_date;
    if (newFilters.employee_id && newFilters.employee_id !== 'ALL') params.employee_id = newFilters.employee_id;
    if (newFilters.service_id && newFilters.service_id !== 'ALL') params.service_id = newFilters.service_id;
    if (newFilters.lead_source && newFilters.lead_source !== 'ALL') params.lead_source = newFilters.lead_source;
    if (newFilters.payment_status && newFilters.payment_status !== 'ALL') params.payment_status = newFilters.payment_status;
    setSearchParams(params, { replace: true });
  }, [setSearchParams]);

  // Load dashboard data from API
  const loadDashboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getSalesDashboardApi(filters);
      setDashboardData(data);
    } catch (err: unknown) {
      console.error('Sales dashboard fetch error:', err);
      const msg = extractErrorMessage(err);
      setError(msg);
      addToastRef.current?.('error', 'Failed to Load Dashboard', msg);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  // Handle Filter Changes
  const handleFilterChange = (newPartial: Partial<SalesDashboardFilterParams>) => {
    const updated = { ...filters, ...newPartial };
    setFilters(updated);
    updateUrlParams(updated);
  };

  // Handle Filter Reset
  const handleReset = () => {
    const resetValues: SalesDashboardFilterParams = {
      preset: 'this_month',
      from_date: undefined,
      to_date: undefined,
      employee_id: dashboardData?.filter_options.can_filter_employees ? 'ALL' : undefined,
      service_id: 'ALL',
      lead_source: 'ALL',
      payment_status: 'ALL',
    };
    setFilters(resetValues);
    updateUrlParams(resetValues);
  };

  // Handle Export CSV
  const handleExport = async () => {
    setIsExporting(true);
    try {
      const { blob, filename } = await exportSalesDashboardCsvApi(filters);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      outletCtx?.addToast?.('success', 'Export Downloaded', `Successfully exported ${filename}`);
    } catch (err: unknown) {
      console.error('Export CSV error:', err);
      const msg = extractErrorMessage(err);
      outletCtx?.addToast?.('error', 'Export Failed', msg);
    } finally {
      setIsExporting(false);
    }
  };

  // Navigation to order details
  const handleViewOrder = (orderId: string) => {
    navigate(`/sales/orders/${orderId}`);
  };

  return (
    <div className="p-4 sm:p-8 max-w-7xl mx-auto w-full space-y-6">
      {/* 1. Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Sales Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Track sales performance and collections
          </p>
        </div>

        {/* Scope / Role Pill */}
        <div className="flex items-center gap-2 self-start sm:self-center">
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50/80 dark:bg-blue-950/40 border border-blue-200/70 dark:border-blue-800/60 text-xs font-semibold text-blue-700 dark:text-blue-300 shadow-2xs">
            <Users className="w-3.5 h-3.5" />
            <span>
              {dashboardData?.filter_options.can_filter_employees
                ? 'All Sales Team'
                : `My Sales (${user?.employee_code || 'Self'})`}
            </span>
          </div>
        </div>
      </div>

      {/* 2. Filter Bar */}
      {dashboardData && (
        <SalesFilterBar
          filters={filters}
          filterOptions={dashboardData.filter_options}
          dateDisplay={{
            formatted_from: dashboardData.date_range.formatted_from,
            formatted_to: dashboardData.date_range.formatted_to,
            from_date: dashboardData.date_range.from_date,
            to_date: dashboardData.date_range.to_date,
          }}
          onFilterChange={handleFilterChange}
          onReset={handleReset}
          onExport={handleExport}
          isExporting={isExporting}
        />
      )}

      {/* 3. Error Banner */}
      {error && !isLoading && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 flex items-center justify-between gap-4 text-xs sm:text-sm">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="w-5 h-5 shrink-0 text-rose-600 dark:text-rose-400" />
            <span>{error}</span>
          </div>
          <button
            type="button"
            onClick={loadDashboard}
            className="px-3 py-1.5 rounded-xl bg-rose-600 text-white font-semibold text-xs hover:bg-rose-700 transition shrink-0 flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* 4. Loading Skeleton */}
      {isLoading && (
        <div className="space-y-6 animate-pulse">
          {/* Skeleton KPI Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-28 bg-white/70 dark:bg-slate-900/70 rounded-2xl border border-slate-200/60 dark:border-slate-800 p-4 space-y-3">
                <div className="w-1/2 h-3 bg-slate-200 dark:bg-slate-800 rounded" />
                <div className="w-3/4 h-6 bg-slate-200 dark:bg-slate-800 rounded" />
              </div>
            ))}
          </div>

          {/* Skeleton Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-72 bg-white/70 dark:bg-slate-900/70 rounded-2xl border border-slate-200/60 dark:border-slate-800 p-5" />
            <div className="h-72 bg-white/70 dark:bg-slate-900/70 rounded-2xl border border-slate-200/60 dark:border-slate-800 p-5" />
            <div className="h-72 bg-white/70 dark:bg-slate-900/70 rounded-2xl border border-slate-200/60 dark:border-slate-800 p-5" />
            <div className="h-72 bg-white/70 dark:bg-slate-900/70 rounded-2xl border border-slate-200/60 dark:border-slate-800 p-5" />
          </div>

          {/* Skeleton Tables */}
          <div className="h-64 bg-white/70 dark:bg-slate-900/70 rounded-2xl border border-slate-200/60 dark:border-slate-800 p-5" />
          <div className="h-64 bg-white/70 dark:bg-slate-900/70 rounded-2xl border border-slate-200/60 dark:border-slate-800 p-5" />
        </div>
      )}

      {/* 5. Loaded Dashboard Data */}
      {!isLoading && dashboardData && (
        <div className="space-y-6">
          {/* KPI Summary Cards */}
          <SalesKpiGrid kpis={dashboardData.kpis} />

          {/* Charts Grid: 4 Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 1. Sales Trend */}
            <SalesTrendChart data={dashboardData.sales_trend} />

            {/* 2. Payment Status Donut */}
            <SalesPaymentDonut data={dashboardData.payment_status} />

            {/* 3. License-wise Sales Bar Chart */}
            <SalesLicenceBarChart data={dashboardData.service_sales} />

            {/* 4. Lead Sources Donut */}
            <SalesLeadSourceDonut data={dashboardData.lead_sources} />
          </div>

          {/* Sales Team Performance Table */}
          <SalesTeamTable rows={dashboardData.team_performance} />

          {/* Recent Sales Orders Table */}
          <RecentSalesOrdersTable
            orders={dashboardData.recent_orders}
            onViewOrder={handleViewOrder}
          />
        </div>
      )}
    </div>
  );
};

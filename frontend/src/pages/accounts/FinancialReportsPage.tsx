import React, { useState, useEffect } from 'react';
import {
  Download,
  Filter,
  CreditCard,
  Clock,
  Receipt,
  FileText,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
} from 'lucide-react';
import { exportAccountsReportApi, getAccountsFilterOptionsApi } from '../../api/accounts';
import type { AccountsFilterOptions } from '../../types/accounts';
import { Button } from '../../components/ui/button';

export const FinancialReportsPage: React.FC = () => {
  const [filterOptions, setFilterOptions] = useState<AccountsFilterOptions | null>(null);
  const [companyId, setCompanyId] = useState<string>('ALL');
  const [employeeId, setEmployeeId] = useState<string>('ALL');
  const [clientName, setClientName] = useState<string>('');
  const [paymentStatus] = useState<string>('ALL');
  const [fromDate, setFromDate] = useState<string>('');
  const [toDate, setToDate] = useState<string>('');
  const [downloadingReport, setDownloadingReport] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    getAccountsFilterOptionsApi()
      .then(setFilterOptions)
      .catch((err) => console.error('Error loading filter options:', err));
  }, []);

  const handleDownload = async (reportType: 'payments' | 'outstanding' | 'expenses' | 'client_statement') => {
    setDownloadingReport(reportType);
    setErrorMsg(null);
    try {
      const { blob, filename } = await exportAccountsReportApi({
        report_type: reportType,
        company_id: companyId,
        employee_id: employeeId,
        client_name: clientName.trim() || undefined,
        payment_status: paymentStatus,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
      });

      // Create download anchor
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccessMsg(`Report "${filename}" downloaded successfully.`);
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      console.error('Error downloading report:', err);
      setErrorMsg(err?.response?.data?.detail || 'Failed to generate financial export.');
    } finally {
      setDownloadingReport(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Top Banner Header */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-blue-950 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-bold text-indigo-200 border border-white/10">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>Financial Statements & Compliance Exports</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Financial Reports & Data Exports
          </h1>
          <p className="text-xs sm:text-sm text-indigo-200 max-w-2xl leading-relaxed">
            Generate audit-safe, sanitized CSV ledgers for management accounts, tax preparation, client account statements, and ageing debt recovery.
          </p>
        </div>
      </div>

      {/* Global Filter Bar for Exports */}
      <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-700 dark:text-slate-300">
          <Filter className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <span>Report Scope & Date Parameters</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Company Scope */}
          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
              Company Scope
            </label>
            <select
              aria-label="Company Filter"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-semibold"
            >
              <option value="ALL">All Authorized Companies</option>
              {filterOptions?.companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>

          {/* Salesperson Scope */}
          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
              Salesperson Filter
            </label>
            <select
              aria-label="Salesperson Filter"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
            >
              <option value="ALL">All Salespersons</option>
              {filterOptions?.salespersons.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>

          {/* Start Date */}
          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
              From Date
            </label>
            <input
              type="date"
              aria-label="From Date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
            />
          </div>

          {/* End Date */}
          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
              To Date
            </label>
            <input
              type="date"
              aria-label="To Date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
            />
          </div>
        </div>

        {/* Client Name Filter for Statement */}
        <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
              Client Name Filter (Optional, for Client Statement)
            </label>
            <input
              type="text"
              placeholder="e.g. Acme Corp..."
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
            />
          </div>
        </div>
      </div>

      {/* Success Banner */}
      {successMsg && (
        <div className="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 flex items-center gap-2.5 text-xs font-semibold">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Error Banner */}
      {errorMsg && (
        <div className="p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 flex items-center gap-2.5 text-xs font-semibold">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Report 1: Payment Register Ledger */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
              <CreditCard className="w-6 h-6" />
            </div>
            <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
              Payment Register & Collection Ledger
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Complete order-wise ledger including agreed order liability, verified receipts, unverified collections, pending balance, payment statuses, and due dates.
            </p>
          </div>

          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <span className="text-[11px] font-mono text-slate-400">Format: CSV (Sanitized)</span>
            <Button
              onClick={() => handleDownload('payments')}
              disabled={downloadingReport === 'payments'}
              size="sm"
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloadingReport === 'payments' ? 'Exporting...' : 'Export Register'}</span>
            </Button>
          </div>
        </div>

        {/* Report 2: Outstanding Receivables & Ageing */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="w-12 h-12 rounded-2xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center">
              <Clock className="w-6 h-6" />
            </div>
            <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
              Outstanding Debtors & Ageing Analysis
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Detailed receivable ageing report categorized by 1–30, 31–60, 61–90, 90+ days past due date, debtor contact phone/email, and latest follow-up promises.
            </p>
          </div>

          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <span className="text-[11px] font-mono text-slate-400">Format: CSV (Sanitized)</span>
            <Button
              onClick={() => handleDownload('outstanding')}
              disabled={downloadingReport === 'outstanding'}
              size="sm"
              className="bg-amber-600 hover:bg-amber-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloadingReport === 'outstanding' ? 'Exporting...' : 'Export Ageing'}</span>
            </Button>
          </div>
        </div>

        {/* Report 3: Client Financial Statement */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
              Client Account Statement Ledger
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Consolidated transaction breakdown across all orders for a client or company, showing debits (orders), credits (verified collections), and running balance.
            </p>
          </div>

          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <span className="text-[11px] font-mono text-slate-400">Format: CSV (Sanitized)</span>
            <Button
              onClick={() => handleDownload('client_statement')}
              disabled={downloadingReport === 'client_statement'}
              size="sm"
              className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloadingReport === 'client_statement' ? 'Exporting...' : 'Export Statement'}</span>
            </Button>
          </div>
        </div>

        {/* Report 4: Direct Expenses & Margin Summary */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="w-12 h-12 rounded-2xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center">
              <Receipt className="w-6 h-6" />
            </div>
            <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
              Direct Costs & Outlay Summary
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Detailed list of government fee payments, vendor outlay, incidental costs, employee reimbursements, and settlement statuses.
            </p>
          </div>

          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <span className="text-[11px] font-mono text-slate-400">Format: CSV (Sanitized)</span>
            <Button
              onClick={() => handleDownload('expenses')}
              disabled={downloadingReport === 'expenses'}
              size="sm"
              className="bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloadingReport === 'expenses' ? 'Exporting...' : 'Export Expenses'}</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Formula Injection Security Note */}
      <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 flex items-center gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
        <div className="text-xs text-slate-500">
          <span className="font-bold text-slate-700 dark:text-slate-200">Spreadsheet Formula Injection Protected:</span> All exported CSV fields starting with dangerous formula triggers (<code className="text-indigo-600 font-mono">=, +, -, @</code>) are automatically neutralized for secure opening in Microsoft Excel and Google Sheets.
        </div>
      </div>
    </div>
  );
};

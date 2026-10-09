import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useOutletContext, useSearchParams } from 'react-router-dom';
import {
  FileSpreadsheet,
  Download,
  Search,
  CheckCircle2,
  Clock,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Edit,
  MapPin,
  RefreshCw,
  Check,
  MessageSquare,
} from 'lucide-react';
import {
  getAccountsEntriesApi,
  updateAccountsEntryApi,
  exportAccountsEntriesCsvApi,
} from '../../api/accounts';
import { extractErrorMessage } from '../../api/client';
import type {
  AccountsEntriesResponse,
  AccountsEntryUpdatePayload,
} from '../../types/accounts';
import { Button } from '../../components/ui/button';
import { TaskConversationModal } from '../../components/conversation/TaskConversationModal';
import { CompanyFilterTabs } from '../../components/common/CompanyFilterTabs';
import { CompanyBadge } from '../../components/common/CompanyBadge';
import { useRemarkNotification } from '../../context/RemarkNotificationContext';

interface OutletContextType {
  addToast?: (type: 'success' | 'error' | 'info', title: string, message: string) => void;
}

type EditableField = 'proforma_invoice_no' | 'tax_invoice_no' | 'reimbursement_note' | 'remarks';

interface ActiveEditCell {
  orderId: string;
  field: EditableField;
}

function formatInr(val: number | string | null | undefined): string {
  const num = typeof val === 'number' ? val : parseFloat(String(val ?? 0));
  const safeNum = isNaN(num) ? 0 : num;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(safeNum);
}

function renderPaymentBadge(status: string) {
  const s = status?.toUpperCase() || '';
  if (s === 'FULLY_PAID') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800/60">
        <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
        Fully Paid
      </span>
    );
  }
  if (s === 'PARTIALLY_PAID') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-400 dark:border-blue-800/60">
        <Clock className="w-3 h-3 text-blue-600 dark:text-blue-400" />
        Partially Paid
      </span>
    );
  }
  if (s === 'PENDING') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-800/60">
        <Clock className="w-3 h-3 text-amber-600 dark:text-amber-400" />
        Pending
      </span>
    );
  }
  if (s === 'OVERDUE') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-800/60">
        <AlertCircle className="w-3 h-3 text-rose-600 dark:text-rose-400" />
        Overdue
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
      {status || '—'}
    </span>
  );
}

function renderWorkStatusBadge(status: string) {
  const s = status?.toUpperCase() || '';
  if (s === 'COMPLETED' || s === 'APPROVED') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800/60">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        Completed
      </span>
    );
  }
  if (['IN_PROGRESS', 'ASSIGNED', 'DOCUMENT_VERIFICATION', 'READY_FOR_SUBMISSION', 'SUBMITTED'].includes(s)) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-400 dark:border-blue-800/60">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
        {s === 'ASSIGNED' ? 'Assigned' : 'In Progress'}
      </span>
    );
  }
  if (['UNASSIGNED', 'PENDING', 'NONE', 'DRAFT'].includes(s)) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700">
        <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
        {s === 'UNASSIGNED' ? 'Unassigned' : 'Pending'}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
      {status || '—'}
    </span>
  );
}

function getFieldLabel(field: EditableField): string {
  switch (field) {
    case 'proforma_invoice_no':
      return 'Proforma Inv. No.';
    case 'tax_invoice_no':
      return 'Tax Inv. No.';
    case 'reimbursement_note':
      return 'Reimbursement Note';
    case 'remarks':
      return 'Remarks';
  }
}

export const AccountsEntriesPage: React.FC = () => {
  const outletCtx = useOutletContext<OutletContextType>();
  const [searchParams, setSearchParams] = useSearchParams();
  const { unreadSummary } = useRemarkNotification();

  // Search & Filter State
  const [search, setSearch] = useState<string>(searchParams.get('search') || '');
  const [companyId, setCompanyId] = useState<string>(searchParams.get('company_id') || 'ALL');
  const [paymentStatus, setPaymentStatus] = useState<string>(searchParams.get('payment_status') || 'ALL');
  const [taskStatus, setTaskStatus] = useState<string>(searchParams.get('task_status') || 'ALL');
  const [fromDate, setFromDate] = useState<string>(searchParams.get('from_date') || '');
  const [toDate, setToDate] = useState<string>(searchParams.get('to_date') || '');
  const [page, setPage] = useState<number>(Number(searchParams.get('page')) || 1);
  const [limit] = useState<number>(50);

  // Sync state if URL searchParams change
  useEffect(() => {
    const urlTaskStatus = searchParams.get('task_status') || 'ALL';
    if (urlTaskStatus !== taskStatus) {
      setTaskStatus(urlTaskStatus);
    }
  }, [searchParams]);

  // Data & State
  const [entriesData, setEntriesData] = useState<AccountsEntriesResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Direct Inline Cell Editing State
  const [activeCell, setActiveCell] = useState<ActiveEditCell | null>(null);
  const [activeValue, setActiveValue] = useState<string>('');
  const [savingCells, setSavingCells] = useState<Record<string, boolean>>({});
  const [lastSavedCell, setLastSavedCell] = useState<string | null>(null);

  // Shared Task Conversation Modal State
  const [conversationOrderId, setConversationOrderId] = useState<string | null>(null);
  const [isConversationOpen, setIsConversationOpen] = useState<boolean>(false);

  // Handle open_conversation_order_id query param
  const openConversationParam = searchParams.get('open_conversation_order_id') || searchParams.get('open_order_id');
  useEffect(() => {
    if (openConversationParam) {
      setConversationOrderId(openConversationParam);
      setIsConversationOpen(true);
    }
  }, [openConversationParam]);

  const inputRef = useRef<HTMLInputElement>(null);

  // Sync state with URL params
  const syncUrl = useCallback(
    (newParams: Record<string, string>) => {
      const p: Record<string, string> = {};
      if (newParams.search) p.search = newParams.search;
      if (newParams.company_id && newParams.company_id !== 'ALL') p.company_id = newParams.company_id;
      if (newParams.payment_status && newParams.payment_status !== 'ALL') p.payment_status = newParams.payment_status;
      if (newParams.task_status && newParams.task_status !== 'ALL') p.task_status = newParams.task_status;
      if (newParams.from_date) p.from_date = newParams.from_date;
      if (newParams.to_date) p.to_date = newParams.to_date;
      if (newParams.page && newParams.page !== '1') p.page = newParams.page;
      setSearchParams(p, { replace: true });
    },
    [setSearchParams]
  );

  const handleCompanyChange = (newCompId: string) => {
    setCompanyId(newCompId);
    setPage(1);
    syncUrl({
      search,
      company_id: newCompId,
      payment_status: paymentStatus,
      task_status: taskStatus,
      from_date: fromDate,
      to_date: toDate,
      page: '1',
    });
  };

  const handleTaskStatusChange = (newStatus: string) => {
    setTaskStatus(newStatus);
    setPage(1);
    syncUrl({
      search,
      company_id: companyId,
      payment_status: paymentStatus,
      task_status: newStatus,
      from_date: fromDate,
      to_date: toDate,
      page: '1',
    });
  };

  // Fetch Accounts Entries
  const loadEntries = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAccountsEntriesApi({
        page,
        limit,
        search: search.trim() || undefined,
        company_id: companyId !== 'ALL' ? companyId : undefined,
        payment_status: paymentStatus !== 'ALL' ? paymentStatus : undefined,
        task_status: taskStatus !== 'ALL' ? taskStatus : undefined,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
      });
      setEntriesData(data);
    } catch (err: any) {
      console.error('Failed to load accounts entries:', err);
      const msg = extractErrorMessage(err) || 'Failed to load accounts entries. Please check permissions.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [page, limit, search, companyId, paymentStatus, taskStatus, fromDate, toDate]);

  useEffect(() => {
    loadEntries();
  }, [loadEntries]);

  // Handle Search Submission
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    syncUrl({
      search,
      company_id: companyId,
      payment_status: paymentStatus,
      task_status: taskStatus,
      from_date: fromDate,
      to_date: toDate,
      page: '1',
    });
    loadEntries();
  };

  // Reset Filters
  const handleResetFilters = () => {
    setSearch('');
    setCompanyId('ALL');
    setPaymentStatus('ALL');
    setTaskStatus('ALL');
    setFromDate('');
    setToDate('');
    setPage(1);
    syncUrl({});
  };

  // Export CSV
  const handleExportCsv = async () => {
    setIsExporting(true);
    try {
      const { blob, filename } = await exportAccountsEntriesCsvApi({
        search: search.trim() || undefined,
        company_id: companyId !== 'ALL' ? companyId : undefined,
        payment_status: paymentStatus !== 'ALL' ? paymentStatus : undefined,
        task_status: taskStatus !== 'ALL' ? taskStatus : undefined,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      outletCtx?.addToast?.('success', 'Export Complete', 'Accounts entries exported successfully to CSV.');
    } catch (err) {
      console.error('Export error:', err);
      const msg = extractErrorMessage(err);
      outletCtx?.addToast?.('error', 'Export Failed', msg);
    } finally {
      setIsExporting(false);
    }
  };

  // Start Inline Cell Edit
  const handleStartCellEdit = (
    orderId: string,
    field: EditableField,
    currentVal: string | null | undefined,
    e?: React.MouseEvent
  ) => {
    if (e) e.stopPropagation();
    setActiveCell({ orderId, field });
    setActiveValue(currentVal ?? '');
  };

  // Commit & Save Inline Cell
  const handleCommitCellEdit = async (
    orderId: string,
    field: EditableField,
    valueToSave: string,
    originalValue: string | null | undefined
  ) => {
    const trimmed = valueToSave.trim();
    const originalTrimmed = (originalValue ?? '').trim();

    // If unchanged, simply exit edit mode
    if (trimmed === originalTrimmed) {
      setActiveCell(null);
      return;
    }

    const cellKey = `${orderId}_${field}`;
    setSavingCells((prev) => ({ ...prev, [cellKey]: true }));

    const payload: AccountsEntryUpdatePayload = {
      [field]: trimmed || null,
    };
    if (field === 'remarks') {
      payload.notes = trimmed || null;
    }

    try {
      const updatedItem = await updateAccountsEntryApi(orderId, payload);

      // Optimistically update item in local entries list
      setEntriesData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          items: prev.items.map((item) => (item.order_id === orderId ? updatedItem : item)),
        };
      });

      setLastSavedCell(cellKey);
      setTimeout(() => setLastSavedCell(null), 2500);

      outletCtx?.addToast?.(
        'success',
        'Saved',
        `${getFieldLabel(field)} for Order #${updatedItem.order_number} saved.`
      );
      setActiveCell(null);
    } catch (err) {
      console.error('Direct inline save error:', err);
      const msg = extractErrorMessage(err) || 'Failed to save changes.';
      outletCtx?.addToast?.('error', 'Save Failed', msg);
      // Keep cell active so user doesn't lose entered text
    } finally {
      setSavingCells((prev) => {
        const next = { ...prev };
        delete next[cellKey];
        return next;
      });
    }
  };

  // Helper to check if a specific cell is active
  const isCellActive = (orderId: string, field: EditableField) => {
    return activeCell?.orderId === orderId && activeCell?.field === field;
  };

  // Helper to check if a specific cell is currently saving
  const isCellSaving = (orderId: string, field: EditableField) => {
    return Boolean(savingCells[`${orderId}_${field}`]);
  };

  const summary = entriesData?.summary;
  const totalPages = entriesData?.total_pages || 1;

  return (
    <div className="space-y-6 max-w-full font-sans pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
              Accounts Entries
            </h1>
            <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300">
              {entriesData?.total_count || 0} Total
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Authorized Sales records. Click directly on any highlighted field (Cols 15, 16, 17, 21) to enter values directly without popups.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportCsv}
            disabled={isExporting || isLoading}
            className="flex items-center gap-1.5 text-xs font-semibold rounded-xl"
          >
            <Download className={`w-4 h-4 ${isExporting ? 'animate-bounce' : ''}`} />
            <span>{isExporting ? 'Exporting...' : 'Export CSV'}</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={loadEntries}
            disabled={isLoading}
            className="flex items-center gap-1.5 text-xs font-semibold rounded-xl"
            title="Refresh Table"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Aggregate Financial Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
        {/* Total Orders */}
        <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Total Orders
          </span>
          <div className="mt-1 text-lg font-bold text-slate-900 dark:text-white">
            {summary?.total_orders || 0}
          </div>
        </div>

        {/* Total Amount */}
        <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Total Amount
          </span>
          <div className="mt-1 text-lg font-bold text-slate-900 dark:text-white">
            {summary?.formatted_total_amount || formatInr(0)}
          </div>
        </div>

        {/* Advance Amount */}
        <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
            Advance Amount
          </span>
          <div className="mt-1 text-lg font-bold text-emerald-600 dark:text-emerald-400">
            {summary?.formatted_total_advance || formatInr(0)}
          </div>
        </div>

        {/* Pending Amount */}
        <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <span className="text-[11px] font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider">
            Pending Amount
          </span>
          <div className="mt-1 text-lg font-bold text-amber-600 dark:text-amber-400">
            {summary?.formatted_total_pending || formatInr(0)}
          </div>
        </div>

        {/* Govt Fees */}
        <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <span className="text-[11px] font-semibold text-purple-600 dark:text-purple-400 uppercase tracking-wider">
            Govt Fees
          </span>
          <div className="mt-1 text-lg font-bold text-purple-600 dark:text-purple-400">
            {summary?.formatted_total_govt_fees || formatInr(0)}
          </div>
        </div>

        {/* Incidental Cost */}
        <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <span className="text-[11px] font-semibold text-orange-600 dark:text-orange-400 uppercase tracking-wider">
            Incidental Cost
          </span>
          <div className="mt-1 text-lg font-bold text-orange-600 dark:text-orange-400">
            {summary?.formatted_total_incidental_cost || formatInr(0)}
          </div>
        </div>

        {/* Estimated Profit */}
        <div className="col-span-2 sm:col-span-1 p-3.5 rounded-2xl bg-gradient-to-br from-emerald-500/10 via-teal-500/5 to-transparent dark:from-emerald-950/30 dark:via-slate-900 border border-emerald-200 dark:border-emerald-800 shadow-xs">
          <span className="text-[11px] font-bold text-emerald-800 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1">
            <Sparkles className="w-3 h-3" />
            Estimated Profit
          </span>
          <div className="mt-1 text-lg font-black text-emerald-700 dark:text-emerald-400">
            {summary?.formatted_total_profits || formatInr(0)}
          </div>
        </div>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-4 shadow-xs space-y-3">
        {/* Company Selector Tabs & Task Status Tabs */}
        <div className="flex items-center justify-between flex-wrap gap-3 pb-3 border-b border-slate-100 dark:border-slate-800/80">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Company Scope:
            </span>
            <CompanyFilterTabs
              selectedCompanyId={companyId}
              onCompanyChange={handleCompanyChange}
              size="sm"
            />
          </div>

          {/* Task Status Quick Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mr-1">
              Task Status:
            </span>
            <div className="inline-flex p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
              <button
                type="button"
                onClick={() => handleTaskStatusChange('ALL')}
                className={`px-3 py-1 text-xs font-bold rounded-lg transition-colors ${
                  taskStatus === 'ALL'
                    ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                All Tasks
              </button>
              <button
                type="button"
                onClick={() => handleTaskStatusChange('COMPLETED')}
                className={`px-3 py-1 text-xs font-bold rounded-lg transition-colors flex items-center gap-1 ${
                  taskStatus === 'COMPLETED'
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <CheckCircle2 className="w-3 h-3" />
                <span>Completed</span>
              </button>
              <button
                type="button"
                onClick={() => handleTaskStatusChange('PENDING')}
                className={`px-3 py-1 text-xs font-bold rounded-lg transition-colors flex items-center gap-1 ${
                  taskStatus === 'PENDING'
                    ? 'bg-amber-600 text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Clock className="w-3 h-3" />
                <span>Pending</span>
              </button>
            </div>
          </div>
        </div>

        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {/* Global Search */}
          <div className="lg:col-span-2 relative">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search client, work, order #, location..."
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-hidden transition"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          </div>

          {/* Payment Status Filter */}
          <div>
            <select
              value={paymentStatus}
              onChange={(e) => {
                setPaymentStatus(e.target.value);
                setPage(1);
                syncUrl({
                  search,
                  company_id: companyId,
                  payment_status: e.target.value,
                  task_status: taskStatus,
                  from_date: fromDate,
                  to_date: toDate,
                  page: '1',
                });
              }}
              className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-hidden transition font-medium"
            >
              <option value="ALL">All Payment Statuses</option>
              <option value="FULLY_PAID">Fully Paid</option>
              <option value="PARTIALLY_PAID">Partially Paid</option>
              <option value="PENDING">Pending</option>
              <option value="OVERDUE">Overdue</option>
            </select>
          </div>

          {/* From Date */}
          <div>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => {
                setFromDate(e.target.value);
                setPage(1);
                syncUrl({
                  search,
                  company_id: companyId,
                  payment_status: paymentStatus,
                  task_status: taskStatus,
                  from_date: e.target.value,
                  to_date: toDate,
                  page: '1',
                });
              }}
              className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-hidden transition"
              title="Sales Date From"
            />
          </div>

          {/* To Date */}
          <div>
            <input
              type="date"
              value={toDate}
              onChange={(e) => {
                setToDate(e.target.value);
                setPage(1);
                syncUrl({
                  search,
                  company_id: companyId,
                  payment_status: paymentStatus,
                  task_status: taskStatus,
                  from_date: fromDate,
                  to_date: e.target.value,
                  page: '1',
                });
              }}
              className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-hidden transition"
              title="Sales Date To"
            />
          </div>

          {/* Actions: Filter & Reset */}
          <div className="flex items-center gap-2">
            <Button
              type="submit"
              variant="primary"
              size="sm"
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold py-2"
            >
              Filter
            </Button>
            {(search || paymentStatus !== 'ALL' || taskStatus !== 'ALL' || fromDate || toDate) && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleResetFilters}
                className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 rounded-xl px-2.5 py-2"
                title="Reset All Filters"
              >
                Clear
              </Button>
            )}
          </div>
        </form>

        {/* Active Task Filter Badge */}
        {taskStatus !== 'ALL' && (
          <div className="flex items-center gap-2 pt-2 border-t border-slate-100 dark:border-slate-800/60 text-xs">
            <span className="text-slate-500 dark:text-slate-400 font-medium">Active Task Filter:</span>
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full font-bold text-xs ${
                taskStatus === 'COMPLETED'
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800'
                  : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-800'
              }`}
            >
              {taskStatus === 'COMPLETED' ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Completed Tasks (Tax Invoice Issued)</span>
                </>
              ) : (
                <>
                  <Clock className="w-3.5 h-3.5" />
                  <span>Pending Tasks (Invoice Pending / In Progress)</span>
                </>
              )}
              <button
                type="button"
                onClick={() => handleTaskStatusChange('ALL')}
                className="ml-1 hover:opacity-75 font-black text-sm leading-none"
                title="Clear task status filter"
              >
                ×
              </button>
            </span>
          </div>
        )}
      </div>

      {/* 21-Column Accounts Table Container */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs overflow-hidden flex flex-col">
        {isLoading ? (
          <div className="p-16 flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
              Loading accounts entries...
            </p>
          </div>
        ) : error ? (
          <div className="p-12 text-center space-y-4">
            <AlertCircle className="w-10 h-10 text-rose-500 mx-auto" />
            <div className="space-y-1">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Failed to load entries</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">{error}</p>
            </div>
            <Button variant="outline" size="sm" onClick={loadEntries}>
              Retry Loading
            </Button>
          </div>
        ) : !entriesData?.items || entriesData.items.length === 0 ? (
          <div className="p-16 text-center space-y-4">
            <div className="w-14 h-14 rounded-3xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mx-auto border border-indigo-100 dark:border-indigo-900">
              <FileSpreadsheet className="w-7 h-7" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">No entries found</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
                No sales records match your filter criteria in your authorized company scope.
              </p>
            </div>
            <div className="flex items-center justify-center gap-3 pt-2">
              <Button variant="ghost" size="sm" onClick={handleResetFilters}>
                Clear Filters
              </Button>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto w-full">
            <table className="w-full text-left border-collapse text-xs whitespace-nowrap">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200/80 dark:border-slate-800 font-semibold text-slate-600 dark:text-slate-300 select-none">
                  {/* Canonical 21 Columns + Action */}
                  <th className="py-3 px-2 text-center w-[52px] min-w-[52px] max-w-[52px] sticky left-0 bg-slate-50 dark:bg-slate-800 z-30">
                    1. S.No
                  </th>
                  <th className="py-3 px-3.5 w-[100px] min-w-[100px]">2. Date</th>
                  <th className="py-3 px-3.5 sticky left-[52px] w-[180px] min-w-[180px] max-w-[180px] bg-slate-50 dark:bg-slate-800 z-30">
                    3. Client Name
                  </th>
                  <th className="py-3 px-3.5 sticky left-[232px] w-[140px] min-w-[140px] max-w-[140px] bg-slate-50 dark:bg-slate-800 z-30 shadow-[4px_0_8px_-2px_rgba(0,0,0,0.08)] dark:shadow-[4px_0_8px_-2px_rgba(0,0,0,0.35)] border-r border-slate-200 dark:border-slate-700">
                    4. Location
                  </th>
                  <th className="py-3 px-3.5">5. Contact No</th>
                  <th className="py-3 px-3.5">6. Source</th>
                  <th className="py-3 px-4 min-w-[160px]">7. Work</th>
                  <th className="py-3 px-3.5">8. Converted By</th>
                  <th className="py-3 px-3.5">9. Assigned To</th>
                  <th className="py-3 px-3.5">10. Work Status</th>
                  <th className="py-3 px-3.5 text-right font-bold text-slate-900 dark:text-white">
                    11. Total Amount
                  </th>
                  <th className="py-3 px-3.5 text-right font-bold text-emerald-700 dark:text-emerald-400">
                    12. Advance Amount
                  </th>
                  <th className="py-3 px-3.5 text-right font-bold text-amber-700 dark:text-amber-400">
                    13. Pending Amount
                  </th>
                  <th className="py-3 px-3.5 text-center">14. Payment Status</th>
                  <th className="py-3 px-3.5 bg-indigo-50/70 dark:bg-indigo-950/30 text-indigo-900 dark:text-indigo-300 font-bold border-x border-indigo-200 dark:border-indigo-800 min-w-[170px]">
                    15. Proforma Inv. No. ✏️
                  </th>
                  <th className="py-3 px-3.5 bg-emerald-50/70 dark:bg-emerald-950/30 text-emerald-900 dark:text-emerald-300 font-bold border-r border-emerald-200 dark:border-emerald-800 min-w-[170px]">
                    16. Tax Inv. No. ✏️
                  </th>
                  <th className="py-3 px-3.5 bg-indigo-50/70 dark:bg-indigo-950/30 text-indigo-900 dark:text-indigo-300 font-bold border-r border-indigo-200 dark:border-indigo-800 min-w-[200px]">
                    17. Reimbursement Note ✏️
                  </th>
                  <th className="py-3 px-3.5 text-right">18. Govt Fees</th>
                  <th className="py-3 px-3.5 text-right">19. Incidental Cost</th>
                  <th className="py-3 px-3.5 text-right font-bold text-emerald-800 dark:text-emerald-300">
                    20. Profits
                  </th>
                  <th className="py-3 px-4 min-w-[220px] bg-indigo-50/70 dark:bg-indigo-950/30 text-indigo-900 dark:text-indigo-300 font-bold border-x border-indigo-200 dark:border-indigo-800">
                    21. Remarks ✏️
                  </th>
                  <th className="py-3 px-3 text-center sticky right-0 bg-slate-50 dark:bg-slate-800 z-30 shadow-[-4px_0_8px_-2px_rgba(0,0,0,0.06)] border-l border-slate-200 dark:border-slate-800 min-w-[70px]">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
                {entriesData.items.map((row) => {
                  const unreadInfo = unreadSummary?.unread_orders?.[row.order_id];
                  const hasUnread = Boolean(unreadInfo && unreadInfo.unread_count > 0);

                  return (
                    <tr
                      key={row.order_id}
                      className={`transition-colors group ${
                        hasUnread
                          ? 'bg-blue-50/70 dark:bg-blue-950/40 border-l-4 border-l-blue-600 dark:border-l-blue-500 hover:bg-blue-100/60 dark:hover:bg-blue-900/50'
                          : 'hover:bg-slate-50/80 dark:hover:bg-slate-800/40'
                      }`}
                    >
                      {/* 1. S.No (Sticky) */}
                      <td className="py-3 px-2 text-center font-mono text-slate-400 font-semibold sticky left-0 w-[52px] min-w-[52px] max-w-[52px] bg-white dark:bg-slate-900 group-hover:bg-slate-50 dark:group-hover:bg-slate-800/80 z-20">
                        {row.s_no}
                      </td>

                      {/* 2. Date */}
                      <td className="py-3 px-3.5 text-slate-700 dark:text-slate-300 font-medium w-[100px] min-w-[100px]">
                        {row.formatted_date || row.order_date}
                      </td>

                      {/* 3. Client Name (Sticky) */}
                      <td className="py-3 px-3.5 font-semibold text-slate-900 dark:text-white sticky left-[52px] w-[180px] min-w-[180px] max-w-[180px] bg-white dark:bg-slate-900 group-hover:bg-slate-50 dark:group-hover:bg-slate-800/80 z-20">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-1.5 truncate">
                            <span className="truncate font-semibold" title={row.client_name}>
                              {row.client_name}
                            </span>
                            {row.confirmation_status === 'CONFIRMED' && (
                              <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 shrink-0">
                                Confirmed
                              </span>
                            )}
                          </div>
                          <CompanyBadge
                            companyName={row.company_name}
                            companyCode={row.company_code}
                            size="xs"
                          />
                        </div>
                      </td>

                      {/* 4. Location (Sticky) */}
                      <td className="py-3 px-3.5 text-slate-600 dark:text-slate-300 sticky left-[232px] w-[140px] min-w-[140px] max-w-[140px] bg-white dark:bg-slate-900 group-hover:bg-slate-50 dark:group-hover:bg-slate-800/80 z-20 shadow-[4px_0_8px_-2px_rgba(0,0,0,0.08)] dark:shadow-[4px_0_8px_-2px_rgba(0,0,0,0.35)] border-r border-slate-100 dark:border-slate-800">
                        {row.location ? (
                          <div className="inline-flex items-center gap-1 font-medium text-slate-700 dark:text-slate-300 truncate max-w-full" title={row.location}>
                            <MapPin className="w-3 h-3 text-indigo-500 shrink-0" />
                            <span className="truncate">{row.location}</span>
                          </div>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>

                      {/* 5. Contact No */}
                      <td className="py-3 px-3.5 text-slate-600 dark:text-slate-400 font-mono">
                        {row.contact_no || '—'}
                      </td>

                      {/* 6. Source */}
                      <td className="py-3 px-3.5">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                          {row.lead_source}
                        </span>
                      </td>

                      {/* 7. Work */}
                      <td className="py-3 px-4 text-slate-800 dark:text-slate-200 font-medium">
                        {row.service_name}
                      </td>

                      {/* 8. Converted By */}
                      <td className="py-3 px-3.5 text-slate-700 dark:text-slate-300">
                        <div className="font-medium">{row.salesperson_name}</div>
                        {row.salesperson_code && (
                          <div className="text-[10px] text-slate-400 font-mono">{row.salesperson_code}</div>
                        )}
                      </td>

                      {/* 9. Assigned To */}
                      <td className="py-3 px-3.5 text-slate-600 dark:text-slate-400">
                        {row.assigned_to_name && row.assigned_to_name !== 'Unassigned' ? (
                          <div>
                            <span className="font-medium text-slate-900 dark:text-slate-100">
                              {row.assigned_to_name}
                            </span>
                            {row.assigned_to_code && (
                              <span className="text-[10px] text-slate-400 font-mono ml-1">
                                ({row.assigned_to_code})
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="text-[11px] text-slate-400 italic">Unassigned</span>
                        )}
                      </td>

                      {/* 10. Work Status */}
                      <td className="py-3 px-3.5">
                        {renderWorkStatusBadge(row.work_status || row.operation_status || 'UNASSIGNED')}
                      </td>

                      {/* 11. Total Amount */}
                      <td className="py-3 px-3.5 text-right font-mono font-bold text-slate-900 dark:text-white">
                        {row.formatted_order_value}
                      </td>

                      {/* 12. Advance Amount */}
                      <td className="py-3 px-3.5 text-right font-mono font-bold text-emerald-600 dark:text-emerald-400">
                        {row.formatted_amount_received}
                      </td>

                      {/* 13. Pending Amount */}
                      <td className="py-3 px-3.5 text-right font-mono font-bold text-amber-600 dark:text-amber-400">
                        {row.formatted_balance_amount}
                      </td>

                      {/* 14. Payment Status */}
                      <td className="py-3 px-3.5 text-center">
                        {renderPaymentBadge(row.payment_status)}
                      </td>

                      {/* 15. Proforma Inv. No. (Direct Inline Click-to-Edit) */}
                      <td
                        className="py-1.5 px-2 font-mono text-xs bg-indigo-50/20 dark:bg-indigo-950/10 min-w-[160px] relative group/cell"
                        onClick={(e) => {
                          if (!isCellActive(row.order_id, 'proforma_invoice_no')) {
                            handleStartCellEdit(row.order_id, 'proforma_invoice_no', row.proforma_invoice_no, e);
                          }
                        }}
                      >
                        {isCellActive(row.order_id, 'proforma_invoice_no') ? (
                          <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                            <input
                              ref={inputRef}
                              type="text"
                              autoFocus
                              value={activeValue}
                              onChange={(e) => setActiveValue(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  handleCommitCellEdit(row.order_id, 'proforma_invoice_no', activeValue, row.proforma_invoice_no);
                                } else if (e.key === 'Escape') {
                                  setActiveCell(null);
                                }
                              }}
                              onBlur={() => {
                                handleCommitCellEdit(row.order_id, 'proforma_invoice_no', activeValue, row.proforma_invoice_no);
                              }}
                              placeholder="Enter Proforma Inv #"
                              className="w-full px-2 py-1 text-xs font-mono font-medium rounded-lg bg-white dark:bg-slate-800 border-2 border-indigo-500 text-slate-900 dark:text-white shadow-xs outline-hidden"
                            />
                            {isCellSaving(row.order_id, 'proforma_invoice_no') && (
                              <RefreshCw className="w-3.5 h-3.5 text-indigo-600 animate-spin shrink-0" />
                            )}
                          </div>
                        ) : (
                          <div className="flex items-center justify-between gap-1.5 cursor-pointer py-1 px-1.5 rounded-lg hover:bg-indigo-100/60 dark:hover:bg-indigo-900/40 border border-transparent hover:border-indigo-300 dark:hover:border-indigo-700 transition">
                            {row.proforma_invoice_no ? (
                              <span className="inline-flex items-center gap-1 font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded-md border border-indigo-200/60 dark:border-indigo-800 truncate">
                                {row.proforma_invoice_no}
                              </span>
                            ) : (
                              <span className="text-slate-400 italic text-[11px]">Click to enter —</span>
                            )}
                            {lastSavedCell === `${row.order_id}_proforma_invoice_no` ? (
                              <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                            ) : (
                              <Edit className="w-3 h-3 text-indigo-400 opacity-0 group-hover/cell:opacity-100 shrink-0 transition" />
                            )}
                          </div>
                        )}
                      </td>

                      {/* 16. Tax Inv. No. (Direct Inline Click-to-Edit) */}
                      <td
                        className="py-1.5 px-2 font-mono text-xs bg-emerald-50/20 dark:bg-emerald-950/10 min-w-[160px] relative group/cell"
                        onClick={(e) => {
                          if (!isCellActive(row.order_id, 'tax_invoice_no')) {
                            handleStartCellEdit(row.order_id, 'tax_invoice_no', row.tax_invoice_no, e);
                          }
                        }}
                      >
                        {isCellActive(row.order_id, 'tax_invoice_no') ? (
                          <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                            <input
                              type="text"
                              autoFocus
                              value={activeValue}
                              onChange={(e) => setActiveValue(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  handleCommitCellEdit(row.order_id, 'tax_invoice_no', activeValue, row.tax_invoice_no);
                                } else if (e.key === 'Escape') {
                                  setActiveCell(null);
                                }
                              }}
                              onBlur={() => {
                                handleCommitCellEdit(row.order_id, 'tax_invoice_no', activeValue, row.tax_invoice_no);
                              }}
                              placeholder="Enter Tax Inv #"
                              className="w-full px-2 py-1 text-xs font-mono font-medium rounded-lg bg-white dark:bg-slate-800 border-2 border-emerald-500 text-slate-900 dark:text-white shadow-xs outline-hidden"
                            />
                            {isCellSaving(row.order_id, 'tax_invoice_no') && (
                              <RefreshCw className="w-3.5 h-3.5 text-emerald-600 animate-spin shrink-0" />
                            )}
                          </div>
                        ) : (
                          <div className="flex items-center justify-between gap-1.5 cursor-pointer py-1 px-1.5 rounded-lg hover:bg-emerald-100/60 dark:hover:bg-emerald-900/40 border border-transparent hover:border-emerald-300 dark:hover:border-emerald-700 transition">
                            {row.tax_invoice_no ? (
                              <span className="inline-flex items-center gap-1 font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-md border border-emerald-200/60 dark:border-emerald-800 truncate">
                                {row.tax_invoice_no}
                              </span>
                            ) : (
                              <span className="text-slate-400 italic text-[11px]">Click to enter —</span>
                            )}
                            {lastSavedCell === `${row.order_id}_tax_invoice_no` ? (
                              <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                            ) : (
                              <Edit className="w-3 h-3 text-emerald-400 opacity-0 group-hover/cell:opacity-100 shrink-0 transition" />
                            )}
                          </div>
                        )}
                      </td>

                      {/* 17. Reimbursement Note (Direct Inline Click-to-Edit) */}
                      <td
                        className="py-1.5 px-2 text-xs bg-indigo-50/20 dark:bg-indigo-950/10 min-w-[200px] relative group/cell"
                        onClick={(e) => {
                          if (!isCellActive(row.order_id, 'reimbursement_note')) {
                            handleStartCellEdit(row.order_id, 'reimbursement_note', row.reimbursement_note, e);
                          }
                        }}
                      >
                        {isCellActive(row.order_id, 'reimbursement_note') ? (
                          <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                            <input
                              type="text"
                              autoFocus
                              value={activeValue}
                              onChange={(e) => setActiveValue(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  handleCommitCellEdit(row.order_id, 'reimbursement_note', activeValue, row.reimbursement_note);
                                } else if (e.key === 'Escape') {
                                  setActiveCell(null);
                                }
                              }}
                              onBlur={() => {
                                handleCommitCellEdit(row.order_id, 'reimbursement_note', activeValue, row.reimbursement_note);
                              }}
                              placeholder="Enter reimbursement note..."
                              className="w-full px-2 py-1 text-xs rounded-lg bg-white dark:bg-slate-800 border-2 border-indigo-500 text-slate-900 dark:text-white shadow-xs outline-hidden"
                            />
                            {isCellSaving(row.order_id, 'reimbursement_note') && (
                              <RefreshCw className="w-3.5 h-3.5 text-indigo-600 animate-spin shrink-0" />
                            )}
                          </div>
                        ) : (
                          <div className="flex items-center justify-between gap-1.5 cursor-pointer py-1 px-1.5 rounded-lg hover:bg-indigo-100/60 dark:hover:bg-indigo-900/40 border border-transparent hover:border-indigo-300 dark:hover:border-indigo-700 transition" title={row.reimbursement_note || 'Click to edit'}>
                            <span className="text-slate-700 dark:text-slate-300 truncate">
                              {row.reimbursement_note || <span className="text-slate-400 italic text-[11px]">Click to enter —</span>}
                            </span>
                            {lastSavedCell === `${row.order_id}_reimbursement_note` ? (
                              <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                            ) : (
                              <Edit className="w-3 h-3 text-indigo-400 opacity-0 group-hover/cell:opacity-100 shrink-0 transition" />
                            )}
                          </div>
                        )}
                      </td>

                      {/* 18. Govt Fees */}
                      <td className="py-3 px-3.5 text-right font-mono text-slate-600 dark:text-slate-400">
                        {row.formatted_govt_fees}
                      </td>

                      {/* 19. Incidental Cost */}
                      <td className="py-3 px-3.5 text-right font-mono text-slate-600 dark:text-slate-400">
                        {row.formatted_incidental_cost}
                      </td>

                      {/* 20. Profits */}
                      <td className="py-3 px-3.5 text-right font-mono font-bold text-emerald-700 dark:text-emerald-400">
                        {row.formatted_profit_amount}
                      </td>

                      {/* 21. Remarks / Shared Conversation */}
                      <td
                        className="py-1.5 px-2 text-xs bg-indigo-50/20 dark:bg-indigo-950/10 min-w-[220px] relative group/cell cursor-pointer"
                        onClick={(e) => {
                          e.stopPropagation();
                          setConversationOrderId(row.order_id);
                          setIsConversationOpen(true);
                        }}
                        title={unreadInfo?.latest_remark_text || row.remarks || row.notes || 'Click to open shared conversation thread'}
                      >
                        {hasUnread ? (
                          <div className="flex flex-col gap-1 p-1.5 rounded-lg bg-blue-100/90 dark:bg-blue-900/60 border border-blue-300 dark:border-blue-700 hover:border-blue-400 transition shadow-xs">
                            <div className="flex items-center justify-between gap-1">
                              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-600 text-white dark:bg-blue-500 shadow-xs">
                                <MessageSquare className="w-2.5 h-2.5" />
                                <span>New update ({unreadInfo?.unread_count})</span>
                              </span>
                              {unreadInfo?.latest_author_name && (
                                <span className="text-[10px] font-semibold text-blue-800 dark:text-blue-300 truncate max-w-[80px]">
                                  {unreadInfo.latest_author_name}
                                </span>
                              )}
                            </div>
                            <span className="text-xs text-slate-800 dark:text-slate-100 truncate font-medium">
                              {unreadInfo?.latest_remark_text || row.remarks || row.notes}
                            </span>
                          </div>
                        ) : (
                          <div className="flex items-center justify-between gap-1.5 py-1 px-1.5 rounded-lg hover:bg-indigo-100/60 dark:hover:bg-indigo-900/40 border border-transparent hover:border-indigo-300 dark:hover:border-indigo-700 transition">
                            <span className="text-slate-700 dark:text-slate-300 truncate font-medium">
                              {row.remarks || row.notes || <span className="text-slate-400 italic text-[11px]">Click to add remark —</span>}
                            </span>
                            <span className="p-1 rounded-md text-indigo-500 hover:text-indigo-700 hover:bg-white/80 dark:hover:bg-slate-800 transition shrink-0" title="Open Conversation Thread">
                              <MessageSquare className="w-3.5 h-3.5" />
                            </span>
                          </div>
                        )}
                      </td>

                      {/* 22. Action Column */}
                      <td className="py-2.5 px-3 text-center sticky right-0 bg-white dark:bg-slate-900 group-hover:bg-slate-50 dark:group-hover:bg-slate-800/80 z-20 shadow-[-4px_0_8px_-2px_rgba(0,0,0,0.06)] border-l border-slate-200 dark:border-slate-800">
                        <div className="flex items-center justify-center gap-1">
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={(e) => handleStartCellEdit(row.order_id, 'proforma_invoice_no', row.proforma_invoice_no, e)}
                            className="p-1.5 h-7 w-7 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 rounded-lg"
                            title="Click to edit invoice details"
                          >
                            <Edit className="w-3.5 h-3.5" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Table Footer / Pagination Controls */}
        {!isLoading && entriesData && entriesData.items.length > 0 && (
          <div className="px-4 py-3 border-t border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500 dark:text-slate-400">
            <div>
              Showing <span className="font-semibold text-slate-800 dark:text-slate-200">{(page - 1) * limit + 1}</span> to{' '}
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {Math.min(page * limit, entriesData.total_count)}
              </span>{' '}
              of <span className="font-semibold text-slate-800 dark:text-slate-200">{entriesData.total_count}</span> entries
            </div>

            <div className="flex items-center gap-1.5">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setPage((p) => Math.max(1, p - 1));
                  syncUrl({
                    search,
                    payment_status: paymentStatus,
                    from_date: fromDate,
                    to_date: toDate,
                    page: String(Math.max(1, page - 1)),
                  });
                }}
                disabled={page <= 1 || isLoading}
                className="rounded-xl flex items-center gap-1"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Prev</span>
              </Button>

              <div className="px-2 font-medium text-slate-700 dark:text-slate-300">
                Page {page} of {totalPages}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setPage((p) => Math.min(totalPages, p + 1));
                  syncUrl({
                    search,
                    payment_status: paymentStatus,
                    from_date: fromDate,
                    to_date: toDate,
                    page: String(Math.min(totalPages, page + 1)),
                  });
                }}
                disabled={page >= totalPages || isLoading}
                className="rounded-xl flex items-center gap-1"
              >
                <span>Next</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Shared Task Conversation Modal */}
      <TaskConversationModal
        isOpen={isConversationOpen}
        onClose={() => {
          setIsConversationOpen(false);
          setConversationOrderId(null);
        }}
        orderId={conversationOrderId}
        onMessagePosted={loadEntries}
      />
    </div>
  );
};

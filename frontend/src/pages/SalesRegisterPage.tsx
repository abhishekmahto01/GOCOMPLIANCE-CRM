import React, { useState, useEffect, useCallback } from 'react';
import { Link, useOutletContext, useSearchParams } from 'react-router-dom';
import {
  FileSpreadsheet,
  FilePlus2,
  Download,
  Search,
  RotateCcw,
  CheckCircle2,
  Clock,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  UserCheck,
  AlertTriangle,
  Send,
  Edit,
  Save,
} from 'lucide-react';
import {
  getSalesRegisterApi,
  exportSalesRegisterCsvApi,
  getSalesFormOptionsApi,
  assignSalesOrderApi,
  updateSalesOrderApi,
} from '../api/sales';
import { extractErrorMessage } from '../api/client';
import type {
  SalesRegisterItem,
  SalesRegisterResponse,
  SalesRegisterFilterParams,
  SalesFormOptionsResponse,
} from '../types/sales';
import { Button } from '../components/ui/button';
import { Modal } from '../components/ui/modal';

interface OutletContextType {
  addToast?: (type: 'success' | 'error' | 'info', title: string, message: string) => void;
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

export const SalesRegisterPage: React.FC = () => {
  const outletCtx = useOutletContext<OutletContextType>();
  const [searchParams, setSearchParams] = useSearchParams();

  // Search & Filter State
  const [search, setSearch] = useState<string>(searchParams.get('search') || '');
  const [paymentStatus, setPaymentStatus] = useState<string>(searchParams.get('payment_status') || 'ALL');
  const [workStatus, setWorkStatus] = useState<string>(searchParams.get('work_status') || 'ALL');
  const [employeeId, setEmployeeId] = useState<string>(searchParams.get('employee_id') || 'ALL');
  const [serviceId, setServiceId] = useState<string>(searchParams.get('service_id') || 'ALL');
  const [fromDate, setFromDate] = useState<string>(searchParams.get('from_date') || '');
  const [toDate, setToDate] = useState<string>(searchParams.get('to_date') || '');
  const [page, setPage] = useState<number>(Number(searchParams.get('page')) || 1);
  const [limit, setLimit] = useState<number>(Number(searchParams.get('limit')) || 25);

  // Data & State
  const [registerData, setRegisterData] = useState<SalesRegisterResponse | null>(null);
  const [formOptions, setFormOptions] = useState<SalesFormOptionsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Order Details Modal
  const [selectedOrder, setSelectedOrder] = useState<SalesRegisterItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Assign Work Modal State (Operations Manager Handoff)
  const [isAssignModalOpen, setIsAssignModalOpen] = useState<boolean>(false);
  const [assigningOrder, setAssigningOrder] = useState<SalesRegisterItem | null>(null);
  const [selectedAssigneeId, setSelectedAssigneeId] = useState<string>('');
  const [assignmentPriority, setAssignmentPriority] = useState<string>('MEDIUM');
  const [assignmentDueDate, setAssignmentDueDate] = useState<string>('');
  const [assignmentNotes, setAssignmentNotes] = useState<string>('');
  const [isAssigning, setIsAssigning] = useState<boolean>(false);
  const [assignError, setAssignError] = useState<string | null>(null);

  // Edit Sales Order Modal State
  const [isEditModalOpen, setIsEditModalOpen] = useState<boolean>(false);
  const [editingOrder, setEditingOrder] = useState<SalesRegisterItem | null>(null);
  const [editClientName, setEditClientName] = useState<string>('');
  const [editContactNo, setEditContactNo] = useState<string>('');
  const [editSalespersonId, setEditSalespersonId] = useState<string>('');
  const [editLeadSource, setEditLeadSource] = useState<string>('WEBSITE');
  const [editOrderDate, setEditOrderDate] = useState<string>('');
  const [editOrderValue, setEditOrderValue] = useState<number>(0);
  const [editAmountReceived, setEditAmountReceived] = useState<number>(0);
  const [editGovtFees, setEditGovtFees] = useState<number>(0);
  const [editIncidentalCost, setEditIncidentalCost] = useState<number>(0);
  const [editProformaInvoiceNo, setEditProformaInvoiceNo] = useState<string>('');
  const [editTaxInvoiceNo, setEditTaxInvoiceNo] = useState<string>('');
  const [editReimbursementNote, setEditReimbursementNote] = useState<string>('');
  const [editNotes, setEditNotes] = useState<string>('');
  const [isSavingEdit, setIsSavingEdit] = useState<boolean>(false);
  const [editError, setEditError] = useState<string | null>(null);

  // Sync state with URL params
  const syncUrl = useCallback(
    (newParams: Record<string, string>) => {
      const p: Record<string, string> = {};
      if (newParams.search) p.search = newParams.search;
      if (newParams.payment_status && newParams.payment_status !== 'ALL') p.payment_status = newParams.payment_status;
      if (newParams.work_status && newParams.work_status !== 'ALL') p.work_status = newParams.work_status;
      if (newParams.employee_id && newParams.employee_id !== 'ALL') p.employee_id = newParams.employee_id;
      if (newParams.service_id && newParams.service_id !== 'ALL') p.service_id = newParams.service_id;
      if (newParams.from_date) p.from_date = newParams.from_date;
      if (newParams.to_date) p.to_date = newParams.to_date;
      if (newParams.page && Number(newParams.page) > 1) p.page = newParams.page;
      if (newParams.limit && Number(newParams.limit) !== 25) p.limit = newParams.limit;
      setSearchParams(p, { replace: true });
    },
    [setSearchParams]
  );

  // Load Form Options for Filters & Operations Assignees
  useEffect(() => {
    let isMounted = true;
    async function loadOptions() {
      try {
        const data = await getSalesFormOptionsApi();
        if (isMounted) setFormOptions(data);
      } catch (err) {
        console.error('Failed to load filter options:', err);
      }
    }
    loadOptions();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch Sales Register Data
  const loadRegister = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: SalesRegisterFilterParams = {
        page,
        limit,
        search: search.trim() || undefined,
        payment_status: paymentStatus !== 'ALL' ? paymentStatus : undefined,
        work_status: workStatus !== 'ALL' ? workStatus : undefined,
        employee_id: employeeId !== 'ALL' ? employeeId : undefined,
        service_id: serviceId !== 'ALL' ? serviceId : undefined,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
      };
      const data = await getSalesRegisterApi(params);
      setRegisterData(data);
    } catch (err) {
      console.error('Failed to load sales register:', err);
      const msg = extractErrorMessage(err);
      setError(msg);
      outletCtx.addToast?.('error', 'Failed to Load Sales Register', msg);
    } finally {
      setIsLoading(false);
    }
  }, [page, limit, search, paymentStatus, workStatus, employeeId, serviceId, fromDate, toDate]);

  useEffect(() => {
    loadRegister();
  }, [loadRegister]);

  // Handle Search input submit
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    syncUrl({
      search,
      payment_status: paymentStatus,
      work_status: workStatus,
      employee_id: employeeId,
      service_id: serviceId,
      from_date: fromDate,
      to_date: toDate,
      page: '1',
      limit: String(limit),
    });
  };

  // Reset Filters
  const handleResetFilters = () => {
    setSearch('');
    setPaymentStatus('ALL');
    setWorkStatus('ALL');
    setEmployeeId('ALL');
    setServiceId('ALL');
    setFromDate('');
    setToDate('');
    setPage(1);
    setSearchParams({}, { replace: true });
  };

  // Export CSV Handler
  const handleExportCsv = async () => {
    setIsExporting(true);
    try {
      const { blob, filename } = await exportSalesRegisterCsvApi({
        search: search.trim() || undefined,
        payment_status: paymentStatus !== 'ALL' ? paymentStatus : undefined,
        work_status: workStatus !== 'ALL' ? workStatus : undefined,
        employee_id: employeeId !== 'ALL' ? employeeId : undefined,
        service_id: serviceId !== 'ALL' ? serviceId : undefined,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      outletCtx.addToast?.('success', 'Export Successful', `Sales Register downloaded as ${filename}`);
    } catch (err) {
      console.error('Export CSV error:', err);
      const msg = extractErrorMessage(err);
      outletCtx.addToast?.('error', 'Export Failed', msg);
    } finally {
      setIsExporting(false);
    }
  };

  // View Row Details Modal
  const handleRowClick = (item: SalesRegisterItem) => {
    setSelectedOrder(item);
    setIsModalOpen(true);
  };

  // Open Assign Work Modal
  const handleOpenAssignModal = (item: SalesRegisterItem, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setAssigningOrder(item);
    setSelectedAssigneeId(item.assigned_to_user_id || '');
    setAssignmentPriority('MEDIUM');
    setAssignmentDueDate('');
    setAssignmentNotes('');
    setAssignError(null);
    setIsAssignModalOpen(true);
  };

  // Submit Operations Task Assignment
  const handleAssignSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assigningOrder) return;
    if (!selectedAssigneeId) {
      setAssignError('Please select an eligible Operations employee');
      return;
    }

    setIsAssigning(true);
    setAssignError(null);
    try {
      const updatedItem = await assignSalesOrderApi(assigningOrder.order_id, {
        assignee_user_id: selectedAssigneeId,
        priority: assignmentPriority,
        target_due_date: assignmentDueDate || undefined,
        notes: assignmentNotes || undefined,
      });

      const assigneeName = updatedItem.assigned_to_name || 'Operations team member';
      outletCtx.addToast?.(
        'success',
        'Work Assigned Successfully',
        `Order ${updatedItem.order_number} has been assigned to ${assigneeName}.`
      );

      // Refresh list & modal view
      setIsAssignModalOpen(false);
      if (selectedOrder && selectedOrder.order_id === updatedItem.order_id) {
        setSelectedOrder(updatedItem);
      }
      loadRegister();
    } catch (err) {
      console.error('Assignment error:', err);
      const msg = extractErrorMessage(err);
      setAssignError(msg);
      outletCtx.addToast?.('error', 'Assignment Failed', msg);
    } finally {
      setIsAssigning(false);
    }
  };

  // Open Edit Order Modal
  const handleOpenEditModal = (item: SalesRegisterItem, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setEditingOrder(item);
    setEditClientName(item.client_name || '');
    setEditContactNo(item.contact_no || '');
    setEditSalespersonId(item.salesperson_user_id || '');
    setEditLeadSource(item.lead_source || 'DIRECT');
    setEditOrderDate(item.order_date || new Date().toISOString().slice(0, 10));
    setEditOrderValue(Number(item.order_value) || 0);
    setEditAmountReceived(Number(item.amount_received) || 0);
    setEditGovtFees(Number(item.govt_fees) || 0);
    setEditIncidentalCost(Number(item.incidental_cost) || 0);
    setEditProformaInvoiceNo(item.proforma_invoice_no || '');
    setEditTaxInvoiceNo(item.tax_invoice_no || '');
    setEditReimbursementNote(item.reimbursement_note || '');
    setEditNotes(item.notes || item.remarks || '');
    setEditError(null);
    setIsEditModalOpen(true);
  };

  // Submit Sales Order Edit
  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingOrder) return;

    if (editOrderValue < 0) {
      setEditError('Total Amount cannot be negative');
      return;
    }
    if (editAmountReceived < 0) {
      setEditError('Advance / Received Amount cannot be negative');
      return;
    }
    if (editAmountReceived > editOrderValue) {
      setEditError('Advance Amount cannot exceed Total Amount');
      return;
    }
    if (editGovtFees < 0 || editIncidentalCost < 0) {
      setEditError('Govt Fees and Incidental Cost cannot be negative');
      return;
    }

    setIsSavingEdit(true);
    setEditError(null);
    try {
      const updatedItem = await updateSalesOrderApi(editingOrder.order_id, {
        client_name: editClientName.trim() || undefined,
        contact_no: editContactNo.trim() || undefined,
        salesperson_user_id: editSalespersonId && editSalespersonId !== editingOrder.salesperson_user_id ? editSalespersonId : undefined,
        lead_source: editLeadSource,
        order_date: editOrderDate,
        order_value: editOrderValue,
        amount_received: editAmountReceived,
        govt_fees: editGovtFees,
        incidental_cost: editIncidentalCost,
        proforma_invoice_no: editProformaInvoiceNo.trim() || undefined,
        tax_invoice_no: editTaxInvoiceNo.trim() || undefined,
        reimbursement_note: editReimbursementNote.trim() || undefined,
        notes: editNotes.trim() || undefined,
      });

      outletCtx.addToast?.(
        'success',
        'Sales Order Updated',
        `Order ${updatedItem.order_number} has been updated successfully.`
      );

      setIsEditModalOpen(false);
      if (selectedOrder && selectedOrder.order_id === updatedItem.order_id) {
        setSelectedOrder(updatedItem);
      }
      loadRegister();
    } catch (err) {
      console.error('Edit error:', err);
      const msg = extractErrorMessage(err);
      setEditError(msg);
      outletCtx.addToast?.('error', 'Update Failed', msg);
    } finally {
      setIsSavingEdit(false);
    }
  };

  const summary = registerData?.summary;
  const operationsAssignees = formOptions?.operations_assignees || [];

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1600px] mx-auto w-full space-y-6">
      {/* Top Header & Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-600 dark:text-blue-400">
              Sales Ledger & Operations Handoff
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-3">
            <span className="p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-sky-500/20 dark:from-blue-500/30 dark:to-cyan-500/30 border border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-400">
              <FileSpreadsheet className="w-6 h-6" />
            </span>
            Sales Register
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Official 20-column ledger showing conversion dates, fee breakdowns, profit balances, and operations statuses.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            variant="outline"
            size="md"
            onClick={handleExportCsv}
            isLoading={isExporting}
            leftIcon={<Download className="w-4 h-4" />}
          >
            Export CSV
          </Button>

          <Link to="/sales/entry">
            <Button
              variant="primary"
              size="md"
              leftIcon={<FilePlus2 className="w-4 h-4" />}
              className="shadow-button-glow"
            >
              + New Sales Entry
            </Button>
          </Link>
        </div>
      </div>

      {/* Top KPI Summary Ribbon */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* Total Orders */}
        <div className="p-4 rounded-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Total Orders
          </span>
          <div className="mt-1.5 text-xl font-bold text-slate-900 dark:text-white">
            {summary?.total_orders || 0}
          </div>
        </div>

        {/* Total Sales */}
        <div className="p-4 rounded-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Total Sales
          </span>
          <div className="mt-1.5 text-xl font-bold text-blue-600 dark:text-blue-400">
            {formatInr(summary?.total_sales || 0)}
          </div>
        </div>

        {/* Total Advance */}
        <div className="p-4 rounded-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Total Advance
          </span>
          <div className="mt-1.5 text-xl font-bold text-emerald-600 dark:text-emerald-400">
            {formatInr(summary?.total_advance || 0)}
          </div>
        </div>

        {/* Total Pending */}
        <div className="p-4 rounded-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Total Pending
          </span>
          <div className="mt-1.5 text-xl font-bold text-amber-600 dark:text-amber-400">
            {formatInr(summary?.total_pending || 0)}
          </div>
        </div>

        {/* Total Govt Fees */}
        <div className="p-4 rounded-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Govt & Incidental
          </span>
          <div className="mt-1.5 text-xl font-bold text-slate-700 dark:text-slate-300">
            {formatInr(Number(summary?.total_govt_fees || 0) + Number(summary?.total_incidental_cost || 0))}
          </div>
        </div>

        {/* Total Net Profits */}
        <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500/10 via-sky-500/5 to-transparent dark:from-emerald-950/30 dark:via-slate-900 border border-emerald-200/80 dark:border-emerald-800/60 shadow-sm">
          <span className="text-[11px] font-bold text-emerald-800 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1">
            <Sparkles className="w-3 h-3" />
            Net Profits
          </span>
          <div className="mt-1.5 text-xl font-black text-emerald-700 dark:text-emerald-400">
            {formatInr(summary?.total_profits || 0)}
          </div>
        </div>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm space-y-4">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-3">
          {/* Global Search */}
          <div className="lg:col-span-2 relative">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search client, phone, order #, invoices..."
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
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
              }}
              className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="ALL">Payment: All</option>
              <option value="FULLY_PAID">Fully Paid</option>
              <option value="PARTIALLY_PAID">Partially Paid</option>
              <option value="PENDING">Pending</option>
              <option value="OVERDUE">Overdue</option>
            </select>
          </div>

          {/* Work Status Filter */}
          <div>
            <select
              value={workStatus}
              onChange={(e) => {
                setWorkStatus(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="ALL">Work Status: All</option>
              <option value="COMPLETED">Completed</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="ASSIGNED">Assigned</option>
              <option value="UNASSIGNED">Unassigned</option>
            </select>
          </div>

          {/* Converted By (Salesperson) Filter */}
          <div>
            <select
              value={employeeId}
              onChange={(e) => {
                setEmployeeId(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="ALL">Converted By: All</option>
              {(formOptions?.salespersons || []).map((sp) => (
                <option key={sp.user_id} value={sp.user_id}>
                  {sp.full_name}
                </option>
              ))}
            </select>
          </div>

          {/* Work (Service) Filter */}
          <div>
            <select
              value={serviceId}
              onChange={(e) => {
                setServiceId(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="ALL">Work: All Services</option>
              {(formOptions?.services || []).map((srv) => (
                <option key={srv.service_id} value={srv.service_id}>
                  {srv.service_name}
                </option>
              ))}
            </select>
          </div>

          {/* Action Buttons: Apply & Reset */}
          <div className="flex items-center gap-2">
            <Button type="submit" variant="primary" size="sm" className="flex-1">
              Filter
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleResetFilters}
              title="Reset Filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </Button>
          </div>
        </form>
      </div>

      {/* 20-Column Sales Register Table Container */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 rounded-3xl shadow-sm overflow-hidden flex flex-col">
        {isLoading ? (
          <div className="p-12 flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 rounded-full border-2 border-blue-600 border-t-transparent animate-spin" />
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
              Loading 20-column sales records...
            </p>
          </div>
        ) : error ? (
          <div className="p-12 text-center space-y-4">
            <AlertCircle className="w-10 h-10 text-rose-500 mx-auto" />
            <div className="space-y-1">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Failed to load register</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">{error}</p>
            </div>
            <Button variant="outline" size="sm" onClick={loadRegister} leftIcon={<RotateCcw className="w-3.5 h-3.5" />}>
              Retry Loading
            </Button>
          </div>
        ) : !registerData?.items || registerData.items.length === 0 ? (
          <div className="p-16 text-center space-y-4">
            <div className="w-14 h-14 rounded-3xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 flex items-center justify-center mx-auto border border-blue-100 dark:border-blue-900">
              <FileSpreadsheet className="w-7 h-7" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">No sales records found</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
                No orders match your filter criteria. Create your first sales entry or reset your filters.
              </p>
            </div>
            <div className="flex items-center justify-center gap-3 pt-2">
              <Button variant="ghost" size="sm" onClick={handleResetFilters}>
                Clear Filters
              </Button>
              <Link to="/sales/entry">
                <Button variant="primary" size="sm" leftIcon={<FilePlus2 className="w-4 h-4" />}>
                  + New Sales Entry
                </Button>
              </Link>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto w-full">
            <table className="w-full text-left border-collapse text-xs whitespace-nowrap">
              <thead>
                <tr className="bg-slate-50/80 dark:bg-slate-800/60 border-b border-slate-200/80 dark:border-slate-800 font-semibold text-slate-600 dark:text-slate-300 select-none">
                  {/* Exact Sequence of 20 Columns */}
                  <th className="py-3 px-3.5 text-center w-12 sticky left-0 bg-slate-50 dark:bg-slate-800 z-10">1. S.No</th>
                  <th className="py-3 px-3.5">2. Date</th>
                  <th className="py-3 px-4 min-w-[180px]">3. Client Name</th>
                  <th className="py-3 px-3.5">4. Contact No</th>
                  <th className="py-3 px-3.5">5. Source</th>
                  <th className="py-3 px-4 min-w-[160px]">6. Work</th>
                  <th className="py-3 px-3.5">7. Converted By</th>
                  <th className="py-3 px-3.5">8. Assigned To</th>
                  <th className="py-3 px-3.5">9. Work Status</th>
                  <th className="py-3 px-3.5 text-right font-bold text-slate-900 dark:text-white">10. Total Amount</th>
                  <th className="py-3 px-3.5 text-right font-bold text-emerald-700 dark:text-emerald-400">11. Advance Amount</th>
                  <th className="py-3 px-3.5 text-right font-bold text-amber-700 dark:text-amber-400">12. Pending Amount</th>
                  <th className="py-3 px-3.5 text-center">13. Payment Status</th>
                  <th className="py-3 px-3.5">14. Proforma Inv. No.</th>
                  <th className="py-3 px-3.5">15. Tax Inv. No.</th>
                  <th className="py-3 px-3.5">16. Reimbursement Note</th>
                  <th className="py-3 px-3.5 text-right">17. Govt Fees</th>
                  <th className="py-3 px-3.5 text-right">18. Incidental Cost</th>
                  <th className="py-3 px-3.5 text-right font-bold text-emerald-800 dark:text-emerald-300">19. Profits</th>
                  <th className="py-3 px-4 min-w-[150px]">20. Remarks</th>
                  <th className="py-3 px-3.5 text-center sticky right-0 bg-slate-50 dark:bg-slate-800 z-10 shadow-[-4px_0_8px_-2px_rgba(0,0,0,0.06)] border-l border-slate-200 dark:border-slate-800 min-w-[90px]">
                    21. Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
                {registerData.items.map((row, idx) => {
                  const sNo = (page - 1) * limit + idx + 1;
                  const isUnassigned = !row.assigned_to_user_id || row.assigned_to_name === 'Unassigned';

                  return (
                    <tr
                      key={row.order_id}
                      onClick={() => handleRowClick(row)}
                      className="hover:bg-blue-50/40 dark:hover:bg-blue-950/20 transition-colors cursor-pointer group"
                    >
                      {/* 1. S.No */}
                      <td className="py-3 px-3.5 text-center font-mono text-slate-400 font-semibold sticky left-0 bg-white dark:bg-slate-900 group-hover:bg-blue-50/40 dark:group-hover:bg-slate-900 z-10">
                        {sNo}
                      </td>

                      {/* 2. Date */}
                      <td className="py-3 px-3.5 text-slate-700 dark:text-slate-300 font-medium">
                        {row.formatted_date || row.order_date}
                      </td>

                      {/* 3. Client Name */}
                      <td className="py-3 px-4 font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                        <span>{row.client_name}</span>
                        {row.confirmation_status === 'CONFIRMED' && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300">
                            Confirmed
                          </span>
                        )}
                      </td>

                      {/* 4. Contact No */}
                      <td className="py-3 px-3.5 text-slate-600 dark:text-slate-400 font-mono">
                        {row.contact_no || '—'}
                      </td>

                      {/* 5. Source */}
                      <td className="py-3 px-3.5">
                        <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                          {row.lead_source}
                        </span>
                      </td>

                      {/* 6. Work */}
                      <td className="py-3 px-4 text-slate-800 dark:text-slate-200 font-medium">
                        {row.service_name}
                      </td>

                      {/* 7. Converted By (Sales Employee Responsible) */}
                      <td className="py-3 px-3.5 text-slate-700 dark:text-slate-300">
                        <div className="font-medium">{row.salesperson_name}</div>
                        {row.salesperson_code && (
                          <div className="text-[10px] text-slate-400 font-mono">{row.salesperson_code}</div>
                        )}
                      </td>

                      {/* 8. Assigned To (Operations Team Member) */}
                      <td className="py-3 px-3.5 text-slate-600 dark:text-slate-400">
                        {!isUnassigned && row.assigned_to_name ? (
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
                          <div className="flex items-center gap-1.5">
                            <span className="text-[11px] text-slate-400 italic">Unassigned</span>
                            <button
                              type="button"
                              onClick={(e) => handleOpenAssignModal(row, e)}
                              className="px-2 py-0.5 text-[10px] font-semibold rounded bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/60 dark:hover:bg-blue-900 text-blue-700 dark:text-blue-300 transition"
                            >
                              Assign
                            </button>
                          </div>
                        )}
                      </td>

                      {/* 9. Work Status */}
                      <td className="py-3 px-3.5">
                        {renderWorkStatusBadge(row.work_status || row.operation_status || 'UNASSIGNED')}
                      </td>

                      {/* 10. Total Amount */}
                      <td className="py-3 px-3.5 text-right font-bold text-slate-900 dark:text-white">
                        {formatInr(row.order_value)}
                      </td>

                      {/* 11. Advance Amount */}
                      <td className="py-3 px-3.5 text-right font-semibold text-emerald-700 dark:text-emerald-400">
                        {formatInr(row.amount_received)}
                      </td>

                      {/* 12. Pending Amount */}
                      <td className="py-3 px-3.5 text-right font-semibold text-amber-700 dark:text-amber-400">
                        {formatInr(row.balance_amount)}
                      </td>

                      {/* 13. Payment Status */}
                      <td className="py-3 px-3.5 text-center">
                        {renderPaymentBadge(row.payment_status)}
                      </td>

                      {/* 14. Proforma Invoice No. (shows — when not populated) */}
                      <td className="py-3 px-3.5 text-slate-600 dark:text-slate-400 font-mono">
                        {row.proforma_invoice_no || '—'}
                      </td>

                      {/* 15. Tax Invoice No. (shows — when not populated) */}
                      <td className="py-3 px-3.5 text-slate-600 dark:text-slate-400 font-mono">
                        {row.tax_invoice_no || '—'}
                      </td>

                      {/* 16. Reimbursement Note (shows — when not populated) */}
                      <td className="py-3 px-3.5 text-slate-600 dark:text-slate-400 max-w-xs truncate" title={row.reimbursement_note || ''}>
                        {row.reimbursement_note || '—'}
                      </td>

                      {/* 17. Govt Fees */}
                      <td className="py-3 px-3.5 text-right text-slate-600 dark:text-slate-400">
                        {formatInr(row.govt_fees)}
                      </td>

                      {/* 18. Incidental Cost */}
                      <td className="py-3 px-3.5 text-right text-slate-600 dark:text-slate-400">
                        {formatInr(row.incidental_cost)}
                      </td>

                      {/* 19. Profits */}
                      <td className="py-3 px-3.5 text-right font-bold text-emerald-700 dark:text-emerald-400">
                        {formatInr(row.profit_amount)}
                      </td>

                      {/* 20. Remarks (shows — when not populated) */}
                      <td className="py-3 px-4 text-slate-500 dark:text-slate-400 max-w-xs truncate" title={row.notes || row.remarks || ''}>
                        {row.notes || row.remarks || '—'}
                      </td>

                      {/* 21. Actions Column with Sticky Edit Button */}
                      <td className="py-2 px-3 text-center sticky right-0 bg-white dark:bg-slate-900 group-hover:bg-blue-50/40 dark:group-hover:bg-slate-900 z-10 shadow-[-4px_0_8px_-2px_rgba(0,0,0,0.06)] border-l border-slate-200 dark:border-slate-800">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => handleOpenEditModal(row, e)}
                          leftIcon={<Edit className="w-3.5 h-3.5" />}
                          className="hover:border-blue-500 hover:text-blue-600 dark:hover:border-blue-400 dark:hover:text-blue-400 font-medium text-xs shadow-none py-1 px-2.5"
                        >
                          Edit
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {registerData && registerData.total_pages > 0 && (
          <div className="p-4 bg-slate-50/50 dark:bg-slate-800/40 border-t border-slate-200/80 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-600 dark:text-slate-400">
            <div className="flex items-center gap-3">
              <span>Rows per page:</span>
              <select
                value={limit}
                onChange={(e) => {
                  setLimit(Number(e.target.value));
                  setPage(1);
                }}
                className="px-2.5 py-1 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 font-medium text-slate-900 dark:text-white"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
              <span>
                Showing {Math.min((page - 1) * limit + 1, registerData.total_count)} to{' '}
                {Math.min(page * limit, registerData.total_count)} of {registerData.total_count} records
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                leftIcon={<ChevronLeft className="w-3.5 h-3.5" />}
              >
                Previous
              </Button>
              <span className="font-semibold text-slate-900 dark:text-white px-2">
                Page {page} of {registerData.total_pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= registerData.total_pages}
                onClick={() => setPage((p) => Math.min(registerData.total_pages, p + 1))}
                rightIcon={<ChevronRight className="w-3.5 h-3.5" />}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Order Detail Modal */}
      {selectedOrder && (
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title={`Order Details: ${selectedOrder.order_number}`}
        >
          <div className="space-y-6 text-sm">
            {/* Top Summary Card */}
            <div className="p-4 rounded-2xl bg-blue-50/60 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900/60 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-slate-900 dark:text-white text-base">
                  {selectedOrder.client_name}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  Order Date: {selectedOrder.formatted_date || selectedOrder.order_date}
                </p>
              </div>
              <div className="text-right">
                {renderPaymentBadge(selectedOrder.payment_status)}
                <div className="mt-1 font-bold text-slate-900 dark:text-white">
                  {formatInr(selectedOrder.order_value)}
                </div>
              </div>
            </div>

            {/* 20 Attributes Breakdown Grid */}
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Work / Service:</span>
                <p className="font-medium text-slate-900 dark:text-white mt-0.5">{selectedOrder.service_name}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Lead Source:</span>
                <p className="font-medium text-slate-900 dark:text-white mt-0.5">{selectedOrder.lead_source}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Converted By (Sales Rep):</span>
                <p className="font-medium text-slate-900 dark:text-white mt-0.5">{selectedOrder.salesperson_name}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Assigned To (Operations):</span>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="font-medium text-slate-900 dark:text-white">
                    {selectedOrder.assigned_to_name || 'Unassigned'}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleOpenAssignModal(selectedOrder)}
                    className="px-2 py-0.5 text-[10px] font-semibold rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 hover:bg-blue-200"
                  >
                    {selectedOrder.assigned_to_user_id ? 'Reassign' : 'Assign Work'}
                  </button>
                </div>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Work Status:</span>
                <p className="mt-0.5">{renderWorkStatusBadge(selectedOrder.work_status)}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Advance Amount:</span>
                <p className="font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">{formatInr(selectedOrder.amount_received)}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Pending Amount:</span>
                <p className="font-bold text-amber-600 dark:text-amber-400 mt-0.5">{formatInr(selectedOrder.balance_amount)}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Net Profit:</span>
                <p className="font-bold text-emerald-700 dark:text-emerald-400 mt-0.5">{formatInr(selectedOrder.profit_amount)}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Govt Fees:</span>
                <p className="text-slate-700 dark:text-slate-300 mt-0.5">{formatInr(selectedOrder.govt_fees)}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Incidental Cost:</span>
                <p className="text-slate-700 dark:text-slate-300 mt-0.5">{formatInr(selectedOrder.incidental_cost)}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Proforma Invoice No:</span>
                <p className="font-mono text-slate-700 dark:text-slate-300 mt-0.5">{selectedOrder.proforma_invoice_no || '—'}</p>
              </div>
              <div>
                <span className="font-semibold text-slate-500 dark:text-slate-400">Tax Invoice No:</span>
                <p className="font-mono text-slate-700 dark:text-slate-300 mt-0.5">{selectedOrder.tax_invoice_no || '—'}</p>
              </div>
            </div>

            {/* Reimbursement & Remarks */}
            {(selectedOrder.reimbursement_note || selectedOrder.notes || selectedOrder.remarks) && (
              <div className="space-y-3 pt-2 border-t border-slate-100 dark:border-slate-800">
                {selectedOrder.reimbursement_note && (
                  <div>
                    <span className="font-semibold text-xs text-slate-500 dark:text-slate-400">Reimbursement Note:</span>
                    <p className="text-xs text-slate-700 dark:text-slate-300 mt-0.5">{selectedOrder.reimbursement_note}</p>
                  </div>
                )}
                {(selectedOrder.notes || selectedOrder.remarks) && (
                  <div>
                    <span className="font-semibold text-xs text-slate-500 dark:text-slate-400">Remarks / Internal Notes:</span>
                    <p className="text-xs text-slate-700 dark:text-slate-300 mt-0.5">{selectedOrder.notes || selectedOrder.remarks}</p>
                  </div>
                )}
              </div>
            )}

            {/* Operations Application Link */}
            {selectedOrder.application_number && (
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs">
                <span className="font-medium text-slate-700 dark:text-slate-300">
                  Operations Application Ref: <strong className="font-mono">{selectedOrder.application_number}</strong>
                </span>
                <span className="px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 font-semibold">
                  {selectedOrder.operation_status || 'ASSIGNED'}
                </span>
              </div>
            )}

            <div className="pt-4 flex items-center justify-end gap-2 border-t border-slate-100 dark:border-slate-800">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setIsModalOpen(false);
                  handleOpenEditModal(selectedOrder);
                }}
                leftIcon={<Edit className="w-3.5 h-3.5" />}
              >
                Edit Sales Order
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleOpenAssignModal(selectedOrder)}
                leftIcon={<UserCheck className="w-3.5 h-3.5" />}
              >
                {selectedOrder.assigned_to_user_id ? 'Reassign Work' : 'Assign Operations Work'}
              </Button>
              <Button variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Operations Manager Work Assignment Modal */}
      {assigningOrder && (
        <Modal
          isOpen={isAssignModalOpen}
          onClose={() => setIsAssignModalOpen(false)}
          title={`Assign Operations Work: ${assigningOrder.order_number}`}
        >
          <form onSubmit={handleAssignSubmit} className="space-y-4 text-xs">
            <div className="p-3.5 rounded-2xl bg-blue-50/70 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900/60 text-slate-800 dark:text-slate-200 space-y-1">
              <div className="font-bold text-sm text-slate-900 dark:text-white">
                {assigningOrder.client_name}
              </div>
              <div className="text-slate-600 dark:text-slate-400">
                Service: <strong className="text-slate-900 dark:text-white">{assigningOrder.service_name}</strong>
              </div>
              <div className="text-slate-600 dark:text-slate-400">
                Converted By: <strong className="text-slate-900 dark:text-white">{assigningOrder.salesperson_name}</strong>
              </div>
            </div>

            {assignError && (
              <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-rose-500" />
                <span>{assignError}</span>
              </div>
            )}

            {/* Select Eligible Operations Employee */}
            <div>
              <label htmlFor="operations_assignee" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1.5 flex items-center justify-between">
                <span>Eligible Operations Team Member <span className="text-rose-500">*</span></span>
                <span className="text-[10px] font-normal text-slate-400">Operations Dept Only</span>
              </label>
              <select
                id="operations_assignee"
                value={selectedAssigneeId}
                onChange={(e) => setSelectedAssigneeId(e.target.value)}
                required
                className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
              >
                <option value="">-- Select Operations Specialist (e.g. Mansi) --</option>
                {operationsAssignees
                  .filter((emp) => !assigningOrder?.assigned_to_user_id || emp.user_id !== assigningOrder.assigned_to_user_id)
                  .map((emp) => (
                    <option key={emp.user_id} value={emp.user_id}>
                      {emp.full_name} ({emp.employee_code})
                    </option>
                  ))}
              </select>
            </div>

            {/* Priority & Target Due Date */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="assign_priority" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Task Priority
                </label>
                <select
                  id="assign_priority"
                  value={assignmentPriority}
                  onChange={(e) => setAssignmentPriority(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium (Standard)</option>
                  <option value="HIGH">High</option>
                  <option value="URGENT">Urgent / Express</option>
                </select>
              </div>

              <div>
                <label htmlFor="assign_due_date" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Target Due Date
                </label>
                <input
                  id="assign_due_date"
                  type="date"
                  value={assignmentDueDate}
                  onChange={(e) => setAssignmentDueDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>

            {/* Handover Instructions / Notes */}
            <div>
              <label htmlFor="assign_notes" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Handover Notes / Instructions
              </label>
              <textarea
                id="assign_notes"
                rows={3}
                value={assignmentNotes}
                onChange={(e) => setAssignmentNotes(e.target.value)}
                placeholder="e.g. Assigned to Mansi for express documentation and filing within 5 days..."
                className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>

            <div className="pt-3 flex items-center justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setIsAssignModalOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                isLoading={isAssigning}
                leftIcon={<Send className="w-3.5 h-3.5" />}
              >
                Confirm Assignment
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Sales Order Edit Modal */}
      {editingOrder && (
        <Modal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          title={`Edit Sales Order: ${editingOrder.order_number}`}
        >
          <form onSubmit={handleEditSubmit} className="space-y-4 text-xs">
            {/* Top Order Context Header */}
            <div className="p-3.5 rounded-2xl bg-blue-50/70 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900/60 flex items-center justify-between">
              <div>
                <div className="font-bold text-sm text-slate-900 dark:text-white">
                  {editingOrder.client_name}
                </div>
                <div className="text-slate-600 dark:text-slate-400 mt-0.5">
                  Service: <strong className="text-slate-900 dark:text-white">{editingOrder.service_name}</strong>
                  <span className="mx-2">•</span>
                  Converted By: <strong className="text-slate-900 dark:text-white">{editingOrder.salesperson_name}</strong>
                </div>
              </div>
              <div>
                {renderWorkStatusBadge(editingOrder.work_status || editingOrder.operation_status || 'UNASSIGNED')}
              </div>
            </div>

            {editError && (
              <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-rose-500" />
                <span>{editError}</span>
              </div>
            )}

            {/* Section 1: Client & Basic Info */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label htmlFor="edit_client_name" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Client Name
                </label>
                <input
                  id="edit_client_name"
                  type="text"
                  value={editClientName}
                  onChange={(e) => setEditClientName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Client Business or Individual Name"
                />
              </div>

              <div>
                <label htmlFor="edit_contact_no" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Contact Phone Number
                </label>
                <input
                  id="edit_contact_no"
                  type="text"
                  value={editContactNo}
                  onChange={(e) => setEditContactNo(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="10-digit Phone Number"
                />
              </div>

              <div>
                <label htmlFor="edit_salesperson_id" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Converted By (Sales Employee)
                </label>
                <select
                  id="edit_salesperson_id"
                  value={editSalespersonId}
                  onChange={(e) => setEditSalespersonId(e.target.value)}
                  disabled={!formOptions?.can_select_salesperson && Boolean(formOptions?.default_salesperson_id)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none disabled:opacity-75 disabled:cursor-not-allowed"
                >
                  {editingOrder.salesperson_user_id &&
                    !formOptions?.salespersons?.some((sp) => sp.user_id === editingOrder.salesperson_user_id) && (
                      <option value={editingOrder.salesperson_user_id}>
                        {editingOrder.salesperson_name || 'Current Assignee'} (Current / Legacy)
                      </option>
                    )}
                  {(formOptions?.salespersons || []).map((sp) => (
                    <option key={sp.user_id} value={sp.user_id}>
                      {sp.full_name} ({sp.employee_code})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="edit_lead_source" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Lead Source
                </label>
                <select
                  id="edit_lead_source"
                  value={editLeadSource}
                  onChange={(e) => setEditLeadSource(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                >
                  {(formOptions?.lead_sources && formOptions.lead_sources.length > 0
                    ? formOptions.lead_sources
                    : ['WEBSITE', 'REFERRAL', 'DIRECT', 'JUSTDIAL', 'INDIAMART', 'OTHERS']
                  ).map((src) => (
                    <option key={src} value={src}>
                      {src}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="edit_order_date" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Order Date
                </label>
                <input
                  id="edit_order_date"
                  type="date"
                  value={editOrderDate}
                  onChange={(e) => setEditOrderDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>

            {/* Section 2: Financial Breakdown & Live Computation */}
            <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
              <span className="font-bold text-slate-900 dark:text-white text-xs uppercase tracking-wider mb-2.5 block">
                Financial Details & Calculations
              </span>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div>
                  <label htmlFor="edit_order_value" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Total Amount (₹) <span className="text-rose-500">*</span>
                  </label>
                  <input
                    id="edit_order_value"
                    type="number"
                    min="0"
                    step="1"
                    value={editOrderValue}
                    onChange={(e) => setEditOrderValue(Math.max(0, Number(e.target.value)))}
                    required
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>

                <div>
                  <label htmlFor="edit_amount_received" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Advance / Recvd (₹) <span className="text-rose-500">*</span>
                  </label>
                  <input
                    id="edit_amount_received"
                    type="number"
                    min="0"
                    step="1"
                    value={editAmountReceived}
                    onChange={(e) => setEditAmountReceived(Math.max(0, Number(e.target.value)))}
                    required
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-emerald-600 dark:text-emerald-400 focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>

                <div>
                  <label htmlFor="edit_govt_fees" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Govt Fees (₹)
                  </label>
                  <input
                    id="edit_govt_fees"
                    type="number"
                    min="0"
                    step="1"
                    value={editGovtFees}
                    onChange={(e) => setEditGovtFees(Math.max(0, Number(e.target.value)))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>

                <div>
                  <label htmlFor="edit_incidental_cost" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Incidental Cost (₹)
                  </label>
                  <input
                    id="edit_incidental_cost"
                    type="number"
                    min="0"
                    step="1"
                    value={editIncidentalCost}
                    onChange={(e) => setEditIncidentalCost(Math.max(0, Number(e.target.value)))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              {/* Real-time Calculation Preview Ribbon */}
              <div className="mt-3 p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 grid grid-cols-3 gap-3 text-center">
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Pending Balance</span>
                  <span className="text-sm font-bold text-amber-600 dark:text-amber-400 mt-0.5 block">
                    {formatInr(Math.max(0, editOrderValue - editAmountReceived))}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Payment Status</span>
                  <div className="mt-1 flex justify-center">
                    {renderPaymentBadge(
                      editOrderValue <= 0
                        ? 'PENDING'
                        : editAmountReceived >= editOrderValue
                        ? 'FULLY_PAID'
                        : editAmountReceived > 0
                        ? 'PARTIALLY_PAID'
                        : 'PENDING'
                    )}
                  </div>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Estimated Profit</span>
                  <span className="text-sm font-bold text-emerald-700 dark:text-emerald-400 mt-0.5 block">
                    {formatInr(editOrderValue - editGovtFees - editIncidentalCost)}
                  </span>
                </div>
              </div>
            </div>

            {/* Section 3: Invoicing & Notes */}
            <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-3">
              <span className="font-bold text-slate-900 dark:text-white text-xs uppercase tracking-wider block">
                Invoicing & Internal Records
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label htmlFor="edit_proforma_no" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Proforma Invoice Number
                  </label>
                  <input
                    id="edit_proforma_no"
                    type="text"
                    value={editProformaInvoiceNo}
                    onChange={(e) => setEditProformaInvoiceNo(e.target.value)}
                    placeholder="e.g. PI-2025-0012"
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs font-mono text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>

                <div>
                  <label htmlFor="edit_tax_invoice_no" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Tax Invoice Number
                  </label>
                  <input
                    id="edit_tax_invoice_no"
                    type="text"
                    value={editTaxInvoiceNo}
                    onChange={(e) => setEditTaxInvoiceNo(e.target.value)}
                    placeholder="e.g. INV-2025-0048"
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs font-mono text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="edit_reimbursement_note" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Reimbursement Note
                </label>
                <input
                  id="edit_reimbursement_note"
                  type="text"
                  value={editReimbursementNote}
                  onChange={(e) => setEditReimbursementNote(e.target.value)}
                  placeholder="e.g. Client to reimburse stamp duty / notary fees upon filing"
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label htmlFor="edit_notes" className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Remarks / Internal Sales Notes
                </label>
                <textarea
                  id="edit_notes"
                  rows={2}
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  placeholder="e.g. Special discounts agreed, balance due after license delivery..."
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>

            {/* Footer Buttons */}
            <div className="pt-3 flex items-center justify-end gap-2 border-t border-slate-100 dark:border-slate-800">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setIsEditModalOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                isLoading={isSavingEdit}
                leftIcon={<Save className="w-3.5 h-3.5" />}
              >
                Save Changes
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};

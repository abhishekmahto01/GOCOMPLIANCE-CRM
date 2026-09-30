import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  RefreshCw,
  History,
  CheckCircle2,
  AlertCircle,
  Clock,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Paperclip,
  Check,
  X,
} from 'lucide-react';
import {
  getPaymentRegisterApi,
  getAccountsFilterOptionsApi,
  recordPaymentApi,
  verifyPaymentApi,
  reversePaymentApi,
  getOrderPaymentHistoryApi,
  uploadAccountsAttachmentApi,
} from '../../api/accounts';
import type {
  PaymentRegisterItemRead,
  PaymentRegisterResponse,
  PaymentRegisterSummary,
  AccountsFilterOptions,
  PaymentTransactionRead,
} from '../../types/accounts';
import { Button } from '../../components/ui/button';
import { useAuth } from '../../context/AuthContext';

export const PaymentRegisterPage: React.FC = () => {
  const { isSuperAdmin, session, hasPermission, hasModuleAccess } = useAuth();
  const isDirector = session.userRole?.toUpperCase() === 'DIRECTOR';
  const canVerify = isSuperAdmin || isDirector || hasPermission('ACCOUNTS_PAYMENT_REGISTER', 'approve') || hasPermission('ACCOUNTS_PAYMENT_REGISTER', 'edit') || hasModuleAccess('ACCOUNTS');
  const canReverse = isSuperAdmin || isDirector || hasPermission('ACCOUNTS_PAYMENT_REGISTER', 'delete') || hasModuleAccess('ACCOUNTS');


  const [data, setData] = useState<PaymentRegisterResponse | null>(null);
  const [summary, setSummary] = useState<PaymentRegisterSummary | null>(null);
  const [filterOptions, setFilterOptions] = useState<AccountsFilterOptions | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Filters
  const [page, setPage] = useState<number>(1);
  const [limit] = useState<number>(20);
  const [search, setSearch] = useState<string>('');
  const [companyId, setCompanyId] = useState<string>('ALL');
  const [employeeId, setEmployeeId] = useState<string>('ALL');
  const [paymentStatus, setPaymentStatus] = useState<string>('ALL');
  const [overdueOnly, setOverdueOnly] = useState<boolean>(false);
  const [fromDate] = useState<string>('');
  const [toDate] = useState<string>('');
  const [sortBy] = useState<string>('order_date');
  const [sortOrder] = useState<string>('desc');

  // Modals state
  const [recordModalOpen, setRecordModalOpen] = useState<boolean>(false);
  const [selectedOrder, setSelectedOrder] = useState<PaymentRegisterItemRead | null>(null);
  const [historyModalOpen, setHistoryModalOpen] = useState<boolean>(false);
  const [orderPayments, setOrderPayments] = useState<PaymentTransactionRead[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);

  // Record payment form fields
  const [paymentAmount, setPaymentAmount] = useState<string>('');
  const [paymentDate, setPaymentDate] = useState<string>(new Date().toISOString().slice(0, 10));
  const [paymentMode, setPaymentMode] = useState<string>('BANK_TRANSFER');
  const [transactionRef, setTransactionRef] = useState<string>('');
  const [receivingAccount, setReceivingAccount] = useState<string>('HDFC Bank Primary');
  const [paymentRemark, setPaymentRemark] = useState<string>('');
  const [proofFile, setProofFile] = useState<File | null>(null);
  const [isSubmittingPayment, setIsSubmittingPayment] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Reversal modal / inline prompt
  const [reversingPaymentId, setReversingPaymentId] = useState<string | null>(null);
  const [reversalReason, setReversalReason] = useState<string>('');
  const [isSubmittingReversal, setIsSubmittingReversal] = useState<boolean>(false);

  // Fetch filter options once
  useEffect(() => {
    getAccountsFilterOptionsApi()
      .then(setFilterOptions)
      .catch((err) => console.error('Error fetching filter options:', err));
  }, []);

  const fetchRegister = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getPaymentRegisterApi({
        page,
        limit,
        search: search.trim() || undefined,
        company_id: companyId,
        employee_id: employeeId,
        payment_status: paymentStatus,
        overdue_only: overdueOnly,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setData(res);
      setSummary(res.summary);
    } catch (err: any) {
      console.error('Error loading payment register:', err);
      setError(err?.response?.data?.detail || 'Failed to fetch payment register');
    } finally {
      setIsLoading(false);
    }
  }, [page, limit, search, companyId, employeeId, paymentStatus, overdueOnly, fromDate, toDate, sortBy, sortOrder]);

  useEffect(() => {
    fetchRegister();
  }, [fetchRegister]);

  // Open Record Payment modal
  const handleOpenRecordPayment = (order?: PaymentRegisterItemRead) => {
    if (order) {
      setSelectedOrder(order);
      setPaymentAmount(order.pending_amount > 0 ? String(order.pending_amount) : '');
    } else {
      setSelectedOrder(null);
      setPaymentAmount('');
    }
    setPaymentDate(new Date().toISOString().slice(0, 10));
    setPaymentMode('BANK_TRANSFER');
    setTransactionRef('');
    setPaymentRemark('');
    setProofFile(null);
    setFormError(null);
    setRecordModalOpen(true);
  };

  // Submit Payment
  const handleSubmitPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOrder) {
      setFormError('Please select a valid order');
      return;
    }
    const amt = parseFloat(paymentAmount);
    if (isNaN(amt) || amt <= 0) {
      setFormError('Please enter a valid positive payment amount');
      return;
    }
    if (amt > selectedOrder.pending_amount) {
      setFormError(`Payment amount (₹${amt}) exceeds pending balance (₹${selectedOrder.pending_amount})`);
      return;
    }

    setIsSubmittingPayment(true);
    setFormError(null);

    try {
      // 1. Upload proof if provided
      if (proofFile) {
        await uploadAccountsAttachmentApi(proofFile, 'payments');
      }

      // 2. Submit payment record
      await recordPaymentApi({
        sales_order_id: selectedOrder.sales_order_id,
        amount: amt,
        payment_date: paymentDate,
        payment_mode: paymentMode,
        transaction_reference: transactionRef.trim() || undefined,
        receiving_account: receivingAccount,
        remark: paymentRemark.trim() || undefined,
        auto_verify: canVerify,
      });

      setSuccessMsg(`Collection of ₹${amt.toLocaleString('en-IN')} recorded successfully for order ${selectedOrder.order_number}`);
      setTimeout(() => setSuccessMsg(null), 4000);
      setRecordModalOpen(false);
      fetchRegister();
    } catch (err: any) {
      console.error('Error submitting payment:', err);
      setFormError(err?.response?.data?.detail || 'Failed to record payment');
    } finally {
      setIsSubmittingPayment(false);
    }
  };

  // View Payment History for an Order
  const handleOpenHistory = async (order: PaymentRegisterItemRead) => {
    setSelectedOrder(order);
    setHistoryModalOpen(true);
    setLoadingHistory(true);
    setReversingPaymentId(null);
    try {
      const res = await getOrderPaymentHistoryApi(order.sales_order_id);
      setOrderPayments(res.items);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  // Verify a payment inside modal
  const handleVerify = async (paymentId: string) => {
    try {
      await verifyPaymentApi(paymentId, { action: 'VERIFY' });
      if (selectedOrder) {
        const res = await getOrderPaymentHistoryApi(selectedOrder.sales_order_id);
        setOrderPayments(res.items);
      }
      fetchRegister();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to verify payment');
    }
  };

  // Reverse a payment inside modal
  const handleReverse = async (paymentId: string) => {
    if (!reversalReason.trim() || reversalReason.trim().length < 3) {
      alert('Please provide a valid reversal reason (at least 3 characters)');
      return;
    }
    setIsSubmittingReversal(true);
    try {
      await reversePaymentApi(paymentId, { reversal_reason: reversalReason.trim() });
      setReversingPaymentId(null);
      setReversalReason('');
      if (selectedOrder) {
        const res = await getOrderPaymentHistoryApi(selectedOrder.sales_order_id);
        setOrderPayments(res.items);
      }
      fetchRegister();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to reverse payment');
    } finally {
      setIsSubmittingReversal(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Payment Register & Collection Ledger
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Real-time ledger of client billing liabilities, verified installment collections, and pending balances.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={() => fetchRegister()}
            disabled={isLoading}
            variant="outline"
            size="sm"
            className="rounded-xl text-xs flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Summary Stat Cards */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Total Payable</span>
            <div className="text-xl font-black text-slate-900 dark:text-white mt-1">
              {summary.formatted_total_payable}
            </div>
            <span className="text-[11px] text-slate-500">{summary.total_orders} total orders</span>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Verified Received</span>
            <div className="text-xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
              {summary.formatted_total_verified_received}
            </div>
            <span className="text-[11px] text-emerald-600 font-semibold">{summary.fully_paid_count} fully paid</span>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Unverified Collections</span>
            <div className="text-xl font-black text-blue-600 dark:text-blue-400 mt-1">
              {summary.formatted_total_unverified_amount}
            </div>
            <span className="text-[11px] text-blue-600 font-semibold">Pending approval</span>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Pending Balance</span>
            <div className="text-xl font-black text-amber-600 dark:text-amber-400 mt-1">
              {summary.formatted_total_pending}
            </div>
            <span className="text-[11px] text-rose-500 font-semibold">{summary.overdue_count} overdue</span>
          </div>
        </div>
      )}

      {/* Success Banner */}
      {successMsg && (
        <div className="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 flex items-center gap-2.5 text-xs font-semibold">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 flex items-center gap-2.5 text-xs font-semibold">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Filters Toolbar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          {/* Search Box */}
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search order no, client, company, service..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Company Filter */}
          {filterOptions && filterOptions.companies.length > 0 && (
            <select
              aria-label="Company Filter"
              value={companyId}
              onChange={(e) => {
                setCompanyId(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 max-w-[170px] truncate"
            >
              <option value="ALL">All Companies</option>
              {filterOptions.companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                </option>
              ))}
            </select>
          )}

          {/* Payment Status Filter */}
          <select
            aria-label="Payment Status Filter"
            value={paymentStatus}
            onChange={(e) => {
              setPaymentStatus(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="FULLY_PAID">Fully Paid</option>
            <option value="PARTIALLY_PAID">Partially Paid</option>
            <option value="PENDING">Pending</option>
            <option value="OVERDUE">Overdue Only</option>
          </select>

          {/* Salesperson Filter */}
          {filterOptions && filterOptions.salespersons.length > 0 && (
            <select
              aria-label="Salesperson Filter"
              value={employeeId}
              onChange={(e) => {
                setEmployeeId(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 max-w-[170px] truncate"
            >
              <option value="ALL">All Salespersons</option>
              {filterOptions.salespersons.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          )}

          {/* Overdue Checkbox Toggle */}
          <label className="flex items-center gap-2 text-xs font-semibold text-rose-600 dark:text-rose-400 cursor-pointer select-none bg-rose-50 dark:bg-rose-950/40 px-3 py-2 rounded-xl border border-rose-200 dark:border-rose-800">
            <input
              type="checkbox"
              checked={overdueOnly}
              onChange={(e) => {
                setOverdueOnly(e.target.checked);
                setPage(1);
              }}
              className="rounded text-rose-600 focus:ring-rose-500"
            />
            <span>Overdue Only</span>
          </label>
        </div>
      </div>

      {/* Main Ledger Table */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200/80 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-3 px-3.5">Order / Date</th>
                <th className="py-3 px-3.5">Company & Client</th>
                <th className="py-3 px-3.5">Work / Service</th>
                <th className="py-3 px-3.5">Salesperson</th>
                <th className="py-3 px-3.5 text-right">Total Payable</th>
                <th className="py-3 px-3.5 text-right">Verified Received</th>
                <th className="py-3 px-3.5 text-right">Pending Balance</th>
                <th className="py-3 px-3.5 text-center">Status</th>
                <th className="py-3 px-3.5">Latest Remark</th>
                <th className="py-3 px-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {isLoading ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-600" />
                    Loading payment register ledger...
                  </td>
                </tr>
              ) : data && data.items.length > 0 ? (
                data.items.map((item) => (
                  <tr
                    key={item.sales_order_id}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    {/* Order ID & Date */}
                    <td className="py-3 px-3.5 font-medium whitespace-nowrap">
                      <div className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                        {item.order_number}
                      </div>
                      <div className="text-[11px] text-slate-400">{item.formatted_order_date}</div>
                    </td>

                    {/* Company & Client */}
                    <td className="py-3 px-3.5">
                      <div className="font-bold text-slate-800 dark:text-slate-200 truncate max-w-[160px]">
                        {item.client_name}
                      </div>
                      <div className="text-[11px] text-slate-400 truncate max-w-[160px]">
                        {item.company_name}
                      </div>
                    </td>

                    {/* Service */}
                    <td className="py-3 px-3.5">
                      <div className="font-medium text-slate-700 dark:text-slate-300 truncate max-w-[150px]">
                        {item.service_name}
                      </div>
                      {item.location && (
                        <div className="text-[10px] text-slate-400">📍 {item.location}</div>
                      )}
                    </td>

                    {/* Salesperson */}
                    <td className="py-3 px-3.5 whitespace-nowrap text-slate-600 dark:text-slate-400">
                      {item.salesperson_name}
                    </td>

                    {/* Total Payable */}
                    <td className="py-3 px-3.5 text-right font-mono font-bold text-slate-900 dark:text-white">
                      {item.formatted_total_payable}
                    </td>

                    {/* Verified Received */}
                    <td className="py-3 px-3.5 text-right font-mono">
                      <span className="font-bold text-emerald-600 dark:text-emerald-400">
                        {item.formatted_verified_received}
                      </span>
                      {item.unverified_amount > 0 && (
                        <div className="text-[10px] text-blue-600 font-semibold" title="Unverified submission pending review">
                          +{item.formatted_unverified_amount} unverified
                        </div>
                      )}
                    </td>

                    {/* Pending Balance */}
                    <td className="py-3 px-3.5 text-right font-mono">
                      <span
                        className={`font-bold ${
                          item.pending_amount > 0
                            ? item.is_overdue
                              ? 'text-rose-600 dark:text-rose-400'
                              : 'text-amber-600 dark:text-amber-400'
                            : 'text-slate-400'
                        }`}
                      >
                        {item.formatted_pending_amount}
                      </span>
                      {item.due_date && item.pending_amount > 0 && (
                        <div className="text-[10px] text-slate-400">
                          Due: {item.formatted_due_date}
                        </div>
                      )}
                    </td>

                    {/* Payment Status Badge */}
                    <td className="py-3 px-3.5 text-center whitespace-nowrap">
                      {item.payment_status === 'FULLY_PAID' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                          <CheckCircle2 className="w-3 h-3" /> Fully Paid
                        </span>
                      )}
                      {item.payment_status === 'PARTIALLY_PAID' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                          <Clock className="w-3 h-3" /> Partial
                        </span>
                      )}
                      {item.payment_status === 'PENDING' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                          <Clock className="w-3 h-3" /> Pending
                        </span>
                      )}
                      {item.payment_status === 'OVERDUE' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
                          <AlertCircle className="w-3 h-3" /> Overdue
                        </span>
                      )}
                    </td>

                    {/* Latest Remark */}
                    <td className="py-3 px-3.5 max-w-[180px]">
                      {item.latest_remark ? (
                        <div className="text-[11px] text-slate-600 dark:text-slate-300 truncate" title={item.latest_remark}>
                          {item.latest_remark}
                        </div>
                      ) : (
                        <span className="text-[11px] text-slate-300 dark:text-slate-600 italic">No remark</span>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-3.5 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-1.5">
                        {item.pending_amount > 0 && (
                          <button
                            onClick={() => handleOpenRecordPayment(item)}
                            className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-950/60 dark:text-emerald-300 font-semibold text-[11px] transition-colors"
                            title="Record Collection"
                          >
                            + Collect
                          </button>
                        )}
                        <button
                          onClick={() => handleOpenHistory(item)}
                          className="p-1.5 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                          title="Payment History & Verification"
                        >
                          <History className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400 text-xs">
                    No payment register entries match the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {data && data.total_pages > 1 && (
          <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
            <span>
              Showing {((page - 1) * limit) + 1} - {Math.min(page * limit, data.total_count)} of {data.total_count} orders
            </span>
            <div className="flex items-center gap-1.5">
              <Button
                size="sm"
                variant="outline"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="h-8 px-2.5 rounded-lg"
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="font-semibold text-slate-700 dark:text-slate-300 px-2">
                Page {page} of {data.total_pages}
              </span>
              <Button
                size="sm"
                variant="outline"
                disabled={page >= data.total_pages}
                onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                className="h-8 px-2.5 rounded-lg"
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Record Payment Modal */}
      {recordModalOpen && selectedOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-lg w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                  Record Payment Collection
                </h3>
                <p className="text-xs text-slate-500">
                  Order {selectedOrder.order_number} &bull; {selectedOrder.client_name}
                </p>
              </div>
              <button
                onClick={() => setRecordModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitPayment} className="p-6 space-y-4">
              {/* Order Balance Context Box */}
              <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800 grid grid-cols-3 gap-2 text-center text-xs">
                <div>
                  <span className="text-slate-400 text-[10px] uppercase font-bold">Total Order</span>
                  <div className="font-bold text-slate-800 dark:text-slate-200">{selectedOrder.formatted_total_payable}</div>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] uppercase font-bold">Verified Recv</span>
                  <div className="font-bold text-emerald-600 dark:text-emerald-400">{selectedOrder.formatted_verified_received}</div>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] uppercase font-bold">Max Allowed</span>
                  <div className="font-extrabold text-amber-600 dark:text-amber-400">{selectedOrder.formatted_pending_amount}</div>
                </div>
              </div>

              {formError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{formError}</span>
                </div>
              )}

              {/* Amount & Date */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Amount Received (₹)*
                  </label>
                  <input
                    type="number"
                    step="any"
                    min="1"
                    max={selectedOrder.pending_amount}
                    required
                    value={paymentAmount}
                    onChange={(e) => setPaymentAmount(e.target.value)}
                    placeholder="Enter amount"
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-bold"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Payment Date*
                  </label>
                  <input
                    type="date"
                    required
                    value={paymentDate}
                    onChange={(e) => setPaymentDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                  />
                </div>
              </div>

              {/* Payment Mode & Reference */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Payment Mode*
                  </label>
                  <select
                    value={paymentMode}
                    onChange={(e) => setPaymentMode(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-semibold"
                  >
                    <option value="BANK_TRANSFER">Bank Transfer (NEFT/RTGS/IMPS)</option>
                    <option value="UPI">UPI / QR Code</option>
                    <option value="CHEQUE">Cheque / Demand Draft</option>
                    <option value="CASH">Cash Deposit</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Transaction Ref / UTR
                  </label>
                  <input
                    type="text"
                    value={transactionRef}
                    onChange={(e) => setTransactionRef(e.target.value)}
                    placeholder="UTR / Cheque No."
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-mono"
                  />
                </div>
              </div>

              {/* Receiving Account */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Receiving Bank / Ledger
                </label>
                <select
                  value={receivingAccount}
                  onChange={(e) => setReceivingAccount(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                >
                  <option value="HDFC Bank Primary">HDFC Bank Primary Current A/C</option>
                  <option value="ICICI Bank Operations">ICICI Bank Operations A/C</option>
                  <option value="Axis Bank Collections">Axis Bank Collections A/C</option>
                  <option value="Cash Ledger">Cash Ledger</option>
                </select>
              </div>

              {/* Proof / Receipt Attachment */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Supporting Proof / Receipt Attachment (PDF, PNG, JPG)
                </label>
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={(e) => setProofFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
                />
              </div>

              {/* Remark */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Accounts Remark
                </label>
                <textarea
                  rows={2}
                  value={paymentRemark}
                  onChange={(e) => setPaymentRemark(e.target.value)}
                  placeholder="Optional collection notes..."
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2.5">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setRecordModalOpen(false)}
                  className="rounded-xl text-xs"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmittingPayment}
                  size="sm"
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5"
                >
                  <Check className="w-4 h-4" />
                  <span>{isSubmittingPayment ? 'Submitting...' : 'Save Collection'}</span>
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Payment History & Reversals Modal */}
      {historyModalOpen && selectedOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-2xl w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                  Payment History & Ledger Entries
                </h3>
                <p className="text-xs text-slate-500">
                  Order {selectedOrder.order_number} &bull; {selectedOrder.client_name} ({selectedOrder.company_name})
                </p>
              </div>
              <button
                onClick={() => setHistoryModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 flex-1">
              {loadingHistory ? (
                <div className="py-12 text-center text-slate-400 text-xs">
                  <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-600" />
                  Loading payment history...
                </div>
              ) : orderPayments.length > 0 ? (
                <div className="space-y-3">
                  {orderPayments.map((p) => (
                    <div
                      key={p.payment_id}
                      className={`p-4 rounded-2xl border ${
                        p.verification_status === 'VERIFIED'
                          ? 'bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800'
                          : p.verification_status === 'REVERSED'
                          ? 'bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 opacity-75'
                          : 'bg-blue-50/40 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-xs text-slate-800 dark:text-slate-200">
                            {p.payment_number}
                          </span>
                          {p.is_opening_balance && (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-700">
                              Opening Legacy Advance
                            </span>
                          )}
                        </div>
                        <div className="text-right">
                          <span className="text-sm font-black text-slate-900 dark:text-white">
                            {p.formatted_amount}
                          </span>
                          <span className="block text-[10px] text-slate-400">{p.formatted_payment_date}</span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-xs mt-2 text-slate-600 dark:text-slate-400">
                        <div>Mode: <span className="font-semibold text-slate-800 dark:text-slate-200">{p.payment_mode}</span></div>
                        <div>Ref: <span className="font-mono font-medium text-slate-800 dark:text-slate-200">{p.transaction_reference || 'N/A'}</span></div>
                        <div>Status: <span className="font-bold">{p.verification_status}</span></div>
                        <div>Submitted By: <span className="font-semibold">{p.submitted_by_name || 'System'}</span></div>
                      </div>

                      {p.remark && (
                        <div className="text-xs text-slate-500 mt-2 bg-white/60 dark:bg-slate-900/60 p-2 rounded-xl">
                          Remark: {p.remark}
                        </div>
                      )}

                      {p.reversal_reason && (
                        <div className="text-xs text-rose-600 mt-2 bg-rose-50 dark:bg-rose-950/40 p-2 rounded-xl">
                          Reversal Reason: {p.reversal_reason} (by {p.reversed_by_name})
                        </div>
                      )}

                      {/* Action buttons */}
                      <div className="mt-3 pt-2 border-t border-slate-200/60 dark:border-slate-700 flex items-center justify-between">
                        {p.proof_attachment_path ? (
                          <a
                            href={`/api/v1/accounts/attachments/payments/${p.proof_attachment_name || 'receipt.pdf'}`}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-600 hover:underline"
                          >
                            <Paperclip className="w-3.5 h-3.5" /> View Proof
                          </a>
                        ) : (
                          <span className="text-[11px] text-slate-400">No attachment</span>
                        )}

                        <div className="flex items-center gap-2">
                          {p.verification_status === 'UNVERIFIED' && canVerify && (
                            <Button
                              size="sm"
                              onClick={() => handleVerify(p.payment_id)}
                              className="h-7 text-xs bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg"
                            >
                              Verify Collection
                            </Button>
                          )}

                          {p.verification_status === 'VERIFIED' && canReverse && !p.is_opening_balance && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setReversingPaymentId(p.payment_id)}
                              className="h-7 text-xs border-rose-200 text-rose-600 hover:bg-rose-50 rounded-lg flex items-center gap-1"
                            >
                              <RotateCcw className="w-3 h-3" /> Reverse
                            </Button>
                          )}
                        </div>
                      </div>

                      {/* Reversal input form */}
                      {reversingPaymentId === p.payment_id && (
                        <div className="mt-3 p-3 bg-rose-50 dark:bg-rose-950/40 rounded-xl border border-rose-200 space-y-2">
                          <label className="block text-xs font-bold text-rose-700">
                            Reason for Reversal (Audit Recorded)*
                          </label>
                          <input
                            type="text"
                            placeholder="e.g. Bank chargeback / Cheque bounced / Wrong allocation"
                            value={reversalReason}
                            onChange={(e) => setReversalReason(e.target.value)}
                            className="w-full text-xs px-3 py-1.5 rounded-lg border border-rose-300"
                          />
                          <div className="flex justify-end gap-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => setReversingPaymentId(null)}
                              className="h-7 text-xs"
                            >
                              Cancel
                            </Button>
                            <Button
                              size="sm"
                              disabled={isSubmittingReversal}
                              onClick={() => handleReverse(p.payment_id)}
                              className="h-7 text-xs bg-rose-600 hover:bg-rose-700 text-white"
                            >
                              Confirm Reversal
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-12 text-center text-slate-400 text-xs">
                  No payment collections recorded for this order yet.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

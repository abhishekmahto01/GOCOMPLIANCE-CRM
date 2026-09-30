import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  RefreshCw,
  PlusCircle,
  CheckCircle2,
  AlertCircle,
  Paperclip,
  Check,
  X,
  ChevronLeft,
  ChevronRight,
  Wallet,
} from 'lucide-react';
import {
  getExpensesListApi,
  recordExpenseApi,
  approveExpenseApi,
  settleReimbursementApi,
  uploadAccountsAttachmentApi,
} from '../../api/accounts';
import type {
  AccountsExpenseRead,
  AccountsExpenseListResponse,
} from '../../types/accounts';
import { Button } from '../../components/ui/button';
import { useAuth } from '../../context/AuthContext';


export const ExpensesReimbursementsPage: React.FC = () => {
  const { isSuperAdmin, session, hasPermission, hasModuleAccess } = useAuth();
  const isDirector = session.userRole?.toUpperCase() === 'DIRECTOR';
  const canApprove = isSuperAdmin || isDirector || hasPermission('ACCOUNTS_EXPENSES', 'approve') || hasPermission('ACCOUNTS_EXPENSES', 'edit') || hasModuleAccess('ACCOUNTS');
  const canSettle = isSuperAdmin || isDirector || hasPermission('ACCOUNTS_EXPENSES', 'edit') || hasModuleAccess('ACCOUNTS');

  const [data, setData] = useState<AccountsExpenseListResponse | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Filters
  const [page, setPage] = useState<number>(1);
  const [limit] = useState<number>(20);
  const [search, setSearch] = useState<string>('');
  const [companyId] = useState<string>('ALL');
  const [category, setCategory] = useState<string>('ALL');
  const [paidByType, setPaidByType] = useState<string>('ALL');
  const [approvalStatus, setApprovalStatus] = useState<string>('ALL');
  const [settlementStatus, setSettlementStatus] = useState<string>('ALL');
  const [fromDate] = useState<string>('');
  const [toDate] = useState<string>('');
  const [sortBy] = useState<string>('expense_date');
  const [sortOrder] = useState<string>('desc');

  // Modals state
  const [recordModalOpen, setRecordModalOpen] = useState<boolean>(false);
  const [selectedExpense, setSelectedExpense] = useState<AccountsExpenseRead | null>(null);
  const [settleModalOpen, setSettleModalOpen] = useState<boolean>(false);
  const [settlementRef, setSettlementRef] = useState<string>('');
  const [isSubmittingSettle, setIsSubmittingSettle] = useState<boolean>(false);

  // Record Expense Form Fields
  const [expCategory, setExpCategory] = useState<'GOVT_FEES' | 'VENDOR_COST' | 'INCIDENTAL_COST' | 'EMPLOYEE_REIMBURSEMENT' | 'OTHER_DIRECT_COST'>('GOVT_FEES');
  const [expAmount, setExpAmount] = useState<string>('');
  const [expDate, setExpDate] = useState<string>(new Date().toISOString().slice(0, 10));
  const [payeeName, setPayeeName] = useState<string>('');
  const [expPaidByType, setExpPaidByType] = useState<'COMPANY' | 'EMPLOYEE'>('COMPANY');
  const [expPaymentMode, setExpPaymentMode] = useState<string>('BANK_TRANSFER');
  const [expTransactionRef, setExpTransactionRef] = useState<string>('');
  const [expRemark, setExpRemark] = useState<string>('');
  const [billFile, setBillFile] = useState<File | null>(null);
  const [isSubmittingExpense, setIsSubmittingExpense] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchExpenses = useCallback(async () => {

    setIsLoading(true);
    setError(null);
    try {
      const res = await getExpensesListApi({
        page,
        limit,
        search: search.trim() || undefined,
        company_id: companyId,
        category,
        paid_by_type: paidByType,
        approval_status: approvalStatus,
        settlement_status: settlementStatus,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setData(res);
    } catch (err: any) {
      console.error('Error loading expenses:', err);
      setError(err?.response?.data?.detail || 'Failed to fetch expense records');
    } finally {
      setIsLoading(false);
    }
  }, [page, limit, search, companyId, category, paidByType, approvalStatus, settlementStatus, fromDate, toDate, sortBy, sortOrder]);

  useEffect(() => {
    fetchExpenses();
  }, [fetchExpenses]);

  // Handle open Add Expense
  const handleOpenAddExpense = () => {
    setExpCategory('GOVT_FEES');
    setExpAmount('');
    setExpDate(new Date().toISOString().slice(0, 10));
    setPayeeName('');
    setExpPaidByType('COMPANY');
    setExpPaymentMode('BANK_TRANSFER');
    setExpTransactionRef('');
    setExpRemark('');
    setBillFile(null);
    setFormError(null);
    setRecordModalOpen(true);
  };

  // Submit Expense
  const handleSubmitExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!payeeName.trim()) {
      setFormError('Please enter payee / vendor name');
      return;
    }
    const amt = parseFloat(expAmount);
    if (isNaN(amt) || amt <= 0) {
      setFormError('Please enter a valid expense amount');
      return;
    }

    setIsSubmittingExpense(true);
    setFormError(null);

    try {
      if (billFile) {
        await uploadAccountsAttachmentApi(billFile, 'expenses');
      }

      await recordExpenseApi({
        category: expCategory,
        amount: amt,
        expense_date: expDate,
        payee_name: payeeName.trim(),
        paid_by_type: expPaidByType,
        payment_mode: expPaymentMode,
        transaction_reference: expTransactionRef.trim() || undefined,
        remark: expRemark.trim() || undefined,
      });

      setSuccessMsg(`Expense entry of ₹${amt.toLocaleString('en-IN')} recorded successfully.`);
      setTimeout(() => setSuccessMsg(null), 4000);
      setRecordModalOpen(false);
      fetchExpenses();
    } catch (err: any) {
      console.error('Error submitting expense:', err);
      setFormError(err?.response?.data?.detail || 'Failed to record expense');
    } finally {
      setIsSubmittingExpense(false);
    }
  };

  // Approve or Reject Expense
  const handleApproveReject = async (expenseId: string, action: 'APPROVE' | 'REJECT') => {
    try {
      await approveExpenseApi(expenseId, { action });
      setSuccessMsg(`Expense ${action === 'APPROVE' ? 'approved' : 'rejected'} successfully.`);
      setTimeout(() => setSuccessMsg(null), 4000);
      fetchExpenses();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to update approval status');
    }
  };

  // Open Settle Reimbursement Modal
  const handleOpenSettle = (exp: AccountsExpenseRead) => {
    setSelectedExpense(exp);
    setSettlementRef('');
    setSettleModalOpen(true);
  };

  // Settle Reimbursement
  const handleSubmitSettle = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedExpense) return;
    setIsSubmittingSettle(true);
    try {
      await settleReimbursementApi(selectedExpense.expense_id, {
        settlement_reference: settlementRef.trim() || undefined,
      });
      setSuccessMsg(`Reimbursement of ₹${selectedExpense.amount.toLocaleString('en-IN')} marked settled.`);
      setTimeout(() => setSuccessMsg(null), 4000);
      setSettleModalOpen(false);
      fetchExpenses();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to settle reimbursement');
    } finally {
      setIsSubmittingSettle(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Direct Expenses & Employee Reimbursements
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Audit-safe tracking of Govt fees, vendor outlay, incidental costs, and employee out-of-pocket claim settlements.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={() => fetchExpenses()}
            disabled={isLoading}
            variant="outline"
            size="sm"
            className="rounded-xl text-xs flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
          <Button
            onClick={handleOpenAddExpense}
            size="sm"
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5 shadow-xs"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Record Expense</span>
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Approved Direct Costs</span>
            <div className="text-xl font-black text-slate-900 dark:text-white mt-1">
              ₹{data.total_approved_expenses.toLocaleString('en-IN')}
            </div>
            <span className="text-[11px] text-slate-500">{data.total_count} total entries</span>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Pending Approvals</span>
            <div className="text-xl font-black text-amber-600 dark:text-amber-400 mt-1">
              ₹{data.total_pending_approval.toLocaleString('en-IN')}
            </div>
            <span className="text-[11px] text-amber-600 font-semibold">Requires verification</span>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Unsettled Claims</span>
            <div className="text-xl font-black text-rose-600 dark:text-rose-400 mt-1">
              ₹{data.total_pending_reimbursements.toLocaleString('en-IN')}
            </div>
            <span className="text-[11px] text-rose-500 font-semibold">Employee reimbursements</span>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Settled Reimbursements</span>
            <div className="text-xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
              ₹{data.total_settled_reimbursements.toLocaleString('en-IN')}
            </div>
            <span className="text-[11px] text-emerald-600 font-semibold">Disbursed to staff</span>
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
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          {/* Search Box */}
          <div className="relative min-w-[220px]">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search payee, order, client..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Category Filter */}
          <select
            aria-label="Expense Category Filter"
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 font-semibold"
          >
            <option value="ALL">All Categories</option>
            <option value="GOVT_FEES">Govt Fees</option>
            <option value="VENDOR_COST">Vendor / Consultant Cost</option>
            <option value="INCIDENTAL_COST">Incidental Cost</option>
            <option value="EMPLOYEE_REIMBURSEMENT">Employee Reimbursement</option>
            <option value="OTHER_DIRECT_COST">Other Direct Costs</option>
          </select>

          {/* Paid By Filter */}
          <select
            aria-label="Paid By Filter"
            value={paidByType}
            onChange={(e) => {
              setPaidByType(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200"
          >
            <option value="ALL">All Payers</option>
            <option value="COMPANY">Company Direct</option>
            <option value="EMPLOYEE">Employee (Reimbursable)</option>
          </select>

          {/* Approval Filter */}
          <select
            aria-label="Approval Status Filter"
            value={approvalStatus}
            onChange={(e) => {
              setApprovalStatus(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200"
          >
            <option value="ALL">All Approvals</option>
            <option value="APPROVED">Approved</option>
            <option value="PENDING">Pending Approval</option>
            <option value="REJECTED">Rejected</option>
          </select>

          {/* Settlement Status */}
          <select
            aria-label="Settlement Status Filter"
            value={settlementStatus}
            onChange={(e) => {
              setSettlementStatus(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200"
          >
            <option value="ALL">All Settlements</option>
            <option value="UNSETTLED">Unsettled Claims</option>
            <option value="SETTLED">Settled Claims</option>
          </select>
        </div>
      </div>

      {/* Expenses Table */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200/80 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-3 px-3.5">Expense # / Date</th>
                <th className="py-3 px-3.5">Category & Payee</th>
                <th className="py-3 px-3.5">Paid By / Mode</th>
                <th className="py-3 px-3.5 text-right">Amount</th>
                <th className="py-3 px-3.5 text-center">Approval</th>
                <th className="py-3 px-3.5 text-center">Settlement</th>
                <th className="py-3 px-3.5">Remark</th>
                <th className="py-3 px-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-600" />
                    Loading expenses...
                  </td>
                </tr>
              ) : data && data.items.length > 0 ? (
                data.items.map((exp) => (
                  <tr
                    key={exp.expense_id}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    {/* Expense # & Date */}
                    <td className="py-3 px-3.5">
                      <div className="font-mono font-bold text-slate-900 dark:text-white">
                        {exp.expense_number}
                      </div>
                      <div className="text-[11px] text-slate-400">{exp.formatted_expense_date}</div>
                    </td>

                    {/* Category & Payee */}
                    <td className="py-3 px-3.5">
                      <div className="font-bold text-slate-800 dark:text-slate-200">{exp.payee_name}</div>
                      <span className="inline-block mt-0.5 text-[10px] font-bold px-2 py-0.2 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                        {exp.category.replace(/_/g, ' ')}
                      </span>
                    </td>

                    {/* Paid By / Mode */}
                    <td className="py-3 px-3.5">
                      <div className="font-medium text-slate-700 dark:text-slate-300">
                        {exp.paid_by_type === 'EMPLOYEE' ? (
                          <span className="text-amber-600 font-bold">Employee Out-of-Pocket</span>
                        ) : (
                          <span>Company Direct</span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-400">{exp.payment_mode}</div>
                    </td>

                    {/* Amount */}
                    <td className="py-3 px-3.5 text-right font-mono font-black text-slate-900 dark:text-white">
                      {exp.formatted_amount}
                    </td>

                    {/* Approval Status */}
                    <td className="py-3 px-3.5 text-center whitespace-nowrap">
                      {exp.approval_status === 'APPROVED' && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          Approved
                        </span>
                      )}
                      {exp.approval_status === 'PENDING' && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                          Pending Review
                        </span>
                      )}
                      {exp.approval_status === 'REJECTED' && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                          Rejected
                        </span>
                      )}
                    </td>

                    {/* Settlement Status */}
                    <td className="py-3 px-3.5 text-center whitespace-nowrap">
                      {exp.paid_by_type === 'EMPLOYEE' ? (
                        exp.settlement_status === 'SETTLED' ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            Settled
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                            Unsettled
                          </span>
                        )
                      ) : (
                        <span className="text-slate-400 text-[10px] font-medium">N/A (Company Paid)</span>
                      )}
                    </td>

                    {/* Remark */}
                    <td className="py-3 px-3.5 max-w-[160px]">
                      {exp.remark ? (
                        <div className="text-[11px] text-slate-600 dark:text-slate-300 truncate" title={exp.remark}>
                          {exp.remark}
                        </div>
                      ) : (
                        <span className="text-[11px] text-slate-300 italic">No notes</span>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-3.5 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-1.5">
                        {exp.bill_attachment_path && (
                          <a
                            href={`/api/v1/accounts/attachments/expenses/${exp.bill_attachment_name || 'bill.pdf'}`}
                            target="_blank"
                            rel="noreferrer"
                            className="p-1 text-indigo-600 hover:bg-indigo-50 rounded-md"
                            title="View Supporting Bill"
                          >
                            <Paperclip className="w-3.5 h-3.5" />
                          </a>
                        )}

                        {exp.approval_status === 'PENDING' && canApprove && (
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => handleApproveReject(exp.expense_id, 'APPROVE')}
                              className="px-2 py-0.5 rounded-md bg-emerald-600 text-white font-semibold text-[10px] hover:bg-emerald-700"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => handleApproveReject(exp.expense_id, 'REJECT')}
                              className="px-2 py-0.5 rounded-md bg-rose-100 text-rose-700 font-semibold text-[10px] hover:bg-rose-200"
                            >
                              Reject
                            </button>
                          </div>
                        )}

                        {exp.paid_by_type === 'EMPLOYEE' &&
                          exp.approval_status === 'APPROVED' &&
                          exp.settlement_status === 'UNSETTLED' &&
                          canSettle && (
                            <button
                              onClick={() => handleOpenSettle(exp)}
                              className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-semibold text-[11px] flex items-center gap-1"
                            >
                              <Wallet className="w-3 h-3" />
                              <span>Settle</span>
                            </button>
                          )}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400 text-xs">
                    No expense records found matching the filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && data.total_count > limit && (
          <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
            <span>Showing {data.items.length} of {data.total_count} expenses</span>
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
              <span className="font-semibold text-slate-700 dark:text-slate-300 px-2">Page {page}</span>
              <Button
                size="sm"
                variant="outline"
                disabled={data.items.length < limit}
                onClick={() => setPage((p) => p + 1)}
                className="h-8 px-2.5 rounded-lg"
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Record Expense Modal */}
      {recordModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-lg w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                  Record Direct Expense / Claim
                </h3>
                <p className="text-xs text-slate-500">
                  Submit operational cost, government fee challan, or staff reimbursement.
                </p>
              </div>
              <button
                onClick={() => setRecordModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitExpense} className="p-6 space-y-4">
              {formError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{formError}</span>
                </div>
              )}

              {/* Category & Amount */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Expense Category*
                  </label>
                  <select
                    value={expCategory}
                    onChange={(e) => setExpCategory(e.target.value as any)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-semibold"
                  >
                    <option value="GOVT_FEES">Govt Fees Challan</option>
                    <option value="VENDOR_COST">Vendor / Consultant Cost</option>
                    <option value="INCIDENTAL_COST">Incidental Cost</option>
                    <option value="EMPLOYEE_REIMBURSEMENT">Employee Reimbursement</option>
                    <option value="OTHER_DIRECT_COST">Other Direct Cost</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Amount (₹)*
                  </label>
                  <input
                    type="number"
                    step="any"
                    min="1"
                    required
                    value={expAmount}
                    onChange={(e) => setExpAmount(e.target.value)}
                    placeholder="Enter amount"
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-bold"
                  />
                </div>
              </div>

              {/* Payee & Date */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Payee / Vendor Name*
                  </label>
                  <input
                    type="text"
                    required
                    value={payeeName}
                    onChange={(e) => setPayeeName(e.target.value)}
                    placeholder="e.g. FSSAI Portal / Consultant"
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Expense Date*
                  </label>
                  <input
                    type="date"
                    required
                    value={expDate}
                    onChange={(e) => setExpDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                  />
                </div>
              </div>

              {/* Paid By Type & Mode */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Paid By*
                  </label>
                  <select
                    value={expPaidByType}
                    onChange={(e) => setExpPaidByType(e.target.value as any)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-semibold"
                  >
                    <option value="COMPANY">Company Bank / Card</option>
                    <option value="EMPLOYEE">Employee (Reimbursable)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Payment Mode
                  </label>
                  <select
                    value={expPaymentMode}
                    onChange={(e) => setExpPaymentMode(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                  >
                    <option value="BANK_TRANSFER">Bank Transfer (NEFT/RTGS)</option>
                    <option value="UPI">UPI / Net Banking</option>
                    <option value="CARD">Company Debit/Credit Card</option>
                    <option value="CASH">Cash</option>
                  </select>
                </div>
              </div>

              {/* Supporting Bill File */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Supporting Bill / Challan Attachment
                </label>
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={(e) => setBillFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
                />
              </div>

              {/* Remark */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Remark / Justification
                </label>
                <textarea
                  rows={2}
                  value={expRemark}
                  onChange={(e) => setExpRemark(e.target.value)}
                  placeholder="Optional notes or Challan reference..."
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
                  disabled={isSubmittingExpense}
                  size="sm"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5"
                >
                  <Check className="w-4 h-4" />
                  <span>{isSubmittingExpense ? 'Saving...' : 'Save Expense'}</span>
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Settle Reimbursement Modal */}
      {settleModalOpen && selectedExpense && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-md w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                  Settle Employee Reimbursement
                </h3>
                <p className="text-xs text-slate-500">
                  Disburse out-of-pocket claim of {selectedExpense.formatted_amount} to employee.
                </p>
              </div>
              <button
                onClick={() => setSettleModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitSettle} className="p-6 space-y-4">
              <div className="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 flex items-center justify-between text-xs">
                <span className="text-emerald-800 dark:text-emerald-200 font-medium">Reimbursement Amount:</span>
                <span className="font-mono font-extrabold text-emerald-700 dark:text-emerald-300 text-sm">
                  {selectedExpense.formatted_amount}
                </span>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Disbursement UTR / Bank Reference
                </label>
                <input
                  type="text"
                  placeholder="e.g. UTR / IMPS reference"
                  value={settlementRef}
                  onChange={(e) => setSettlementRef(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-mono"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2.5">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setSettleModalOpen(false)}
                  className="rounded-xl text-xs"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmittingSettle}
                  size="sm"
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5"
                >
                  <Check className="w-4 h-4" />
                  <span>{isSubmittingSettle ? 'Settling...' : 'Confirm Settlement'}</span>
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

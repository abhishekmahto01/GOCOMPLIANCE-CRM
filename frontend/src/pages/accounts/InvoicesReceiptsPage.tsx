import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  RefreshCw,
  PlusCircle,
  CheckCircle2,
  AlertCircle,
  Paperclip,
  ChevronLeft,
  ChevronRight,
  Check,
  X,
} from 'lucide-react';
import {
  getInvoicesListApi,
  getAccountsFilterOptionsApi,
  createInvoiceApi,
  uploadAccountsAttachmentApi,
} from '../../api/accounts';
import type {
  AccountsInvoiceListResponse,
  AccountsFilterOptions,
} from '../../types/accounts';
import { Button } from '../../components/ui/button';
import { useAuth } from '../../context/AuthContext';

export const InvoicesReceiptsPage: React.FC = () => {
  const { isSuperAdmin, session, hasPermission, hasModuleAccess } = useAuth();
  const isDirector = session.userRole?.toUpperCase() === 'DIRECTOR';
  const canCreate = isSuperAdmin || isDirector || hasPermission('ACCOUNTS_INVOICES', 'create') || hasModuleAccess('ACCOUNTS');


  const [data, setData] = useState<AccountsInvoiceListResponse | null>(null);
  const [filterOptions, setFilterOptions] = useState<AccountsFilterOptions | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Filters
  const [page, setPage] = useState<number>(1);
  const [limit] = useState<number>(20);
  const [search, setSearch] = useState<string>('');
  const [companyId, setCompanyId] = useState<string>('ALL');
  const [invoiceType, setInvoiceType] = useState<string>('ALL');
  const [missingOnly, setMissingOnly] = useState<boolean>(false);
  const [fromDate] = useState<string>('');
  const [toDate] = useState<string>('');
  const [sortBy] = useState<string>('invoice_date');
  const [sortOrder] = useState<string>('desc');

  // Create Invoice Modal State
  const [createModalOpen, setCreateModalOpen] = useState<boolean>(false);
  const [salesOrderId, setSalesOrderId] = useState<string>('');
  const [invType, setInvType] = useState<'PROFORMA' | 'TAX_INVOICE'>('TAX_INVOICE');
  const [invoiceNumber, setInvoiceNumber] = useState<string>('');
  const [invoiceDate, setInvoiceDate] = useState<string>(new Date().toISOString().slice(0, 10));
  const [dueDate, setDueDate] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [taxableAmount, setTaxableAmount] = useState<string>('');
  const [cgstAmount, setCgstAmount] = useState<string>('');
  const [sgstAmount, setSgstAmount] = useState<string>('');
  const [igstAmount, setIgstAmount] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [invoiceFile, setInvoiceFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    getAccountsFilterOptionsApi()
      .then(setFilterOptions)
      .catch((err) => console.error('Error fetching filter options:', err));
  }, []);

  const fetchInvoices = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getInvoicesListApi({
        page,
        limit,
        search: search.trim() || undefined,
        company_id: companyId,
        invoice_type: invoiceType,
        missing_only: missingOnly,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setData(res);
    } catch (err: any) {
      console.error('Error loading invoices:', err);
      setError(err?.response?.data?.detail || 'Failed to fetch invoice records');
    } finally {
      setIsLoading(false);
    }
  }, [page, limit, search, companyId, invoiceType, missingOnly, fromDate, toDate, sortBy, sortOrder]);

  useEffect(() => {
    fetchInvoices();
  }, [fetchInvoices]);

  const handleOpenCreateModal = () => {
    setSalesOrderId('');
    setInvType('TAX_INVOICE');
    setInvoiceNumber('');
    setInvoiceDate(new Date().toISOString().slice(0, 10));
    setDueDate('');
    setAmount('');
    setTaxableAmount('');
    setCgstAmount('');
    setSgstAmount('');
    setIgstAmount('');
    setNotes('');
    setInvoiceFile(null);
    setFormError(null);
    setCreateModalOpen(true);
  };

  const handleCreateInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!invoiceNumber.trim()) {
      setFormError('Please enter an invoice number');
      return;
    }
    const amt = parseFloat(amount);
    if (isNaN(amt) || amt <= 0) {
      setFormError('Please enter a valid invoice amount');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      // 1. Upload PDF if provided
      if (invoiceFile) {
        await uploadAccountsAttachmentApi(invoiceFile, 'invoices');
      }

      await createInvoiceApi({
        sales_order_id: salesOrderId,
        invoice_type: invType,
        invoice_number: invoiceNumber.trim(),
        invoice_date: invoiceDate,
        due_date: dueDate || undefined,
        amount: amt,
        taxable_amount: taxableAmount ? parseFloat(taxableAmount) : undefined,
        cgst_amount: cgstAmount ? parseFloat(cgstAmount) : undefined,
        sgst_amount: sgstAmount ? parseFloat(sgstAmount) : undefined,
        igst_amount: igstAmount ? parseFloat(igstAmount) : undefined,
        notes: notes.trim() || undefined,
      });

      setSuccessMsg(`Invoice ${invoiceNumber.trim()} created and linked successfully.`);
      setTimeout(() => setSuccessMsg(null), 4000);
      setCreateModalOpen(false);
      fetchInvoices();
    } catch (err: any) {
      console.error('Error creating invoice:', err);
      setFormError(err?.response?.data?.detail || 'Failed to save invoice record');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Invoices & Billing Receipts
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Manage Proforma Invoices, Tax Invoices, PDF attachments, and missing invoice alerts.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={() => fetchInvoices()}
            disabled={isLoading}
            variant="outline"
            size="sm"
            className="rounded-xl text-xs flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
          {canCreate && (
            <Button
              onClick={handleOpenCreateModal}
              size="sm"
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5 shadow-xs"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Link New Invoice</span>
            </Button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Total Invoiced Value</span>
            <div className="text-xl font-black text-slate-900 dark:text-white mt-1">
              ₹{data.total_invoiced_amount.toLocaleString('en-IN')}
            </div>
            <span className="text-[11px] text-slate-500">{data.total_count} total invoices</span>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Tax Invoices</span>
            <div className="text-xl font-black text-indigo-600 dark:text-indigo-400 mt-1">
              {data.total_tax_invoice_count}
            </div>
            <span className="text-[11px] text-indigo-600 font-semibold">Official GST invoices</span>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Proforma Invoices</span>
            <div className="text-xl font-black text-amber-600 dark:text-amber-400 mt-1">
              {data.total_proforma_count}
            </div>
            <span className="text-[11px] text-amber-600 font-semibold">Quotations / PI</span>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Missing Invoices</span>
            <div className="text-xl font-black text-rose-600 dark:text-rose-400 mt-1">
              {data.orders_without_invoice_count}
            </div>
            <span className="text-[11px] text-rose-500 font-semibold">Confirmed orders pending invoice</span>
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
          <div className="relative min-w-[240px]">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search invoice no, client, order..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Invoice Type Filter */}
          <select
            aria-label="Invoice Type Filter"
            value={invoiceType}
            onChange={(e) => {
              setInvoiceType(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 font-semibold"
          >
            <option value="ALL">All Invoice Types</option>
            <option value="TAX_INVOICE">Tax Invoices Only</option>
            <option value="PROFORMA">Proforma Invoices Only</option>
          </select>

          {/* Company Filter */}
          {filterOptions && filterOptions.companies.length > 0 && (
            <select
              aria-label="Company Filter"
              value={companyId}
              onChange={(e) => {
                setCompanyId(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 max-w-[170px] truncate"
            >
              <option value="ALL">All Companies</option>
              {filterOptions.companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                </option>
              ))}
            </select>
          )}

          {/* Missing Invoices Toggle */}
          <label className="flex items-center gap-2 text-xs font-semibold text-rose-600 dark:text-rose-400 cursor-pointer select-none bg-rose-50 dark:bg-rose-950/40 px-3 py-2 rounded-xl border border-rose-200 dark:border-rose-800">
            <input
              type="checkbox"
              checked={missingOnly}
              onChange={(e) => {
                setMissingOnly(e.target.checked);
                setPage(1);
              }}
              className="rounded text-rose-600 focus:ring-rose-500"
            />
            <span>Missing Tax Invoice Only</span>
          </label>
        </div>
      </div>

      {/* Invoices Table */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200/80 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-3 px-3.5">Invoice # & Type</th>
                <th className="py-3 px-3.5">Company & Client</th>
                <th className="py-3 px-3.5">Order / Service</th>
                <th className="py-3 px-3.5">Invoice Date</th>
                <th className="py-3 px-3.5 text-right">Invoice Amount</th>
                <th className="py-3 px-3.5 text-center">Status</th>
                <th className="py-3 px-3.5 text-right">Attachment / Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-600" />
                    Loading invoices...
                  </td>
                </tr>
              ) : data && data.items.length > 0 ? (
                data.items.map((inv) => (
                  <tr
                    key={inv.invoice_id}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    {/* Invoice # & Type */}
                    <td className="py-3 px-3.5">
                      <div className="font-mono font-bold text-slate-900 dark:text-white">
                        {inv.invoice_number}
                      </div>
                      <span
                        className={`inline-block mt-0.5 text-[10px] font-bold px-2 py-0.2 rounded-full ${
                          inv.invoice_type === 'TAX_INVOICE'
                            ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                            : 'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}
                      >
                        {inv.invoice_type === 'TAX_INVOICE' ? 'Tax Invoice' : 'Proforma Invoice'}
                      </span>
                    </td>

                    {/* Company & Client */}
                    <td className="py-3 px-3.5">
                      <div className="font-bold text-slate-800 dark:text-slate-200 truncate max-w-[160px]">
                        {inv.client_name || 'N/A'}
                      </div>
                      <div className="text-[11px] text-slate-400 truncate max-w-[160px]">
                        {inv.company_name}
                      </div>
                    </td>

                    {/* Order & Service */}
                    <td className="py-3 px-3.5">
                      <div className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                        {inv.sales_order_number || 'N/A'}
                      </div>
                      <div className="text-[11px] text-slate-600 dark:text-slate-300 truncate max-w-[160px]">
                        {inv.service_name}
                      </div>
                    </td>

                    {/* Invoice Date */}
                    <td className="py-3 px-3.5 whitespace-nowrap">
                      <div className="font-medium text-slate-700 dark:text-slate-300">{inv.formatted_invoice_date}</div>
                      {inv.formatted_due_date && (
                        <div className="text-[10px] text-slate-400">Due: {inv.formatted_due_date}</div>
                      )}
                    </td>

                    {/* Invoice Amount */}
                    <td className="py-3 px-3.5 text-right font-mono font-bold text-slate-900 dark:text-white">
                      {inv.formatted_amount}
                    </td>

                    {/* Status */}
                    <td className="py-3 px-3.5 text-center whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {inv.status}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-3.5 text-right whitespace-nowrap">
                      {inv.file_path ? (
                        <a
                          href={`/api/v1/accounts/attachments/invoices/${inv.file_name || 'invoice.pdf'}`}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 font-semibold text-[11px] transition-colors"
                        >
                          <Paperclip className="w-3.5 h-3.5" />
                          <span>PDF</span>
                        </a>
                      ) : (
                        <span className="text-[11px] text-slate-400 italic">No PDF attached</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400 text-xs">
                    No invoice records found matching the filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && data.total_count > limit && (
          <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
            <span>Showing {data.items.length} of {data.total_count} invoices</span>
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

      {/* Link New Invoice Modal */}
      {createModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-lg w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                  Link / Record Invoice
                </h3>
                <p className="text-xs text-slate-500">
                  Enter invoice details and attach supporting PDF document.
                </p>
              </div>
              <button
                onClick={() => setCreateModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateInvoice} className="p-6 space-y-4">
              {formError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{formError}</span>
                </div>
              )}

              {/* Invoice Type & Number */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Invoice Type*
                  </label>
                  <select
                    value={invType}
                    onChange={(e) => setInvType(e.target.value as any)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-semibold"
                  >
                    <option value="TAX_INVOICE">Tax Invoice</option>
                    <option value="PROFORMA">Proforma Invoice</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Invoice Number*
                  </label>
                  <input
                    type="text"
                    required
                    value={invoiceNumber}
                    onChange={(e) => setInvoiceNumber(e.target.value)}
                    placeholder="e.g. INV/2026/001"
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-mono font-bold"
                  />
                </div>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Invoice Date*
                  </label>
                  <input
                    type="date"
                    required
                    value={invoiceDate}
                    onChange={(e) => setInvoiceDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Due Date
                  </label>
                  <input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                  />
                </div>
              </div>

              {/* Amount */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Invoice Amount (₹)*
                </label>
                <input
                  type="number"
                  step="any"
                  min="1"
                  required
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="Total amount"
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-bold"
                />
              </div>

              {/* PDF File */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Invoice PDF Attachment
                </label>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setInvoiceFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
                />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Notes
                </label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Optional invoice notes..."
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2.5">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setCreateModalOpen(false)}
                  className="rounded-xl text-xs"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  size="sm"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5"
                >
                  <Check className="w-4 h-4" />
                  <span>{isSubmitting ? 'Saving...' : 'Save Invoice'}</span>
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

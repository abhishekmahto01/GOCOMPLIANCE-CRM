import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  RefreshCw,
  PhoneCall,
  CheckCircle2,
  AlertCircle,
  History,
  ChevronLeft,
  ChevronRight,
  Check,
  X,
} from 'lucide-react';
import {
  getOutstandingAccountsApi,
  getAccountsFilterOptionsApi,
  recordOrderFollowUpApi,
  getOrderFollowUpsApi,
} from '../../api/accounts';
import type {
  OutstandingItemRead,
  OutstandingResponse,
  OutstandingAgeingSummary,
  AccountsFilterOptions,
  AccountsFollowUpRead,
} from '../../types/accounts';
import { Button } from '../../components/ui/button';

export const OutstandingFollowupsPage: React.FC = () => {
  const [data, setData] = useState<OutstandingResponse | null>(null);
  const [summary, setSummary] = useState<OutstandingAgeingSummary | null>(null);
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
  const [ageingBucket, setAgeingBucket] = useState<string>('ALL');
  const [opsCompletedOnly, setOpsCompletedOnly] = useState<boolean>(false);
  const [sortBy] = useState<string>('days_overdue');
  const [sortOrder] = useState<string>('desc');

  // Modals state
  const [selectedOrder, setSelectedOrder] = useState<OutstandingItemRead | null>(null);
  const [addFollowUpModalOpen, setAddFollowUpModalOpen] = useState<boolean>(false);
  const [historyModalOpen, setHistoryModalOpen] = useState<boolean>(false);
  const [followUpList, setFollowUpList] = useState<AccountsFollowUpRead[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);

  // Add follow-up form state
  const [followUpDate, setFollowUpDate] = useState<string>(new Date().toISOString().slice(0, 10));
  const [nextFollowUpDate, setNextFollowUpDate] = useState<string>('');
  const [contactChannel, setContactChannel] = useState<string>('PHONE');
  const [contactPerson, setContactPerson] = useState<string>('');
  const [remarkText, setRemarkText] = useState<string>('');
  const [isSubmittingFollowUp, setIsSubmittingFollowUp] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    getAccountsFilterOptionsApi()
      .then(setFilterOptions)
      .catch((err) => console.error('Error fetching filter options:', err));
  }, []);

  const fetchOutstanding = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getOutstandingAccountsApi({
        page,
        limit,
        search: search.trim() || undefined,
        company_id: companyId,
        employee_id: employeeId,
        ageing_bucket: ageingBucket,
        operations_completed_only: opsCompletedOnly,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setData(res);
      setSummary(res.summary);
    } catch (err: any) {
      console.error('Error loading outstanding debtors:', err);
      setError(err?.response?.data?.detail || 'Failed to fetch outstanding accounts');
    } finally {
      setIsLoading(false);
    }
  }, [page, limit, search, companyId, employeeId, ageingBucket, opsCompletedOnly, sortBy, sortOrder]);

  useEffect(() => {
    fetchOutstanding();
  }, [fetchOutstanding]);

  // Open Log Follow-up Modal
  const handleOpenAddFollowUp = (order: OutstandingItemRead) => {
    setSelectedOrder(order);
    setFollowUpDate(new Date().toISOString().slice(0, 10));
    setNextFollowUpDate('');
    setContactChannel('PHONE');
    setContactPerson(order.client_name || '');
    setRemarkText('');
    setFormError(null);
    setAddFollowUpModalOpen(true);
  };

  // Submit Follow-up
  const handleSubmitFollowUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOrder) return;
    if (!remarkText.trim()) {
      setFormError('Please enter a follow-up remark');
      return;
    }

    setIsSubmittingFollowUp(true);
    setFormError(null);

    try {
      await recordOrderFollowUpApi(selectedOrder.sales_order_id, {
        follow_up_date: followUpDate,
        next_follow_up_date: nextFollowUpDate || undefined,
        contact_channel: contactChannel,
        contact_person: contactPerson.trim() || undefined,
        remark_text: remarkText.trim(),
      });

      setSuccessMsg(`Follow-up logged successfully for ${selectedOrder.order_number}`);
      setTimeout(() => setSuccessMsg(null), 4000);
      setAddFollowUpModalOpen(false);
      fetchOutstanding();
    } catch (err: any) {
      console.error('Error recording follow-up:', err);
      setFormError(err?.response?.data?.detail || 'Failed to record follow-up');
    } finally {
      setIsSubmittingFollowUp(false);
    }
  };

  // Open Follow-up History Modal
  const handleOpenHistory = async (order: OutstandingItemRead) => {
    setSelectedOrder(order);
    setHistoryModalOpen(true);
    setLoadingHistory(true);
    try {
      const list = await getOrderFollowUpsApi(order.sales_order_id);
      setFollowUpList(list);
    } catch (err) {
      console.error('Error loading follow-up history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Outstanding Receivables & Debtor Follow-ups
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Track ageing balances (1–30, 31–60, 61–90, 90+ days), completed operations work, and debtor collection promises.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={() => fetchOutstanding()}
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

      {/* Ageing Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {/* Current (Not Due) */}
          <div
            onClick={() => setAgeingBucket(ageingBucket === 'CURRENT' ? 'ALL' : 'CURRENT')}
            className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
              ageingBucket === 'CURRENT'
                ? 'bg-blue-50 border-blue-500 dark:bg-blue-950/60'
                : 'bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800'
            }`}
          >
            <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider block">Current / Not Due</span>
            <div className="text-base font-black text-slate-900 dark:text-white mt-1">
              ₹{summary.current_amount.toLocaleString('en-IN')}
            </div>
            <span className="text-[10px] text-slate-400">{summary.current_count} orders</span>
          </div>

          {/* 1 - 30 Days Overdue */}
          <div
            onClick={() => setAgeingBucket(ageingBucket === '1_30_DAYS' ? 'ALL' : '1_30_DAYS')}
            className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
              ageingBucket === '1_30_DAYS'
                ? 'bg-amber-50 border-amber-500 dark:bg-amber-950/60'
                : 'bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800'
            }`}
          >
            <span className="text-[10px] font-bold text-amber-600 uppercase tracking-wider block">1–30 Days</span>
            <div className="text-base font-black text-amber-600 mt-1">
              ₹{summary.days_1_30_amount.toLocaleString('en-IN')}
            </div>
            <span className="text-[10px] text-slate-400">{summary.days_1_30_count} orders</span>
          </div>

          {/* 31 - 60 Days Overdue */}
          <div
            onClick={() => setAgeingBucket(ageingBucket === '31_60_DAYS' ? 'ALL' : '31_60_DAYS')}
            className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
              ageingBucket === '31_60_DAYS'
                ? 'bg-orange-50 border-orange-500 dark:bg-orange-950/60'
                : 'bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800'
            }`}
          >
            <span className="text-[10px] font-bold text-orange-600 uppercase tracking-wider block">31–60 Days</span>
            <div className="text-base font-black text-orange-600 mt-1">
              ₹{summary.days_31_60_amount.toLocaleString('en-IN')}
            </div>
            <span className="text-[10px] text-slate-400">{summary.days_31_60_count} orders</span>
          </div>

          {/* 61 - 90 Days Overdue */}
          <div
            onClick={() => setAgeingBucket(ageingBucket === '61_90_DAYS' ? 'ALL' : '61_90_DAYS')}
            className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
              ageingBucket === '61_90_DAYS'
                ? 'bg-rose-50 border-rose-500 dark:bg-rose-950/60'
                : 'bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800'
            }`}
          >
            <span className="text-[10px] font-bold text-rose-600 uppercase tracking-wider block">61–90 Days</span>
            <div className="text-base font-black text-rose-600 mt-1">
              ₹{summary.days_61_90_amount.toLocaleString('en-IN')}
            </div>
            <span className="text-[10px] text-slate-400">{summary.days_61_90_count} orders</span>
          </div>

          {/* Over 90 Days Overdue */}
          <div
            onClick={() => setAgeingBucket(ageingBucket === 'OVER_90_DAYS' ? 'ALL' : 'OVER_90_DAYS')}
            className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
              ageingBucket === 'OVER_90_DAYS'
                ? 'bg-red-50 border-red-600 dark:bg-red-950/60'
                : 'bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800'
            }`}
          >
            <span className="text-[10px] font-bold text-red-600 uppercase tracking-wider block">90+ Days (Critical)</span>
            <div className="text-base font-black text-red-600 mt-1">
              ₹{summary.over_90_days_amount.toLocaleString('en-IN')}
            </div>
            <span className="text-[10px] text-slate-400">{summary.over_90_days_count} orders</span>
          </div>

          {/* No Due Date */}
          <div
            onClick={() => setAgeingBucket(ageingBucket === 'NO_DUE_DATE' ? 'ALL' : 'NO_DUE_DATE')}
            className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
              ageingBucket === 'NO_DUE_DATE'
                ? 'bg-slate-200 border-slate-600 dark:bg-slate-800'
                : 'bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800'
            }`}
          >
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">No Due Date</span>
            <div className="text-base font-black text-slate-700 dark:text-slate-300 mt-1">
              ₹{summary.no_due_date_amount.toLocaleString('en-IN')}
            </div>
            <span className="text-[10px] text-slate-400">{summary.no_due_date_count} orders</span>
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
              placeholder="Search client, order no, license..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Ageing Bucket Filter */}
          <select
            aria-label="Ageing Filter"
            value={ageingBucket}
            onChange={(e) => {
              setAgeingBucket(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 font-semibold"
          >
            <option value="ALL">All Ageing Buckets</option>
            <option value="CURRENT">Current (Not Yet Due)</option>
            <option value="1_30_DAYS">1–30 Days Overdue</option>
            <option value="31_60_DAYS">31–60 Days Overdue</option>
            <option value="61_90_DAYS">61–90 Days Overdue</option>
            <option value="OVER_90_DAYS">90+ Days (Critical)</option>
            <option value="NO_DUE_DATE">No Due Date Set</option>
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

          {/* Salesperson Filter */}
          {filterOptions && filterOptions.salespersons.length > 0 && (
            <select
              aria-label="Salesperson Filter"
              value={employeeId}
              onChange={(e) => {
                setEmployeeId(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 max-w-[170px] truncate"
            >
              <option value="ALL">All Salespersons</option>
              {filterOptions.salespersons.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          )}

          {/* Ops Completed Work Only Toggle */}
          <label className="flex items-center gap-2 text-xs font-semibold text-indigo-600 dark:text-indigo-400 cursor-pointer select-none bg-indigo-50 dark:bg-indigo-950/40 px-3 py-2 rounded-xl border border-indigo-200 dark:border-indigo-800">
            <input
              type="checkbox"
              checked={opsCompletedOnly}
              onChange={(e) => {
                setOpsCompletedOnly(e.target.checked);
                setPage(1);
              }}
              className="rounded text-indigo-600 focus:ring-indigo-500"
            />
            <span>Ops Work Completed</span>
          </label>
        </div>
      </div>

      {/* Debtors Table */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200/80 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-3 px-3.5">Client / Company</th>
                <th className="py-3 px-3.5">Order / Service</th>
                <th className="py-3 px-3.5 text-right">Total Payable</th>
                <th className="py-3 px-3.5 text-right">Received</th>
                <th className="py-3 px-3.5 text-right">Pending Amount</th>
                <th className="py-3 px-3.5 text-center">Due Date / Overdue</th>
                <th className="py-3 px-3.5 text-center">Ageing Bucket</th>
                <th className="py-3 px-3.5">Latest Follow-up</th>
                <th className="py-3 px-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {isLoading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-600" />
                    Loading outstanding debtor records...
                  </td>
                </tr>
              ) : data && data.items.length > 0 ? (
                data.items.map((item) => (
                  <tr
                    key={item.sales_order_id}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    {/* Client & Company */}
                    <td className="py-3 px-3.5">
                      <div className="font-bold text-slate-800 dark:text-slate-200 truncate max-w-[160px]">
                        {item.client_name}
                      </div>
                      <div className="text-[11px] text-slate-400 truncate max-w-[160px]">
                        {item.company_name}
                      </div>
                      {item.client_phone && (
                        <div className="text-[10px] text-slate-400 font-mono">📞 {item.client_phone}</div>
                      )}
                    </td>

                    {/* Order & Service */}
                    <td className="py-3 px-3.5">
                      <div className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                        {item.order_number}
                      </div>
                      <div className="text-[11px] text-slate-600 dark:text-slate-300 truncate max-w-[160px]">
                        {item.service_name}
                      </div>
                      {item.is_work_completed && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.2 rounded-md">
                          <CheckCircle2 className="w-2.5 h-2.5" /> Ops Done
                        </span>
                      )}
                    </td>

                    {/* Total Payable */}
                    <td className="py-3 px-3.5 text-right font-mono font-bold text-slate-800 dark:text-slate-200">
                      {item.formatted_total_payable}
                    </td>

                    {/* Verified Received */}
                    <td className="py-3 px-3.5 text-right font-mono font-bold text-emerald-600 dark:text-emerald-400">
                      {item.formatted_verified_received}
                    </td>

                    {/* Pending Amount */}
                    <td className="py-3 px-3.5 text-right font-mono font-black text-rose-600 dark:text-rose-400">
                      {item.formatted_pending_amount}
                    </td>

                    {/* Due Date & Days Overdue */}
                    <td className="py-3 px-3.5 text-center whitespace-nowrap">
                      {item.due_date ? (
                        <div>
                          <div className="font-medium text-slate-700 dark:text-slate-300">{item.formatted_due_date}</div>
                          {item.days_overdue > 0 ? (
                            <span className="text-[10px] font-bold text-rose-600">
                              {item.days_overdue} days overdue
                            </span>
                          ) : (
                            <span className="text-[10px] font-bold text-emerald-600">
                              On schedule
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-[11px] text-slate-400 italic">No Due Date</span>
                      )}
                    </td>

                    {/* Ageing Bucket Badge */}
                    <td className="py-3 px-3.5 text-center whitespace-nowrap">
                      {item.ageing_bucket === 'CURRENT' && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                          Current
                        </span>
                      )}
                      {item.ageing_bucket === '1_30_DAYS' && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                          1–30 Days
                        </span>
                      )}
                      {item.ageing_bucket === '31_60_DAYS' && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-orange-50 text-orange-700 border border-orange-200">
                          31–60 Days
                        </span>
                      )}
                      {item.ageing_bucket === '61_90_DAYS' && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                          61–90 Days
                        </span>
                      )}
                      {item.ageing_bucket === 'OVER_90_DAYS' && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-700 border border-red-300">
                          90+ Days
                        </span>
                      )}
                      {item.ageing_bucket === 'NO_DUE_DATE' && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-600 border border-slate-200">
                          No Due Date
                        </span>
                      )}
                    </td>

                    {/* Latest Follow-up */}
                    <td className="py-3 px-3.5 max-w-[200px]">
                      {item.latest_follow_up ? (
                        <div>
                          <div className="text-[11px] text-slate-700 dark:text-slate-300 truncate" title={item.latest_follow_up.remark_text}>
                            {item.latest_follow_up.remark_text}
                          </div>
                          <div className="text-[10px] text-slate-400">
                            {item.latest_follow_up.formatted_follow_up_date} &bull; {item.latest_follow_up.created_by_name}
                            {item.latest_follow_up.next_follow_up_date && ` &bull; Next: ${item.latest_follow_up.formatted_next_follow_up_date}`}
                          </div>
                        </div>
                      ) : (
                        <span className="text-[11px] text-slate-300 dark:text-slate-600 italic">No follow-ups yet</span>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-3.5 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleOpenAddFollowUp(item)}
                          className="px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 font-semibold text-[11px] transition-colors flex items-center gap-1"
                          title="Log Follow-up"
                        >
                          <PhoneCall className="w-3 h-3" />
                          <span>Follow-up</span>
                        </button>
                        <button
                          onClick={() => handleOpenHistory(item)}
                          className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-slate-100 rounded-lg transition-colors"
                          title="Follow-up Timeline"
                        >
                          <History className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400 text-xs">
                    No outstanding debtor records found matching the filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
            <span>
              Showing {((page - 1) * limit) + 1} - {Math.min(page * limit, data.total_count)} of {data.total_count} debtors
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

      {/* Log Follow-up Modal */}
      {addFollowUpModalOpen && selectedOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-md w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                  Log Debtor Follow-up
                </h3>
                <p className="text-xs text-slate-500">
                  {selectedOrder.client_name} &bull; Order {selectedOrder.order_number}
                </p>
              </div>
              <button
                onClick={() => setAddFollowUpModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitFollowUp} className="p-6 space-y-4">
              {/* Order Pending Balance Box */}
              <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 flex items-center justify-between text-xs">
                <span className="text-amber-800 dark:text-amber-200 font-medium">Pending Balance:</span>
                <span className="font-mono font-extrabold text-amber-700 dark:text-amber-300 text-sm">
                  {selectedOrder.formatted_pending_amount}
                </span>
              </div>

              {formError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{formError}</span>
                </div>
              )}

              {/* Follow-up Date & Channel */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Contact Channel*
                  </label>
                  <select
                    value={contactChannel}
                    onChange={(e) => setContactChannel(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 font-semibold"
                  >
                    <option value="PHONE">Phone Call</option>
                    <option value="WHATSAPP">WhatsApp</option>
                    <option value="EMAIL">Email</option>
                    <option value="IN_PERSON">In-Person Visit</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Follow-up Date*
                  </label>
                  <input
                    type="date"
                    required
                    value={followUpDate}
                    onChange={(e) => setFollowUpDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                  />
                </div>
              </div>

              {/* Contact Person & Next Date */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Contact Person / Spoke With
                  </label>
                  <input
                    type="text"
                    value={contactPerson}
                    onChange={(e) => setContactPerson(e.target.value)}
                    placeholder="Name of contact"
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Next Promised Date
                  </label>
                  <input
                    type="date"
                    value={nextFollowUpDate}
                    onChange={(e) => setNextFollowUpDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                  />
                </div>
              </div>

              {/* Remark */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Follow-up Notes / Client Commitment*
                </label>
                <textarea
                  rows={3}
                  required
                  value={remarkText}
                  onChange={(e) => setRemarkText(e.target.value)}
                  placeholder="Client confirmed payment will be released on Friday via NEFT..."
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2.5">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setAddFollowUpModalOpen(false)}
                  className="rounded-xl text-xs"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmittingFollowUp}
                  size="sm"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5"
                >
                  <Check className="w-4 h-4" />
                  <span>{isSubmittingFollowUp ? 'Saving...' : 'Save Follow-up'}</span>
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Follow-up Timeline Modal */}
      {historyModalOpen && selectedOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-lg w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                  Follow-up Timeline & History
                </h3>
                <p className="text-xs text-slate-500">
                  {selectedOrder.client_name} &bull; Order {selectedOrder.order_number}
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
                  Loading timeline...
                </div>
              ) : followUpList.length > 0 ? (
                <div className="relative border-l-2 border-slate-200 dark:border-slate-700 ml-4 space-y-6">
                  {followUpList.map((f) => (
                    <div key={f.follow_up_id} className="relative pl-6">
                      {/* Timeline dot */}
                      <div className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-indigo-600 border-2 border-white dark:border-slate-900" />

                      <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800 space-y-1.5">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-slate-800 dark:text-slate-200">
                            {f.contact_channel} &bull; {f.created_by_name || 'Staff'}
                          </span>
                          <span className="text-[10px] text-slate-400">{f.formatted_follow_up_date}</span>
                        </div>

                        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                          {f.remark_text}
                        </p>

                        {f.next_follow_up_date && (
                          <div className="text-[11px] font-bold text-amber-600 pt-1 border-t border-slate-200/60 dark:border-slate-700">
                            Next Follow-up: {f.formatted_next_follow_up_date}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-12 text-center text-slate-400 text-xs">
                  No follow-up history logged yet for this debtor.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useState, useEffect, useRef } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Clock,
  Search,
  RefreshCw,
  AlertCircle,
  Eye,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  UserPlus,
  MapPin,
  User,
  RotateCcw,
} from 'lucide-react';
import type {
  AssigneeOption,
  OperationApplication,
  OperationsTaskListResponse,
} from '../../types/operations';
import {
  getUnassignedOperationsOrdersApi,
  getOperationsAssigneesApi,
  assignOperationTaskApi,
} from '../../api/operations';
import { TaskDetailModal } from '../../components/operations/TaskDetailModal';
import { CompanyFilterTabs } from '../../components/common/CompanyFilterTabs';
import { CompanyBadge } from '../../components/common/CompanyBadge';

export const UnassignedOrdersPage: React.FC = () => {
  const context = useOutletContext<{
    addToast?: (type: 'success' | 'error' | 'info', title: string, message: string) => void;
  }>();

  const [taskListResponse, setTaskListResponse] = useState<OperationsTaskListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [clientName, setClientName] = useState('');
  const [debouncedClientName, setDebouncedClientName] = useState('');
  const [companyId, setCompanyId] = useState('ALL');
  const [page, setPage] = useState(1);
  const limit = 20;

  const currentRequestIdRef = useRef(0);

  // Debounce search input (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search.trim());
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  // Debounce client name input (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedClientName(clientName.trim());
    }, 300);
    return () => clearTimeout(timer);
  }, [clientName]);

  // Assignee options
  const [eligibleAssignees, setEligibleAssignees] = useState<AssigneeOption[]>([]);

  // Inline Quick Assign Modal State
  const [assigningTask, setAssigningTask] = useState<OperationApplication | null>(null);
  const [selectedAssigneeId, setSelectedAssigneeId] = useState('');
  const [assignPriority, setAssignPriority] = useState('MEDIUM');
  const [assignDueDate, setAssignDueDate] = useState('');
  const [assignNotes, setAssignNotes] = useState('');
  const [isSubmittingAssign, setIsSubmittingAssign] = useState(false);

  // Selected task modal state
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const loadUnassigned = async () => {
    const requestId = ++currentRequestIdRef.current;
    try {
      setLoading(true);
      setError(null);
      const data = await getUnassignedOperationsOrdersApi({
        page,
        limit,
        company_id: companyId !== 'ALL' ? companyId : undefined,
        search: debouncedSearch || undefined,
        client_name: debouncedClientName || undefined,
      });
      if (requestId === currentRequestIdRef.current) {
        setTaskListResponse(data);
      }
    } catch (err: any) {
      if (requestId === currentRequestIdRef.current) {
        setError(err?.response?.data?.detail || 'Failed to load unassigned applications.');
        setTaskListResponse(null);
      }
    } finally {
      if (requestId === currentRequestIdRef.current) {
        setLoading(false);
      }
    }
  };

  const loadAssignees = async () => {
    try {
      const data = await getOperationsAssigneesApi();
      setEligibleAssignees(data);
    } catch (err) {
      console.error('Failed to load eligible assignees', err);
    }
  };

  useEffect(() => {
    loadUnassigned();
  }, [page, companyId, debouncedSearch, debouncedClientName]);

  useEffect(() => {
    loadAssignees();
  }, []);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    setPage(1);
  };

  const handleClientNameChange = (val: string) => {
    setClientName(val);
    setPage(1);
  };

  const hasActiveFilters = Boolean(
    search ||
    clientName ||
    companyId !== 'ALL'
  );

  const handleClearFilters = () => {
    setSearch('');
    setDebouncedSearch('');
    setClientName('');
    setDebouncedClientName('');
    setCompanyId('ALL');
    setPage(1);
  };

  const handleAssignSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assigningTask || !selectedAssigneeId) return;
    if (!assignDueDate) {
      if (context?.addToast) {
        context.addToast('error', 'Due Date Required', 'Target Due Date is mandatory. Please select a due date.');
      }
      return;
    }
    try {
      setIsSubmittingAssign(true);
      await assignOperationTaskApi(assigningTask.application_id, {
        assignee_user_id: selectedAssigneeId,
        priority: assignPriority,
        target_due_date: assignDueDate,
        notes: assignNotes.trim() || undefined,
      });
      if (context?.addToast) {
        context.addToast('success', 'Task Assigned', `Application ${assigningTask.application_number} assigned successfully.`);
      }
      setAssigningTask(null);
      setSelectedAssigneeId('');
      setAssignNotes('');
      loadUnassigned();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to assign task.';
      if (context?.addToast) {
        context.addToast('error', 'Assignment Failed', msg);
      }
    } finally {
      setIsSubmittingAssign(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
            <Clock className="w-6 h-6 text-amber-500" />
            Unassigned Orders & Applications
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Confirmed client sales orders awaiting allocation to Operations specialists.
          </p>
        </div>

        <button
          type="button"
          onClick={() => loadUnassigned()}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 shadow-xs transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-blue-600' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Company Selector Tabs */}
      <div className="flex items-center justify-between flex-wrap gap-3 p-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-2xl border border-slate-200/80 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            Company Scope:
          </span>
          <CompanyFilterTabs
            selectedCompanyId={companyId}
            onCompanyChange={(newCompId) => {
              setCompanyId(newCompId);
              setPage(1);
            }}
            size="sm"
          />
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col gap-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-3 items-center">
          {/* General Search */}
          <div className="relative lg:col-span-6">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
              placeholder="Search by app #, order #, service, phone..."
              className="w-full pl-10 pr-4 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 focus:bg-white dark:focus:bg-slate-900 focus:ring-2 focus:ring-blue-500 outline-hidden transition"
              aria-label="Search unassigned orders"
            />
          </div>

          {/* Dedicated Client Name Filter */}
          <div className="relative lg:col-span-4">
            <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={clientName}
              onChange={(e) => handleClientNameChange(e.target.value)}
              placeholder="Client Name (e.g. Varun)..."
              className="w-full pl-10 pr-4 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 focus:bg-white dark:focus:bg-slate-900 focus:ring-2 focus:ring-blue-500 outline-hidden transition"
              aria-label="Client Name"
            />
          </div>

          {/* Clear Filters Button */}
          <div className="lg:col-span-2 flex justify-end">
            <button
              type="button"
              onClick={handleClearFilters}
              disabled={!hasActiveFilters}
              className={`w-full inline-flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-xl border transition ${
                hasActiveFilters
                  ? 'border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 cursor-pointer'
                  : 'border-slate-100 dark:border-slate-800/50 bg-slate-50/50 dark:bg-slate-900/50 text-slate-400 dark:text-slate-600 cursor-not-allowed'
              }`}
              title="Clear all active filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
        {error && (
          <div className="p-8 text-center bg-red-50/40 dark:bg-red-950/20 border-b border-red-200 dark:border-red-900/40 space-y-3">
            <div className="inline-flex p-2.5 rounded-full bg-red-100 dark:bg-red-900/40 text-red-600 dark:text-red-400">
              <AlertCircle className="w-5 h-5" />
            </div>
            <p className="text-sm font-semibold text-red-700 dark:text-red-300">{error}</p>
            <div>
              <button
                type="button"
                onClick={() => loadUnassigned()}
                className="px-4 py-1.5 text-xs font-bold rounded-xl bg-red-600 hover:bg-red-700 text-white shadow-xs transition"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {loading && (
          <div className="py-20 flex flex-col items-center justify-center text-slate-400 space-y-2">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
            <p className="text-sm">Loading unassigned orders...</p>
          </div>
        )}

        {!loading && !error && taskListResponse && taskListResponse.items.length === 0 && (
          <div className="py-20 text-center text-slate-400 space-y-2">
            <CheckCircle2 className="w-10 h-10 mx-auto text-emerald-500" />
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              {hasActiveFilters ? 'No matching unassigned orders found' : 'All caught up!'}
            </p>
            <p className="text-xs text-slate-500">
              {hasActiveFilters
                ? 'No unassigned orders match your search criteria.'
                : 'There are no unassigned orders at this time.'}
            </p>
            {hasActiveFilters && (
              <button
                type="button"
                onClick={handleClearFilters}
                className="mt-3 px-3.5 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition"
              >
                Clear all filters
              </button>
            )}
          </div>
        )}

        {!loading && taskListResponse && taskListResponse.items.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 text-slate-500 dark:text-slate-400 uppercase text-[10px] font-bold">
                  <th className="py-3.5 px-4">Application #</th>
                  <th className="py-3.5 px-4">Order #</th>
                  <th className="py-3.5 px-4">Client Name</th>
                  <th className="py-3.5 px-4">Location</th>
                  <th className="py-3.5 px-4">Service</th>
                  <th className="py-3.5 px-4">Converted By</th>
                  <th className="py-3.5 px-4">Order Date</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
                {taskListResponse.items.map((task) => (
                  <tr key={task.application_id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-blue-600 dark:text-blue-400">
                      {task.application_number}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-500">{task.sales_order_number || '—'}</td>
                    <td className="py-3.5 px-4 font-bold text-slate-900 dark:text-white">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span>{task.client_name}</span>
                        <CompanyBadge
                          companyName={task.company_name}
                          companyCode={task.company_code}
                          size="xs"
                        />
                        {task.assignment_notes && task.assignment_notes.includes('Coordinator setup required') && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10.5px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-800" title="Company coordinator mapping missing or inactive">
                            <AlertCircle className="w-3 h-3 text-amber-600 dark:text-amber-400" />
                            Coordinator setup required
                          </span>
                        )}
                      </div>
                      {task.client_phone && (
                        <div className="text-[11px] font-normal text-slate-400">{task.client_phone}</div>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 dark:text-slate-300 whitespace-nowrap">
                      {task.location ? (
                        <span className="inline-flex items-center gap-1 font-medium text-slate-800 dark:text-slate-200">
                          <MapPin className="w-3.5 h-3.5 text-blue-500 shrink-0 inline" />
                          <span>{task.location}</span>
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-700 dark:text-slate-300">
                      {task.service_name}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {task.salesperson_name || '—'} ({task.salesperson_code || '—'})
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">{task.formatted_order_date || '—'}</td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          type="button"
                          onClick={() => {
                            setAssigningTask(task);
                            setSelectedAssigneeId('');
                            setAssignDueDate('');
                            setAssignNotes('');
                          }}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs transition"
                        >
                          <UserPlus className="w-3.5 h-3.5" />
                          <span>Assign Work</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedAppId(task.application_id);
                            setIsDetailModalOpen(true);
                          }}
                          className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition"
                          title="View Details"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {taskListResponse && taskListResponse.total_pages > 1 && (
          <div className="p-4 border-t border-slate-200/80 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
            <span>
              Page {taskListResponse.page} of {taskListResponse.total_pages} ({taskListResponse.total_count} orders)
            </span>
            <div className="flex gap-1">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                type="button"
                disabled={page >= taskListResponse.total_pages}
                onClick={() => setPage(page + 1)}
                className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 disabled:opacity-40"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Quick Assign Modal */}
      {assigningTask && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="relative w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-4 text-slate-800 dark:text-slate-100">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              Assign Application {assigningTask.application_number}
            </h2>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
              <div>
                <span className="text-slate-500">Client:</span>{' '}
                <span className="font-semibold text-slate-900 dark:text-white">{assigningTask.client_name}</span>
              </div>
              <div>
                <span className="text-slate-500">Service:</span>{' '}
                <span className="font-semibold text-blue-600 dark:text-blue-400">{assigningTask.service_name}</span>
              </div>
            </div>

            <form onSubmit={handleAssignSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Assign To Operations Employee <span className="text-red-500">*</span>
                </label>
                <select
                  value={selectedAssigneeId}
                  onChange={(e) => setSelectedAssigneeId(e.target.value)}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 outline-hidden focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">-- Select Assignee --</option>
                  {eligibleAssignees.map((emp) => (
                    <option key={emp.user_id} value={emp.user_id}>
                      {emp.full_name || emp.name} ({emp.employee_code}){emp.company_name ? ` - ${emp.company_name}` : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Priority</label>
                  <select
                    value={assignPriority}
                    onChange={(e) => setAssignPriority(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 outline-hidden"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Target Due Date <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={assignDueDate}
                    onChange={(e) => setAssignDueDate(e.target.value)}
                    required
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 outline-hidden"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Assignment Notes</label>
                <textarea
                  value={assignNotes}
                  onChange={(e) => setAssignNotes(e.target.value)}
                  rows={2}
                  placeholder="Special instructions or handover notes..."
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 outline-hidden"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setAssigningTask(null)}
                  className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingAssign}
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold shadow-md disabled:opacity-50"
                >
                  {isSubmittingAssign ? 'Assigning...' : 'Confirm Assignment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Task Details Modal */}
      <TaskDetailModal
        applicationId={selectedAppId}
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedAppId(null);
        }}
        onRefresh={loadUnassigned}
        onShowToast={context?.addToast}
      />
    </div>
  );
};

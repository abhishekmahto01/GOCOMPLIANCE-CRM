import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  UserCheck,
  Search,
  RefreshCw,
  Eye,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  ArrowRightLeft,
} from 'lucide-react';
import type {
  AssigneeOption,
  OperationApplication,
  OperationsTaskListResponse,
} from '../../types/operations';
import {
  getOperationsTasksApi,
  getOperationsAssigneesApi,
  reassignOperationTaskApi,
} from '../../api/operations';
import { TaskDetailModal } from '../../components/operations/TaskDetailModal';

export const TaskAssignmentPage: React.FC = () => {
  const context = useOutletContext<{
    addToast?: (type: 'success' | 'error' | 'info', title: string, message: string) => void;
  }>();

  const [taskListResponse, setTaskListResponse] = useState<OperationsTaskListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [assigneeFilter, setAssigneeFilter] = useState('ALL');
  const [page, setPage] = useState(1);
  const limit = 20;

  // Assignees
  const [eligibleAssignees, setEligibleAssignees] = useState<AssigneeOption[]>([]);

  // Quick Reassign Modal
  const [reassigningTask, setReassigningTask] = useState<OperationApplication | null>(null);
  const [newAssigneeId, setNewAssigneeId] = useState('');
  const [reassignReason, setReassignReason] = useState('');
  const [reassignPriority, setReassignPriority] = useState('MEDIUM');
  const [reassignDueDate, setReassignDueDate] = useState('');
  const [isSubmittingReassign, setIsSubmittingReassign] = useState(false);

  // Selected task detail modal
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getOperationsTasksApi({
        page,
        limit,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
        priority: priorityFilter !== 'ALL' ? priorityFilter : undefined,
        assigned_to_user_id: assigneeFilter !== 'ALL' ? assigneeFilter : undefined,
        search: search.trim() || undefined,
      });
      setTaskListResponse(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load task assignments.');
    } finally {
      setLoading(false);
    }
  };

  const loadAssignees = async () => {
    try {
      const data = await getOperationsAssigneesApi();
      setEligibleAssignees(data);
    } catch (err) {
      console.error('Failed to load assignees', err);
    }
  };

  useEffect(() => {
    loadTasks();
    loadAssignees();
  }, [page, statusFilter, priorityFilter, assigneeFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadTasks();
  };

  const handleReassignSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reassigningTask || !newAssigneeId || !reassignReason.trim()) return;
    if (reassigningTask.assigned_to_user_id && newAssigneeId === reassigningTask.assigned_to_user_id) {
      if (context?.addToast) {
        context.addToast('error', 'Invalid Assignee', 'Cannot reassign task to the current assignee.');
      }
      return;
    }
    try {
      setIsSubmittingReassign(true);
      await reassignOperationTaskApi(reassigningTask.application_id, {
        new_assignee_user_id: newAssigneeId,
        reason: reassignReason.trim(),
        priority: reassignPriority,
        target_due_date: reassignDueDate || undefined,
      });
      if (context?.addToast) {
        context.addToast('success', 'Task Reassigned', 'Task has been reassigned successfully.');
      }
      setReassigningTask(null);
      setNewAssigneeId('');
      setReassignReason('');
      loadTasks();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to reassign task.';
      if (context?.addToast) {
        context.addToast('error', 'Reassignment Failed', msg);
      }
    } finally {
      setIsSubmittingReassign(false);
    }
  };

  const getPriorityBadge = (p: string) => {
    switch (p?.toUpperCase()) {
      case 'URGENT':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-300">URGENT</span>;
      case 'HIGH':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">HIGH</span>;
      case 'LOW':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">LOW</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">MEDIUM</span>;
    }
  };

  const getStatusBadge = (s: string) => {
    switch (s?.toUpperCase()) {
      case 'APPROVED':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">Approved</span>;
      case 'IN_PROGRESS':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300">In Progress</span>;
      case 'PENDING_DOCUMENTS':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">Pending Docs</span>;
      case 'READY_FOR_SUBMISSION':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-cyan-100 text-cyan-700 dark:bg-cyan-950/60 dark:text-cyan-300">Ready to Submit</span>;
      case 'SUBMITTED':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300">Submitted</span>;
      case 'AUTHORITY_QUERY':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300">Authority Query</span>;
      case 'CANCELLED':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300">Cancelled</span>;
      case 'UNASSIGNED':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">Unassigned</span>;
      default:
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">Assigned</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
            <UserCheck className="w-6 h-6 text-blue-600" />
            All Operations Tasks & Work Assignment
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            View, assign, reassign, and monitor all compliance applications across the Operations team.
          </p>
        </div>

        <button
          type="button"
          onClick={loadTasks}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 shadow-xs transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-blue-600' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Metric Summary Strip */}
      {taskListResponse && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
            <span className="text-[11px] font-semibold text-slate-500">Total Tasks</span>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">
              {taskListResponse.summary.total_tasks}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-200/60 dark:border-blue-900/40 shadow-xs">
            <span className="text-[11px] font-semibold text-blue-600 dark:text-blue-400">Assigned</span>
            <p className="text-xl font-bold text-blue-700 dark:text-blue-300 mt-1">
              {taskListResponse.summary.assigned}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-200/60 dark:border-indigo-900/40 shadow-xs">
            <span className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400">In Progress</span>
            <p className="text-xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">
              {taskListResponse.summary.in_progress}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/40 shadow-xs">
            <span className="text-[11px] font-semibold text-amber-600 dark:text-amber-400">Pending Docs</span>
            <p className="text-xl font-bold text-amber-600 dark:text-amber-400 mt-1">
              {taskListResponse.summary.pending_docs}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-900/40 shadow-xs">
            <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">Completed</span>
            <p className="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
              {taskListResponse.summary.completed}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-red-50/50 dark:bg-red-950/20 border border-red-200/60 dark:border-red-900/40 shadow-xs">
            <span className="text-[11px] font-semibold text-red-600 dark:text-red-400">Overdue</span>
            <p className="text-xl font-bold text-red-600 dark:text-red-400 mt-1">
              {taskListResponse.summary.overdue}
            </p>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by client, service, application #, order #..."
            className="w-full pl-10 pr-4 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 focus:bg-white dark:focus:bg-slate-900 focus:ring-2 focus:ring-blue-500 outline-hidden transition"
          />
        </form>

        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Assignee Filter */}
          <select
            value={assigneeFilter}
            onChange={(e) => {
              setAssigneeFilter(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 text-xs font-semibold rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 outline-hidden"
          >
            <option value="ALL">All Assignees</option>
            {eligibleAssignees.map((emp) => (
              <option key={emp.user_id} value={emp.user_id}>
                {emp.full_name || emp.name} ({emp.employee_code})
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 text-xs font-semibold rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 outline-hidden"
          >
            <option value="ALL">All Statuses</option>
            <option value="ASSIGNED">Assigned</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="PENDING_DOCUMENTS">Pending Documents</option>
            <option value="READY_FOR_SUBMISSION">Ready for Submission</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="AUTHORITY_QUERY">Authority Query</option>
            <option value="APPROVED">Approved</option>
            <option value="OVERDUE">Overdue</option>
          </select>

          {/* Priority Filter */}
          <select
            value={priorityFilter}
            onChange={(e) => {
              setPriorityFilter(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 text-xs font-semibold rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 outline-hidden"
          >
            <option value="ALL">All Priorities</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="URGENT">Urgent</option>
          </select>
        </div>
      </div>

      {/* Task Assignment Table */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
        {error && (
          <div className="p-6 text-center text-red-600 dark:text-red-400 text-sm flex items-center justify-center gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}

        {loading && (
          <div className="py-20 flex flex-col items-center justify-center text-slate-400 space-y-2">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
            <p className="text-sm">Loading task allocations...</p>
          </div>
        )}

        {!loading && taskListResponse && taskListResponse.items.length === 0 && (
          <div className="py-20 text-center text-slate-400 space-y-2">
            <UserCheck className="w-10 h-10 mx-auto text-slate-300 dark:text-slate-700" />
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">No applications found</p>
            <p className="text-xs text-slate-500">No tasks match your current filter selection.</p>
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
                  <th className="py-3.5 px-4">Service</th>
                  <th className="py-3.5 px-4">Current Assignee</th>
                  <th className="py-3.5 px-4">Converted By</th>
                  <th className="py-3.5 px-4">Due Date</th>
                  <th className="py-3.5 px-4">Priority</th>
                  <th className="py-3.5 px-4">Status</th>
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
                      {task.client_name}
                      {task.client_phone && (
                        <div className="text-[11px] font-normal text-slate-400">{task.client_phone}</div>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-700 dark:text-slate-300">
                      {task.service_name}
                    </td>
                    <td className="py-3.5 px-4">
                      {task.assigned_to_name ? (
                        <div className="font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-blue-500" />
                          <span>{task.assigned_to_name}</span>
                          <span className="text-[11px] text-slate-400 font-mono">({task.assigned_to_code})</span>
                        </div>
                      ) : (
                        <span className="text-amber-500 font-semibold">Unassigned</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">{task.salesperson_name || '—'}</td>
                    <td className="py-3.5 px-4">
                      <span className={task.is_overdue ? 'text-red-600 font-bold' : 'text-slate-600 dark:text-slate-400'}>
                        {task.formatted_due_date || 'No Date'}
                        {task.is_overdue && ' ⚠️'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">{getPriorityBadge(task.priority)}</td>
                    <td className="py-3.5 px-4">{getStatusBadge(task.application_status)}</td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => {
                            setReassigningTask(task);
                            setNewAssigneeId('');
                            setReassignReason('');
                            setReassignPriority(task.priority || 'MEDIUM');
                            setReassignDueDate(task.target_due_date || '');
                          }}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 dark:bg-blue-950 dark:text-blue-300 text-xs font-bold transition"
                          title="Reassign Task"
                        >
                          <ArrowRightLeft className="w-3.5 h-3.5" />
                          <span>Reassign</span>
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
              Page {taskListResponse.page} of {taskListResponse.total_pages} ({taskListResponse.total_count} tasks)
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

      {/* Quick Reassign Modal */}
      {reassigningTask && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="relative w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-4 text-slate-800 dark:text-slate-100">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              Reassign Application {reassigningTask.application_number}
            </h2>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
              <div>
                <span className="text-slate-500">Client:</span>{' '}
                <span className="font-semibold text-slate-900 dark:text-white">{reassigningTask.client_name}</span>
              </div>
              <div>
                <span className="text-slate-500">Service:</span>{' '}
                <span className="font-semibold text-blue-600 dark:text-blue-400">{reassigningTask.service_name}</span>
              </div>
              <div>
                <span className="text-slate-500">Current Assignee:</span>{' '}
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {reassigningTask.assigned_to_name || 'Unassigned'}
                </span>
              </div>
            </div>

            <form onSubmit={handleReassignSubmit} className="space-y-4 text-xs">
              <div>
                <label htmlFor="reassign-assignee-select" className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                  New Operations Assignee <span className="text-red-500">*</span>
                </label>
                <select
                  id="reassign-assignee-select"
                  value={newAssigneeId}
                  onChange={(e) => setNewAssigneeId(e.target.value)}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 outline-hidden focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">-- Select New Assignee --</option>
                  {eligibleAssignees
                    .filter((emp) => emp.user_id !== reassigningTask?.assigned_to_user_id)
                    .map((emp) => (
                      <option key={emp.user_id} value={emp.user_id}>
                        {emp.full_name || emp.name} ({emp.employee_code})
                      </option>
                    ))}
                </select>
              </div>

              <div>
                <label htmlFor="reassign-reason-textarea" className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Mandatory Reassignment Reason <span className="text-red-500">*</span>
                </label>
                <textarea
                  id="reassign-reason-textarea"
                  value={reassignReason}
                  onChange={(e) => setReassignReason(e.target.value)}
                  required
                  rows={2}
                  placeholder="e.g. Employee on leave, workload balancing, specialist required..."
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 outline-hidden"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="reassign-priority-select" className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Priority</label>
                  <select
                    id="reassign-priority-select"
                    value={reassignPriority}
                    onChange={(e) => setReassignPriority(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 outline-hidden"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="reassign-due-date-input" className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Target Due Date</label>
                  <input
                    id="reassign-due-date-input"
                    type="date"
                    value={reassignDueDate}
                    onChange={(e) => setReassignDueDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 outline-hidden"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setReassigningTask(null)}
                  className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingReassign}
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold shadow-md disabled:opacity-50"
                >
                  {isSubmittingReassign ? 'Reassigning...' : 'Confirm Reassignment'}
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
        onRefresh={loadTasks}
        onShowToast={context?.addToast}
      />
    </div>
  );
};

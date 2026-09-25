import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  CheckSquare,
  Search,
  RefreshCw,
  Eye,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import type { OperationsTaskListResponse } from '../../types/operations';
import { getMyOperationsTasksApi } from '../../api/operations';
import { TaskDetailModal } from '../../components/operations/TaskDetailModal';

export const MyTasksPage: React.FC = () => {
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
  const [page, setPage] = useState(1);
  const limit = 20;

  // Selected task modal state
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await getMyOperationsTasksApi({
        page,
        limit,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
        priority: priorityFilter !== 'ALL' ? priorityFilter : undefined,
        search: search.trim() || undefined,
      });

      setTaskListResponse(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load your assigned tasks.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [page, statusFilter, priorityFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadTasks();
  };

  const openTaskDetail = (appId: string) => {
    setSelectedAppId(appId);
    setIsDetailModalOpen(true);
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
            <CheckSquare className="w-6 h-6 text-blue-600" />
            My Assigned Tasks
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Track and manage compliance applications currently assigned to you.
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
            <span className="text-[11px] font-semibold text-slate-500">Total Assigned</span>
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

      {/* Task List Table */}
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
            <p className="text-sm">Loading your tasks...</p>
          </div>
        )}

        {!loading && taskListResponse && taskListResponse.items.length === 0 && (
          <div className="py-20 text-center text-slate-400 space-y-2">
            <CheckSquare className="w-10 h-10 mx-auto text-slate-300 dark:text-slate-700" />
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">No tasks found</p>
            <p className="text-xs text-slate-500">You currently have no tasks assigned matching the selected filters.</p>
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
                  <th className="py-3.5 px-4">Converted By</th>
                  <th className="py-3.5 px-4">Assigned Date</th>
                  <th className="py-3.5 px-4">Target Due</th>
                  <th className="py-3.5 px-4">Priority</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
                {taskListResponse.items.map((task) => (
                  <tr
                    key={task.application_id}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition cursor-pointer"
                    onClick={() => openTaskDetail(task.application_id)}
                  >
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
                    <td className="py-3.5 px-4 text-slate-500">
                      {task.salesperson_name || '—'}
                      {task.salesperson_code && (
                        <span className="text-[11px] text-slate-400"> ({task.salesperson_code})</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">{task.formatted_assigned_at || '—'}</td>
                    <td className="py-3.5 px-4">
                      <span className={task.is_overdue ? 'text-red-600 font-bold' : 'text-slate-600 dark:text-slate-400'}>
                        {task.formatted_due_date || 'No Date'}
                        {task.is_overdue && ' ⚠️'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">{getPriorityBadge(task.priority)}</td>
                    <td className="py-3.5 px-4">{getStatusBadge(task.application_status)}</td>
                    <td className="py-3.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <button
                        type="button"
                        onClick={() => openTaskDetail(task.application_id)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 dark:bg-blue-950 dark:text-blue-300 text-xs font-bold transition"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Open Task</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {taskListResponse && taskListResponse.total_pages > 1 && (
          <div className="p-4 border-t border-slate-200/80 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
            <span>
              Showing Page {taskListResponse.page} of {taskListResponse.total_pages} ({taskListResponse.total_count} tasks)
            </span>
            <div className="flex gap-1">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                type="button"
                disabled={page >= taskListResponse.total_pages}
                onClick={() => setPage(page + 1)}
                className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

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

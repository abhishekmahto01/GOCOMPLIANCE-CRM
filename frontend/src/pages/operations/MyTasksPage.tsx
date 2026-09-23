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
import type { OperationsTaskListResponse, AssigneeOption } from '../../types/operations';
import { getMyOperationsTasksApi, getOperationsAssigneesApi } from '../../api/operations';
import { TaskDetailModal } from '../../components/operations/TaskDetailModal';
import { useAuth } from '../../context/AuthContext';

export const MyTasksPage: React.FC = () => {
  const context = useOutletContext<{
    addToast?: (type: 'success' | 'error' | 'info', title: string, message: string) => void;
  }>();

  const { user } = useAuth();

  const [taskListResponse, setTaskListResponse] = useState<OperationsTaskListResponse | null>(null);
  const [eligibleAssignees, setEligibleAssignees] = useState<AssigneeOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [assigneeFilter, setAssigneeFilter] = useState('ALL'); // 'ALL' | 'SELF' | 'REASSIGNED' | userId
  const [page, setPage] = useState(1);
  const limit = 20;

  // Selected task modal state
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const loadAssignees = async () => {
    try {
      const data = await getOperationsAssigneesApi();
      setEligibleAssignees(data);
    } catch (err) {
      console.error('Failed to load assignees', err);
    }
  };

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);

      // Determine assigned_to_user_id query param based on filter
      let assignedToParam: string | undefined = undefined;
      if (assigneeFilter === 'SELF' && user?.user_id) {
        assignedToParam = user.user_id;
      } else if (assigneeFilter !== 'ALL' && assigneeFilter !== 'REASSIGNED') {
        assignedToParam = assigneeFilter;
      }

      const data = await getMyOperationsTasksApi({
        page,
        limit,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
        priority: priorityFilter !== 'ALL' ? priorityFilter : undefined,
        search: search.trim() || undefined,
        assigned_to_user_id: assignedToParam,
      });

      // If user selected 'REASSIGNED' (tasks assigned to someone other than self)
      if (assigneeFilter === 'REASSIGNED' && user?.user_id) {
        const filteredItems = data.items.filter(
          (t) => t.assigned_to_user_id && t.assigned_to_user_id !== user.user_id
        );
        setTaskListResponse({
          ...data,
          items: filteredItems,
          total_count: filteredItems.length,
        });
      } else {
        setTaskListResponse(data);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load your assigned tasks.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssignees();
  }, []);

  useEffect(() => {
    loadTasks();
  }, [page, statusFilter, priorityFilter, assigneeFilter]);

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

  // Count self vs reassigned in current items
  const selfCount = (taskListResponse?.items || []).filter(
    (t) => t.assigned_to_user_id === user?.user_id
  ).length;
  const reassignedCount = (taskListResponse?.items || []).filter(
    (t) => t.assigned_to_user_id && t.assigned_to_user_id !== user?.user_id
  ).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
            <CheckSquare className="w-6 h-6 text-blue-600" />
            Operations Task Manager & Workspace
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Track all tasks assigned to you, statutory filings, and tasks delegated or reassigned across the operations team.
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
            <span className="text-[11px] font-semibold text-slate-500">Total Workspace Tasks</span>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">
              {taskListResponse.summary.total_tasks}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-200/60 dark:border-blue-900/40 shadow-xs">
            <span className="text-[11px] font-semibold text-blue-600 dark:text-blue-400">Direct / Self Handled</span>
            <p className="text-xl font-bold text-blue-700 dark:text-blue-300 mt-1">
              {selfCount}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-rose-50/60 dark:bg-rose-950/25 border border-rose-200/60 dark:border-rose-900/40 shadow-xs">
            <span className="text-[11px] font-semibold text-rose-700 dark:text-rose-400">Reassigned to Team</span>
            <p className="text-xl font-bold text-rose-800 dark:text-rose-300 mt-1">
              {reassignedCount}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
            <span className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400">In Progress</span>
            <p className="text-xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">
              {taskListResponse.summary.in_progress}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
            <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">Completed</span>
            <p className="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
              {taskListResponse.summary.completed}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
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
            placeholder="Search by client, service, application #, order #, or assignee..."
            className="w-full pl-10 pr-4 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 focus:bg-white dark:focus:bg-slate-900 focus:ring-2 focus:ring-blue-500 outline-hidden transition"
          />
        </form>

        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Assignment / Delegation Filter */}
          <select
            value={assigneeFilter}
            onChange={(e) => {
              setAssigneeFilter(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 text-xs font-semibold rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 outline-hidden"
          >
            <option value="ALL">All Allocations (Self & Reassigned)</option>
            <option value="SELF">Direct Assigned (Self Only)</option>
            <option value="REASSIGNED">Reassigned to Team Members</option>
            {eligibleAssignees
              .filter((emp) => emp.user_id !== user?.user_id)
              .map((emp) => (
                <option key={emp.user_id} value={emp.user_id}>
                  Reassigned: {emp.full_name || emp.name} ({emp.employee_code})
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

      {/* Visual Indicator Legend */}
      <div className="flex flex-wrap items-center gap-4 px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400">
        <span className="font-semibold text-slate-700 dark:text-slate-300">Task Allocation Legend:</span>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-blue-500" />
          <span>Direct / Self Handled Tasks</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-rose-500" />
          <span className="font-medium text-rose-800 dark:text-rose-300">Reassigned / Delegated to Operations Executive (Light Beetroot Tint)</span>
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
            <p className="text-sm">Loading tasks...</p>
          </div>
        )}

        {!loading && taskListResponse && taskListResponse.items.length === 0 && (
          <div className="py-20 text-center text-slate-400 space-y-2">
            <CheckSquare className="w-10 h-10 mx-auto text-slate-300 dark:text-slate-700" />
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">No tasks found</p>
            <p className="text-xs text-slate-500">You currently have no tasks matching the selected filters.</p>
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
                  <th className="py-3.5 px-4 min-w-[200px]">Assigned / Reassigned To</th>
                  <th className="py-3.5 px-4">Assigned Date</th>
                  <th className="py-3.5 px-4">Target Due</th>
                  <th className="py-3.5 px-4">Priority</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
                {taskListResponse.items.map((task) => {
                  const isSelfAssigned = Boolean(
                    task.assigned_to_user_id && user?.user_id && task.assigned_to_user_id === user.user_id
                  );
                  const isReassigned = Boolean(
                    task.assigned_to_user_id && user?.user_id && task.assigned_to_user_id !== user.user_id
                  );

                  return (
                    <tr
                      key={task.application_id}
                      className={`transition cursor-pointer ${
                        isReassigned
                          ? 'bg-rose-50/80 dark:bg-rose-950/30 hover:bg-rose-100/80 dark:hover:bg-rose-900/40 border-l-4 border-l-rose-500'
                          : 'bg-white dark:bg-slate-900 hover:bg-slate-50/80 dark:hover:bg-slate-800/50 border-l-4 border-l-transparent'
                      }`}
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
                      <td className="py-3.5 px-4">
                        {isSelfAssigned ? (
                          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-blue-50 text-blue-700 dark:bg-blue-950/70 dark:text-blue-300 border border-blue-200/70 dark:border-blue-800/60">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-600 dark:bg-blue-400" />
                            <span>Self</span>
                            <span className="text-[11px] text-blue-500 dark:text-blue-400 font-mono">
                              ({task.assigned_to_code || user?.employee_code})
                            </span>
                          </div>
                        ) : isReassigned ? (
                          <div className="flex flex-col gap-0.5">
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold bg-rose-100 text-rose-900 dark:bg-rose-950/80 dark:text-rose-200 border border-rose-200/80 dark:border-rose-800/80 shadow-2xs">
                              <span className="w-1.5 h-1.5 rounded-full bg-rose-600 dark:bg-rose-400 animate-pulse" />
                              <span>Reassigned: {task.assigned_to_name}</span>
                              <span className="text-[11px] text-rose-700 dark:text-rose-300 font-mono font-normal">
                                ({task.assigned_to_code})
                              </span>
                            </span>
                            {task.assigned_by_name && (
                              <span className="text-[10px] text-slate-500 dark:text-slate-400 pl-1">
                                Delegated by {task.assigned_by_name}
                              </span>
                            )}
                          </div>
                        ) : task.assigned_to_name ? (
                          <div className="font-semibold text-slate-800 dark:text-slate-200">
                            {task.assigned_to_name} ({task.assigned_to_code})
                          </div>
                        ) : (
                          <span className="text-amber-500 font-semibold text-xs">Unassigned</span>
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
                  );
                })}
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

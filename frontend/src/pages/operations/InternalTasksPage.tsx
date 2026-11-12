import React, { useCallback, useEffect, useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  ClipboardCheck,
  Clock,
  FlaskConical,
  MessageSquare,
  PlayCircle,
  Plus,
  RefreshCw,
  Search,
  UserCog,
  X,
} from 'lucide-react';
import {
  createInternalTaskApi,
  getInternalTaskAssigneesApi,
  getInternalTasksApi,
  reassignInternalTaskApi,
} from '../../api/internalTasks';
import { extractErrorMessage } from '../../api/client';
import { useDebounce } from '../../hooks/useDebounce';
import { InternalTaskChatModal } from '../../components/internalTasks/InternalTaskChatModal';
import {
  INTERNAL_PRIORITY_LABEL,
  INTERNAL_STATUS_META,
  INTERNAL_TYPE_LABEL,
  formatInternalDate,
} from '../../components/internalTasks/internalTaskMeta';
import type {
  InternalTask,
  InternalTaskListResponse,
  InternalTaskPriority,
  InternalTaskStatus,
  InternalTaskType,
  InternalTaskUserRef,
} from '../../types/internalTask';

const inputCls =
  'w-full px-3 py-2 rounded-xl text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition';

interface CardProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  tone: string;
  active: boolean;
  onClick: () => void;
}

const SummaryCard: React.FC<CardProps> = ({ label, value, icon, tone, active, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    aria-pressed={active}
    className={`flex items-center gap-4 p-4 rounded-2xl border text-left transition shadow-xs hover:shadow-md ${tone} ${
      active ? 'ring-2 ring-blue-500/60' : ''
    }`}
  >
    <span className="w-12 h-12 rounded-full bg-white/70 dark:bg-slate-900/60 flex items-center justify-center shrink-0">{icon}</span>
    <span>
      <span className="block text-sm font-semibold text-slate-600 dark:text-slate-300">{label}</span>
      <span className="block text-2xl font-bold text-slate-900 dark:text-white">{value}</span>
    </span>
  </button>
);

const emptyForm = {
  title: '',
  description: '',
  task_type: 'RESEARCH' as InternalTaskType,
  priority: 'MEDIUM' as InternalTaskPriority,
  assigned_to_user_id: '',
  due_date: '',
};

export const InternalTasksPage: React.FC = () => {
  const [data, setData] = useState<InternalTaskListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] = useState<InternalTaskStatus | ''>('');
  const [typeFilter, setTypeFilter] = useState<InternalTaskType | ''>('');
  const [mineOnly, setMineOnly] = useState(false);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 350);

  const [chatTaskId, setChatTaskId] = useState<string | null>(null);

  const [assignees, setAssignees] = useState<InternalTaskUserRef[]>([]);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const [reassignTask, setReassignTask] = useState<InternalTask | null>(null);
  const [reassignTo, setReassignTo] = useState('');
  const [reassignReason, setReassignReason] = useState('');

  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(
        await getInternalTasksApi({ status: statusFilter, task_type: typeFilter, search: debouncedSearch, mine: mineOnly })
      );
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [statusFilter, typeFilter, debouncedSearch, mineOnly]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const canAssign = Boolean(data?.capabilities.can_create || data?.capabilities.can_assign);

  const ensureAssignees = async () => {
    if (assignees.length > 0) return;
    try {
      setAssignees(await getInternalTaskAssigneesApi());
    } catch (err) {
      setFormError(extractErrorMessage(err));
    }
  };

  const openCreate = async () => {
    setForm(emptyForm);
    setFormError(null);
    setIsCreateOpen(true);
    await ensureAssignees();
  };

  const submitCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) return setFormError('Please enter a task title.');
    if (!form.assigned_to_user_id) return setFormError('Please select an employee to assign.');
    setSaving(true);
    setFormError(null);
    try {
      await createInternalTaskApi({
        title: form.title.trim(),
        description: form.description.trim() || null,
        task_type: form.task_type,
        priority: form.priority,
        assigned_to_user_id: form.assigned_to_user_id,
        due_date: form.due_date || null,
      });
      setIsCreateOpen(false);
      await loadTasks();
    } catch (err) {
      setFormError(extractErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const openReassign = async (task: InternalTask) => {
    setReassignTask(task);
    setReassignTo('');
    setReassignReason('');
    setFormError(null);
    await ensureAssignees();
  };

  const submitReassign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reassignTask || !reassignTo) return setFormError('Please select an employee.');
    setSaving(true);
    setFormError(null);
    try {
      await reassignInternalTaskApi(reassignTask.task_id, reassignTo, reassignReason.trim() || undefined);
      setReassignTask(null);
      await loadTasks();
    } catch (err) {
      setFormError(extractErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const toggleStatus = (s: InternalTaskStatus | '') => setStatusFilter((cur) => (cur === s ? '' : s));
  const summary = data?.summary;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
            <FlaskConical className="w-6 h-6 text-blue-600" />
            R&amp;D / Internal Tasks
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Research, vendor and other internal work — not linked to sales orders.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => loadTasks()}
            disabled={loading}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 shadow-xs transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-blue-600' : ''}`} />
            <span>Refresh</span>
          </button>
          {canAssign && (
            <button
              type="button"
              onClick={openCreate}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-blue-700 hover:bg-blue-800 text-white shadow-md transition"
            >
              <Plus className="w-4 h-4" />
              Assign Task
            </button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          label="Total Tasks"
          value={summary?.total ?? 0}
          icon={<ClipboardCheck className="w-6 h-6 text-blue-600" />}
          tone="bg-blue-50/70 border-blue-100 dark:bg-blue-950/20 dark:border-blue-900/40"
          active={statusFilter === ''}
          onClick={() => setStatusFilter('')}
        />
        <SummaryCard
          label="In Progress"
          value={summary?.in_progress ?? 0}
          icon={<PlayCircle className="w-6 h-6 text-emerald-600" />}
          tone="bg-emerald-50/70 border-emerald-100 dark:bg-emerald-950/20 dark:border-emerald-900/40"
          active={statusFilter === 'IN_PROGRESS'}
          onClick={() => toggleStatus('IN_PROGRESS')}
        />
        <SummaryCard
          label="Pending"
          value={summary?.pending ?? 0}
          icon={<Clock className="w-6 h-6 text-amber-600" />}
          tone="bg-amber-50/70 border-amber-100 dark:bg-amber-950/20 dark:border-amber-900/40"
          active={statusFilter === 'PENDING'}
          onClick={() => toggleStatus('PENDING')}
        />
        <SummaryCard
          label="Completed"
          value={summary?.completed ?? 0}
          icon={<CheckCircle2 className="w-6 h-6 text-indigo-600" />}
          tone="bg-indigo-50/70 border-indigo-100 dark:bg-indigo-950/20 dark:border-indigo-900/40"
          active={statusFilter === 'COMPLETED'}
          onClick={() => toggleStatus('COMPLETED')}
        />
      </div>

      {/* Tasks Table */}
      <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs">
        <div className="p-4 sm:p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Assigned Tasks</h2>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search task or ID..."
                aria-label="Search tasks"
                className="pl-9 pr-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 outline-none focus:border-blue-500 w-48"
              />
            </div>
            <select
              aria-label="Filter by type"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as InternalTaskType | '')}
              className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 outline-none"
            >
              <option value="">All Types</option>
              <option value="RESEARCH">Research</option>
              <option value="VENDOR">Vendor</option>
              <option value="OTHER">Other</option>
            </select>
            <select
              aria-label="Filter by status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as InternalTaskStatus | '')}
              className="px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 outline-none"
            >
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
            {data?.capabilities.is_manager && (
              <label className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 px-2">
                <input type="checkbox" checked={mineOnly} onChange={(e) => setMineOnly(e.target.checked)} />
                Only my tasks
              </label>
            )}
          </div>
        </div>

        {error && (
          <div className="m-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2" role="alert">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/60 text-left text-slate-700 dark:text-slate-300">
                <th className="px-4 py-3 font-semibold">Task ID</th>
                <th className="px-4 py-3 font-semibold">Task / Project</th>
                <th className="px-4 py-3 font-semibold">Type</th>
                <th className="px-4 py-3 font-semibold">Assigned To</th>
                <th className="px-4 py-3 font-semibold">Due Date</th>
                <th className="px-4 py-3 font-semibold">Status</th>
                <th className="px-4 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {!loading && data && data.items.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-sm text-slate-500">
                    No tasks found.
                  </td>
                </tr>
              )}
              {data?.items.map((t) => {
                const meta = INTERNAL_STATUS_META[t.status];
                return (
                  <tr key={t.task_id} className="border-t border-slate-100 dark:border-slate-800 hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                    <td className="px-4 py-3 font-mono text-xs font-semibold text-slate-700 dark:text-slate-300">{t.task_number}</td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-900 dark:text-white">{t.title}</div>
                      <div className="text-[11px] text-slate-400">
                        {INTERNAL_PRIORITY_LABEL[t.priority]} priority
                        {t.created_by ? ` • by ${t.created_by.name}` : ''}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-600 dark:text-slate-300">{INTERNAL_TYPE_LABEL[t.task_type]}</td>
                    <td className="px-4 py-3">
                      <div className="text-slate-800 dark:text-slate-200">{t.assigned_to?.name || 'Unassigned'}</div>
                      {t.assigned_to?.department_name && (
                        <div className="text-[11px] text-slate-400">{t.assigned_to.department_name}</div>
                      )}
                    </td>
                    <td className={`px-4 py-3 text-xs ${t.is_overdue ? 'text-rose-600 font-semibold' : 'text-slate-600 dark:text-slate-300'}`}>
                      {formatInternalDate(t.due_date)}
                      {t.is_overdue && <span className="block text-[10px]">Overdue</span>}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-block px-3 py-1 rounded-lg text-xs font-semibold border ${meta.badge}`}>{meta.label}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          type="button"
                          onClick={() => setChatTaskId(t.task_id)}
                          aria-label={`Open chat for ${t.task_number}`}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/40 dark:text-blue-300 transition"
                        >
                          <MessageSquare className="w-3.5 h-3.5" />
                          {t.message_count > 0 ? t.message_count : 'Chat'}
                        </button>
                        {t.can_reassign && (
                          <button
                            type="button"
                            onClick={() => openReassign(t)}
                            aria-label={`Reassign ${t.task_number}`}
                            title="Reassign"
                            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                          >
                            <UserCog className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Assign Task Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm" onClick={() => setIsCreateOpen(false)}>
          <form
            onSubmit={submitCreate}
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="assign-task-title"
            className="w-full max-w-lg bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-4"
          >
            <div className="flex items-center justify-between">
              <h3 id="assign-task-title" className="text-lg font-bold text-slate-900 dark:text-white">Assign Task</h3>
              <button type="button" onClick={() => setIsCreateOpen(false)} aria-label="Close" className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
                <X className="w-5 h-5" />
              </button>
            </div>

            <label className="block space-y-1">
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">Task title *</span>
              <input
                className={inputCls}
                value={form.title}
                maxLength={200}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                placeholder="e.g. Market Research – Fitness Industry"
              />
            </label>

            <label className="block space-y-1">
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">Details (optional — shown as the first chat message)</span>
              <textarea
                className={inputCls}
                rows={3}
                value={form.description}
                maxLength={5000}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </label>

            <div className="grid grid-cols-2 gap-3">
              <label className="block space-y-1">
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">Type</span>
                <select className={inputCls} value={form.task_type} onChange={(e) => setForm({ ...form, task_type: e.target.value as InternalTaskType })}>
                  <option value="RESEARCH">Research</option>
                  <option value="VENDOR">Vendor</option>
                  <option value="OTHER">Other</option>
                </select>
              </label>
              <label className="block space-y-1">
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">Priority</span>
                <select className={inputCls} value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value as InternalTaskPriority })}>
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="URGENT">Urgent</option>
                </select>
              </label>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <label className="block space-y-1">
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">Assign to *</span>
                <select className={inputCls} value={form.assigned_to_user_id} onChange={(e) => setForm({ ...form, assigned_to_user_id: e.target.value })}>
                  <option value="">Select employee</option>
                  {assignees.map((u) => (
                    <option key={u.user_id} value={u.user_id}>
                      {u.name} ({u.employee_code}){u.department_name ? ` – ${u.department_name}` : ''}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block space-y-1">
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">Due date</span>
                <input type="date" className={inputCls} value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
              </label>
            </div>

            {formError && (
              <div role="alert" className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                {formError}
              </div>
            )}

            <div className="flex justify-end gap-2 pt-1">
              <button type="button" onClick={() => setIsCreateOpen(false)} className="px-4 py-2 rounded-xl text-sm font-semibold border border-slate-200 dark:border-slate-700">
                Cancel
              </button>
              <button type="submit" disabled={saving} className="px-4 py-2 rounded-xl text-sm font-semibold bg-blue-700 hover:bg-blue-800 text-white disabled:opacity-50">
                {saving ? 'Assigning...' : 'Assign Task'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Reassign Modal */}
      {reassignTask && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm" onClick={() => setReassignTask(null)}>
          <form
            onSubmit={submitReassign}
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="reassign-task-title"
            className="w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-4"
          >
            <h3 id="reassign-task-title" className="text-lg font-bold text-slate-900 dark:text-white">
              Reassign {reassignTask.task_number}
            </h3>
            <label className="block space-y-1">
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">New assignee *</span>
              <select className={inputCls} value={reassignTo} onChange={(e) => setReassignTo(e.target.value)}>
                <option value="">Select employee</option>
                {assignees
                  .filter((u) => u.user_id !== reassignTask.assigned_to?.user_id)
                  .map((u) => (
                    <option key={u.user_id} value={u.user_id}>
                      {u.name} ({u.employee_code}){u.department_name ? ` – ${u.department_name}` : ''}
                    </option>
                  ))}
              </select>
            </label>
            <label className="block space-y-1">
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">Reason (optional)</span>
              <input className={inputCls} value={reassignReason} maxLength={1000} onChange={(e) => setReassignReason(e.target.value)} />
            </label>
            {formError && (
              <div role="alert" className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
                {formError}
              </div>
            )}
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setReassignTask(null)} className="px-4 py-2 rounded-xl text-sm font-semibold border border-slate-200 dark:border-slate-700">
                Cancel
              </button>
              <button type="submit" disabled={saving} className="px-4 py-2 rounded-xl text-sm font-semibold bg-blue-700 hover:bg-blue-800 text-white disabled:opacity-50">
                {saving ? 'Saving...' : 'Reassign'}
              </button>
            </div>
          </form>
        </div>
      )}

      <InternalTaskChatModal
        isOpen={Boolean(chatTaskId)}
        taskId={chatTaskId}
        onClose={() => setChatTaskId(null)}
        onChanged={loadTasks}
      />
    </div>
  );
};

export default InternalTasksPage;

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { AlertCircle, CalendarDays, MessageSquare, RotateCcw, Send, Sparkles, User, X } from 'lucide-react';
import {
  getInternalTaskThreadApi,
  postInternalTaskMessageApi,
  updateInternalTaskStatusApi,
} from '../../api/internalTasks';
import { extractErrorMessage } from '../../api/client';
import type { InternalTaskStatus, InternalTaskThread } from '../../types/internalTask';
import { INTERNAL_STATUS_META, INTERNAL_TYPE_LABEL, formatInternalDate } from './internalTaskMeta';

export interface InternalTaskChatModalProps {
  isOpen: boolean;
  taskId: string | null;
  onClose: () => void;
  /** Called after a message is posted or status changes so the list can refresh. */
  onChanged?: () => void;
}

function formatDateGroupHeader(dateStr: string): string {
  const d = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (d.toDateString() === today.toDateString()) return 'Today';
  if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

function getInitials(name?: string | null): string {
  if (!name) return 'SY';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

const STATUS_OPTIONS: InternalTaskStatus[] = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'];

export const InternalTaskChatModal: React.FC<InternalTaskChatModalProps> = ({ isOpen, taskId, onClose, onChanged }) => {
  const [thread, setThread] = useState<InternalTaskThread | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draft, setDraft] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  const fetchThread = useCallback(
    async (silent = false) => {
      if (!taskId) return;
      if (!silent) setIsLoading(true);
      setError(null);
      try {
        setThread(await getInternalTaskThreadApi(taskId));
      } catch (err) {
        setError(extractErrorMessage(err));
      } finally {
        if (!silent) setIsLoading(false);
      }
    },
    [taskId]
  );

  useEffect(() => {
    if (isOpen && taskId) {
      setThread(null);
      setDraft('');
      setSendError(null);
      fetchThread(false);
    }
  }, [isOpen, taskId, fetchThread]);

  useEffect(() => {
    endRef.current?.scrollIntoView?.({ behavior: 'smooth' });
  }, [thread?.messages.length]);

  if (!isOpen || !taskId) return null;

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const text = draft.trim();
    if (!text || isSending) return;
    setIsSending(true);
    setSendError(null);
    try {
      await postInternalTaskMessageApi(taskId, text);
      setDraft('');
      await fetchThread(true);
      onChanged?.();
    } catch (err) {
      setSendError(extractErrorMessage(err));
    } finally {
      setIsSending(false);
    }
  };

  const handleStatusChange = async (status: InternalTaskStatus) => {
    if (!thread || status === thread.task.status) return;
    setIsUpdatingStatus(true);
    setSendError(null);
    try {
      await updateInternalTaskStatusApi(taskId, status);
      await fetchThread(true);
      onChanged?.();
    } catch (err) {
      setSendError(extractErrorMessage(err));
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const groups: { header: string; items: InternalTaskThread['messages'] }[] = [];
  for (const m of thread?.messages ?? []) {
    const header = formatDateGroupHeader(m.created_at);
    const last = groups[groups.length - 1];
    if (last && last.header === header) last.items.push(m);
    else groups.push({ header, items: [m] });
  }

  const task = thread?.task;
  const statusMeta = task ? INTERNAL_STATUS_META[task.status] : null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-950/70 backdrop-blur-md animate-fade-in"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-3xl max-h-[92vh] flex flex-col bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200/90 dark:border-slate-800 overflow-hidden text-slate-900 dark:text-slate-100"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="internal-task-chat-title"
      >
        {/* Header */}
        <div className="border-b border-slate-200/80 dark:border-slate-800">
          <div className="px-5 sm:px-6 py-3.5 flex items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800/60">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 text-white flex items-center justify-center shadow-md shadow-blue-500/20 shrink-0">
                <MessageSquare className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                <h3 id="internal-task-chat-title" className="text-sm sm:text-base font-bold tracking-tight truncate">
                  {task ? task.title : 'Task Conversation'}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">R&amp;D / Internal task conversation</p>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 dark:hover:text-slate-200 dark:hover:bg-slate-800 transition-colors"
              aria-label="Close conversation"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {task && (
            <div className="px-5 sm:px-6 py-2.5 bg-slate-50/70 dark:bg-slate-950/40 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs">
              <span className="font-mono font-bold bg-white dark:bg-slate-800 px-2 py-0.5 rounded-md border border-slate-200/90 dark:border-slate-700">
                {task.task_number}
              </span>
              <span className="text-slate-600 dark:text-slate-300 font-medium">{INTERNAL_TYPE_LABEL[task.task_type]}</span>
              {task.due_date && (
                <span className={`inline-flex items-center gap-1 ${task.is_overdue ? 'text-rose-600 font-semibold' : 'text-slate-500 dark:text-slate-400'}`}>
                  <CalendarDays className="w-3.5 h-3.5" />
                  Due {formatInternalDate(task.due_date)}
                </span>
              )}
              <span className="inline-flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                <User className="w-3.5 h-3.5" />
                {task.assigned_to?.name || 'Unassigned'}
                {task.assigned_to?.employee_code && (
                  <span className="font-mono text-[10px] text-slate-400">({task.assigned_to.employee_code})</span>
                )}
              </span>
              <div className="ml-auto flex items-center gap-2">
                {task.can_update_status ? (
                  <select
                    aria-label="Change status"
                    value={task.status}
                    disabled={isUpdatingStatus}
                    onChange={(e) => handleStatusChange(e.target.value as InternalTaskStatus)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold border outline-none cursor-pointer ${statusMeta?.badge}`}
                  >
                    {STATUS_OPTIONS.map((s) => (
                      <option key={s} value={s}>
                        {INTERNAL_STATUS_META[s].label}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold border ${statusMeta?.badge}`}>
                    {statusMeta?.label}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5 bg-slate-50/50 dark:bg-slate-950/40 min-h-[320px] max-h-[58vh]">
          {isLoading && (
            <div className="py-10 text-center text-xs text-slate-500" role="status">
              Loading conversation...
            </div>
          )}

          {!isLoading && error && (
            <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300 flex items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span className="font-medium">{error}</span>
              </div>
              <button type="button" onClick={() => fetchThread(false)} className="inline-flex items-center gap-1 font-bold hover:underline">
                <RotateCcw className="w-3.5 h-3.5" /> Retry
              </button>
            </div>
          )}

          {!isLoading &&
            groups.map((g) => (
              <div key={g.header} className="space-y-4">
                <div className="relative flex items-center justify-center my-4">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-slate-200/80 dark:border-slate-800" />
                  </div>
                  <div className="relative px-3.5 py-0.5 rounded-full bg-slate-100/90 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    {g.header}
                  </div>
                </div>

                {g.items.map((msg) => {
                  if (msg.message_type === 'SYSTEM_EVENT') {
                    return (
                      <div key={msg.message_id} className="flex justify-center my-3">
                        <div className="max-w-[95%] sm:max-w-lg px-4 py-2 rounded-2xl bg-slate-100/90 dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700/70 text-xs text-slate-700 dark:text-slate-300 flex items-center gap-3">
                          <span className="w-6 h-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-700 flex items-center justify-center shrink-0">
                            <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
                          </span>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium leading-snug">{msg.message_text}</p>
                            <span className="text-[10px] text-slate-400 font-mono mt-0.5 block">{formatTime(msg.created_at)}</span>
                          </div>
                        </div>
                      </div>
                    );
                  }

                  if (msg.is_own) {
                    return (
                      <div key={msg.message_id} className="flex items-start justify-end gap-2.5 max-w-[90%] sm:max-w-[82%] ml-auto">
                        <div className="flex flex-col items-end space-y-1">
                          <div className="flex items-center gap-1.5 text-[11px] text-slate-500 px-1">
                            <span className="font-mono text-[10px] text-slate-400">{formatTime(msg.created_at)}</span>
                            <span className="font-bold text-blue-600 dark:text-blue-400">You</span>
                          </div>
                          <div className="p-3.5 sm:p-4 rounded-2xl rounded-tr-xs bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/10 text-xs leading-relaxed whitespace-pre-wrap break-words">
                            {msg.message_text}
                          </div>
                        </div>
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center text-xs font-bold shrink-0 ring-2 ring-white dark:ring-slate-900">
                          You
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div key={msg.message_id} className="flex items-start gap-2.5 max-w-[90%] sm:max-w-[82%]">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-slate-600 to-slate-700 text-white flex items-center justify-center text-xs font-bold shrink-0 ring-2 ring-white dark:ring-slate-900">
                        {getInitials(msg.author_name)}
                      </div>
                      <div className="flex flex-col space-y-1 min-w-0">
                        <div className="flex items-center gap-1.5 flex-wrap text-xs px-0.5">
                          <span className="font-bold">{msg.author_name}</span>
                          {msg.author_employee_code && (
                            <span className="font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-1.5 rounded border border-slate-200/80 dark:border-slate-700 text-[10px] font-semibold">
                              {msg.author_employee_code}
                            </span>
                          )}
                          {msg.author_department_name && (
                            <span className="px-2 rounded-full text-[9.5px] font-semibold border bg-slate-50 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700">
                              {msg.author_department_name}
                            </span>
                          )}
                          <span className="font-mono text-[10px] text-slate-400">{formatTime(msg.created_at)}</span>
                        </div>
                        <div className="p-3.5 sm:p-4 rounded-2xl rounded-tl-xs bg-white dark:bg-slate-800/95 border border-slate-200/90 dark:border-slate-700/80 shadow-xs text-xs leading-relaxed whitespace-pre-wrap break-words">
                          {msg.message_text}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ))}
          <div ref={endRef} />
        </div>

        {/* Composer */}
        <div className="p-4 sm:p-5 border-t border-slate-200/80 dark:border-slate-800 space-y-2.5">
          {sendError && (
            <div role="alert" className="p-3 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span className="font-medium">{sendError}</span>
            </div>
          )}
          <form onSubmit={handleSend}>
            <div className="rounded-2xl border border-slate-200 dark:border-slate-700/90 bg-slate-50/60 dark:bg-slate-800/40 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10 transition-all overflow-hidden">
              <textarea
                rows={2}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Type an update... (Enter to send, Shift+Enter for new line)"
                aria-label="Message"
                maxLength={5000}
                className="w-full px-4 pt-3 pb-2 text-xs bg-transparent outline-none resize-none leading-relaxed placeholder:text-slate-400"
              />
              <div className="flex items-center justify-end px-4 pb-2.5 pt-1 border-t border-slate-100 dark:border-slate-800/70">
                <button
                  type="submit"
                  disabled={isSending || !draft.trim()}
                  className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-xs font-bold shadow-md shadow-blue-500/20 transition-all disabled:opacity-40 disabled:pointer-events-none"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{isSending ? 'Sending...' : 'Send'}</span>
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

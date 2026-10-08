import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  X,
  Send,
  MessageSquare,
  Clock,
  UserCheck,
  RefreshCw,
  Sparkles,
  AlertCircle,
  FileText,
  Building2,
  MapPin,
  Receipt,
  RotateCcw,
  Shield,
} from 'lucide-react';
import {
  getConversationThreadApi,
  getTaskConversationByApplicationApi,
  postConversationMessageApi,
} from '../../api/conversation';
import { extractErrorMessage } from '../../api/client';
import type {
  ConversationMessage,
  ConversationThread,
} from '../../types/conversation';

export interface TaskConversationModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderId?: string | null;
  applicationId?: string | null;
  onMessagePosted?: () => void;
}

function formatDateGroupHeader(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(today.getDate() - 1);

    if (d.toDateString() === today.toDateString()) {
      return 'Today';
    }
    if (d.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    }
    return d.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function getDepartmentBadgeClass(deptName?: string | null): string {
  const d = (deptName || '').toLowerCase();
  if (d.includes('sale')) {
    return 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800';
  }
  if (d.includes('operat')) {
    return 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-950/60 dark:text-purple-300 dark:border-purple-800';
  }
  if (d.includes('account')) {
    return 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800';
  }
  return 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700';
}

function getSystemEventIcon(eventType?: string | null) {
  const e = (eventType || '').toUpperCase();
  if (e.includes('ASSIGN') || e.includes('REASSIGN')) {
    return <UserCheck className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400 shrink-0" />;
  }
  if (e.includes('STATUS')) {
    return <RefreshCw className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />;
  }
  if (e.includes('CREATE') || e.includes('CONFIRM')) {
    return <Sparkles className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0" />;
  }
  return <Clock className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400 shrink-0" />;
}

export const TaskConversationModal: React.FC<TaskConversationModalProps> = ({
  isOpen,
  onClose,
  orderId,
  applicationId,
  onMessagePosted,
}) => {
  const [thread, setThread] = useState<ConversationThread | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Message composer state
  const [messageDraft, setMessageDraft] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);
  const [sendError, setSendError] = useState<string | null>(null);

  // Pagination cursor state
  const [isLoadingOlder, setIsLoadingOlder] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const fetchThread = useCallback(
    async (isBackground = false) => {
      if (!orderId && !applicationId) return;

      if (!isBackground) {
        setIsLoading(true);
        setError(null);
      }

      try {
        let data: ConversationThread;
        if (orderId) {
          data = await getConversationThreadApi(orderId);
        } else if (applicationId) {
          data = await getTaskConversationByApplicationApi(applicationId);
        } else {
          return;
        }

        setThread(data);
      } catch (err) {
        if (!isBackground) {
          setError(extractErrorMessage(err));
        }
      } finally {
        if (!isBackground) {
          setIsLoading(false);
        }
      }
    },
    [orderId, applicationId]
  );

  // Initial load when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchThread(false);
      setSendError(null);
    } else {
      setThread(null);
      setMessageDraft('');
      setSendError(null);
    }
  }, [isOpen, fetchThread]);

  // Periodic polling (every 10s) and window focus refetching while thread is open
  useEffect(() => {
    if (!isOpen) return;

    const interval = setInterval(() => {
      fetchThread(true);
    }, 10000);

    const handleFocus = () => {
      fetchThread(true);
    };

    window.addEventListener('focus', handleFocus);

    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', handleFocus);
    };
  }, [isOpen, fetchThread]);

  // Scroll to bottom on initial thread load or after sending
  useEffect(() => {
    if (thread?.items && !isLoadingOlder && typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [thread?.items?.length, isLoadingOlder]);

  // Handle Load Older Messages
  const handleLoadOlder = async () => {
    if (!thread || !thread.items.length || isLoadingOlder) return;

    const oldestMsg = thread.items[0];
    setIsLoadingOlder(true);

    try {
      let olderData: ConversationThread;
      if (orderId) {
        olderData = await getConversationThreadApi(orderId, {
          before_id: oldestMsg.message_id,
          limit: 30,
        });
      } else if (applicationId) {
        olderData = await getTaskConversationByApplicationApi(applicationId, {
          before_id: oldestMsg.message_id,
          limit: 30,
        });
      } else {
        return;
      }

      setThread((prev) => {
        if (!prev) return olderData;
        const newItemsMap = new Map<string, ConversationMessage>();
        for (const m of olderData.items) newItemsMap.set(m.message_id, m);
        for (const m of prev.items) newItemsMap.set(m.message_id, m);

        const combined = Array.from(newItemsMap.values()).sort(
          (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );

        return {
          ...prev,
          items: combined,
          has_more_older: olderData.has_more_older,
        };
      });
    } catch (err) {
      setSendError('Failed to load older messages.');
    } finally {
      setIsLoadingOlder(false);
    }
  };

  // Send message
  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    const trimmed = messageDraft.trim();
    if (!trimmed || !thread || isSending) return;

    setIsSending(true);
    setSendError(null);

    // Client-side generated idempotency key for double-click protection
    const idempotencyKey = `${thread.order_id}_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    try {
      const newMsg = await postConversationMessageApi(thread.order_id, {
        message_text: trimmed,
        idempotency_key: idempotencyKey,
      });

      // Clear draft
      setMessageDraft('');

      // Optimistically append message to local state
      setThread((prev) => {
        if (!prev) return null;
        const exists = prev.items.some((m) => m.message_id === newMsg.message_id);
        if (exists) return prev;
        return {
          ...prev,
          items: [...prev.items, newMsg],
          total_count: prev.total_count + 1,
        };
      });

      // Trigger parent callback (to update table remark preview)
      if (onMessagePosted) {
        onMessagePosted();
      }

      // Re-focus composer
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 50);
    } catch (err) {
      setSendError(extractErrorMessage(err));
    } finally {
      setIsSending(false);
    }
  };

  // Keyboard shortcut: Enter to send, Shift+Enter for newline
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  // Group messages by Date for chronological timeline separators
  const groupedMessages: { dateHeader: string; messages: ConversationMessage[] }[] = [];
  if (thread?.items) {
    let currentHeader = '';
    let currentGroup: ConversationMessage[] = [];

    for (const msg of thread.items) {
      const header = formatDateGroupHeader(msg.created_at);
      if (header !== currentHeader) {
        if (currentGroup.length > 0) {
          groupedMessages.push({ dateHeader: currentHeader, messages: currentGroup });
        }
        currentHeader = header;
        currentGroup = [msg];
      } else {
        currentGroup.push(msg);
      }
    }
    if (currentGroup.length > 0) {
      groupedMessages.push({ dateHeader: currentHeader, messages: currentGroup });
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/70 backdrop-blur-md animate-fade-in"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-3xl max-h-[92vh] flex flex-col bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200/80 dark:border-slate-800 overflow-hidden transform transition-all text-slate-900 dark:text-slate-100"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="conversation-modal-title"
      >
        {/* Modal Header */}
        <div className="px-5 sm:px-6 py-4 border-b border-slate-200/80 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/90 backdrop-blur-sm flex items-start justify-between gap-4">
          <div className="space-y-1.5 flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800 dark:bg-blue-950/80 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                <MessageSquare className="w-3.5 h-3.5" />
                Shared Task Conversation
              </span>
              {thread && (
                <span className="font-mono text-xs font-bold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 px-2 py-0.5 rounded-md border border-slate-200 dark:border-slate-700">
                  {thread.order_number}
                </span>
              )}
              {thread?.application_number && (
                <span className="font-mono text-xs font-semibold text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-950/60 px-2 py-0.5 rounded-md border border-purple-200 dark:border-purple-800">
                  {thread.application_number}
                </span>
              )}
              {thread?.gst_invoice_required && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10.5px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-400 dark:border-emerald-800">
                  <Receipt className="w-3 h-3 text-emerald-600" />
                  GST Invoice
                </span>
              )}
            </div>

            {/* Task Info Summary */}
            {thread && (
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600 dark:text-slate-300 pt-0.5">
                <div className="font-semibold text-slate-900 dark:text-white flex items-center gap-1 truncate max-w-[200px]" title={thread.client_name}>
                  <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <span className="truncate">{thread.client_name}</span>
                </div>
                <div className="flex items-center gap-1 text-slate-700 dark:text-slate-300 font-medium truncate max-w-[220px]" title={thread.service_name}>
                  <FileText className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                  <span className="truncate">{thread.service_name}</span>
                </div>
                {thread.location && (
                  <div className="flex items-center gap-1 text-slate-500 dark:text-slate-400 truncate max-w-[150px]" title={thread.location}>
                    <MapPin className="w-3 h-3 text-indigo-500 shrink-0" />
                    <span className="truncate">{thread.location}</span>
                  </div>
                )}
                <div className="flex items-center gap-1.5 ml-auto text-[11px] font-medium text-slate-500 dark:text-slate-400">
                  <span>Assignee:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-800 px-2 py-0.5 rounded-md border border-slate-200/80 dark:border-slate-700">
                    {thread.current_assignee_name || 'Unassigned'}
                    {thread.current_assignee_code && ` (${thread.current_assignee_code})`}
                  </span>
                </div>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-200/70 dark:hover:text-slate-200 dark:hover:bg-slate-800 transition"
            aria-label="Close conversation modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Message Thread Body */}
        <div
          ref={messagesContainerRef}
          className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5 bg-gradient-to-b from-slate-50/50 to-white dark:from-slate-900/50 dark:to-slate-900 min-h-[320px] max-h-[58vh]"
        >
          {/* Loading Skeleton */}
          {isLoading && (
            <div className="space-y-4 py-8">
              <div className="flex justify-start">
                <div className="w-2/3 h-16 bg-slate-200 dark:bg-slate-800 rounded-2xl animate-pulse" />
              </div>
              <div className="flex justify-end">
                <div className="w-1/2 h-14 bg-blue-100 dark:bg-blue-950/40 rounded-2xl animate-pulse" />
              </div>
              <div className="flex justify-center">
                <div className="w-1/3 h-6 bg-slate-100 dark:bg-slate-800 rounded-full animate-pulse" />
              </div>
            </div>
          )}

          {/* Error State */}
          {!isLoading && error && (
            <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300 flex items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                <span>{error}</span>
              </div>
              <button
                type="button"
                onClick={() => fetchThread(false)}
                className="inline-flex items-center gap-1 font-bold text-rose-700 dark:text-rose-400 hover:underline shrink-0"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Retry
              </button>
            </div>
          )}

          {/* Load Older Messages Button */}
          {!isLoading && thread && thread.has_more_older && (
            <div className="flex justify-center">
              <button
                type="button"
                disabled={isLoadingOlder}
                onClick={handleLoadOlder}
                className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 shadow-2xs transition disabled:opacity-50"
              >
                <RotateCcw className={`w-3.5 h-3.5 ${isLoadingOlder ? 'animate-spin text-blue-600' : ''}`} />
                <span>{isLoadingOlder ? 'Loading older history...' : 'Load older messages'}</span>
              </button>
            </div>
          )}

          {/* Empty Conversation State */}
          {!isLoading && !error && thread && thread.items.length === 0 && (
            <div className="py-12 text-center space-y-2">
              <div className="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 flex items-center justify-center mx-auto shadow-inner">
                <MessageSquare className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">No conversation remarks yet</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
                This shared timeline keeps Sales, Operations, and Accounts synchronized. Add the first update below.
              </p>
            </div>
          )}

          {/* Grouped Messages Timeline */}
          {!isLoading &&
            groupedMessages.map((group) => (
              <div key={group.dateHeader} className="space-y-4">
                {/* Date Separator Pill */}
                <div className="flex items-center justify-center my-2">
                  <span className="px-3 py-0.5 rounded-full text-[10.5px] font-semibold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700/80 shadow-2xs">
                    {group.dateHeader}
                  </span>
                </div>

                {/* Messages in Group */}
                {group.messages.map((msg) => {
                  // 1. SYSTEM EVENT RENDERING
                  if (msg.message_type === 'SYSTEM_EVENT') {
                    return (
                      <div
                        key={msg.message_id}
                        className="flex justify-center my-2 animate-fade-in"
                      >
                        <div className="max-w-[90%] sm:max-w-md px-3.5 py-2 rounded-2xl bg-slate-100/90 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/70 text-xs text-slate-700 dark:text-slate-300 shadow-2xs flex items-center gap-2.5">
                          <span className="p-1 rounded-lg bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-700 shadow-2xs">
                            {getSystemEventIcon(msg.event_type)}
                          </span>
                          <div className="flex-1 min-w-0">
                            <p className="leading-snug">{msg.message_text}</p>
                            <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono mt-0.5 block">
                              {msg.formatted_created_at}
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  }

                  // 2. MY COMMENTS (Right aligned)
                  if (msg.is_mine) {
                    return (
                      <div
                        key={msg.message_id}
                        className="flex flex-col items-end space-y-1 animate-fade-in"
                      >
                        <div className="flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400 px-1">
                          <span className="font-bold text-blue-700 dark:text-blue-400">You</span>
                          {msg.author_department_name && (
                            <span className={`px-1.5 py-0.2 rounded text-[9.5px] font-semibold border ${getDepartmentBadgeClass(msg.author_department_name)}`}>
                              {msg.author_department_name}
                            </span>
                          )}
                          <span className="font-mono text-[10px]">{msg.formatted_created_at}</span>
                        </div>

                        <div className="max-w-[85%] sm:max-w-md p-3.5 rounded-2xl rounded-tr-xs bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-md text-xs leading-relaxed whitespace-pre-wrap break-words">
                          {msg.message_text}
                        </div>
                      </div>
                    );
                  }

                  // 3. OTHER EMPLOYEES' COMMENTS (Left aligned)
                  return (
                    <div
                      key={msg.message_id}
                      className="flex flex-col items-start space-y-1 animate-fade-in"
                    >
                      <div className="flex items-center gap-1.5 text-[11px] text-slate-600 dark:text-slate-400 px-1">
                        <span className="font-bold text-slate-900 dark:text-slate-100">
                          {msg.author_name}
                        </span>
                        {msg.author_employee_code && (
                          <span className="font-mono text-slate-400 text-[10px]">
                            ({msg.author_employee_code})
                          </span>
                        )}
                        {msg.author_department_name && (
                          <span className={`px-1.5 py-0.2 rounded text-[9.5px] font-semibold border ${getDepartmentBadgeClass(msg.author_department_name)}`}>
                            {msg.author_department_name}
                          </span>
                        )}
                        <span className="font-mono text-[10px] text-slate-400 ml-1">
                          {msg.formatted_created_at}
                        </span>
                      </div>

                      <div className="max-w-[85%] sm:max-w-md p-3.5 rounded-2xl rounded-tl-xs bg-white dark:bg-slate-800/90 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700/80 shadow-xs text-xs leading-relaxed whitespace-pre-wrap break-words">
                        {msg.message_text}
                      </div>
                    </div>
                  );
                })}
              </div>
            ))}

          <div ref={messagesEndRef} />
        </div>

        {/* Composer Action Box */}
        <div className="p-4 sm:p-5 border-t border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2.5">
          {sendError && (
            <div className="p-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300 text-xs flex items-center justify-between gap-2">
              <div className="flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                <span>{sendError}</span>
              </div>
              <button
                type="button"
                onClick={() => setSendError(null)}
                className="text-rose-600 hover:underline text-[11px] font-semibold"
              >
                Dismiss
              </button>
            </div>
          )}

          {thread && thread.can_post ? (
            <form onSubmit={handleSendMessage} className="space-y-2">
              <div className="relative rounded-2xl border border-slate-300 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/60 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:bg-white dark:focus-within:bg-slate-900 transition shadow-inner">
                <textarea
                  ref={textareaRef}
                  rows={2}
                  value={messageDraft}
                  onChange={(e) => {
                    setMessageDraft(e.target.value);
                    if (sendError) setSendError(null);
                  }}
                  onKeyDown={handleKeyDown}
                  placeholder="Type an update or remark... (Enter to send, Shift+Enter for new line)"
                  className="w-full px-3.5 py-2.5 text-xs text-slate-900 dark:text-white bg-transparent outline-hidden resize-none leading-relaxed"
                  maxLength={3000}
                />

                <div className="flex items-center justify-between px-3.5 pb-2 text-[11px] text-slate-400 dark:text-slate-500">
                  <span className="text-[10px]">
                    {messageDraft.length > 0 && `${messageDraft.length} / 3000`}
                  </span>
                  <button
                    type="submit"
                    disabled={isSending || !messageDraft.trim()}
                    className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-xs font-bold shadow-md shadow-blue-500/20 transition disabled:opacity-40 disabled:pointer-events-none active:scale-98"
                  >
                    <Send className={`w-3.5 h-3.5 ${isSending ? 'animate-spin' : ''}`} />
                    <span>{isSending ? 'Sending...' : 'Send Remark'}</span>
                  </button>
                </div>
              </div>
            </form>
          ) : (
            <div className="p-3 rounded-2xl bg-slate-100 dark:bg-slate-800/70 text-slate-500 dark:text-slate-400 text-xs flex items-center gap-2">
              <Shield className="w-4 h-4 shrink-0 text-slate-400" />
              <span>
                You have view-only access to this conversation thread. Posting is permitted to authorized sales representatives, assigned operations staff, or managers.
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

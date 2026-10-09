import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useInRouterContext } from 'react-router-dom';
import {
  Bell,
  MessageSquare,
  Clock,
  ChevronRight,
  RefreshCw,
  User,
} from 'lucide-react';
import { useRemarkNotification } from '../../context/RemarkNotificationContext';
import { getRemarkNotificationsApi } from '../../api/conversation';
import type { RemarkNotificationItem } from '../../types/conversation';

function getModuleBadgeClass(moduleName?: string | null): string {
  const m = (moduleName || '').toUpperCase();
  if (m === 'SALES') {
    return 'bg-emerald-50 text-emerald-700 border-emerald-200/80 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800/80';
  }
  if (m === 'OPERATIONS') {
    return 'bg-purple-50 text-purple-700 border-purple-200/80 dark:bg-purple-950/50 dark:text-purple-300 dark:border-purple-800/80';
  }
  if (m === 'ACCOUNTS') {
    return 'bg-cyan-50 text-cyan-700 border-cyan-200/80 dark:bg-cyan-950/50 dark:text-cyan-300 dark:border-cyan-800/80';
  }
  return 'bg-amber-50 text-amber-700 border-amber-200/80 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800/80';
}

export const NotificationBell: React.FC = () => {
  const { totalUnreadCount, refreshUnreadSummary } = useRemarkNotification();
  const inRouter = useInRouterContext();
  const routerNavigate = inRouter ? useNavigate() : null;
  const navigate = (to: string) => {
    if (routerNavigate) {
      routerNavigate(to);
    } else {
      window.location.href = to;
    }
  };

  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [notifications, setNotifications] = useState<RemarkNotificationItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [unreadOnly, setUnreadOnly] = useState<boolean>(false);

  const dropdownRef = useRef<HTMLDivElement | null>(null);

  const fetchNotifications = useCallback(
    async (pageToFetch = 1, append = false, unreadFilter = unreadOnly) => {
      setIsLoading(true);
      try {
        const data = await getRemarkNotificationsApi({
          page: pageToFetch,
          limit: 10,
          unread_only: unreadFilter,
        });

        if (append) {
          setNotifications((prev) => [...prev, ...data.items]);
        } else {
          setNotifications(data.items);
        }
        setPage(data.page);
        setTotalPages(data.total_pages);
      } catch {
        // Fallback gracefully
      } finally {
        setIsLoading(false);
      }
    },
    [unreadOnly]
  );

  // Fetch when dropdown is opened
  useEffect(() => {
    if (isOpen) {
      fetchNotifications(1, false, unreadOnly);
    }
  }, [isOpen, unreadOnly, fetchNotifications]);

  // Click outside listener to close dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleNotificationClick = (item: RemarkNotificationItem) => {
    setIsOpen(false);
    navigate(item.target_route);
  };

  const handleLoadMore = () => {
    if (page < totalPages && !isLoading) {
      fetchNotifications(page + 1, true, unreadOnly);
    }
  };

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      {/* Bell Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`relative inline-flex items-center justify-center p-2 rounded-full transition duration-200 select-none ${
          isOpen
            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300 ring-2 ring-blue-500/40'
            : 'bg-white/80 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-750 border border-slate-200/80 dark:border-slate-700'
        } shadow-xs`}
        title={`Notifications (${totalUnreadCount} unread)`}
        aria-label="Remark Notifications"
        data-testid="header-notification-bell"
      >
        <Bell className="w-4 h-4 stroke-[2.2]" />

        {/* Dynamic Unread Badge */}
        {totalUnreadCount > 0 && (
          <span
            data-testid="notification-bell-badge"
            className="absolute -top-1 -right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full bg-blue-600 text-white text-[10px] font-extrabold shadow-sm ring-2 ring-white dark:ring-slate-900 animate-in fade-in duration-200"
          >
            {totalUnreadCount > 99 ? '99+' : totalUnreadCount}
          </span>
        )}
      </button>

      {/* Notification Dropdown Popover */}
      {isOpen && (
        <div
          data-testid="notification-dropdown-panel"
          className="absolute right-0 mt-2 w-[340px] sm:w-[400px] max-w-[90vw] rounded-2xl bg-white/95 dark:bg-slate-900/95 backdrop-blur-2xl border border-slate-200/90 dark:border-slate-800 shadow-2xl z-50 overflow-hidden flex flex-col animate-in fade-in slide-in-from-top-2 duration-200"
        >
          {/* Header */}
          <div className="p-3.5 border-b border-slate-100 dark:border-slate-800/80 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/50">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <h3 className="text-xs sm:text-sm font-bold text-slate-800 dark:text-slate-100">
                Remark Updates
              </h3>
              {totalUnreadCount > 0 && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-950/70 dark:text-blue-300 border border-blue-200/80 dark:border-blue-800/80">
                  {totalUnreadCount} new
                </span>
              )}
            </div>

            {/* Filter Toggle */}
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => setUnreadOnly(!unreadOnly)}
                className={`text-[11px] font-semibold px-2 py-1 rounded-lg transition border ${
                  unreadOnly
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-750'
                }`}
              >
                {unreadOnly ? 'Unread only' : 'All'}
              </button>

              <button
                type="button"
                onClick={() => {
                  fetchNotifications(1, false, unreadOnly);
                  refreshUnreadSummary();
                }}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                title="Refresh notifications"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          {/* List Area */}
          <div className="max-h-[380px] overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800/60 custom-scrollbar">
            {isLoading && notifications.length === 0 ? (
              <div className="py-10 flex flex-col items-center justify-center gap-2 text-slate-400">
                <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
                <span className="text-xs font-medium">Loading remark updates...</span>
              </div>
            ) : notifications.length === 0 ? (
              <div className="py-12 px-4 flex flex-col items-center justify-center text-center">
                <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 mb-2">
                  <Bell className="w-5 h-5" />
                </div>
                <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  {unreadOnly ? 'No unread remark updates' : 'No recent remark updates'}
                </p>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Remarks posted across Sales, Operations, and Accounts will appear here.
                </p>
              </div>
            ) : (
              notifications.map((item) => (
                <div
                  key={item.message_id}
                  onClick={() => handleNotificationClick(item)}
                  data-testid={`notification-item-${item.message_id}`}
                  className={`p-3 transition-colors cursor-pointer flex gap-2.5 items-start group hover:bg-blue-50/50 dark:hover:bg-blue-950/20 ${
                    !item.is_read
                      ? 'bg-blue-50/30 dark:bg-blue-950/15 border-l-2 border-l-blue-600 dark:border-l-blue-500'
                      : 'border-l-2 border-l-transparent'
                  }`}
                >
                  {/* Origin Icon / Unread Dot */}
                  <div className="pt-0.5 shrink-0 flex flex-col items-center gap-1.5">
                    {!item.is_read ? (
                      <span
                        data-testid="unread-dot"
                        className="w-2 h-2 rounded-full bg-blue-600 dark:bg-blue-400 ring-2 ring-blue-200 dark:ring-blue-900/60"
                        title="Unread remark"
                      />
                    ) : (
                      <span className="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-700" />
                    )}
                  </div>

                  {/* Main Content */}
                  <div className="flex-1 min-w-0">
                    {/* Top Row: Module Badge + Order Number + Timestamp */}
                    <div className="flex items-center justify-between gap-1 mb-1 flex-wrap">
                      <div className="flex items-center gap-1.5">
                        <span
                          className={`text-[9px] font-bold px-1.5 py-0.2 rounded border uppercase tracking-wider ${getModuleBadgeClass(
                            item.originating_module
                          )}`}
                        >
                          {item.originating_module || 'CRM'}
                        </span>
                        <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition">
                          {item.order_number}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400 dark:text-slate-500 flex items-center gap-0.5 font-medium">
                        <Clock className="w-2.5 h-2.5" />
                        {item.formatted_created_at}
                      </span>
                    </div>

                    {/* Client & Service */}
                    <div className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 truncate">
                      {item.client_name}{' '}
                      <span className="font-normal text-slate-400">· {item.service_name}</span>
                    </div>

                    {/* Remark Text Preview */}
                    <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 mt-1 leading-relaxed bg-white/60 dark:bg-slate-800/60 p-1.5 rounded-lg border border-slate-100 dark:border-slate-800 font-normal">
                      {item.message_text}
                    </p>

                    {/* Author Footer */}
                    <div className="flex items-center justify-between mt-1.5 text-[10px] text-slate-500 dark:text-slate-400">
                      <span className="font-medium inline-flex items-center gap-1">
                        <User className="w-2.5 h-2.5 text-slate-400" />
                        {item.author_name}
                        {item.author_department_name ? ` (${item.author_department_name})` : ''}
                      </span>
                      <span className="text-blue-600 dark:text-blue-400 font-bold opacity-0 group-hover:opacity-100 transition inline-flex items-center gap-0.5">
                        Open thread
                        <ChevronRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer with Load More if available */}
          {page < totalPages && (
            <div className="p-2 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 text-center">
              <button
                type="button"
                onClick={handleLoadMore}
                disabled={isLoading}
                className="text-[11px] font-bold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition py-1 px-3 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-950/30"
              >
                {isLoading ? 'Loading...' : 'Load older notifications'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

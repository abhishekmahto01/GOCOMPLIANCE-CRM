import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
} from 'react';
import { useAuth } from './AuthContext';
import {
  getUnreadSummaryApi,
  markMessagesAsReadApi,
  markNotificationMessagesAsReadApi,
  markAllNotificationsAsReadApi,
} from '../api/conversation';
import type { UnreadSummaryResponse } from '../types/conversation';

interface RemarkNotificationContextType {
  unreadSummary: UnreadSummaryResponse | null;
  totalUnreadCount: number;
  isLoading: boolean;
  refreshUnreadSummary: () => Promise<void>;
  markMessagesRead: (orderId: string, messageIds: string[]) => Promise<void>;
  markBatchMessagesRead: (messageIds: string[]) => Promise<void>;
  markAllAsRead: () => Promise<void>;
}

const RemarkNotificationContext = createContext<RemarkNotificationContextType | undefined>(
  undefined
);

export const RemarkNotificationProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { user, isAuthenticated } = useAuth();
  const [unreadSummary, setUnreadSummary] = useState<UnreadSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const isFetchingRef = useRef<boolean>(false);
  const currentUserId = user?.user_id || (user as any)?.id;

  const fetchSummary = useCallback(async () => {
    if (!isAuthenticated || !currentUserId || isFetchingRef.current) return;

    isFetchingRef.current = true;
    try {
      const data = await getUnreadSummaryApi();
      setUnreadSummary(data);
    } catch {
      // Do not crash UI or overwrite valid state on intermittent network failure
    } finally {
      isFetchingRef.current = false;
      setIsLoading(false);
    }
  }, [isAuthenticated, currentUserId]);

  // Initial fetch when authenticated identity changes
  useEffect(() => {
    if (isAuthenticated && currentUserId) {
      setIsLoading(true);
      setUnreadSummary(null);
      fetchSummary();
    } else {
      setUnreadSummary(null);
    }
  }, [isAuthenticated, currentUserId, fetchSummary]);

  // Polling every 45 seconds while authenticated, and refetch on window focus
  useEffect(() => {
    if (!isAuthenticated || !currentUserId) return;

    const interval = setInterval(() => {
      fetchSummary();
    }, 45000);

    const handleFocus = () => {
      fetchSummary();
    };

    window.addEventListener('focus', handleFocus);

    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', handleFocus);
    };
  }, [isAuthenticated, currentUserId, fetchSummary]);

  // Mark displayed messages read for a specific order
  const markMessagesRead = useCallback(
    async (orderId: string, messageIds: string[]) => {
      if (!orderId || !messageIds || messageIds.length === 0) return;

      try {
        await markMessagesAsReadApi(orderId, messageIds);
        await fetchSummary();
      } catch {
        // Silently handle or let caller handle
      }
    },
    [fetchSummary]
  );

  // Batch mark notification messages read across orders
  const markBatchMessagesRead = useCallback(
    async (messageIds: string[]) => {
      if (!messageIds || messageIds.length === 0) return;

      try {
        await markNotificationMessagesAsReadApi(messageIds);
        await fetchSummary();
      } catch {
        // Silently handle
      }
    },
    [fetchSummary]
  );

  // Mark all authorized notifications read
  const markAllAsRead = useCallback(async () => {
    try {
      await markAllNotificationsAsReadApi();
      setUnreadSummary({
        total_unread_count: 0,
        unread_orders: {},
      });
      await fetchSummary();
    } catch {
      // Silently handle
    }
  }, [fetchSummary]);

  const totalUnreadCount = unreadSummary?.total_unread_count ?? 0;

  return (
    <RemarkNotificationContext.Provider
      value={{
        unreadSummary,
        totalUnreadCount,
        isLoading,
        refreshUnreadSummary: fetchSummary,
        markMessagesRead,
        markBatchMessagesRead,
        markAllAsRead,
      }}
    >
      {children}
    </RemarkNotificationContext.Provider>
  );
};

const defaultFallback: RemarkNotificationContextType = {
  unreadSummary: null,
  totalUnreadCount: 0,
  isLoading: false,
  refreshUnreadSummary: async () => {},
  markMessagesRead: async () => {},
  markBatchMessagesRead: async () => {},
  markAllAsRead: async () => {},
};

export const useRemarkNotification = (): RemarkNotificationContextType => {
  const context = useContext(RemarkNotificationContext);
  if (!context) {
    return defaultFallback;
  }
  return context;
};

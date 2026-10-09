import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
} from 'react';
import { useAuth } from './AuthContext';
import { getUnreadSummaryApi, markMessagesAsReadApi } from '../api/conversation';
import type { UnreadSummaryResponse } from '../types/conversation';

interface RemarkNotificationContextType {
  unreadSummary: UnreadSummaryResponse | null;
  totalUnreadCount: number;
  isLoading: boolean;
  refreshUnreadSummary: () => Promise<void>;
  markMessagesRead: (orderId: string, messageIds: string[]) => Promise<void>;
}

const RemarkNotificationContext = createContext<RemarkNotificationContextType | undefined>(
  undefined
);

export const RemarkNotificationProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { isAuthenticated } = useAuth();
  const [unreadSummary, setUnreadSummary] = useState<UnreadSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const isFetchingRef = useRef<boolean>(false);

  const fetchSummary = useCallback(async () => {
    if (!isAuthenticated || isFetchingRef.current) return;

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
  }, [isAuthenticated]);

  // Initial fetch when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      setIsLoading(true);
      fetchSummary();
    } else {
      setUnreadSummary(null);
    }
  }, [isAuthenticated, fetchSummary]);

  // Polling every 45 seconds while authenticated, and refetch on window focus
  useEffect(() => {
    if (!isAuthenticated) return;

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
  }, [isAuthenticated, fetchSummary]);

  // Mark displayed messages read
  const markMessagesRead = useCallback(
    async (orderId: string, messageIds: string[]) => {
      if (!orderId || !messageIds || messageIds.length === 0) return;

      try {
        await markMessagesAsReadApi(orderId, messageIds);
        // Optimistically update local state & refresh
        await fetchSummary();
      } catch {
        // Silently handle or let caller handle
      }
    },
    [fetchSummary]
  );

  const totalUnreadCount = unreadSummary?.total_unread_count ?? 0;

  return (
    <RemarkNotificationContext.Provider
      value={{
        unreadSummary,
        totalUnreadCount,
        isLoading,
        refreshUnreadSummary: fetchSummary,
        markMessagesRead,
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
};

export const useRemarkNotification = (): RemarkNotificationContextType => {
  const context = useContext(RemarkNotificationContext);
  if (!context) {
    return defaultFallback;
  }
  return context;
};

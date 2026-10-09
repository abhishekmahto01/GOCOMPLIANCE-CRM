import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { NotificationBell } from '../components/dashboard/NotificationBell';
import { TaskConversationModal } from '../components/conversation/TaskConversationModal';
import { RemarkNotificationProvider } from '../context/RemarkNotificationContext';
import * as conversationApi from '../api/conversation';

// Mock AuthContext
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: {
      id: 'user-karishma-id',
      email: 'karishma@gocompliance.in',
      name: 'Karishma Sales',
      role: 'SALES_EXECUTIVE',
    },
    isAuthenticated: true,
    isSuperAdmin: false,
    hasPermission: () => true,
    getEffectiveScope: () => 'OWN',
  }),
}));

// Mock conversation APIs
vi.mock('../api/conversation', () => ({
  getUnreadSummaryApi: vi.fn(),
  getRemarkNotificationsApi: vi.fn(),
  getConversationThreadApi: vi.fn(),
  postConversationMessageApi: vi.fn(),
  markMessagesAsReadApi: vi.fn(),
}));

describe('Shared Remark Notification & Per-User Unread UI Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders NotificationBell with total unread count badge', async () => {
    vi.mocked(conversationApi.getUnreadSummaryApi).mockResolvedValue({
      total_unread_count: 3,
      unread_orders: {
        'order-1': {
          order_id: 'order-1',
          unread_count: 2,
          latest_unread_id: 'msg-1',
          latest_remark_text: 'GST documents required',
          latest_author_name: 'Deepak Operations',
          latest_author_department: 'Operations',
          latest_created_at: '2026-10-09T10:00:00Z',
          formatted_latest_created_at: '09 Oct 2026, 10:00',
        },
        'order-2': {
          order_id: 'order-2',
          unread_count: 1,
          latest_unread_id: 'msg-2',
          latest_remark_text: 'Payment received in full',
          latest_author_name: 'Priya Accounts',
          latest_author_department: 'Accounts',
          latest_created_at: '2026-10-09T11:00:00Z',
          formatted_latest_created_at: '09 Oct 2026, 11:00',
        },
      },
    });

    render(
      <MemoryRouter>
        <RemarkNotificationProvider>
          <NotificationBell />
        </RemarkNotificationProvider>
      </MemoryRouter>
    );

    // Unread count badge should appear
    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });

  it('opening NotificationBell dropdown fetches notification list without marking as read', async () => {
    vi.mocked(conversationApi.getUnreadSummaryApi).mockResolvedValue({
      total_unread_count: 1,
      unread_orders: {
        'order-1': {
          order_id: 'order-1',
          unread_count: 1,
          latest_unread_id: 'msg-1',
          latest_remark_text: 'Draft filed successfully',
          latest_author_name: 'Deepak Operations',
          latest_author_department: 'Operations',
          latest_created_at: '2026-10-09T10:00:00Z',
          formatted_latest_created_at: '09 Oct 2026, 10:00',
        },
      },
    });

    vi.mocked(conversationApi.getRemarkNotificationsApi).mockResolvedValue({
      items: [
        {
          message_id: 'msg-1',
          sales_order_id: 'order-1',
          order_number: 'ORD-2026-001',
          client_name: 'Acme Pvt Ltd',
          service_name: 'Pvt Ltd Registration',
          location: 'Bangalore',
          originating_module: 'OPERATIONS',
          message_text: 'Draft filed successfully with ROC.',
          author_name: 'Deepak Operations',
          author_employee_code: 'EMP-OPS-01',
          author_department_name: 'Operations',
          author_role_name: 'OPERATIONS_EXECUTIVE',
          created_at: '2026-10-09T10:00:00Z',
          formatted_created_at: '09 Oct 2026, 10:00',
          is_read: false,
          target_route: '/operations/my-tasks?open_conversation_order_id=order-1',
        },
      ],
      total_count: 1,
      unread_count: 1,
      page: 1,
      limit: 15,
      total_pages: 1,
    });

    render(
      <MemoryRouter>
        <RemarkNotificationProvider>
          <NotificationBell />
        </RemarkNotificationProvider>
      </MemoryRouter>
    );

    const bellBtn = await screen.findByRole('button', { name: /notifications/i });
    fireEvent.click(bellBtn);

    // Notification item should appear in dropdown
    await waitFor(() => {
      expect(screen.getByText('Acme Pvt Ltd')).toBeInTheDocument();
      expect(screen.getByText('Draft filed successfully with ROC.')).toBeInTheDocument();
      expect(screen.getByText('OPERATIONS')).toBeInTheDocument();
    });

    // Opening the bell alone must NOT call markMessagesAsReadApi
    expect(conversationApi.markMessagesAsReadApi).not.toHaveBeenCalled();
  });

  it('opening TaskConversationModal explicitly marks only displayed unread message IDs as read', async () => {
    vi.mocked(conversationApi.getConversationThreadApi).mockResolvedValue({
      order_id: 'order-1',
      order_number: 'ORD-2026-001',
      client_name: 'Acme Pvt Ltd',
      service_name: 'Pvt Ltd Registration',
      location: 'Bangalore',
      salesperson_name: 'Karishma Sales',
      salesperson_code: 'EMP-SALES-01',
      current_assignee_id: 'user-deepak-id',
      current_assignee_name: 'Deepak Operations',
      current_assignee_code: 'EMP-OPS-01',
      application_id: 'app-1',
      application_number: 'APP-2026-001',
      work_status: 'IN_PROGRESS',
      payment_status: 'FULLY_PAID',
      gst_invoice_required: true,
      can_post: true,
      items: [
        {
          message_id: 'msg-read-1',
          sales_order_id: 'order-1',
          author_user_id: 'user-deepak-id',
          message_type: 'COMMENT',
          message_text: 'First remark (already read)',
          originating_module: 'OPERATIONS',
          author_name: 'Deepak Operations',
          created_at: '2026-10-09T09:00:00Z',
          formatted_created_at: '09 Oct 2026, 09:00',
          is_mine: false,
          is_read: true,
        },
        {
          message_id: 'msg-unread-2',
          sales_order_id: 'order-1',
          author_user_id: 'user-deepak-id',
          message_type: 'COMMENT',
          message_text: 'Second remark (fresh unread update)',
          originating_module: 'OPERATIONS',
          author_name: 'Deepak Operations',
          created_at: '2026-10-09T10:00:00Z',
          formatted_created_at: '09 Oct 2026, 10:00',
          is_mine: false,
          is_read: false,
        },
      ],
      total_count: 2,
      has_more_older: false,
    });

    vi.mocked(conversationApi.markMessagesAsReadApi).mockResolvedValue({
      sales_order_id: 'order-1',
      marked_read_count: 1,
      read_message_ids: ['msg-unread-2'],
    });

    render(
      <MemoryRouter>
        <RemarkNotificationProvider>
          <TaskConversationModal
            isOpen={true}
            onClose={vi.fn()}
            orderId="order-1"
          />
        </RemarkNotificationProvider>
      </MemoryRouter>
    );

    // Messages render
    await waitFor(() => {
      expect(screen.getByText('Second remark (fresh unread update)')).toBeInTheDocument();
    });

    // markMessagesAsReadApi should be called specifically for msg-unread-2 (not msg-read-1)
    await waitFor(() => {
      expect(conversationApi.markMessagesAsReadApi).toHaveBeenCalledWith('order-1', ['msg-unread-2']);
    });
  });
});

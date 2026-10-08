import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { TaskConversationModal } from '../components/conversation/TaskConversationModal';
import * as authApi from '../api/auth';
import * as conversationApi from '../api/conversation';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { ConversationThread } from '../types/conversation';

// Mock ResizeObserver and scrollIntoView
globalThis.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

window.HTMLElement.prototype.scrollIntoView = vi.fn();

const mockUser: CurrentUser = {
  user_id: 'user-current-1',
  employee_code: 'CT0002',
  first_name: 'Manshi',
  last_name: 'Ops',
  official_email: 'manshi@testcorp.com',
  mobile_number: '+919999900002',
  company_id: 'comp-1',
  department_id: 'dept-ops',
  designation_id: 'desig-ops',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const mockThread: ConversationThread = {
  order_id: 'order-123',
  order_number: 'SO-2026-0001',
  client_name: 'Acme Global Private Limited',
  service_name: 'GST Registration',
  location: 'Mumbai Branch',
  salesperson_name: 'Karishma Sales',
  salesperson_code: 'CT0001',
  current_assignee_id: 'user-ops-1',
  current_assignee_name: 'Manshi Ops',
  current_assignee_code: 'CT0002',
  application_id: 'app-456',
  application_number: 'APP-2026-0001',
  work_status: 'IN_PROGRESS',
  payment_status: 'PARTIALLY_PAID',
  gst_invoice_required: true,
  can_post: true,
  total_count: 3,
  has_more_older: false,
  items: [
    {
      message_id: 'msg-1',
      sales_order_id: 'order-123',
      author_user_id: 'user-sales-1',
      message_type: 'COMMENT',
      message_text: 'Initial client requirement from Karishma.',
      author_name: 'Karishma Sales',
      author_employee_code: 'CT0001',
      author_department_name: 'Sales Department',
      author_role_name: 'Sales Executive',
      created_at: '2026-03-01T10:00:00Z',
      formatted_created_at: '01/03/2026, 03:30:00 pm',
      is_mine: false,
    },
    {
      message_id: 'msg-2',
      sales_order_id: 'order-123',
      author_user_id: 'user-admin-1',
      message_type: 'SYSTEM_EVENT',
      message_text: 'Task assigned to Manshi Ops by Director Admin.',
      author_name: 'System',
      event_type: 'TASK_ASSIGNED',
      event_metadata: { new_assignee_name: 'Manshi Ops' },
      created_at: '2026-03-01T11:00:00Z',
      formatted_created_at: '01/03/2026, 04:30:00 pm',
      is_mine: false,
    },
    {
      message_id: 'msg-3',
      sales_order_id: 'order-123',
      author_user_id: 'user-current-1',
      message_type: 'COMMENT',
      message_text: 'Documents uploaded to government portal.',
      author_name: 'Manshi Ops',
      author_employee_code: 'CT0002',
      author_department_name: 'Operations Department',
      author_role_name: 'Operations Executive',
      created_at: '2026-03-01T12:00:00Z',
      formatted_created_at: '01/03/2026, 05:30:00 pm',
      is_mine: true,
    },
  ],
};

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider>
      <AuthProvider>
        <MemoryRouter>{ui}</MemoryRouter>
      </AuthProvider>
    </ThemeProvider>
  );
};

describe('TaskConversationModal Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'test-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);
  });

  it('renders thread header and metadata correctly', async () => {
    vi.spyOn(conversationApi, 'getConversationThreadApi').mockResolvedValue(mockThread);

    renderWithProviders(
      <TaskConversationModal
        isOpen={true}
        onClose={vi.fn()}
        orderId="order-123"
      />
    );

    // Verify task identification header elements
    await waitFor(() => {
      expect(screen.getByText(/Shared Task Conversation/i)).toBeInTheDocument();
      expect(screen.getByText('Acme Global Private Limited')).toBeInTheDocument();
      expect(screen.getByText('SO-2026-0001')).toBeInTheDocument();
      expect(screen.getByText('GST Registration')).toBeInTheDocument();
      expect(screen.getByText('Mumbai Branch')).toBeInTheDocument();
      expect(screen.getAllByText(/Manshi Ops/).length).toBeGreaterThan(0);
      expect(screen.getByText(/GST Invoice/)).toBeInTheDocument();
    });
  });

  it('renders chronological messages with distinct user and system event styles', async () => {
    vi.spyOn(conversationApi, 'getConversationThreadApi').mockResolvedValue(mockThread);

    renderWithProviders(
      <TaskConversationModal
        isOpen={true}
        onClose={vi.fn()}
        orderId="order-123"
      />
    );

    await waitFor(() => {
      // 1. Other user's comment
      expect(screen.getByText('Initial client requirement from Karishma.')).toBeInTheDocument();
      expect(screen.getByText('Karishma Sales')).toBeInTheDocument();
      expect(screen.getByText('Sales Department')).toBeInTheDocument();

      // 2. System event
      expect(screen.getByText('Task assigned to Manshi Ops by Director Admin.')).toBeInTheDocument();

      // 3. My comment
      expect(screen.getByText('Documents uploaded to government portal.')).toBeInTheDocument();
      expect(screen.getAllByText('You').length).toBeGreaterThan(0);
    });
  });

  it('posts a new message, updates the thread, and calls onMessagePosted callback', async () => {
    vi.spyOn(conversationApi, 'getConversationThreadApi').mockResolvedValue(mockThread);
    const postSpy = vi.spyOn(conversationApi, 'postConversationMessageApi').mockResolvedValue({
      message_id: 'msg-4',
      sales_order_id: 'order-123',
      author_user_id: 'user-current-1',
      message_type: 'COMMENT',
      message_text: 'Newly added remark from Manshi.',
      author_name: 'Manshi Ops',
      author_employee_code: 'CT0002',
      author_department_name: 'Operations Department',
      created_at: new Date().toISOString(),
      formatted_created_at: 'Just now',
      is_mine: true,
    });

    const handleMessagePosted = vi.fn();

    renderWithProviders(
      <TaskConversationModal
        isOpen={true}
        onClose={vi.fn()}
        orderId="order-123"
        onMessagePosted={handleMessagePosted}
      />
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Type an update or remark/)).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(/Type an update or remark/);
    const sendButton = screen.getByRole('button', { name: /Send Remark/i });

    // Type a remark
    fireEvent.change(textarea, { target: { value: 'Newly added remark from Manshi.' } });
    expect(textarea).toHaveValue('Newly added remark from Manshi.');

    // Click Send
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(postSpy).toHaveBeenCalledWith(
        'order-123',
        expect.objectContaining({
          message_text: 'Newly added remark from Manshi.',
        })
      );
      expect(handleMessagePosted).toHaveBeenCalledTimes(1);
    });
  });

  it('preserves draft message if posting fails', async () => {
    vi.spyOn(conversationApi, 'getConversationThreadApi').mockResolvedValue(mockThread);
    vi.spyOn(conversationApi, 'postConversationMessageApi').mockRejectedValue(
      new Error('Network connectivity issue. Please try again.')
    );

    renderWithProviders(
      <TaskConversationModal
        isOpen={true}
        onClose={vi.fn()}
        orderId="order-123"
      />
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Type an update or remark/)).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(/Type an update or remark/);
    const sendButton = screen.getByRole('button', { name: /Send Remark/i });

    fireEvent.change(textarea, { target: { value: 'Draft that should not be lost.' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Network connectivity issue/)).toBeInTheDocument();
      // Textarea draft must still be preserved!
      expect(textarea).toHaveValue('Draft that should not be lost.');
    });
  });

  it('handles pagination with Load Older Messages button', async () => {
    const threadWithMore: ConversationThread = {
      ...mockThread,
      has_more_older: true,
      total_count: 50,
    };

    const getSpy = vi.spyOn(conversationApi, 'getConversationThreadApi').mockResolvedValue(threadWithMore);

    renderWithProviders(
      <TaskConversationModal
        isOpen={true}
        onClose={vi.fn()}
        orderId="order-123"
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Load older messages/i)).toBeInTheDocument();
    });

    const loadMoreButton = screen.getByText(/Load older messages/i);
    fireEvent.click(loadMoreButton);

    await waitFor(() => {
      expect(getSpy).toHaveBeenCalledWith('order-123', expect.objectContaining({ before_id: 'msg-1' }));
    });
  });

  it('disables composer when user lacks posting permission (can_post === false)', async () => {
    const readOnlyThread: ConversationThread = {
      ...mockThread,
      can_post: false,
    };

    vi.spyOn(conversationApi, 'getConversationThreadApi').mockResolvedValue(readOnlyThread);

    renderWithProviders(
      <TaskConversationModal
        isOpen={true}
        onClose={vi.fn()}
        orderId="order-123"
      />
    );

    await waitFor(() => {
      expect(
        screen.getByText(/You have view-only access to this conversation thread/i)
      ).toBeInTheDocument();
      expect(screen.queryByPlaceholderText(/Type an update or remark/)).not.toBeInTheDocument();
    });
  });
});

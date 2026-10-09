/**
 * TypeScript interfaces for Shared Task Conversation, Remarks, and Per-User Read Receipts.
 */

export interface ConversationMessage {
  message_id: string;
  sales_order_id: string;
  author_user_id?: string | null;
  message_type: 'COMMENT' | 'SYSTEM_EVENT';
  message_text: string;
  originating_module?: string | null;
  author_name: string;
  author_employee_code?: string | null;
  author_department_name?: string | null;
  author_role_name?: string | null;
  event_type?: string | null;
  event_metadata?: Record<string, any> | null;
  created_at: string;
  formatted_created_at: string;
  is_mine: boolean;
  is_read?: boolean;
}

export interface ConversationThread {
  order_id: string;
  order_number: string;
  client_name: string;
  service_name: string;
  location?: string | null;
  salesperson_name: string;
  salesperson_code?: string | null;
  current_assignee_id?: string | null;
  current_assignee_name?: string | null;
  current_assignee_code?: string | null;
  application_id?: string | null;
  application_number?: string | null;
  work_status: string;
  payment_status: string;
  gst_invoice_required: boolean;
  company_id?: string | null;
  company_name?: string | null;
  company_code?: string | null;
  can_post: boolean;
  items: ConversationMessage[];
  total_count: number;
  has_more_older: boolean;
}

export interface PostMessagePayload {
  message_text: string;
  originating_module?: string;
  idempotency_key?: string;
}

export interface MarkReadRequest {
  message_ids: string[];
}

export interface MarkReadResponse {
  sales_order_id: string;
  marked_read_count: number;
  read_message_ids: string[];
}

export interface UnreadOrderSummaryItem {
  order_id: string;
  unread_count: number;
  latest_unread_id?: string | null;
  latest_remark_text?: string | null;
  latest_author_name?: string | null;
  latest_author_department?: string | null;
  latest_created_at?: string | null;
  formatted_latest_created_at?: string | null;
}

export interface UnreadSummaryResponse {
  total_unread_count: number;
  unread_orders: Record<string, UnreadOrderSummaryItem>;
}

export interface RemarkNotificationItem {
  message_id: string;
  sales_order_id: string;
  order_number: string;
  client_name: string;
  service_name: string;
  location?: string | null;
  originating_module?: string | null;
  message_text: string;
  author_name: string;
  author_employee_code?: string | null;
  author_department_name?: string | null;
  author_role_name?: string | null;
  created_at: string;
  formatted_created_at: string;
  is_read: boolean;
  target_route: string;
}

export interface RemarkNotificationListResponse {
  items: RemarkNotificationItem[];
  total_count: number;
  unread_count: number;
  page: number;
  limit: number;
  total_pages: number;
}

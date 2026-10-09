/**
 * API client methods for Shared Task Conversation and Remark Notifications.
 */
import { apiClient } from './client';
import type {
  ConversationMessage,
  ConversationThread,
  MarkReadResponse,
  PostMessagePayload,
  RemarkNotificationListResponse,
  UnreadSummaryResponse,
} from '../types/conversation';

/**
 * Retrieve the shared conversation thread for a Sales Order / Compliance Task.
 */
export async function getConversationThreadApi(
  orderId: string,
  params?: { limit?: number; before_id?: string; offset?: number }
): Promise<ConversationThread> {
  const queryParams: Record<string, any> = {};
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.before_id) queryParams.before_id = params.before_id;
  if (params?.offset) queryParams.offset = params.offset;

  const response = await apiClient.get<ConversationThread>(`/conversations/${orderId}`, {
    params: queryParams,
  });
  return response.data;
}

/**
 * Retrieve conversation thread using an Operations application ID.
 */
export async function getTaskConversationByApplicationApi(
  applicationId: string,
  params?: { limit?: number; before_id?: string; offset?: number }
): Promise<ConversationThread> {
  const queryParams: Record<string, any> = {};
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.before_id) queryParams.before_id = params.before_id;
  if (params?.offset) queryParams.offset = params.offset;

  const response = await apiClient.get<ConversationThread>(
    `/operations/tasks/${applicationId}/conversation`,
    { params: queryParams }
  );
  return response.data;
}

/**
 * Post an append-only remark to the shared task conversation.
 */
export async function postConversationMessageApi(
  orderId: string,
  payload: PostMessagePayload
): Promise<ConversationMessage> {
  const response = await apiClient.post<ConversationMessage>(
    `/conversations/${orderId}/messages`,
    payload
  );
  return response.data;
}

/**
 * Post remark using an Operations application ID.
 */
export async function postTaskConversationByApplicationApi(
  applicationId: string,
  payload: PostMessagePayload
): Promise<ConversationMessage> {
  const response = await apiClient.post<ConversationMessage>(
    `/operations/tasks/${applicationId}/conversation`,
    payload
  );
  return response.data;
}

/**
 * Retrieve aggregated unread summary for authenticated user across all authorized tasks.
 */
export async function getUnreadSummaryApi(): Promise<UnreadSummaryResponse> {
  const response = await apiClient.get<UnreadSummaryResponse>('/conversations/unread-summary');
  return response.data;
}

/**
 * Retrieve paginated remark notifications for the notification bell dropdown.
 */
export async function getRemarkNotificationsApi(params?: {
  page?: number;
  limit?: number;
  unread_only?: boolean;
}): Promise<RemarkNotificationListResponse> {
  const queryParams: Record<string, any> = {};
  if (params?.page) queryParams.page = params.page;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.unread_only !== undefined) queryParams.unread_only = params.unread_only;

  const response = await apiClient.get<RemarkNotificationListResponse>('/conversations/notifications', {
    params: queryParams,
  });
  return response.data;
}

/**
 * Explicitly mark displayed message IDs as read for the authenticated user.
 */
export async function markMessagesAsReadApi(
  orderId: string,
  messageIds: string[]
): Promise<MarkReadResponse> {
  const response = await apiClient.post<MarkReadResponse>(`/conversations/${orderId}/mark-read`, {
    message_ids: messageIds,
  });
  return response.data;
}

/** API client for R&D / Internal Tasks. */
import { apiClient } from './client';
import type {
  InternalTask,
  InternalTaskCreatePayload,
  InternalTaskListParams,
  InternalTaskListResponse,
  InternalTaskMessage,
  InternalTaskStatus,
  InternalTaskThread,
  InternalTaskUserRef,
} from '../types/internalTask';

export async function getInternalTasksApi(params: InternalTaskListParams = {}): Promise<InternalTaskListResponse> {
  const query: Record<string, string | boolean> = {};
  if (params.status) query.status = params.status;
  if (params.task_type) query.task_type = params.task_type;
  if (params.search && params.search.trim()) query.search = params.search.trim();
  if (params.mine) query.mine = true;
  const res = await apiClient.get<InternalTaskListResponse>('/internal-tasks', { params: query });
  return res.data;
}

export async function getInternalTaskAssigneesApi(): Promise<InternalTaskUserRef[]> {
  const res = await apiClient.get<InternalTaskUserRef[]>('/internal-tasks/assignees');
  return res.data;
}

export async function createInternalTaskApi(payload: InternalTaskCreatePayload): Promise<InternalTask> {
  const res = await apiClient.post<InternalTask>('/internal-tasks', payload);
  return res.data;
}

export async function updateInternalTaskStatusApi(
  taskId: string,
  status: InternalTaskStatus,
  comment?: string
): Promise<InternalTask> {
  const res = await apiClient.post<InternalTask>(`/internal-tasks/${taskId}/status`, {
    status,
    ...(comment ? { comment } : {}),
  });
  return res.data;
}

export async function reassignInternalTaskApi(
  taskId: string,
  assignedToUserId: string,
  reason?: string
): Promise<InternalTask> {
  const res = await apiClient.post<InternalTask>(`/internal-tasks/${taskId}/reassign`, {
    assigned_to_user_id: assignedToUserId,
    ...(reason ? { reason } : {}),
  });
  return res.data;
}

export async function getInternalTaskThreadApi(taskId: string): Promise<InternalTaskThread> {
  const res = await apiClient.get<InternalTaskThread>(`/internal-tasks/${taskId}/messages`);
  return res.data;
}

export async function postInternalTaskMessageApi(taskId: string, messageText: string): Promise<InternalTaskMessage> {
  const res = await apiClient.post<InternalTaskMessage>(`/internal-tasks/${taskId}/messages`, {
    message_text: messageText,
  });
  return res.data;
}

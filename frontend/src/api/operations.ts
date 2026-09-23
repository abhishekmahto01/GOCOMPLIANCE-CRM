/**
 * API client methods for Operations Dashboard, Tasks, Assignments, Documents, and Status.
 */
import { apiClient } from './client';
import type {
  ApplicationDoc,
  ApplicationDocUpdate,
  ApplicationStatusUpdateRequest,
  AssigneeOption,
  OperationApplicationDetail,
  OperationsDashboardResponse,
  OperationsTaskListResponse,
  TaskAssignRequest,
  TaskReassignRequest,
} from '../types/operations';

export interface OperationsFilterParams {
  page?: number;
  limit?: number;
  status?: string;
  priority?: string;
  search?: string;
  assigned_to_user_id?: string;
  start_date?: string;
  end_date?: string;
  sort_by?: string;
  sort_order?: string;
}

/**
 * Fetch Operations Dashboard aggregated metrics, status breakdown, and executive workload.
 */
export async function getOperationsDashboardApi(): Promise<OperationsDashboardResponse> {
  const response = await apiClient.get<OperationsDashboardResponse>('/operations/dashboard');
  return response.data;
}

/**
 * List all operations tasks scoped to user permissions.
 */
export async function getOperationsTasksApi(
  params?: OperationsFilterParams
): Promise<OperationsTaskListResponse> {
  const queryParams: Record<string, any> = {};
  if (params?.page) queryParams.page = params.page;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.status && params.status !== 'ALL') queryParams.status = params.status;
  if (params?.priority && params.priority !== 'ALL') queryParams.priority = params.priority;
  if (params?.search) queryParams.search = params.search;
  if (params?.assigned_to_user_id && params.assigned_to_user_id !== 'ALL') {
    queryParams.assigned_to_user_id = params.assigned_to_user_id;
  }
  if (params?.start_date) queryParams.start_date = params.start_date;
  if (params?.end_date) queryParams.end_date = params.end_date;
  if (params?.sort_by) queryParams.sort_by = params.sort_by;
  if (params?.sort_order) queryParams.sort_order = params.sort_order;

  const response = await apiClient.get<OperationsTaskListResponse>('/operations/tasks', {
    params: queryParams,
  });
  return response.data;
}

/**
 * List tasks assigned strictly to the logged in employee.
 */
export async function getMyOperationsTasksApi(
  params?: OperationsFilterParams
): Promise<OperationsTaskListResponse> {
  const queryParams: Record<string, any> = {};
  if (params?.page) queryParams.page = params.page;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.status && params.status !== 'ALL') queryParams.status = params.status;
  if (params?.priority && params.priority !== 'ALL') queryParams.priority = params.priority;
  if (params?.search) queryParams.search = params.search;
  if (params?.start_date) queryParams.start_date = params.start_date;
  if (params?.end_date) queryParams.end_date = params.end_date;
  if (params?.sort_by) queryParams.sort_by = params.sort_by;
  if (params?.sort_order) queryParams.sort_order = params.sort_order;

  const response = await apiClient.get<OperationsTaskListResponse>('/operations/tasks/my-tasks', {
    params: queryParams,
  });
  return response.data;
}

/**
 * List unassigned applications awaiting assignment.
 */
export async function getUnassignedOperationsOrdersApi(
  params?: { page?: number; limit?: number; search?: string; sort_by?: string; sort_order?: string }
): Promise<OperationsTaskListResponse> {
  const queryParams: Record<string, any> = {};
  if (params?.page) queryParams.page = params.page;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.search) queryParams.search = params.search;
  if (params?.sort_by) queryParams.sort_by = params.sort_by;
  if (params?.sort_order) queryParams.sort_order = params.sort_order;

  const response = await apiClient.get<OperationsTaskListResponse>('/operations/tasks/unassigned', {
    params: queryParams,
  });
  return response.data;
}

/**
 * Get detailed task information, documents, and audit logs.
 */
export async function getOperationTaskDetailApi(
  applicationId: string
): Promise<OperationApplicationDetail> {
  const response = await apiClient.get<OperationApplicationDetail>(`/operations/tasks/${applicationId}`);
  return response.data;
}

/**
 * Assign task to an operations employee.
 */
export async function assignOperationTaskApi(
  applicationId: string,
  data: TaskAssignRequest
): Promise<OperationApplicationDetail> {
  const response = await apiClient.post<OperationApplicationDetail>(
    `/operations/tasks/${applicationId}/assign`,
    data
  );
  return response.data;
}

/**
 * Reassign task to a different employee with audit reason.
 */
export async function reassignOperationTaskApi(
  applicationId: string,
  data: TaskReassignRequest
): Promise<OperationApplicationDetail> {
  const response = await apiClient.post<OperationApplicationDetail>(
    `/operations/tasks/${applicationId}/reassign`,
    data
  );
  return response.data;
}

/**
 * Transition application lifecycle status.
 */
export async function updateOperationTaskStatusApi(
  applicationId: string,
  data: ApplicationStatusUpdateRequest
): Promise<OperationApplicationDetail> {
  const response = await apiClient.post<OperationApplicationDetail>(
    `/operations/tasks/${applicationId}/status`,
    data
  );
  return response.data;
}

/**
 * Verify or reject document checklist item.
 */
export async function updateApplicationDocStatusApi(
  appDocId: string,
  data: ApplicationDocUpdate
): Promise<ApplicationDoc> {
  const response = await apiClient.post<ApplicationDoc>(
    `/operations/tasks/documents/${appDocId}/status`,
    data
  );
  return response.data;
}

/**
 * List eligible Operations assignees.
 */
export async function getOperationsAssigneesApi(): Promise<AssigneeOption[]> {
  const response = await apiClient.get<AssigneeOption[]>('/operations/assignees');
  return response.data;
}

/**
 * Department Master API client functions.
 */
import { apiClient } from './client';
import type {
  Department,
  DepartmentCreatePayload,
  DepartmentFilterParams,
  DepartmentUpdatePayload,
} from '../types/department';

/**
 * Retrieve list of departments with optional filters.
 */
export async function getDepartmentsApi(params?: DepartmentFilterParams): Promise<Department[]> {
  const query = new URLSearchParams();
  if (params?.company_id) query.append('company_id', params.company_id);
  if (params?.search) query.append('search', params.search);
  if (params?.status && params.status !== 'ALL') query.append('status', params.status);

  const endpoint = `/admin/departments${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await apiClient.get<Department[]>(endpoint);
  return response.data;
}

/**
 * Create a new department master record.
 */
export async function createDepartmentApi(payload: DepartmentCreatePayload): Promise<Department> {
  const response = await apiClient.post<Department>('/admin/departments', payload);
  return response.data;
}

/**
 * Retrieve single department by UUID.
 */
export async function getDepartmentByIdApi(departmentId: string): Promise<Department> {
  const response = await apiClient.get<Department>(`/admin/departments/${departmentId}`);
  return response.data;
}

/**
 * Update an existing department.
 */
export async function updateDepartmentApi(
  departmentId: string,
  payload: DepartmentUpdatePayload
): Promise<Department> {
  const response = await apiClient.patch<Department>(`/admin/departments/${departmentId}`, payload);
  return response.data;
}

/**
 * Delete a department by UUID.
 */
export async function deleteDepartmentApi(departmentId: string): Promise<{ success: boolean; message: string }> {
  const response = await apiClient.delete<{ success: boolean; message: string }>(`/admin/departments/${departmentId}`);
  return response.data;
}

/**
 * Designation Master API client functions.
 */
import { apiClient } from './client';
import type {
  Designation,
  DesignationCreatePayload,
  DesignationFilterParams,
  DesignationUpdatePayload,
} from '../types/designation';

/**
 * Retrieve list of designations with optional filters.
 */
export async function getDesignationsApi(params?: DesignationFilterParams): Promise<Designation[]> {
  const query = new URLSearchParams();
  if (params?.company_id) query.append('company_id', params.company_id);
  if (params?.search) query.append('search', params.search);
  if (params?.status && params.status !== 'ALL') query.append('status', params.status);

  const endpoint = `/admin/designations${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await apiClient.get<Designation[]>(endpoint);
  return response.data;
}

/**
 * Create a new designation master record.
 */
export async function createDesignationApi(payload: DesignationCreatePayload): Promise<Designation> {
  const response = await apiClient.post<Designation>('/admin/designations', payload);
  return response.data;
}

/**
 * Retrieve single designation by UUID.
 */
export async function getDesignationByIdApi(designationId: string): Promise<Designation> {
  const response = await apiClient.get<Designation>(`/admin/designations/${designationId}`);
  return response.data;
}

/**
 * Update an existing designation.
 */
export async function updateDesignationApi(
  designationId: string,
  payload: DesignationUpdatePayload
): Promise<Designation> {
  const response = await apiClient.patch<Designation>(`/admin/designations/${designationId}`, payload);
  return response.data;
}

/**
 * Delete a designation by UUID.
 */
export async function deleteDesignationApi(designationId: string): Promise<{ success: boolean; message: string }> {
  const response = await apiClient.delete<{ success: boolean; message: string }>(`/admin/designations/${designationId}`);
  return response.data;
}

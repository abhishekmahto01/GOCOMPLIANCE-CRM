import { apiClient } from './client';
import {
  CopyPermissionsRequest,
  CopyPermissionsResponse,
  PermissionCatalogResponse,
  UserPermissionsDetailResponse,
  UserPermissionsSaveRequest,
} from '../types/permission';

export async function getPermissionCatalogApi(): Promise<PermissionCatalogResponse> {
  const response = await apiClient.get<PermissionCatalogResponse>('/admin/permission-catalog');
  return response.data;
}

export async function getUserPermissionsApi(userId: string): Promise<UserPermissionsDetailResponse> {
  const response = await apiClient.get<UserPermissionsDetailResponse>(`/admin/users/${userId}/permissions`);
  return response.data;
}

export async function saveUserPermissionsApi(
  userId: string,
  payload: UserPermissionsSaveRequest
): Promise<UserPermissionsDetailResponse> {
  const response = await apiClient.put<UserPermissionsDetailResponse>(
    `/admin/users/${userId}/permissions`,
    payload
  );
  return response.data;
}

export async function copyUserPermissionsApi(
  userId: string,
  payload: CopyPermissionsRequest
): Promise<CopyPermissionsResponse> {
  const response = await apiClient.post<CopyPermissionsResponse>(
    `/admin/users/${userId}/permissions/copy`,
    payload
  );
  return response.data;
}

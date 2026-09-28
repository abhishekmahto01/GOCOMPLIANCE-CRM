import { apiClient } from './client';
import type {
  License,
  LicenseCreatePayload,
  LicenseUpdatePayload,
} from '../types/license';

export interface LicenseFilterParams {
  search?: string;
  category?: string;
  status?: string;
}

export const getLicensesApi = async (
  params?: LicenseFilterParams
): Promise<License[]> => {
  const response = await apiClient.get<License[]>('/admin/licenses', {
    params,
  });
  return response.data;
};

export const getLicenseByIdApi = async (
  licenseId: string
): Promise<License> => {
  const response = await apiClient.get<License>(
    `/admin/licenses/${licenseId}`
  );
  return response.data;
};

export const createLicenseApi = async (
  payload: LicenseCreatePayload
): Promise<License> => {
  const response = await apiClient.post<License>(
    '/admin/licenses',
    payload
  );
  return response.data;
};

export const updateLicenseApi = async (
  licenseId: string,
  payload: LicenseUpdatePayload
): Promise<License> => {
  const response = await apiClient.patch<License>(
    `/admin/licenses/${licenseId}`,
    payload
  );
  return response.data;
};

export const deleteLicenseApi = async (
  licenseId: string
): Promise<{ message: string; license_id: string }> => {
  const response = await apiClient.delete<{ message: string; license_id: string }>(
    `/admin/licenses/${licenseId}`
  );
  return response.data;
};

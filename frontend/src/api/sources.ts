import { apiClient } from './client';
import type {
  SourceMaster,
  SourceCreatePayload,
  SourceUpdatePayload,
  SourceFilterParams,
} from '../types/source';

export const getSourcesApi = async (
  params?: SourceFilterParams
): Promise<SourceMaster[]> => {
  const response = await apiClient.get<SourceMaster[]>('/admin/sources', {
    params,
  });
  return response.data;
};

export const getSourceByIdApi = async (
  sourceId: string
): Promise<SourceMaster> => {
  const response = await apiClient.get<SourceMaster>(
    `/admin/sources/${sourceId}`
  );
  return response.data;
};

export const createSourceApi = async (
  payload: SourceCreatePayload
): Promise<SourceMaster> => {
  const response = await apiClient.post<SourceMaster>(
    '/admin/sources',
    payload
  );
  return response.data;
};

export const updateSourceApi = async (
  sourceId: string,
  payload: SourceUpdatePayload
): Promise<SourceMaster> => {
  const response = await apiClient.put<SourceMaster>(
    `/admin/sources/${sourceId}`,
    payload
  );
  return response.data;
};

export const deleteSourceApi = async (
  sourceId: string
): Promise<{ success: boolean; message: string; deleted_id: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string; deleted_id: string }>(
    `/admin/sources/${sourceId}`
  );
  return response.data;
};


import { apiClient } from './client';
import type {
  Company,
  CompanyCreatePayload,
  CompanyUpdatePayload,
} from '../types/company';

export interface CompanyFilterParams {
  search?: string;
  status?: string;
}

export const getCompaniesApi = async (
  params?: CompanyFilterParams
): Promise<Company[]> => {
  const response = await apiClient.get<Company[]>('/admin/companies', {
    params,
  });
  return response.data;
};

export const getCompanyByIdApi = async (
  companyId: string
): Promise<Company> => {
  const response = await apiClient.get<Company>(
    `/admin/companies/${companyId}`
  );
  return response.data;
};

export const createCompanyApi = async (
  payload: CompanyCreatePayload
): Promise<Company> => {
  const response = await apiClient.post<Company>(
    '/admin/companies',
    payload
  );
  return response.data;
};

export const updateCompanyApi = async (
  companyId: string,
  payload: CompanyUpdatePayload
): Promise<Company> => {
  const response = await apiClient.patch<Company>(
    `/admin/companies/${companyId}`,
    payload
  );
  return response.data;
};

export const deleteCompanyApi = async (
  companyId: string
): Promise<{ message: string; company_id: string }> => {
  const response = await apiClient.delete<{ message: string; company_id: string }>(
    `/admin/companies/${companyId}`
  );
  return response.data;
};

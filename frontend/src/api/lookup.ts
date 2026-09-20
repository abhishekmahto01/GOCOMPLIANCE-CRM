import { apiClient } from './client';
import type {
  CompanyLookup,
  DepartmentLookup,
  DesignationLookup,
  ManagerLookup,
} from '../types/lookup';

export async function getLookupCompaniesApi(): Promise<CompanyLookup[]> {
  const response = await apiClient.get<CompanyLookup[]>('/admin/lookup/companies');
  return response.data;
}

export async function getLookupDepartmentsApi(companyId?: string): Promise<DepartmentLookup[]> {
  const params: Record<string, string> = {};
  if (companyId) params.company_id = companyId;
  const response = await apiClient.get<DepartmentLookup[]>('/admin/lookup/departments', { params });
  return response.data;
}

export async function getLookupDesignationsApi(companyId?: string): Promise<DesignationLookup[]> {
  const params: Record<string, string> = {};
  if (companyId) params.company_id = companyId;
  const response = await apiClient.get<DesignationLookup[]>('/admin/lookup/designations', { params });
  return response.data;
}

export async function getLookupManagersApi(
  companyId?: string,
  excludeUserId?: string
): Promise<ManagerLookup[]> {
  const params: Record<string, string> = {};
  if (companyId) params.company_id = companyId;
  if (excludeUserId) params.exclude_user_id = excludeUserId;
  const response = await apiClient.get<ManagerLookup[]>('/admin/lookup/managers', { params });
  return response.data;
}

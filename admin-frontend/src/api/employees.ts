import { apiClient } from './client';
import {
  Employee,
  EmployeeCreatePayload,
  EmployeeFilterParams,
  EmployeeStatusUpdatePayload,
  EmployeeUpdatePayload,
  PaginatedEmployees,
} from '../types/employee';

export async function getEmployeesApi(
  params: EmployeeFilterParams = {}
): Promise<PaginatedEmployees> {
  const cleanParams: Record<string, string | number> = {};
  if (params.page) cleanParams.page = params.page;
  if (params.page_size) cleanParams.page_size = params.page_size;
  if (params.search && params.search.trim()) cleanParams.search = params.search.trim();
  if (params.company_id) cleanParams.company_id = params.company_id;
  if (params.department_id) cleanParams.department_id = params.department_id;
  if (params.designation_id) cleanParams.designation_id = params.designation_id;
  if (params.manager_user_id) cleanParams.manager_user_id = params.manager_user_id;
  if (params.account_status) cleanParams.account_status = params.account_status;

  const response = await apiClient.get<PaginatedEmployees>('/admin/employees', {
    params: cleanParams,
  });
  return response.data;
}

export async function getEmployeeByIdApi(userId: string): Promise<Employee> {
  const response = await apiClient.get<Employee>(`/admin/employees/${userId}`);
  return response.data;
}

export async function createEmployeeApi(payload: EmployeeCreatePayload): Promise<Employee> {
  const response = await apiClient.post<Employee>('/admin/employees', payload);
  return response.data;
}

export async function updateEmployeeApi(
  userId: string,
  payload: EmployeeUpdatePayload
): Promise<Employee> {
  const response = await apiClient.patch<Employee>(`/admin/employees/${userId}`, payload);
  return response.data;
}

export async function updateEmployeeStatusApi(
  userId: string,
  payload: EmployeeStatusUpdatePayload
): Promise<Employee> {
  const response = await apiClient.patch<Employee>(`/admin/employees/${userId}/status`, payload);
  return response.data;
}

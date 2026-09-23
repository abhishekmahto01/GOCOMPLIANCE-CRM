/**
 * API client methods for Sales Dashboard, Sales Register, Entry Form, and Analytics.
 */
import { apiClient } from './client';
import type {
  SalesDashboardFilterParams,
  SalesDashboardResponse,
  SalesEmployeeOption,
  SalesEntryFormData,
  SalesFormOptionsResponse,
  SalesOrderAssignRequest,
  SalesRegisterFilterParams,
  SalesRegisterItem,
  SalesRegisterResponse,
} from '../types/sales';

/**
 * Fetch Sales Dashboard aggregated metrics, charts, and recent activity.
 */
export async function getSalesDashboardApi(
  params?: SalesDashboardFilterParams
): Promise<SalesDashboardResponse> {
  const queryParams: Record<string, string> = {};
  if (params?.preset) queryParams.preset = params.preset;
  if (params?.from_date) queryParams.from_date = params.from_date;
  if (params?.to_date) queryParams.to_date = params.to_date;
  if (params?.employee_id && params.employee_id !== 'ALL') queryParams.employee_id = params.employee_id;
  if (params?.service_id && params.service_id !== 'ALL') queryParams.service_id = params.service_id;
  if (params?.lead_source && params.lead_source !== 'ALL') queryParams.lead_source = params.lead_source;
  if (params?.payment_status && params.payment_status !== 'ALL') queryParams.payment_status = params.payment_status;

  const response = await apiClient.get<SalesDashboardResponse>('/sales/dashboard', {
    params: queryParams,
  });
  return response.data;
}

/**
 * Export filtered Sales Dashboard to a downloadable CSV file.
 */
export async function exportSalesDashboardCsvApi(
  params?: SalesDashboardFilterParams
): Promise<{ blob: Blob; filename: string }> {
  const queryParams: Record<string, string> = {};
  if (params?.preset) queryParams.preset = params.preset;
  if (params?.from_date) queryParams.from_date = params.from_date;
  if (params?.to_date) queryParams.to_date = params.to_date;
  if (params?.employee_id && params.employee_id !== 'ALL') queryParams.employee_id = params.employee_id;
  if (params?.service_id && params.service_id !== 'ALL') queryParams.service_id = params.service_id;
  if (params?.lead_source && params.lead_source !== 'ALL') queryParams.lead_source = params.lead_source;
  if (params?.payment_status && params.payment_status !== 'ALL') queryParams.payment_status = params.payment_status;

  const response = await apiClient.get('/sales/dashboard/export', {
    params: queryParams,
    responseType: 'blob',
  });

  let filename = `sales_orders_export_${new Date().toISOString().slice(0, 10)}.csv`;
  const disposition = response.headers['content-disposition'];
  if (disposition && disposition.indexOf('filename=') !== -1) {
    const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
    if (matches != null && matches[1]) {
      filename = matches[1].replace(/['"]/g, '');
    }
  }

  return { blob: response.data, filename };
}

/**
 * Fetch Form Options (services, salespersons, existing clients) for New Sales Entry.
 */
export async function getSalesFormOptionsApi(): Promise<SalesFormOptionsResponse> {
  const response = await apiClient.get<SalesFormOptionsResponse>('/sales/form-options');
  return response.data;
}

/**
 * Fetch Sales Register table records (all 20 columns) with pagination, search, and filters.
 */
export async function getSalesRegisterApi(
  params?: SalesRegisterFilterParams
): Promise<SalesRegisterResponse> {
  const queryParams: Record<string, string | number> = {};
  if (params?.page) queryParams.page = params.page;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.search && params.search.trim()) queryParams.search = params.search.trim();
  if (params?.payment_status && params.payment_status !== 'ALL') queryParams.payment_status = params.payment_status;
  if (params?.work_status && params.work_status !== 'ALL') queryParams.work_status = params.work_status;
  if (params?.employee_id && params.employee_id !== 'ALL') queryParams.employee_id = params.employee_id;
  if (params?.service_id && params.service_id !== 'ALL') queryParams.service_id = params.service_id;
  if (params?.lead_source && params.lead_source !== 'ALL') queryParams.lead_source = params.lead_source;
  if (params?.from_date) queryParams.from_date = params.from_date;
  if (params?.to_date) queryParams.to_date = params.to_date;
  if (params?.sort_by) queryParams.sort_by = params.sort_by;
  if (params?.sort_dir) queryParams.sort_dir = params.sort_dir;

  const response = await apiClient.get<SalesRegisterResponse>('/sales/register', {
    params: queryParams,
  });
  return response.data;
}

/**
 * Export full 20-column Sales Register dataset to CSV.
 */
export async function exportSalesRegisterCsvApi(
  params?: SalesRegisterFilterParams
): Promise<{ blob: Blob; filename: string }> {
  const queryParams: Record<string, string | number> = {};
  if (params?.search && params.search.trim()) queryParams.search = params.search.trim();
  if (params?.payment_status && params.payment_status !== 'ALL') queryParams.payment_status = params.payment_status;
  if (params?.work_status && params.work_status !== 'ALL') queryParams.work_status = params.work_status;
  if (params?.employee_id && params.employee_id !== 'ALL') queryParams.employee_id = params.employee_id;
  if (params?.service_id && params.service_id !== 'ALL') queryParams.service_id = params.service_id;
  if (params?.lead_source && params.lead_source !== 'ALL') queryParams.lead_source = params.lead_source;
  if (params?.from_date) queryParams.from_date = params.from_date;
  if (params?.to_date) queryParams.to_date = params.to_date;

  const response = await apiClient.get('/sales/register/export', {
    params: queryParams,
    responseType: 'blob',
  });

  let filename = `sales_register_${new Date().toISOString().slice(0, 10)}.csv`;
  const disposition = response.headers['content-disposition'];
  if (disposition && disposition.indexOf('filename=') !== -1) {
    const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
    if (matches != null && matches[1]) {
      filename = matches[1].replace(/['"]/g, '');
    }
  }

  return { blob: response.data, filename };
}

/**
 * Create a new Sales Entry.
 */
export async function createSalesEntryApi(
  data: SalesEntryFormData
): Promise<SalesRegisterItem> {
  const response = await apiClient.post<SalesRegisterItem>('/sales/orders', data);
  return response.data;
}

/**
 * Fetch a single Sales Order detail by ID.
 */
export async function getSalesOrderDetailApi(
  orderId: string
): Promise<SalesRegisterItem> {
  const response = await apiClient.get<SalesRegisterItem>(`/sales/orders/${orderId}`);
  return response.data;
}

/**
 * Fetch eligible Operations team members for task assignment.
 */
export async function getOperationsAssigneesApi(): Promise<SalesEmployeeOption[]> {
  const response = await apiClient.get<SalesEmployeeOption[]>('/sales/operations-assignees');
  return response.data;
}

/**
 * Assign or reassign an order's Operations application to an Operations team member.
 */
export async function assignSalesOrderApi(
  orderId: string,
  data: SalesOrderAssignRequest
): Promise<SalesRegisterItem> {
  const response = await apiClient.post<SalesRegisterItem>(`/sales/orders/${orderId}/assign`, data);
  return response.data;
}

/**
 * API client methods for Sales Dashboard and Orders.
 */
import { apiClient } from './client';
import type {
  SalesDashboardFilterParams,
  SalesDashboardResponse,
  RecentOrderItem,
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
 * Export filtered Sales Orders to a downloadable CSV file.
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

  // Extract filename from Content-Disposition header if available
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
 * Fetch Sales Orders list with pagination and search.
 */
export async function getSalesOrdersApi(
  limit: number = 50,
  offset: number = 0
): Promise<RecentOrderItem[]> {
  const response = await apiClient.get<RecentOrderItem[]>('/sales/orders', {
    params: { limit, offset },
  });
  return response.data;
}

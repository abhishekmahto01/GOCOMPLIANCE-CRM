/**
 * API client methods for Bulk Sales Import (Excel/CSV) & Bulk Operations Assignment.
 */
import { apiClient } from './client';
import type {
  SalesImportExecuteRequest,
  SalesImportExecuteResponse,
  SalesImportPreviewResponse,
  SalesImportRowValidation,
} from '../types/sales_import';

/**
 * Download official Excel (.xlsx) master import template.
 */
export async function downloadMasterTemplateXlsxApi(): Promise<{ blob: Blob; filename: string }> {
  const response = await apiClient.get('/sales/import/template/xlsx', {
    responseType: 'blob',
  });
  return {
    blob: response.data,
    filename: 'sales_import_master_template.xlsx',
  };
}

/**
 * Download official CSV (.csv) master import template.
 */
export async function downloadMasterTemplateCsvApi(): Promise<{ blob: Blob; filename: string }> {
  const response = await apiClient.get('/sales/import/template/csv', {
    responseType: 'blob',
  });
  return {
    blob: response.data,
    filename: 'sales_import_master_template.csv',
  };
}

/**
 * Upload Excel or CSV file to validate all rows, detect duplicates, and preview records before importing.
 * Pure validation, no database records are created.
 */
export async function previewSalesImportApi(
  file: File,
  applyGst: boolean = false
): Promise<SalesImportPreviewResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const url = applyGst ? '/sales/import/preview?apply_gst=true' : '/sales/import/preview';
  const response = await apiClient.post<SalesImportPreviewResponse>(
    url,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
}

/**
 * Atomically create sales orders and assign them to the selected Operations assignee.
 */
export async function executeBulkImportApi(
  data: SalesImportExecuteRequest
): Promise<SalesImportExecuteResponse> {
  const response = await apiClient.post<SalesImportExecuteResponse>(
    '/sales/import/execute',
    data
  );
  return response.data;
}

/**
 * Download row-by-row validation error report as CSV.
 */
export async function downloadErrorReportApi(
  rows: SalesImportRowValidation[]
): Promise<{ blob: Blob; filename: string }> {
  const response = await apiClient.post('/sales/import/error-report', rows, {
    responseType: 'blob',
  });
  return {
    blob: response.data,
    filename: 'sales_import_validation_errors.csv',
  };
}

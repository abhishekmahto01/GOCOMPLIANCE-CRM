/**
 * Types for Bulk Sales Import, Preview, Validation, and Bulk Assignment.
 */

export interface SalesImportRowValidation {
  row_number: number;
  sl_no?: string | null;
  location?: string | null;
  client_name?: string | null;
  contact?: string | null;
  source?: string | null;
  work?: string | null;
  base_amount?: number | null;
  gst_amount?: number | null;
  gst_rate?: number | null;
  gst_invoice_required?: boolean;
  total_amount?: number | null;
  advance_amount?: number | null;
  incidental_cost?: number | null;
  service_id?: string | null;
  service_name?: string | null;
  is_valid: boolean;
  is_duplicate_in_file: boolean;
  is_duplicate_in_db: boolean;
  errors: string[];
  warnings: string[];
}

export interface SalesImportPreviewResponse {
  filename: string;
  total_rows: number;
  valid_rows_count: number;
  error_rows_count: number;
  duplicate_warnings_count: number;
  can_import: boolean;
  apply_gst?: boolean;
  total_base_amount?: number | null;
  total_gst_amount?: number | null;
  rows: SalesImportRowValidation[];
}

export interface SalesImportExecuteRequest {
  rows: SalesImportRowValidation[];
  assignee_user_id: string;
  idempotency_key?: string | null;
  allow_duplicates?: boolean;
  apply_gst?: boolean;
}

export interface SalesImportExecuteResponse {
  success: boolean;
  imported_count: number;
  assignments_count: number;
  order_numbers: string[];
  message: string;
}

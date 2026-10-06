/**
 * API client functions for the Accounts & Financial Management module.
 */
import { apiClient } from './client';
import type {
  AccountsDashboardResponse,
  AccountsEntriesResponse,
  AccountsEntryItem,
  AccountsEntryUpdatePayload,
  AccountsExpenseApprovalRequest,
  AccountsExpenseCreateRequest,
  AccountsExpenseListResponse,
  AccountsExpenseRead,
  AccountsFilterOptions,
  AccountsFollowUpCreateRequest,
  AccountsFollowUpRead,
  AccountsInvoiceCreateRequest,
  AccountsInvoiceListResponse,
  AccountsInvoiceRead,
  AccountsReimbursementSettleRequest,
  OutstandingResponse,
  PaymentRegisterResponse,
  PaymentTransactionCreateRequest,
  PaymentTransactionListResponse,
  PaymentTransactionRead,
  PaymentTransactionReverseRequest,
  PaymentTransactionVerifyRequest,
} from '../types/accounts';

/**
 * Fetch filtered, paginated Accounts entries showing shared Sales orders across company scope.
 */
export async function getAccountsEntriesApi(params?: {
  page?: number;
  limit?: number;
  search?: string;
  payment_status?: string;
  from_date?: string;
  to_date?: string;
  company_id?: string;
}): Promise<AccountsEntriesResponse> {
  const queryParams: Record<string, any> = {};
  if (params?.page) queryParams.page = params.page;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.search) queryParams.search = params.search;
  if (params?.payment_status && params.payment_status !== 'ALL') queryParams.payment_status = params.payment_status;
  if (params?.from_date) queryParams.from_date = params.from_date;
  if (params?.to_date) queryParams.to_date = params.to_date;
  if (params?.company_id && params.company_id !== 'ALL') queryParams.company_id = params.company_id;

  const response = await apiClient.get<AccountsEntriesResponse>('/accounts/entries', {
    params: queryParams,
  });
  return response.data;
}

/**
 * Update allowed 4 fields (Proforma Inv, Tax Inv, Reimbursement Note, Remarks) on an entry.
 */
export async function updateAccountsEntryApi(
  orderId: string,
  data: AccountsEntryUpdatePayload
): Promise<AccountsEntryItem> {
  const response = await apiClient.patch<AccountsEntryItem>(`/accounts/entries/${orderId}`, data);
  return response.data;
}

/**
 * Export filtered Accounts Entries with all 21 canonical columns to CSV.
 */
export async function exportAccountsEntriesCsvApi(params?: {
  search?: string;
  payment_status?: string;
  from_date?: string;
  to_date?: string;
  company_id?: string;
}): Promise<{ blob: Blob; filename: string }> {
  const queryParams: Record<string, any> = {};
  if (params?.search) queryParams.search = params.search;
  if (params?.payment_status && params.payment_status !== 'ALL') queryParams.payment_status = params.payment_status;
  if (params?.from_date) queryParams.from_date = params.from_date;
  if (params?.to_date) queryParams.to_date = params.to_date;
  if (params?.company_id && params.company_id !== 'ALL') queryParams.company_id = params.company_id;

  const response = await apiClient.get('/accounts/entries/export', {
    params: queryParams,
    responseType: 'blob',
  });

  let filename = `accounts_entries_${new Date().toISOString().slice(0, 10)}.csv`;
  const disposition = response.headers['content-disposition'];
  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename="?([^"]+)"?/);
    if (match && match[1]) {
      filename = match[1];
    }
  }

  return { blob: response.data, filename };
}

/**
 * Fetch dynamic filter dropdown options (companies, salespersons, payment statuses, etc.)
 */
export async function getAccountsFilterOptionsApi(): Promise<AccountsFilterOptions> {
  const response = await apiClient.get<AccountsFilterOptions>('/accounts/filter-options');
  return response.data;
}

/**
 * Fetch Accounts Dashboard analytics, KPIs, trends, and ageing breakdown.
 */
export async function getAccountsDashboardApi(params?: {
  preset?: string;
  from_date?: string;
  to_date?: string;
  company_id?: string;
  employee_id?: string;
}): Promise<AccountsDashboardResponse> {
  const queryParams: Record<string, string> = {};
  if (params?.preset) queryParams.preset = params.preset;
  if (params?.from_date) queryParams.from_date = params.from_date;
  if (params?.to_date) queryParams.to_date = params.to_date;
  if (params?.company_id && params.company_id !== 'ALL') queryParams.company_id = params.company_id;
  if (params?.employee_id && params.employee_id !== 'ALL') queryParams.employee_id = params.employee_id;

  const response = await apiClient.get<AccountsDashboardResponse>('/accounts/dashboard', {
    params: queryParams,
  });
  return response.data;
}

/**
 * List Payment Register ledger rows with pagination and filters.
 */
export async function getPaymentRegisterApi(params?: {
  page?: number;
  limit?: number;
  search?: string;
  company_id?: string;
  employee_id?: string;
  payment_status?: string;
  overdue_only?: boolean;
  from_date?: string;
  to_date?: string;
  sort_by?: string;
  sort_order?: string;
}): Promise<PaymentRegisterResponse> {
  const queryParams: Record<string, any> = {};
  if (params?.page) queryParams.page = params.page;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.search) queryParams.search = params.search;
  if (params?.company_id && params.company_id !== 'ALL') queryParams.company_id = params.company_id;
  if (params?.employee_id && params.employee_id !== 'ALL') queryParams.employee_id = params.employee_id;
  if (params?.payment_status && params.payment_status !== 'ALL') queryParams.payment_status = params.payment_status;
  if (params?.overdue_only) queryParams.overdue_only = params.overdue_only;
  if (params?.from_date) queryParams.from_date = params.from_date;
  if (params?.to_date) queryParams.to_date = params.to_date;
  if (params?.sort_by) queryParams.sort_by = params.sort_by;
  if (params?.sort_order) queryParams.sort_order = params.sort_order;

  const response = await apiClient.get<PaymentRegisterResponse>('/accounts/payments', {
    params: queryParams,
  });
  return response.data;
}

/**
 * Record a payment / collection installment against a Sales Order.
 */
export async function recordPaymentApi(data: PaymentTransactionCreateRequest): Promise<PaymentTransactionRead> {
  const response = await apiClient.post<PaymentTransactionRead>('/accounts/payments', data);
  return response.data;
}

/**
 * Authorize and verify a submitted payment transaction.
 */
export async function verifyPaymentApi(
  paymentId: string,
  data: PaymentTransactionVerifyRequest
): Promise<PaymentTransactionRead> {
  const response = await apiClient.post<PaymentTransactionRead>(`/accounts/payments/${paymentId}/verify`, data);
  return response.data;
}

/**
 * Reverse a verified payment with mandatory explanation.
 */
export async function reversePaymentApi(
  paymentId: string,
  data: PaymentTransactionReverseRequest
): Promise<PaymentTransactionRead> {
  const response = await apiClient.post<PaymentTransactionRead>(`/accounts/payments/${paymentId}/reverse`, data);
  return response.data;
}

/**
 * Fetch all payments, installments, and reversals for a specific Sales Order.
 */
export async function getOrderPaymentHistoryApi(orderId: string): Promise<PaymentTransactionListResponse> {
  const response = await apiClient.get<PaymentTransactionListResponse>(`/accounts/orders/${orderId}/payments`);
  return response.data;
}

/**
 * List Outstanding Receivables and Ageing debtor tracking.
 */
export async function getOutstandingAccountsApi(params?: {
  page?: number;
  limit?: number;
  search?: string;
  company_id?: string;
  employee_id?: string;
  ageing_bucket?: string;
  operations_completed_only?: boolean;
  sort_by?: string;
  sort_order?: string;
}): Promise<OutstandingResponse> {
  const queryParams: Record<string, any> = {};
  if (params?.page) queryParams.page = params.page;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.search) queryParams.search = params.search;
  if (params?.company_id && params.company_id !== 'ALL') queryParams.company_id = params.company_id;
  if (params?.employee_id && params.employee_id !== 'ALL') queryParams.employee_id = params.employee_id;
  if (params?.ageing_bucket && params.ageing_bucket !== 'ALL') queryParams.ageing_bucket = params.ageing_bucket;
  if (params?.operations_completed_only) queryParams.operations_completed_only = params.operations_completed_only;
  if (params?.sort_by) queryParams.sort_by = params.sort_by;
  if (params?.sort_order) queryParams.sort_order = params.sort_order;

  const response = await apiClient.get<OutstandingResponse>('/accounts/outstanding', {
    params: queryParams,
  });
  return response.data;
}

/**
 * Record a follow-up action/promise on an outstanding debtor order.
 */
export async function recordOrderFollowUpApi(
  orderId: string,
  data: AccountsFollowUpCreateRequest
): Promise<AccountsFollowUpRead> {
  const response = await apiClient.post<AccountsFollowUpRead>(`/accounts/orders/${orderId}/follow-up`, data);
  return response.data;
}

/**
 * Get follow-up timeline for an order.
 */
export async function getOrderFollowUpsApi(orderId: string): Promise<AccountsFollowUpRead[]> {
  const response = await apiClient.get<AccountsFollowUpRead[]>(`/accounts/orders/${orderId}/follow-ups`);
  return response.data;
}

/**
 * List Invoices (Proforma & Tax Invoices).
 */
export async function getInvoicesListApi(params?: {
  page?: number;
  limit?: number;
  search?: string;
  company_id?: string;
  order_id?: string;
  invoice_type?: string;
  missing_only?: boolean;
  from_date?: string;
  to_date?: string;
  sort_by?: string;
  sort_order?: string;
}): Promise<AccountsInvoiceListResponse> {
  const queryParams: Record<string, any> = {};
  if (params?.page) queryParams.page = params.page;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.search) queryParams.search = params.search;
  if (params?.company_id && params.company_id !== 'ALL') queryParams.company_id = params.company_id;
  if (params?.order_id) queryParams.order_id = params.order_id;
  if (params?.invoice_type && params.invoice_type !== 'ALL') queryParams.invoice_type = params.invoice_type;
  if (params?.missing_only) queryParams.missing_only = params.missing_only;
  if (params?.from_date) queryParams.from_date = params.from_date;
  if (params?.to_date) queryParams.to_date = params.to_date;
  if (params?.sort_by) queryParams.sort_by = params.sort_by;
  if (params?.sort_order) queryParams.sort_order = params.sort_order;

  const response = await apiClient.get<AccountsInvoiceListResponse>('/accounts/invoices', {
    params: queryParams,
  });
  return response.data;
}

/**
 * Create or link an invoice to a Sales Order.
 */
export async function createInvoiceApi(data: AccountsInvoiceCreateRequest): Promise<AccountsInvoiceRead> {
  const response = await apiClient.post<AccountsInvoiceRead>('/accounts/invoices', data);
  return response.data;
}

/**
 * List Direct Expenses and Reimbursements.
 */
export async function getExpensesListApi(params?: {
  page?: number;
  limit?: number;
  search?: string;
  company_id?: string;
  order_id?: string;
  category?: string;
  paid_by_type?: string;
  approval_status?: string;
  settlement_status?: string;
  from_date?: string;
  to_date?: string;
  sort_by?: string;
  sort_order?: string;
}): Promise<AccountsExpenseListResponse> {
  const queryParams: Record<string, any> = {};
  if (params?.page) queryParams.page = params.page;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.search) queryParams.search = params.search;
  if (params?.company_id && params.company_id !== 'ALL') queryParams.company_id = params.company_id;
  if (params?.order_id) queryParams.order_id = params.order_id;
  if (params?.category && params.category !== 'ALL') queryParams.category = params.category;
  if (params?.paid_by_type && params.paid_by_type !== 'ALL') queryParams.paid_by_type = params.paid_by_type;
  if (params?.approval_status && params.approval_status !== 'ALL') queryParams.approval_status = params.approval_status;
  if (params?.settlement_status && params.settlement_status !== 'ALL') queryParams.settlement_status = params.settlement_status;
  if (params?.from_date) queryParams.from_date = params.from_date;
  if (params?.to_date) queryParams.to_date = params.to_date;
  if (params?.sort_by) queryParams.sort_by = params.sort_by;
  if (params?.sort_order) queryParams.sort_order = params.sort_order;

  const response = await apiClient.get<AccountsExpenseListResponse>('/accounts/expenses', {
    params: queryParams,
  });
  return response.data;
}

/**
 * Record an order expense or reimbursement claim.
 */
export async function recordExpenseApi(data: AccountsExpenseCreateRequest): Promise<AccountsExpenseRead> {
  const response = await apiClient.post<AccountsExpenseRead>('/accounts/expenses', data);
  return response.data;
}

/**
 * Approve or reject an expense entry.
 */
export async function approveExpenseApi(
  expenseId: string,
  data: AccountsExpenseApprovalRequest
): Promise<AccountsExpenseRead> {
  const response = await apiClient.post<AccountsExpenseRead>(`/accounts/expenses/${expenseId}/approve`, data);
  return response.data;
}

/**
 * Settle an employee reimbursement.
 */
export async function settleReimbursementApi(
  expenseId: string,
  data: AccountsReimbursementSettleRequest
): Promise<AccountsExpenseRead> {
  const response = await apiClient.post<AccountsExpenseRead>(`/accounts/expenses/${expenseId}/settle`, data);
  return response.data;
}

/**
 * Export filtered accounts reports to CSV with formula injection protection.
 */
export async function exportAccountsReportApi(params: {
  report_type: 'payments' | 'outstanding' | 'expenses' | 'client_statement';
  company_id?: string;
  employee_id?: string;
  client_name?: string;
  payment_status?: string;
  category?: string;
  from_date?: string;
  to_date?: string;
}): Promise<{ blob: Blob; filename: string }> {
  const queryParams: Record<string, any> = { report_type: params.report_type };
  if (params.company_id && params.company_id !== 'ALL') queryParams.company_id = params.company_id;
  if (params.employee_id && params.employee_id !== 'ALL') queryParams.employee_id = params.employee_id;
  if (params.client_name) queryParams.client_name = params.client_name;
  if (params.payment_status && params.payment_status !== 'ALL') queryParams.payment_status = params.payment_status;
  if (params.category && params.category !== 'ALL') queryParams.category = params.category;
  if (params.from_date) queryParams.from_date = params.from_date;
  if (params.to_date) queryParams.to_date = params.to_date;

  const response = await apiClient.get('/accounts/reports/export', {
    params: queryParams,
    responseType: 'blob',
  });

  let filename = `${params.report_type}_export_${new Date().toISOString().slice(0, 10)}.csv`;
  const disposition = response.headers['content-disposition'];
  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename="?([^"]+)"?/);
    if (match && match[1]) {
      filename = match[1];
    }
  }

  return { blob: response.data, filename };
}

/**
 * Upload a supporting document (proof receipt, invoice, expense challan).
 */
export async function uploadAccountsAttachmentApi(
  file: File,
  subfolder: 'payments' | 'invoices' | 'expenses' = 'payments'
): Promise<{ file_path: string; filename: string; size: number }> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<{ file_path: string; filename: string; size: number }>(
    `/accounts/upload-attachment?subfolder=${subfolder}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
}

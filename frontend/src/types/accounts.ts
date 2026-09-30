/**
 * TypeScript definitions for the Accounts & Financial Management Module.
 */

export interface AccountsFilterOptionItem {
  id: string;
  label: string;
}

export interface AccountsFilterOptions {
  companies: AccountsFilterOptionItem[];
  clients: AccountsFilterOptionItem[];
  salespersons: AccountsFilterOptionItem[];
  payment_statuses: AccountsFilterOptionItem[];
  payment_modes: AccountsFilterOptionItem[];
  expense_categories: AccountsFilterOptionItem[];
  receiving_accounts: string[];
}

export interface AccountsKpiSummary {
  confirmed_order_value: number;
  formatted_confirmed_order_value: string;
  confirmed_order_count: number;
  verified_collections: number;
  formatted_verified_collections: string;
  verified_collections_count: number;
  unverified_collections: number;
  formatted_unverified_collections: string;
  unverified_collections_count: number;
  current_outstanding: number;
  formatted_current_outstanding: string;
  outstanding_orders_count: number;
  current_overdue: number;
  formatted_current_overdue: string;
  overdue_orders_count: number;
  recorded_direct_costs: number;
  formatted_recorded_direct_costs: string;
  estimated_order_margin: number;
  formatted_estimated_order_margin: string;
  margin_percentage: number;
}

export interface CollectionsTrendPoint {
  date: string;
  label: string;
  verified_amount: number;
  order_count: number;
}

export interface AgeingBreakdownItem {
  bucket: string;
  label: string;
  amount: number;
  count: number;
  percentage: number;
  color: string;
}

export interface CompanyFinancialItem {
  company_id: string;
  company_name: string;
  order_value: number;
  verified_received: number;
  outstanding: number;
  collection_rate: number;
}

export interface CategoryExpenseItem {
  category: string;
  label: string;
  amount: number;
  percentage: number;
  count: number;
}

export interface RecentTransactionItem {
  payment_id: string;
  payment_number: string;
  sales_order_number: string;
  client_name: string;
  amount: number;
  formatted_amount: string;
  payment_date: string;
  payment_mode: string;
  verification_status: string;
}

export interface TopOutstandingItem {
  sales_order_id: string;
  order_number: string;
  client_name: string;
  service_name: string;
  salesperson_name: string;
  total_payable: number;
  verified_received: number;
  pending_amount: number;
  formatted_pending_amount: string;
  days_overdue: number;
  operation_status?: string | null;
}

export interface AccountsDashboardResponse {
  date_range: Record<string, string>;
  kpis: AccountsKpiSummary;
  collections_trend: CollectionsTrendPoint[];
  ageing_breakdown: AgeingBreakdownItem[];
  company_breakdown: CompanyFinancialItem[];
  expense_breakdown: CategoryExpenseItem[];
  recent_transactions: RecentTransactionItem[];
  top_outstanding: TopOutstandingItem[];
  filter_options: AccountsFilterOptions;
}

export interface PaymentTransactionRead {
  payment_id: string;
  company_id: string;
  company_name?: string | null;
  sales_order_id: string;
  sales_order_number?: string | null;
  client_id?: string | null;
  client_name?: string | null;
  payment_number: string;
  amount: number;
  formatted_amount: string;
  payment_date: string;
  formatted_payment_date: string;
  payment_mode: string;
  transaction_reference?: string | null;
  receiving_account?: string | null;
  proof_attachment_path?: string | null;
  proof_attachment_name?: string | null;
  remark?: string | null;
  submitted_by_user_id: string;
  submitted_by_name?: string | null;
  submitted_at: string;
  formatted_submitted_at?: string | null;
  verification_status: 'VERIFIED' | 'UNVERIFIED' | 'REJECTED' | 'REVERSED';
  verified_by_user_id?: string | null;
  verified_by_name?: string | null;
  verified_at?: string | null;
  formatted_verified_at?: string | null;
  reversal_reason?: string | null;
  reversed_by_user_id?: string | null;
  reversed_by_name?: string | null;
  reversed_at?: string | null;
  is_opening_balance: boolean;
  created_at: string;
}

export interface PaymentTransactionListResponse {
  items: PaymentTransactionRead[];
  total_count: number;
  total_verified_amount: number;
  total_unverified_amount: number;
}

export interface PaymentRegisterItemRead {
  sales_order_id: string;
  order_number: string;
  order_date: string;
  formatted_order_date: string;
  company_id: string;
  company_name: string;
  client_id: string;
  client_name: string;
  client_phone?: string | null;
  location?: string | null;
  service_id: string;
  service_name: string;
  service_code?: string | null;
  salesperson_user_id: string;
  salesperson_name: string;
  salesperson_code?: string | null;
  total_payable: number;
  formatted_total_payable: string;
  verified_received: number;
  formatted_verified_received: string;
  unverified_amount: number;
  formatted_unverified_amount: string;
  pending_amount: number;
  formatted_pending_amount: string;
  payment_status: 'FULLY_PAID' | 'PARTIALLY_PAID' | 'PENDING' | 'OVERDUE';
  due_date?: string | null;
  formatted_due_date?: string | null;
  is_overdue: boolean;
  days_overdue: number;
  proforma_invoice_no?: string | null;
  tax_invoice_no?: string | null;
  govt_fees: number;
  incidental_cost: number;
  profit_amount: number;
  operation_status?: string | null;
  latest_remark?: string | null;
  latest_remark_date?: string | null;
  latest_remark_author?: string | null;
  payment_count: number;
  unverified_payment_count: number;
}

export interface PaymentRegisterSummary {
  total_orders: number;
  total_payable: number;
  total_verified_received: number;
  total_unverified_amount: number;
  total_pending: number;
  fully_paid_count: number;
  partially_paid_count: number;
  pending_count: number;
  overdue_count: number;
  formatted_total_payable: string;
  formatted_total_verified_received: string;
  formatted_total_unverified_amount: string;
  formatted_total_pending: string;
}

export interface PaymentRegisterResponse {
  items: PaymentRegisterItemRead[];
  summary: PaymentRegisterSummary;
  total_count: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface AccountsFollowUpRead {
  follow_up_id: string;
  sales_order_id: string;
  company_id: string;
  follow_up_date: string;
  formatted_follow_up_date: string;
  next_follow_up_date?: string | null;
  formatted_next_follow_up_date?: string | null;
  contact_channel: string;
  contact_person?: string | null;
  remark_text: string;
  created_by_user_id: string;
  created_by_name?: string | null;
  created_at: string;
  formatted_created_at?: string | null;
}

export interface OutstandingItemRead {
  sales_order_id: string;
  order_number: string;
  order_date: string;
  formatted_order_date: string;
  company_id: string;
  company_name: string;
  client_id: string;
  client_name: string;
  client_phone?: string | null;
  client_email?: string | null;
  location?: string | null;
  service_id: string;
  service_name: string;
  salesperson_name: string;
  salesperson_code?: string | null;
  total_payable: number;
  formatted_total_payable: string;
  verified_received: number;
  formatted_verified_received: string;
  pending_amount: number;
  formatted_pending_amount: string;
  due_date?: string | null;
  formatted_due_date?: string | null;
  days_overdue: number;
  ageing_bucket: 'CURRENT' | '1_30_DAYS' | '31_60_DAYS' | '61_90_DAYS' | 'OVER_90_DAYS' | 'NO_DUE_DATE';
  operation_status?: string | null;
  is_work_completed: boolean;
  latest_follow_up?: AccountsFollowUpRead | null;
  follow_up_count: number;
}

export interface OutstandingAgeingSummary {
  total_outstanding_amount: number;
  formatted_total_outstanding: string;
  total_overdue_amount: number;
  formatted_total_overdue: string;
  total_debtors_count: number;
  current_amount: number;
  current_count: number;
  days_1_30_amount: number;
  days_1_30_count: number;
  days_31_60_amount: number;
  days_31_60_count: number;
  days_61_90_amount: number;
  days_61_90_count: number;
  over_90_days_amount: number;
  over_90_days_count: number;
  no_due_date_amount: number;
  no_due_date_count: number;
  completed_work_pending_amount: number;
  completed_work_pending_count: number;
}

export interface OutstandingResponse {
  items: OutstandingItemRead[];
  summary: OutstandingAgeingSummary;
  total_count: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface AccountsInvoiceRead {
  invoice_id: string;
  company_id: string;
  company_name?: string | null;
  sales_order_id: string;
  sales_order_number?: string | null;
  client_id?: string | null;
  client_name?: string | null;
  service_name?: string | null;
  invoice_type: 'PROFORMA' | 'TAX_INVOICE';
  invoice_number: string;
  invoice_date: string;
  formatted_invoice_date: string;
  due_date?: string | null;
  formatted_due_date?: string | null;
  amount: number;
  formatted_amount: string;
  taxable_amount?: number | null;
  cgst_amount?: number | null;
  sgst_amount?: number | null;
  igst_amount?: number | null;
  status: string;
  file_path?: string | null;
  file_name?: string | null;
  notes?: string | null;
  created_by_user_id: string;
  created_by_name?: string | null;
  created_at: string;
}

export interface AccountsInvoiceListResponse {
  items: AccountsInvoiceRead[];
  total_count: number;
  total_proforma_count: number;
  total_tax_invoice_count: number;
  total_invoiced_amount: number;
  orders_without_invoice_count: number;
}

export interface AccountsExpenseRead {
  expense_id: string;
  company_id: string;
  company_name?: string | null;
  sales_order_id?: string | null;
  sales_order_number?: string | null;
  client_name?: string | null;
  expense_number: string;
  category: 'GOVT_FEES' | 'VENDOR_COST' | 'INCIDENTAL_COST' | 'EMPLOYEE_REIMBURSEMENT' | 'OTHER_DIRECT_COST';
  amount: number;
  formatted_amount: string;
  expense_date: string;
  formatted_expense_date: string;
  payee_name: string;
  paid_by_type: 'COMPANY' | 'EMPLOYEE' | 'CLIENT';
  paid_by_user_id?: string | null;
  paid_by_user_name?: string | null;
  payment_mode: string;
  transaction_reference?: string | null;
  bill_attachment_path?: string | null;
  bill_attachment_name?: string | null;
  remark?: string | null;
  approval_status: 'PENDING' | 'APPROVED' | 'REJECTED';
  approved_by_user_id?: string | null;
  approved_by_name?: string | null;
  approved_at?: string | null;
  rejection_reason?: string | null;
  settlement_status: 'UNSETTLED' | 'SETTLED';
  settled_at?: string | null;
  settled_by_user_id?: string | null;
  settled_by_name?: string | null;
  settlement_reference?: string | null;
  created_by_user_id: string;
  created_by_name?: string | null;
  created_at: string;
}

export interface AccountsExpenseListResponse {
  items: AccountsExpenseRead[];
  total_count: number;
  total_approved_expenses: number;
  total_pending_approval: number;
  total_pending_reimbursements: number;
  total_settled_reimbursements: number;
}

// Request Payload Types
export interface PaymentTransactionCreateRequest {
  sales_order_id: string;
  amount: number;
  payment_date: string;
  payment_mode: string;
  transaction_reference?: string;
  receiving_account?: string;
  remark?: string;
  auto_verify?: boolean;
}

export interface PaymentTransactionVerifyRequest {
  action: 'VERIFY' | 'REJECT';
  rejection_reason?: string;
}

export interface PaymentTransactionReverseRequest {
  reversal_reason: string;
}

export interface AccountsFollowUpCreateRequest {
  follow_up_date?: string;
  next_follow_up_date?: string;
  contact_channel?: string;
  contact_person?: string;
  remark_text: string;
}

export interface AccountsInvoiceCreateRequest {
  sales_order_id: string;
  invoice_type: 'PROFORMA' | 'TAX_INVOICE';
  invoice_number: string;
  invoice_date?: string;
  due_date?: string;
  amount: number;
  taxable_amount?: number;
  cgst_amount?: number;
  sgst_amount?: number;
  igst_amount?: number;
  notes?: string;
}

export interface AccountsExpenseCreateRequest {
  sales_order_id?: string;
  category: 'GOVT_FEES' | 'VENDOR_COST' | 'INCIDENTAL_COST' | 'EMPLOYEE_REIMBURSEMENT' | 'OTHER_DIRECT_COST';
  amount: number;
  expense_date?: string;
  payee_name: string;
  paid_by_type?: 'COMPANY' | 'EMPLOYEE';
  paid_by_user_id?: string;
  payment_mode?: string;
  transaction_reference?: string;
  remark?: string;
}

export interface AccountsExpenseApprovalRequest {
  action: 'APPROVE' | 'REJECT';
  rejection_reason?: string;
}

export interface AccountsReimbursementSettleRequest {
  settlement_reference?: string;
}

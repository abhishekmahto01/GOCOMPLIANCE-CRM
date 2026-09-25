/**
 * TypeScript definitions for Sales Dashboard, Entry Form, Sales Register, and KPIs.
 */

export interface KpiMetric {
  value: number;
  formatted_value: string;
  previous_value: number;
  percentage_change: number;
  is_positive: boolean;
  comparison_label: string;
}

export interface SalesKpiSummary {
  total_sales: KpiMetric;
  confirmed_orders: KpiMetric;
  amount_received: KpiMetric;
  outstanding: KpiMetric;
  avg_order_value: KpiMetric;
  total_clients: KpiMetric;
}

export interface SalesTrendPoint {
  date: string;
  label: string;
  sales_value: number;
  order_count: number;
}

export interface PaymentStatusItem {
  status: string;
  label: string;
  count: number;
  percentage: number;
  amount: number;
}

export interface PaymentStatusBreakdown {
  total_orders: number;
  items: PaymentStatusItem[];
}

export interface ServiceSalesItem {
  service_id: string;
  service_code: string;
  service_name: string;
  total_sales: number;
  order_count: number;
}

export interface LeadSourceItem {
  source: string;
  label: string;
  count: number;
  percentage: number;
}

export interface LeadSourcesBreakdown {
  total_leads: number;
  items: LeadSourceItem[];
}

export interface TeamPerformanceRow {
  salesperson_id: string;
  salesperson_name: string;
  employee_code: string;
  orders_count: number;
  total_sales: number;
  amount_received: number;
  outstanding: number;
}

export interface RecentOrderItem {
  order_id: string;
  order_number: string;
  order_date: string;
  formatted_date: string;
  client_name: string;
  service_name: string;
  salesperson_name: string;
  order_value: number;
  amount_received: number;
  balance_amount: number;
  payment_status: 'FULLY_PAID' | 'PARTIALLY_PAID' | 'PENDING' | 'OVERDUE' | string;
  operation_status: 'UNASSIGNED' | 'ASSIGNED' | 'DOCUMENT_VERIFICATION' | 'IN_PROGRESS' | 'COMPLETED' | 'REJECTED' | 'PENDING' | string;
  confirmation_status: 'DRAFT' | 'CONFIRMED' | 'CANCELLED' | string;
}

export interface FilterOptionItem {
  id: string;
  label: string;
}

export interface SalesFilterOptions {
  employees: FilterOptionItem[];
  services: FilterOptionItem[];
  lead_sources: FilterOptionItem[];
  payment_statuses: FilterOptionItem[];
  can_filter_employees: boolean;
  default_employee_id?: string | null;
}

export interface SalesDashboardResponse {
  date_range: {
    preset: string;
    from_date: string;
    to_date: string;
    formatted_from: string;
    formatted_to: string;
    comparison_label: string;
  };
  kpis: SalesKpiSummary;
  sales_trend: SalesTrendPoint[];
  payment_status: PaymentStatusBreakdown;
  service_sales: ServiceSalesItem[];
  lead_sources: LeadSourcesBreakdown;
  team_performance: TeamPerformanceRow[];
  recent_orders: RecentOrderItem[];
  filter_options: SalesFilterOptions;
}

export interface SalesDashboardFilterParams {
  preset?: string;
  from_date?: string;
  to_date?: string;
  employee_id?: string;
  service_id?: string;
  lead_source?: string;
  payment_status?: string;
}

/**
 * 20 Columns in exact director-specified order for the Sales Register.
 */
export interface SalesRegisterItem {
  // 1. S.No
  s_no: number;
  // 2. Date
  order_date: string;
  formatted_date?: string;
  // 3. Client Name
  client_name: string;
  // 4. Contact No
  contact_no?: string;
  // 5. Source
  lead_source: string;
  // 6. Work
  service_name: string;
  service_code?: string;
  // 7. Converted By
  salesperson_name: string;
  salesperson_code?: string;
  // 8. Assigned To
  assigned_to_name?: string;
  assigned_to_code?: string;
  assigned_to_user_id?: string | null;
  // 9. Work Status
  work_status: string;
  // 10. Total Amount
  order_value: number;
  // 11. Advance Amount
  amount_received: number;
  // 12. Pending Amount
  balance_amount: number;
  // 13. Payment Status
  payment_status: 'FULLY_PAID' | 'PARTIALLY_PAID' | 'PENDING' | 'OVERDUE' | string;
  // 14. Proforma Invoice No.
  proforma_invoice_no?: string | null;
  // 15. Tax Invoice No.
  tax_invoice_no?: string | null;
  // 16. Reimbursement Note
  reimbursement_note?: string | null;
  // 17. Govt Fees
  govt_fees: number;
  // 18. Incidental Cost
  incidental_cost: number;
  // 19. Profits
  profit_amount: number;
  // 20. Remarks
  notes?: string | null;
  remarks?: string | null;

  // Metadata
  order_id: string;
  order_number: string;
  company_id: string;
  client_id: string;
  service_id: string;
  salesperson_user_id: string;
  confirmation_status: string;
  confirmed_at?: string | null;
  application_id?: string | null;
  application_number?: string | null;
  operation_status?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface SalesRegisterSummary {
  total_orders: number;
  total_sales: number;
  total_advance: number;
  total_pending: number;
  total_govt_fees: number;
  total_incidental_cost: number;
  total_profits: number;
  formatted_total_sales: string;
  formatted_total_advance: string;
  formatted_total_pending: string;
  formatted_total_govt_fees: string;
  formatted_total_incidental_cost: string;
  formatted_total_profits: string;
}

export interface SalesRegisterResponse {
  items: SalesRegisterItem[];
  total_count: number;
  page: number;
  limit: number;
  total_pages: number;
  summary: SalesRegisterSummary;
}

export interface SalesRegisterFilterParams {
  page?: number;
  limit?: number;
  search?: string;
  payment_status?: string;
  work_status?: string;
  employee_id?: string;
  service_id?: string;
  lead_source?: string;
  from_date?: string;
  to_date?: string;
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
}

export interface SalesServiceOption {
  service_id: string;
  service_code: string;
  service_name: string;
  category: string;
  base_price: number;
  govt_fee: number;
}

export interface SalesEmployeeOption {
  user_id: string;
  employee_code: string;
  full_name: string;
  department_name?: string | null;
  designation_name?: string | null;
}

export interface SalesClientOption {
  client_id: string;
  client_name: string;
  contact_phone: string;
  contact_email?: string | null;
  contact_person?: string | null;
  entity_type?: string | null;
}

export interface SalesFormOptionsResponse {
  services: SalesServiceOption[];
  salespersons: SalesEmployeeOption[];
  clients: SalesClientOption[];
  lead_sources: string[];
  operations_assignees?: SalesEmployeeOption[];
  default_salesperson_id?: string | null;
  can_select_salesperson: boolean;
  company_id: string;
  company_name: string;
}

export interface SalesOrderAssignRequest {
  assignee_user_id: string;
  priority?: string;
  target_due_date?: string;
  notes?: string;
}

export interface SalesEntryFormData {
  order_date: string;
  client_id?: string;
  client_name?: string;
  contact_no?: string;
  service_id: string;
  salesperson_user_id?: string;
  lead_source: string;
  order_value: number;
  amount_received: number;
  govt_fees: number;
  incidental_cost: number;
  payment_status?: string;
  proforma_invoice_no?: string;
  tax_invoice_no?: string;
  reimbursement_note?: string;
  notes?: string;
  auto_confirm?: boolean;
}

export interface SalesOrderUpdateRequest {
  order_value?: number;
  amount_received?: number;
  govt_fees?: number;
  incidental_cost?: number;
  payment_status?: string;
  lead_source?: string;
  order_date?: string;
  salesperson_user_id?: string;
  proforma_invoice_no?: string;
  tax_invoice_no?: string;
  reimbursement_note?: string;
  notes?: string;
  client_name?: string;
  contact_no?: string;
}


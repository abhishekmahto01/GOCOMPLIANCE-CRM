/**
 * TypeScript definitions for Sales Dashboard, KPIs, charts, and orders.
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

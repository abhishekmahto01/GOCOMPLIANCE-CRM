import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { SalesDashboardPage } from '../pages/SalesDashboardPage';
import { SalesLayout } from '../components/sales/SalesLayout';
import * as authApi from '../api/auth';
import * as salesApi from '../api/sales';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';
import type { SalesDashboardResponse } from '../types/sales';

// Mock ResizeObserver for Recharts ResponsiveContainer in test environment
globalThis.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

const mockUser: CurrentUser = {
  user_id: 'usr-karishma-0001',
  employee_code: 'GC0001',
  first_name: 'Karishma',
  last_name: 'Upadhyay',
  official_email: 'karishma@gocompliances.com',
  mobile_number: '+919999900001',
  company_id: 'comp-1',
  department_id: 'dept-sales',
  designation_id: 'desig-mgr',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const mockModules: AccessibleModule[] = [
  {
    module_id: 'mod-sales',
    module_code: 'SALES',
    module_name: 'Sales',
    display_order: 10,
    is_navigation: true,
    can_view: true,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_approve: false,
    can_export: false,
    data_scope: 'TEAM',
  },
  {
    module_id: 'mod-sales-dash',
    module_code: 'SALES_DASHBOARD',
    module_name: 'Sales Dashboard',
    display_order: 10,
    is_navigation: true,
    can_view: true,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_approve: false,
    can_export: true,
    data_scope: 'TEAM',
  },
];

const mockDashboardData: SalesDashboardResponse = {
  date_range: {
    preset: 'this_month',
    from_date: '2025-03-01',
    to_date: '2025-03-31',
    formatted_from: '01/03/2025',
    formatted_to: '31/03/2025',
    comparison_label: 'vs last month',
  },
  kpis: {
    total_sales: {
      value: 480000,
      formatted_value: '₹4,80,000',
      previous_value: 420000,
      percentage_change: 12,
      is_positive: true,
      comparison_label: 'vs last month',
    },
    confirmed_orders: {
      value: 32,
      formatted_value: '32',
      previous_value: 28,
      percentage_change: 14,
      is_positive: true,
      comparison_label: 'vs last month',
    },
    amount_received: {
      value: 320000,
      formatted_value: '₹3,20,000',
      previous_value: 270000,
      percentage_change: 18,
      is_positive: true,
      comparison_label: 'vs last month',
    },
    outstanding: {
      value: 160000,
      formatted_value: '₹1,60,000',
      previous_value: 150000,
      percentage_change: 5,
      is_positive: false,
      comparison_label: 'vs last month',
    },
    avg_order_value: {
      value: 15000,
      formatted_value: '₹15,000',
      previous_value: 14000,
      percentage_change: 8,
      is_positive: true,
      comparison_label: 'vs last month',
    },
    total_clients: {
      value: 24,
      formatted_value: '24',
      previous_value: 22,
      percentage_change: 9,
      is_positive: true,
      comparison_label: 'vs last month',
    },
  },
  sales_trend: [
    { date: '2025-03-01', label: 'Mar 1', sales_value: 50000, order_count: 4 },
    { date: '2025-03-15', label: 'Mar 15', sales_value: 120000, order_count: 10 },
    { date: '2025-03-31', label: 'Mar 31', sales_value: 310000, order_count: 18 },
  ],
  payment_status: {
    total_orders: 32,
    items: [
      { status: 'FULLY_PAID', label: 'Fully Paid', count: 18, percentage: 56.2, amount: 250000 },
      { status: 'PARTIALLY_PAID', label: 'Partially Paid', count: 8, percentage: 25.0, amount: 120000 },
      { status: 'PENDING', label: 'Pending', count: 4, percentage: 12.5, amount: 80000 },
      { status: 'OVERDUE', label: 'Overdue', count: 2, percentage: 6.3, amount: 30000 },
    ],
  },
  service_sales: [
    { service_id: 'srv-1', service_code: 'PVT_LTD', service_name: 'Private Limited', total_sales: 180000, order_count: 12 },
    { service_id: 'srv-2', service_code: 'LLP', service_name: 'LLP', total_sales: 100000, order_count: 8 },
  ],
  lead_sources: {
    total_leads: 32,
    items: [
      { source: 'WEBSITE', label: 'Website', count: 12, percentage: 37.5 },
      { source: 'REFERRAL', label: 'Referral', count: 8, percentage: 25.0 },
      { source: 'DIRECT', label: 'Direct', count: 6, percentage: 18.8 },
      { source: 'OTHERS', label: 'Others', count: 6, percentage: 18.8 },
    ],
  },
  team_performance: [
    {
      salesperson_id: 'usr-1',
      salesperson_name: 'Karishma Upadhyay',
      employee_code: 'GC0001',
      orders_count: 12,
      total_sales: 180000,
      amount_received: 120000,
      outstanding: 60000,
    },
    {
      salesperson_id: 'usr-2',
      salesperson_name: 'Amit Sharma',
      employee_code: 'GC0002',
      orders_count: 8,
      total_sales: 120000,
      amount_received: 80000,
      outstanding: 40000,
    },
  ],
  recent_orders: [
    {
      order_id: 'ord-0048',
      order_number: 'SO-2025-0048',
      order_date: '2025-03-28',
      formatted_date: '28 Mar 2025',
      client_name: 'Sharma Enterprises',
      service_name: 'Private Limited',
      salesperson_name: 'Karishma Upadhyay',
      order_value: 60000,
      amount_received: 60000,
      balance_amount: 0,
      payment_status: 'FULLY_PAID',
      operation_status: 'COMPLETED',
      confirmation_status: 'CONFIRMED',
    },
  ],
  filter_options: {
    employees: [
      { id: 'ALL', label: 'All Sales Team' },
      { id: 'usr-1', label: 'Karishma Upadhyay' },
      { id: 'usr-2', label: 'Amit Sharma' },
    ],
    services: [
      { id: 'ALL', label: 'All Services' },
      { id: 'srv-1', label: 'Private Limited' },
      { id: 'srv-2', label: 'LLP' },
    ],
    lead_sources: [
      { id: 'ALL', label: 'All Sources' },
      { id: 'WEBSITE', label: 'Website' },
      { id: 'REFERRAL', label: 'Referral' },
    ],
    payment_statuses: [
      { id: 'ALL', label: 'All Status' },
      { id: 'FULLY_PAID', label: 'Fully Paid' },
      { id: 'PENDING', label: 'Pending' },
    ],
    can_filter_employees: true,
    default_employee_id: null,
  },
};

describe('Sales Dashboard Frontend Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'test-access-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModules);
  });

  it('renders Sales Dashboard with live KPI values and visual sections', async () => {
    vi.spyOn(salesApi, 'getSalesDashboardApi').mockResolvedValue(mockDashboardData);

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/dashboard']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="dashboard" element={<SalesDashboardPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    // Verify page header
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales dashboard/i })).toBeInTheDocument();
    });

    // Verify 6 KPI metrics rendered
    expect(screen.getByText('₹4,80,000')).toBeInTheDocument(); // Total Sales
    expect(screen.getAllByText('32').length).toBeGreaterThanOrEqual(1); // Confirmed Orders & Donut Counts
    expect(screen.getByText('₹3,20,000')).toBeInTheDocument(); // Amount Received
    expect(screen.getByText('₹1,60,000')).toBeInTheDocument(); // Outstanding
    expect(screen.getByText('₹15,000')).toBeInTheDocument(); // Avg Order Value
    expect(screen.getByText('24')).toBeInTheDocument(); // Total Clients

    // Verify Chart Card Titles
    expect(screen.getByRole('heading', { name: /sales trend/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /payment status/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /license-wise sales/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /lead sources/i })).toBeInTheDocument();

    // Verify Tables
    expect(screen.getByRole('heading', { name: /sales team performance/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /recent sales orders/i })).toBeInTheDocument();
    expect(screen.getByText('SO-2025-0048')).toBeInTheDocument();
    expect(screen.getByText('Sharma Enterprises')).toBeInTheDocument();
  });

  it('allows filter adjustments and triggers API refetch', async () => {
    const user = userEvent.setup();
    const fetchSpy = vi.spyOn(salesApi, 'getSalesDashboardApi').mockResolvedValue(mockDashboardData);

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/dashboard']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="dashboard" element={<SalesDashboardPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales dashboard/i })).toBeInTheDocument();
    });

    // Change Preset filter to "Today"
    const presetSelect = screen.getByLabelText(/preset date selector/i);
    await user.selectOptions(presetSelect, 'today');

    // Verify API called with preset today
    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith(expect.objectContaining({ preset: 'today' }));
    });
  });

  it('handles CSV export click and triggers API', async () => {
    const user = userEvent.setup();
    vi.spyOn(salesApi, 'getSalesDashboardApi').mockResolvedValue(mockDashboardData);
    const exportSpy = vi.spyOn(salesApi, 'exportSalesDashboardCsvApi').mockResolvedValue({
      blob: new Blob(['OrderID,Date\nSO-1,2025-03-01'], { type: 'text/csv' }),
      filename: 'sales_export_2025-03-01.csv',
    });

    // Mock URL.createObjectURL
    globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    globalThis.URL.revokeObjectURL = vi.fn();

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/dashboard']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="dashboard" element={<SalesDashboardPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales dashboard/i })).toBeInTheDocument();
    });

    const exportBtn = screen.getByRole('button', { name: /export/i });
    await user.click(exportBtn);

    await waitFor(() => {
      expect(exportSpy).toHaveBeenCalled();
    });
  });

  it('renders error state with retry button on API failure', async () => {
    const user = userEvent.setup();
    const fetchSpy = vi
      .spyOn(salesApi, 'getSalesDashboardApi')
      .mockRejectedValue(new Error('Network connection timeout'));

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/dashboard']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="dashboard" element={<SalesDashboardPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    // Verify header and error banner rendered
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales dashboard/i })).toBeInTheDocument();
    });

    const errorMsgs = await screen.findAllByText(/network connection timeout/i);
    expect(errorMsgs.length).toBeGreaterThanOrEqual(1);

    // Provide mock resolved value before clicking retry
    fetchSpy.mockResolvedValue(mockDashboardData);

    // Click Retry
    const retryBtn = screen.getByRole('button', { name: /retry/i });
    await user.click(retryBtn);

    // Verify dashboard loads after retry
    await waitFor(() => {
      expect(screen.getByText('₹4,80,000')).toBeInTheDocument();
    });
  });
});

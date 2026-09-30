import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { DashboardPage } from '../pages/DashboardPage';
import { AccountsLayout } from '../components/accounts/AccountsLayout';
import { AccountsDashboardPage } from '../pages/accounts/AccountsDashboardPage';
import { PaymentRegisterPage } from '../pages/accounts/PaymentRegisterPage';
import { OutstandingFollowupsPage } from '../pages/accounts/OutstandingFollowupsPage';
import { InvoicesReceiptsPage } from '../pages/accounts/InvoicesReceiptsPage';
import { ExpensesReimbursementsPage } from '../pages/accounts/ExpensesReimbursementsPage';
import { FinancialReportsPage } from '../pages/accounts/FinancialReportsPage';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import * as authApi from '../api/auth';
import * as accountsApi from '../api/accounts';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';
import type { AccountsDashboardResponse } from '../types/accounts';

// Mock ResizeObserver for Recharts
globalThis.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

const superAdminUser: CurrentUser = {
  user_id: 'usr-admin-0001',
  employee_code: 'CG0001',
  first_name: 'Super',
  last_name: 'Admin',
  official_email: 'admin@gocompliances.in',
  mobile_number: '+919999999999',
  company_id: 'comp-1',
  department_id: 'dept-admin',
  designation_id: 'desig-dir',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const mockAccessibleModules: AccessibleModule[] = [
  {
    module_id: 'mod-accounts',
    module_code: 'ACCOUNTS',
    module_name: 'Accounts',
    display_order: 30,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: true,
    can_approve: true,
    can_export: true,
    data_scope: 'ALL',
  },
];

const mockDashboardData: AccountsDashboardResponse = {
  date_range: {
    from_date: '2026-09-01',
    to_date: '2026-09-30',
  },
  kpis: {
    confirmed_order_value: 500000.0,
    formatted_confirmed_order_value: '₹5,00,000',
    confirmed_order_count: 10,
    verified_collections: 350000.0,
    formatted_verified_collections: '₹3,50,000',
    verified_collections_count: 7,
    unverified_collections: 50000.0,
    formatted_unverified_collections: '₹50,000',
    unverified_collections_count: 1,
    current_outstanding: 150000.0,
    formatted_current_outstanding: '₹1,50,000',
    outstanding_orders_count: 3,
    current_overdue: 80000.0,
    formatted_current_overdue: '₹80,000',
    overdue_orders_count: 2,
    recorded_direct_costs: 45000.0,
    formatted_recorded_direct_costs: '₹45,000',
    estimated_order_margin: 455000.0,
    formatted_estimated_order_margin: '₹4,55,000',
    margin_percentage: 91.0,
  },
  collections_trend: [
    { date: '2026-09-01', label: '01 Sep', verified_amount: 50000.0, order_count: 2 },
    { date: '2026-09-15', label: '15 Sep', verified_amount: 100000.0, order_count: 3 },
  ],
  ageing_breakdown: [
    { bucket: '1_30_DAYS', label: '1 - 30 Days', amount: 30000.0, count: 2, percentage: 37.5, color: '#3B82F6' },
    { bucket: '31_60_DAYS', label: '31 - 60 Days', amount: 50000.0, count: 1, percentage: 62.5, color: '#F59E0B' },
  ],
  company_breakdown: [
    {
      company_id: 'comp-1',
      company_name: 'GoCompliances Pvt Ltd',
      order_value: 500000.0,
      verified_received: 350000.0,
      outstanding: 150000.0,
      collection_rate: 70.0,
    },
  ],
  expense_breakdown: [
    { category: 'GOVT_FEES', label: 'Govt Fees', amount: 25000.0, percentage: 55.5, count: 2 },
  ],
  recent_transactions: [],
  top_outstanding: [
    {
      sales_order_id: 'so-1',
      order_number: 'SO-001',
      client_name: 'Apex Corp',
      service_name: 'GST Registration',
      salesperson_name: 'Rahul Sharma',
      total_payable: 100000.0,
      verified_received: 20000.0,
      pending_amount: 80000.0,
      formatted_pending_amount: '₹80,000',
      days_overdue: 45,
      operation_status: 'IN_PROGRESS',
    },
  ],
  filter_options: {
    companies: [{ id: 'comp-1', label: 'GoCompliances Pvt Ltd' }],
    clients: [],
    salespersons: [{ id: 'u-1', label: 'Rahul Sharma' }],
    payment_statuses: [],
    payment_modes: [],
    expense_categories: [],
    receiving_accounts: [],
  },
};

describe('Accounts Module & Workspace Navigation Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock-jwt-token');
    vi.clearAllMocks();
  });

  const renderWithAccountsRouter = (initialRoute = '/dashboard') => {
    return render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={[initialRoute]}>
            <Routes>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route
                path="/accounts"
                element={
                  <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                    <AccountsLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<AccountsDashboardPage />} />
                <Route path="dashboard" element={<AccountsDashboardPage />} />
                <Route path="payments" element={<PaymentRegisterPage />} />
                <Route path="outstanding" element={<OutstandingFollowupsPage />} />
                <Route path="invoices" element={<InvoicesReceiptsPage />} />
                <Route path="expenses" element={<ExpensesReimbursementsPage />} />
                <Route path="reports" element={<FinancialReportsPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );
  };

  it('1. Renders Accounts card on Dashboard for Super Admin and navigates directly to /accounts on click', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAccessibleModules);
    vi.spyOn(accountsApi, 'getAccountsDashboardApi').mockResolvedValue(mockDashboardData);
    vi.spyOn(accountsApi, 'getAccountsFilterOptionsApi').mockResolvedValue(mockDashboardData.filter_options);

    renderWithAccountsRouter('/dashboard');

    // Wait for module cards to load
    await screen.findByRole('heading', { name: 'Accounts' });
    expect(screen.getByRole('heading', { name: 'Accounts' })).toBeInTheDocument();

    // Click Accounts card
    const accountsCard = screen.getByRole('heading', { name: 'Accounts' }).closest('div');
    expect(accountsCard).toBeTruthy();
    await userEvent.click(accountsCard!);

    // Should navigate directly to Accounts Dashboard
    await screen.findByText(/Financial Health & Collections/i);
    expect(screen.getByText(/Financial Health & Collections/i)).toBeInTheDocument();
  });

  it('2. Renders Accounts KPI summary cards and financial metrics on /accounts', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAccessibleModules);
    vi.spyOn(accountsApi, 'getAccountsDashboardApi').mockResolvedValue(mockDashboardData);
    vi.spyOn(accountsApi, 'getAccountsFilterOptionsApi').mockResolvedValue(mockDashboardData.filter_options);

    renderWithAccountsRouter('/accounts');

    await screen.findByText(/Financial Health & Collections/i);
    expect(screen.getAllByText(/Confirmed Order Value/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Verified Collections/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Current Outstanding/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Overdue Receivables/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Direct Operational Costs/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Estimated Order Margin/i).length).toBeGreaterThan(0);
  });

  it('3. Accounts sidebar renders all 6 navigation links and Back to Main Portal link', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAccessibleModules);
    vi.spyOn(accountsApi, 'getAccountsDashboardApi').mockResolvedValue(mockDashboardData);
    vi.spyOn(accountsApi, 'getAccountsFilterOptionsApi').mockResolvedValue(mockDashboardData.filter_options);

    renderWithAccountsRouter('/accounts');

    await screen.findByText(/Financial Health & Collections/i);
    expect(screen.getByRole('link', { name: /Payment Register/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Outstanding & Ageing/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Invoices & Receipts/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Expenses & Reimbursements/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Financial Reports/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Main Dashboard/i })).toBeInTheDocument();
  });
});

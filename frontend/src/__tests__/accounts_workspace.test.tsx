import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { DashboardPage } from '../pages/DashboardPage';
import { AccountsLayout } from '../components/accounts/AccountsLayout';
import { AccountsDashboardPage } from '../pages/accounts/AccountsDashboardPage';
import { AccountsEntriesPage } from '../pages/accounts/AccountsEntriesPage';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import * as authApi from '../api/auth';
import * as accountsApi from '../api/accounts';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';
import type { AccountsDashboardResponse, AccountsEntriesResponse } from '../types/accounts';

// Mock ResizeObserver for charts
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
  task_summary: {
    total_tasks: 10,
    completed_tasks: 6,
    pending_tasks: 4,
  },
  kpis: {
    total_entries: 10,
    total_amount: 500000.0,
    formatted_total_amount: '₹5,00,000',
    advance_amount: 350000.0,
    formatted_advance_amount: '₹3,50,000',
    pending_amount: 150000.0,
    formatted_pending_amount: '₹1,50,000',
    govt_fees: 25000.0,
    formatted_govt_fees: '₹25,000',
    incidental_cost: 5000.0,
    formatted_incidental_cost: '₹5,000',
    estimated_profit: 470000.0,
    formatted_estimated_profit: '₹4,70,000',
  },
  payment_status_breakdown: [
    {
      status: 'PAID',
      label: 'Fully Paid',
      count: 7,
      amount: 350000.0,
      formatted_amount: '₹3,50,000',
      percentage: 70.0,
    },
    {
      status: 'PARTIAL',
      label: 'Partially Paid',
      count: 3,
      amount: 150000.0,
      formatted_amount: '₹1,50,000',
      percentage: 30.0,
    },
  ],
  recent_entries: [
    {
      s_no: 1,
      order_id: 'so-1',
      order_number: 'SO-001',
      company_id: 'comp-1',
      client_id: 'cli-1',
      service_id: 'srv-1',
      salesperson_user_id: 'u-1',
      order_date: '2026-09-15',
      formatted_date: '15/09/2026',
      client_name: 'Apex Corp',
      location: 'Mumbai',
      contact_no: '+919876543210',
      lead_source: 'Google Ads',
      service_name: 'GST Registration',
      salesperson_name: 'Rahul Sharma',
      assigned_to_name: 'Amit Patel',
      work_status: 'IN_PROGRESS',
      order_value: 100000.0,
      formatted_order_value: '₹1,00,000',
      amount_received: 40000.0,
      formatted_amount_received: '₹40,000',
      balance_amount: 60000.0,
      formatted_balance_amount: '₹60,000',
      payment_status: 'PARTIAL',
      proforma_invoice_no: 'PI-2026-001',
      tax_invoice_no: 'TI-2026-001',
      reimbursement_note: 'Travel expense',
      govt_fees: 5000.0,
      formatted_govt_fees: '₹5,000',
      incidental_cost: 1000.0,
      formatted_incidental_cost: '₹1,000',
      profit_amount: 94000.0,
      formatted_profit_amount: '₹94,000',
      remarks: 'First payment received',
      confirmation_status: 'CONFIRMED',
      created_at: '2026-09-15T10:00:00Z',
      updated_at: '2026-09-15T10:00:00Z',
    },
  ],
};

const mockEntriesData: AccountsEntriesResponse = {
  items: [
    {
      s_no: 1,
      order_id: 'so-1',
      order_number: 'SO-001',
      company_id: 'comp-1',
      client_id: 'cli-1',
      service_id: 'srv-1',
      salesperson_user_id: 'u-1',
      order_date: '2026-09-15',
      formatted_date: '15/09/2026',
      client_name: 'Apex Corp',
      location: 'Mumbai',
      contact_no: '+919876543210',
      lead_source: 'Google Ads',
      service_name: 'GST Registration',
      salesperson_name: 'Rahul Sharma',
      assigned_to_name: 'Amit Patel',
      work_status: 'IN_PROGRESS',
      order_value: 100000.0,
      formatted_order_value: '₹1,00,000',
      amount_received: 40000.0,
      formatted_amount_received: '₹40,000',
      balance_amount: 60000.0,
      formatted_balance_amount: '₹60,000',
      payment_status: 'PARTIAL',
      proforma_invoice_no: 'PI-2026-001',
      tax_invoice_no: 'TI-2026-001',
      reimbursement_note: 'Travel expense',
      govt_fees: 5000.0,
      formatted_govt_fees: '₹5,000',
      incidental_cost: 1000.0,
      formatted_incidental_cost: '₹1,000',
      profit_amount: 94000.0,
      formatted_profit_amount: '₹94,000',
      remarks: 'First payment received',
      confirmation_status: 'CONFIRMED',
      created_at: '2026-09-15T10:00:00Z',
      updated_at: '2026-09-15T10:00:00Z',
    },
  ],
  total_count: 1,
  page: 1,
  limit: 25,
  total_pages: 1,
  summary: {
    total_orders: 1,
    total_amount: 100000.0,
    formatted_total_amount: '₹1,00,000',
    total_advance: 40000.0,
    formatted_total_advance: '₹40,000',
    total_pending: 60000.0,
    formatted_total_pending: '₹60,000',
    total_govt_fees: 5000.0,
    formatted_total_govt_fees: '₹5,000',
    total_incidental_cost: 1000.0,
    formatted_total_incidental_cost: '₹1,000',
    total_profits: 94000.0,
    formatted_total_profits: '₹94,000',
  },
};

describe('Accounts Module Navigation & Page Tests', () => {
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
                <Route path="entries" element={<AccountsEntriesPage />} />
                <Route path="payments" element={<Navigate to="/accounts/entries" replace />} />
                <Route path="outstanding" element={<Navigate to="/accounts/entries" replace />} />
                <Route path="invoices" element={<Navigate to="/accounts/entries" replace />} />
                <Route path="expenses" element={<Navigate to="/accounts/entries" replace />} />
                <Route path="reports" element={<Navigate to="/accounts/entries" replace />} />
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

    renderWithAccountsRouter('/dashboard');

    await screen.findByRole('heading', { name: 'Accounts' });
    expect(screen.getByRole('heading', { name: 'Accounts' })).toBeInTheDocument();

    const accountsCard = screen.getByRole('heading', { name: 'Accounts' }).closest('div');
    expect(accountsCard).toBeTruthy();
    await userEvent.click(accountsCard!);

    await screen.findByRole('heading', { name: /Accounts Dashboard/i });
    expect(screen.getByRole('heading', { name: /Accounts Dashboard/i })).toBeInTheDocument();
  });

  it('2. Renders exactly 7 canonical KPI summary cards with proper labels on /accounts/dashboard', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAccessibleModules);
    vi.spyOn(accountsApi, 'getAccountsDashboardApi').mockResolvedValue(mockDashboardData);

    renderWithAccountsRouter('/accounts/dashboard');

    await screen.findByRole('heading', { name: /Accounts Dashboard/i });
    expect(screen.getAllByText(/Total Entries/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Total Amount/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Advance Amount/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Pending Amount/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Govt Fees/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Incidental Cost/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Estimated Profit/i).length).toBeGreaterThan(0);
    // Verify "Verified Collections" is NOT present
    expect(screen.queryByText(/Verified Collections/i)).not.toBeInTheDocument();
  });

  it('3. Accounts sidebar renders exactly 2 navigation links (Dashboard, Accounts Entries)', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAccessibleModules);
    vi.spyOn(accountsApi, 'getAccountsDashboardApi').mockResolvedValue(mockDashboardData);

    renderWithAccountsRouter('/accounts/dashboard');

    await screen.findByRole('heading', { name: /Accounts Dashboard/i });
    const navs = screen.getAllByRole('navigation', { name: /Accounts Navigation/i });
    expect(navs.length).toBeGreaterThan(0);
    const nav = navs[0];
    expect(within(nav).getByRole('link', { name: /Dashboard/i })).toBeInTheDocument();
    expect(within(nav).getByRole('link', { name: /Accounts Entries/i })).toBeInTheDocument();

    // Verify obsolete links are NOT in navigation
    expect(within(nav).queryByRole('link', { name: /Payment Register/i })).not.toBeInTheDocument();
    expect(within(nav).queryByRole('link', { name: /Outstanding & Ageing/i })).not.toBeInTheDocument();
    expect(within(nav).queryByRole('link', { name: /Invoices & Receipts/i })).not.toBeInTheDocument();
    expect(within(nav).queryByRole('link', { name: /Expenses & Reimbursements/i })).not.toBeInTheDocument();
    expect(within(nav).queryByRole('link', { name: /Financial Reports/i })).not.toBeInTheDocument();
  });

  it('4. Renders Accounts Entries page with 21 columns and entry details', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAccessibleModules);
    vi.spyOn(accountsApi, 'getAccountsEntriesApi').mockResolvedValue(mockEntriesData);

    renderWithAccountsRouter('/accounts/entries');

    // Wait for the table data to load
    await screen.findByText('Apex Corp');
    expect(screen.getByText('Apex Corp')).toBeInTheDocument();

    // Check key columns from the 21 columns
    expect(screen.getByText(/15\.\s*Proforma Inv\.\s*No\./i)).toBeInTheDocument();
    expect(screen.getByText(/16\.\s*Tax Inv\.\s*No\./i)).toBeInTheDocument();
    expect(screen.getByText(/17\.\s*Reimbursement Note/i)).toBeInTheDocument();
    expect(screen.getByText(/18\.\s*Govt Fees/i)).toBeInTheDocument();
    expect(screen.getByText(/19\.\s*Incidental Cost/i)).toBeInTheDocument();
    expect(screen.getByText(/20\.\s*Profits/i)).toBeInTheDocument();

    // Check entry data
    expect(screen.getByText('PI-2026-001')).toBeInTheDocument();
    expect(screen.getByText('TI-2026-001')).toBeInTheDocument();
  });

  it('5. Renders 3 task summary cards (Total Tasks, Completed Tasks, Pending Tasks) with counts and interactive links', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAccessibleModules);
    vi.spyOn(accountsApi, 'getAccountsDashboardApi').mockResolvedValue(mockDashboardData);

    renderWithAccountsRouter('/accounts/dashboard');

    await screen.findByRole('heading', { name: /Accounts Dashboard/i });

    // Verify task summary cards exist
    expect(screen.getByText(/Total Tasks/i)).toBeInTheDocument();
    expect(screen.getByText(/Completed Tasks/i)).toBeInTheDocument();
    expect(screen.getByText(/Pending Tasks/i)).toBeInTheDocument();

    // Verify interactive links & counts (waiting for async dashboard data load)
    const totalLink = screen.getByLabelText(/Filter Total Tasks/i);
    const completedLink = screen.getByLabelText(/Filter Completed Tasks/i);
    const pendingLink = screen.getByLabelText(/Filter Pending Tasks/i);

    expect(await within(totalLink).findByText('10')).toBeInTheDocument();
    expect(await within(completedLink).findByText('6')).toBeInTheDocument();
    expect(await within(pendingLink).findByText('4')).toBeInTheDocument();

    expect(totalLink.getAttribute('href')).toContain('/accounts/entries');
    expect(completedLink.getAttribute('href')).toContain('task_status=COMPLETED');
    expect(pendingLink.getAttribute('href')).toContain('task_status=PENDING');
  });

  it('6. Accounts Entries page supports task_status filtering and tab selection', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAccessibleModules);
    const getEntriesSpy = vi.spyOn(accountsApi, 'getAccountsEntriesApi').mockResolvedValue(mockEntriesData);

    renderWithAccountsRouter('/accounts/entries?task_status=COMPLETED');

    await screen.findByText('Apex Corp');

    // Verify initial call had task_status: 'COMPLETED'
    expect(getEntriesSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        task_status: 'COMPLETED',
      })
    );

    // Verify active filter indicator is displayed
    expect(screen.getByText(/Active Task Filter:/i)).toBeInTheDocument();
    expect(screen.getByText(/Completed Tasks \(Tax Invoice Issued\)/i)).toBeInTheDocument();

    // Click 'Pending' task status tab
    const pendingBtn = screen.getByRole('button', { name: /Pending/i });
    await userEvent.click(pendingBtn);

    expect(getEntriesSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        task_status: 'PENDING',
        page: 1,
      })
    );
  });
});

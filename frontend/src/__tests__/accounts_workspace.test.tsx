import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { DashboardPage } from '../pages/DashboardPage';
import { AccountsLayout } from '../components/accounts/AccountsLayout';
import { AccountsDashboardPage } from '../pages/accounts/AccountsDashboardPage';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import * as authApi from '../api/auth';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';

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
                <Route
                  path="dashboard"
                  element={
                    <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                      <AccountsDashboardPage />
                    </ProtectedRoute>
                  }
                />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );
  };

  it('1. Renders Accounts card on Dashboard for Super Admin and navigates directly to /accounts on click without opening a modal', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);

    renderWithAccountsRouter('/dashboard');

    // Wait for modules to load
    await screen.findByRole('heading', { name: 'Accounts' });
    expect(screen.getByRole('heading', { name: 'Accounts' })).toBeInTheDocument();

    // Click Accounts card
    const accountsCard = screen.getByRole('heading', { name: 'Accounts' }).closest('div');
    expect(accountsCard).toBeTruthy();
    await userEvent.click(accountsCard!);

    // Should navigate directly to Accounts Workspace page
    await screen.findByRole('heading', { name: /Financial Management & Ledgers/i });
    expect(screen.getByRole('heading', { name: /Financial Management & Ledgers/i })).toBeInTheDocument();

    // Ensure the old "Module Under Alignment" popup is NOT present
    expect(screen.queryByText(/Module Under Alignment/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Understood' })).not.toBeInTheDocument();
  });

  it('2. Renders Accounts KPI summary cards and workspace canvas on /accounts', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);

    renderWithAccountsRouter('/accounts');

    await screen.findByText(/Total Invoiced/i);
    expect(screen.getByText(/Total Invoiced/i)).toBeInTheDocument();
    expect(screen.getByText(/Collected Amount/i)).toBeInTheDocument();
    expect(screen.getByText(/Pending Balance/i)).toBeInTheDocument();
    expect(screen.getByText(/Active Client Ledgers/i)).toBeInTheDocument();
    expect(screen.getByText(/Accounts & Financial Workspace/i)).toBeInTheDocument();
  });

  it('3. Accounts sidebar renders clean single Accounts Overview link and Back to Dashboard link', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);

    renderWithAccountsRouter('/accounts');

    await screen.findByText('Accounts Overview');
    expect(screen.getByText('Accounts Overview')).toBeInTheDocument();
    expect(screen.queryByText('Invoices & Billing')).not.toBeInTheDocument();
    expect(screen.queryByText('Payments & Receipts')).not.toBeInTheDocument();
    expect(screen.queryByText('Client Ledgers')).not.toBeInTheDocument();
    expect(screen.queryByText('Financial Reports')).not.toBeInTheDocument();
    expect(screen.getByText('Back to Dashboard')).toBeInTheDocument();
  });
});

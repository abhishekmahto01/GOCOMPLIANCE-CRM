import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { DashboardPage } from '../pages/DashboardPage';
import { UnauthorizedPage } from '../pages/UnauthorizedPage';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import * as authApi from '../api/auth';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';

// Fixture 1: Karishma Upadhyay (Sales Dashboard Read + Export only)
const karishmaUser: CurrentUser = {
  user_id: 'usr-karishma-0004',
  employee_code: 'CG0004',
  first_name: 'Karishma',
  last_name: 'Upadhyay',
  official_email: 'karishma.u@gocompliances.in',
  mobile_number: '+919876543210',
  company_id: 'comp-1',
  department_id: 'dept-sales',
  designation_id: 'desig-exec',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const karishmaSalesModules: AccessibleModule[] = [
  {
    module_id: 'mod-sales-root',
    module_code: 'SALES',
    module_name: 'Sales',
    display_order: 20,
    is_navigation: true,
    can_view: true,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_approve: false,
    can_export: false,
    data_scope: 'SELF',
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
    data_scope: 'SELF',
  },
];

// Fixture 2: Operations-only employee
const opsUser: CurrentUser = {
  user_id: 'usr-ops-0005',
  employee_code: 'CG0005',
  first_name: 'Rohan',
  last_name: 'Verma',
  official_email: 'rohan.v@gocompliances.in',
  mobile_number: '+919876543211',
  company_id: 'comp-1',
  department_id: 'dept-ops',
  designation_id: 'desig-exec',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const opsModules: AccessibleModule[] = [
  {
    module_id: 'mod-ops-root',
    module_code: 'OPERATIONS',
    module_name: 'Operations',
    display_order: 30,
    is_navigation: true,
    can_view: true,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_approve: false,
    data_scope: 'SELF',
  },
  {
    module_id: 'mod-ops-dash',
    module_code: 'OPERATION_DASHBOARD',
    module_name: 'Operation Dashboard',
    display_order: 10,
    is_navigation: true,
    can_view: true,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_approve: false,
    can_export: true,
    data_scope: 'SELF',
  },
];

// Fixture 3: Dual-permission employee (Sales + Operations)
const dualUser: CurrentUser = {
  user_id: 'usr-dual-0006',
  employee_code: 'CG0006',
  first_name: 'Amit',
  last_name: 'Sharma',
  official_email: 'amit.s@gocompliances.in',
  mobile_number: '+919876543212',
  company_id: 'comp-1',
  department_id: 'dept-general',
  designation_id: 'desig-mgr',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const dualModules: AccessibleModule[] = [
  ...karishmaSalesModules,
  ...opsModules,
];

// Fixture 4: Super Admin
const superAdminUser: CurrentUser = {
  user_id: 'usr-admin-0001',
  employee_code: 'CG0001',
  first_name: 'Super',
  last_name: 'Admin',
  official_email: 'admin@gocompliances.in',
  mobile_number: '+919876543200',
  company_id: 'comp-1',
  department_id: 'dept-admin',
  designation_id: 'desig-dir',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const superAdminModules: AccessibleModule[] = [
  {
    module_id: 'mod-admin-root',
    module_code: 'ADMIN',
    module_name: 'Admin',
    display_order: 10,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: true,
    can_approve: true,
    data_scope: 'ALL',
  },
  {
    module_id: 'mod-admin-access',
    module_code: 'ADMIN_ACCESS',
    module_name: 'Access Control',
    display_order: 50,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: true,
    can_approve: true,
    data_scope: 'ALL',
  },
  ...karishmaSalesModules,
  ...opsModules,
];

const renderWithProviders = (initialRoute = '/dashboard') => {
  return render(
    <ThemeProvider>
      <AuthProvider>
        <MemoryRouter initialEntries={[initialRoute]}>
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route
              path="/sales"
              element={
                <ProtectedRoute requiredModule="SALES">
                  <div data-testid="sales-page">Sales Workspace</div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/operations"
              element={
                <ProtectedRoute requiredModule="OPERATIONS">
                  <div data-testid="operations-page">Operations Workspace</div>
                </ProtectedRoute>
              }
            />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="/login" element={<div data-testid="login-page">Login Page</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    </ThemeProvider>
  );
};

describe('Permission-based Module Visibility & Authorization', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'test-access-token');
  });

  it('1. Sales-only user (Karishma fixture) sees only Sales card', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(karishmaSalesModules);

    renderWithProviders();

    await screen.findByRole('heading', { name: 'Sales' });
    expect(screen.getByRole('heading', { name: 'Sales' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Operations' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Admin' })).not.toBeInTheDocument();
  });

  it('2. Operation-only user sees only Operations card', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(opsUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(opsModules);

    renderWithProviders();

    await screen.findByRole('heading', { name: 'Operations' });
    expect(screen.getByRole('heading', { name: 'Operations' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Sales' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Admin' })).not.toBeInTheDocument();
  });

  it('3. User with both permissions sees both cards', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(dualUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(dualModules);

    renderWithProviders();

    await screen.findByRole('heading', { name: 'Sales' });
    expect(screen.getByRole('heading', { name: 'Sales' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Operations' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Admin' })).not.toBeInTheDocument();
  });

  it('4. User with no permissions sees No Modules Assigned empty state', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);

    renderWithProviders();

    await screen.findByText('No Modules Assigned');
    expect(screen.getByText('No Modules Assigned')).toBeInTheDocument();
    expect(screen.getByText(/Please contact your administrator to request access/i)).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Sales' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Operations' })).not.toBeInTheDocument();
  });

  it('5. Super Admin sees all modules', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(superAdminModules);

    renderWithProviders();

    await screen.findByRole('heading', { name: 'Admin' });
    expect(screen.getByRole('heading', { name: 'Admin' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Sales' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Operations' })).toBeInTheDocument();
  });

  it('6. Loading state renders skeleton and does not flash cards', async () => {
    let resolveModules!: (mods: AccessibleModule[]) => void;
    const modulesPromise = new Promise<AccessibleModule[]>((res) => {
      resolveModules = res;
    });

    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockReturnValue(modulesPromise);

    renderWithProviders();

    expect(screen.getByTestId('modules-loading')).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Sales' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Operations' })).not.toBeInTheDocument();

    resolveModules(karishmaSalesModules);

    await screen.findByRole('heading', { name: 'Sales' });
    expect(screen.getByRole('heading', { name: 'Sales' })).toBeInTheDocument();
    expect(screen.queryByTestId('modules-loading')).not.toBeInTheDocument();
  });

  it('7. Permission API failure does not grant access and shows retry state', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockRejectedValue(new Error('Network Error'));

    renderWithProviders();

    await screen.findByTestId('permission-error-state');
    expect(screen.getByText('Unable to Load Permissions')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Sales' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Operations' })).not.toBeInTheDocument();
  });

  it('8. Sales-only user cannot manually open an Operation route (redirects to /unauthorized)', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(karishmaSalesModules);

    renderWithProviders('/operations');

    await screen.findByText('Access Restricted');
    expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    expect(screen.queryByTestId('operations-page')).not.toBeInTheDocument();
  });

  it('9. Operation-only user cannot manually open a Sales route (redirects to /unauthorized)', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(opsUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(opsModules);

    renderWithProviders('/sales');

    await screen.findByText('Access Restricted');
    expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    expect(screen.queryByTestId('sales-page')).not.toBeInTheDocument();
  });

  it('10. Logout clears permission state', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(karishmaSalesModules);
    vi.spyOn(authApi, 'logoutApi').mockResolvedValue();

    const LogoutTestComponent: React.FC = () => {
      const { logout, modules, isAuthenticated } = useAuth();
      return (
        <div>
          <button onClick={() => logout()}>Logout Button</button>
          <span data-testid="mod-count">{modules.length}</span>
          <span data-testid="auth-state">{isAuthenticated ? 'AUTH' : 'NOT_AUTH'}</span>
        </div>
      );
    };

    render(
      <AuthProvider>
        <LogoutTestComponent />
      </AuthProvider>
    );

    await screen.findByText('AUTH');
    expect(screen.getByTestId('mod-count').textContent).toBe('2');

    const logoutBtn = screen.getByText('Logout Button');
    await userEvent.click(logoutBtn);

    await waitFor(() => {
      expect(screen.getByTestId('auth-state').textContent).toBe('NOT_AUTH');
      expect(screen.getByTestId('mod-count').textContent).toBe('0');
    });
  });

  it('11. Logging in as another employee does not reuse previous permissions', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(karishmaSalesModules);
    vi.spyOn(authApi, 'loginApi').mockResolvedValue({
      access_token: 'new-token',
      refresh_token: 'new-refresh',
      token_type: 'bearer',
      expires_in: 3600,
      must_change_password: false,
    });

    const SwitchUserComponent: React.FC = () => {
      const { login, hasModuleAccess } = useAuth();
      return (
        <div>
          <div data-testid="has-sales">{hasModuleAccess('SALES') ? 'YES_SALES' : 'NO_SALES'}</div>
          <div data-testid="has-ops">{hasModuleAccess('OPERATIONS') ? 'YES_OPS' : 'NO_OPS'}</div>
          <button
            onClick={() =>
              login({ identifier: 'rohan.v@gocompliances.in', password: 'password123' })
            }
          >
            Switch to Ops
          </button>
        </div>
      );
    };

    render(
      <AuthProvider>
        <SwitchUserComponent />
      </AuthProvider>
    );

    await screen.findByText('YES_SALES');
    expect(screen.getByTestId('has-sales').textContent).toBe('YES_SALES');
    expect(screen.getByTestId('has-ops').textContent).toBe('NO_OPS');

    // Simulate login response for Ops user
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(opsUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(opsModules);

    const switchBtn = screen.getByRole('button', { name: 'Switch to Ops' });
    await userEvent.click(switchBtn);

    await waitFor(() => {
      expect(screen.getByTestId('has-ops').textContent).toBe('YES_OPS');
      expect(screen.getByTestId('has-sales').textContent).toBe('NO_SALES');
    });
  });

  it('12. Permission codes from backend map correctly to modules (e.g. child codes without root code)', async () => {
    // Child page code without explicit root module in accessible modules array
    const childOnlyModules: AccessibleModule[] = [
      {
        module_id: 'mod-task',
        module_code: 'OPERATION_TASK_ASSIGNMENT',
        module_name: 'Task Assignment',
        display_order: 30,
        is_navigation: true,
        can_view: true,
        can_create: false,
        can_edit: false,
        can_delete: false,
        can_approve: false,
        data_scope: 'SELF',
      },
    ];

    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(opsUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(childOnlyModules);

    renderWithProviders();

    await screen.findByRole('heading', { name: 'Operations' });
    expect(screen.getByRole('heading', { name: 'Operations' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Sales' })).not.toBeInTheDocument();
  });

  it('13. Karishma effective permission fixture strictly produces only Sales card', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(karishmaSalesModules);

    renderWithProviders();

    await screen.findByRole('heading', { name: 'Sales' });
    const moduleHeadings = screen.getAllByRole('heading', { level: 3 });
    expect(moduleHeadings).toHaveLength(1);
    expect(moduleHeadings[0].textContent).toBe('Sales');
  });
});

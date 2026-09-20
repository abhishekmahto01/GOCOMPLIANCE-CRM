import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { DashboardPage } from '../pages/DashboardPage';
import { EmployeeListPage } from '../pages/EmployeeListPage';
import { EmployeeFormPage } from '../pages/EmployeeFormPage';
import { AdminPlaceholderPage } from '../pages/AdminPlaceholderPage';
import { UnauthorizedPage } from '../pages/UnauthorizedPage';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import { AdminLayout } from '../components/admin/AdminLayout';
import { AdminIndexRedirect } from '../components/admin/AdminIndexRedirect';
import * as authApi from '../api/auth';
import * as lookupApi from '../api/lookup';
import * as employeesApi from '../api/employees';
import { ACCESS_TOKEN_KEY } from '../api/client';

describe('Admin Module Layout & Collapsible Sidebar Routing', () => {
  const mockAdminUser = {
    user_id: '11111111-1111-1111-1111-111111111111',
    employee_code: 'CG0001',
    first_name: 'Super',
    last_name: 'Admin',
    official_email: 'admin@gocompliances.in',
    mobile_number: '+919876543210',
    company_id: '22222222-2222-2222-2222-222222222222',
    department_id: '33333333-3333-3333-3333-333333333333',
    designation_id: '44444444-4444-4444-4444-444444444444',
    account_status: 'ACTIVE' as const,
    must_change_password: false,
    company_name: 'Gocompliances',
    department_name: 'Administration',
    designation_name: 'Director',
  };

  const mockSalesUser = {
    ...mockAdminUser,
    user_id: '99999999-9999-9999-9999-999999999999',
    employee_code: 'CG0002',
    first_name: 'Sales',
    last_name: 'Executive',
    official_email: 'sales@gocompliances.in',
    designation_name: 'Executive',
  };

  const fullAdminModules = [
    {
      module_id: 'm-admin',
      module_code: 'ADMIN',
      module_name: 'Administration',
      parent_module_id: null,
      display_order: 1,
      is_navigation: true,
      can_view: true,
      can_create: true,
      can_edit: true,
      can_delete: true,
      can_approve: true,
      data_scope: 'ALL' as const,
    },
    {
      module_id: 'm-emp',
      module_code: 'ADMIN_EMPLOYEES',
      module_name: 'Employees',
      parent_module_id: 'm-admin',
      display_order: 2,
      is_navigation: true,
      can_view: true,
      can_create: true,
      can_edit: true,
      can_delete: true,
      can_approve: true,
      data_scope: 'ALL' as const,
    },
  ];

  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'valid-token');
    vi.spyOn(lookupApi, 'getLookupCompaniesApi').mockResolvedValue([]);
    vi.spyOn(lookupApi, 'getLookupDepartmentsApi').mockResolvedValue([]);
    vi.spyOn(lookupApi, 'getLookupDesignationsApi').mockResolvedValue([]);
    vi.spyOn(lookupApi, 'getLookupManagersApi').mockResolvedValue([]);
    vi.spyOn(employeesApi, 'getEmployeesApi').mockResolvedValue({
      items: [],
      page: 1,
      page_size: 20,
      total: 0,
      pages: 1,
    });
  });

  const renderAdminApp = (initialRoute = '/admin/employees') => {
    return render(
      <AuthProvider>
        <MemoryRouter initialEntries={[initialRoute]}>
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                  <AdminLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<AdminIndexRedirect />} />
              <Route
                path="employees"
                element={
                  <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="view">
                    <EmployeeListPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="employees/new"
                element={
                  <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="create">
                    <EmployeeFormPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="access"
                element={
                  <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                    <AdminPlaceholderPage featureKey="access" />
                  </ProtectedRoute>
                }
              />
              <Route
                path="account-activation"
                element={
                  <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                    <AdminPlaceholderPage featureKey="activation" />
                  </ProtectedRoute>
                }
              />
            </Route>
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );
  };

  it('renders persistent sidebar with navigation groups on Admin routes', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullAdminModules);

    renderAdminApp('/admin/employees');

    const sidebar = await screen.findByTestId('admin-sidebar');

    // Sidebar Header Branding
    expect(within(sidebar).getByText('Administration')).toBeInTheDocument();
    expect(within(sidebar).getByText('Control Panel')).toBeInTheDocument();

    // Top Direct Navigation Item
    expect(within(sidebar).getByRole('link', { name: /Dashboard/i })).toBeInTheDocument();

    // Parent Groups
    expect(within(sidebar).getByRole('button', { name: /Employee Management/i })).toBeInTheDocument();
    expect(within(sidebar).getByRole('button', { name: /User Control/i })).toBeInTheDocument();

    // Child Links for Employee Management (auto-expanded)
    expect(within(sidebar).getByRole('link', { name: /Employee List/i })).toBeInTheDocument();
    expect(within(sidebar).getByRole('link', { name: /Add Employee/i })).toBeInTheDocument();

    // Expand User Control to view its child links
    const user = userEvent.setup();
    const userControlBtn = within(sidebar).getByRole('button', { name: /User Control/i });
    await user.click(userControlBtn);

    expect(within(sidebar).getByRole('link', { name: /Access Control & Scopes/i })).toBeInTheDocument();
    expect(within(sidebar).getByRole('link', { name: /Login Credentials/i })).toBeInTheDocument();
  });

  it('parent menu toggles expand and collapse state on click', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullAdminModules);

    renderAdminApp('/admin/employees');

    const user = userEvent.setup();
    const toggleButton = await screen.findByRole('button', { name: /Employee Management/i });
    expect(toggleButton).toHaveAttribute('aria-expanded', 'true');

    // Click to collapse
    await user.click(toggleButton);
    expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
    expect(screen.queryByRole('link', { name: /Employee List/i })).not.toBeInTheDocument();

    // Click to expand again
    await user.click(toggleButton);
    expect(toggleButton).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('link', { name: /Employee List/i })).toBeInTheDocument();
  });

  it('automatically expands the group containing the active route', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullAdminModules);

    renderAdminApp('/admin/access');

    await waitFor(() => {
      const userControlButton = screen.getByRole('button', { name: /User Control/i });
      expect(userControlButton).toHaveAttribute('aria-expanded', 'true');
      expect(screen.getByRole('link', { name: /Access Control & Scopes/i })).toBeInTheDocument();
    });
  });

  it('highlights the active child route with accent styling', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullAdminModules);

    renderAdminApp('/admin/employees');

    await waitFor(() => {
      const activeLink = screen.getByRole('link', { name: /Employee List/i });
      expect(activeLink.className).toContain('bg-blue-50');
      expect(activeLink.className).toContain('text-blue-700');
    });
  });

  it('hides child items if user lacks specific action permission', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    // User has can_view for ADMIN_EMPLOYEES but NOT can_create
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([
      {
        module_id: 'm-admin',
        module_code: 'ADMIN',
        module_name: 'Administration',
        parent_module_id: null,
        display_order: 1,
        is_navigation: true,
        can_view: true,
        can_create: true,
        can_edit: true,
        can_delete: true,
        can_approve: true,
        data_scope: 'ALL' as const,
      },
      {
        module_id: 'm-emp',
        module_code: 'ADMIN_EMPLOYEES',
        module_name: 'Employees',
        parent_module_id: 'm-admin',
        display_order: 2,
        is_navigation: true,
        can_view: true,
        can_create: false, // NO CREATE PERMISSION
        can_edit: false,
        can_delete: false,
        can_approve: false,
        data_scope: 'SELF' as const,
      },
    ]);

    renderAdminApp('/admin/employees');

    await waitFor(() => {
      expect(screen.getByRole('link', { name: /Employee List/i })).toBeInTheDocument();
      // Add Employee child link is hidden because can_create is false
      expect(screen.queryByRole('link', { name: /Add Employee/i })).not.toBeInTheDocument();
    });
  });

  it('hides entire parent group when user has no permitted child items', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    // User has ADMIN view (can see User Control) but NO ADMIN_EMPLOYEES view or create
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([
      {
        module_id: 'm-admin',
        module_code: 'ADMIN',
        module_name: 'Administration',
        parent_module_id: null,
        display_order: 1,
        is_navigation: true,
        can_view: true,
        can_create: true,
        can_edit: true,
        can_delete: true,
        can_approve: true,
        data_scope: 'ALL' as const,
      },
    ]);

    renderAdminApp('/admin/access');

    await waitFor(() => {
      // User Control is visible
      expect(screen.getByRole('button', { name: /User Control/i })).toBeInTheDocument();
      // Employee Management is COMPLETELY hidden
      expect(screen.queryByRole('button', { name: /Employee Management/i })).not.toBeInTheDocument();
    });
  });

  it('navigates back to /dashboard when clicking Dashboard link in sidebar', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullAdminModules);

    renderAdminApp('/admin/employees');

    const user = userEvent.setup();
    const sidebar = await screen.findByTestId('admin-sidebar');
    const dashboardLink = within(sidebar).getByRole('link', { name: /Dashboard/i });
    await user.click(dashboardLink);

    await waitFor(() => {
      expect(screen.getByText('Compliance')).toBeInTheDocument();
      expect(screen.getByText('Growth')).toBeInTheDocument();
      expect(screen.getByText('Together')).toBeInTheDocument();
    });
  });

  it('automatically redirects /admin to the first authorized child route (/admin/employees)', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullAdminModules);

    renderAdminApp('/admin');

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Employee Directory' })).toBeInTheDocument();
    });
  });

  it('opens and closes the mobile drawer when toggling menu and close button', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullAdminModules);

    renderAdminApp('/admin/employees');

    const user = userEvent.setup();
    const openMenuBtn = await screen.findByRole('button', { name: /Open Navigation Menu/i });
    await user.click(openMenuBtn);

    // Close button appears in drawer
    const closeBtn = await screen.findByRole('button', { name: /Close Sidebar Menu/i });
    expect(closeBtn).toBeInTheDocument();

    await user.click(closeBtn);
    await waitFor(() => {
      expect(screen.queryByRole('button', { name: /Close Sidebar Menu/i })).not.toBeInTheDocument();
    });
  });

  it('hides Admin card on main dashboard when user lacks ADMIN permission and leaves Sales/Operations unaffected', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockSalesUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([
      {
        module_id: 'm-sales',
        module_code: 'SALES',
        module_name: 'Sales',
        parent_module_id: null,
        display_order: 2,
        is_navigation: true,
        can_view: true,
        can_create: true,
        can_edit: true,
        can_delete: false,
        can_approve: false,
        data_scope: 'SELF' as const,
      },
    ]);

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.queryByText('Admin')).not.toBeInTheDocument();
      expect(screen.getByText('Sales')).toBeInTheDocument();
      expect(screen.getByText('Operations')).toBeInTheDocument();
    });
  });
});

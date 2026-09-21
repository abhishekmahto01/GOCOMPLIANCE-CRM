import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { DashboardPage } from '../pages/DashboardPage';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { AdminHeader } from '../components/dashboard/AdminHeader';
import * as authApi from '../api/auth';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';

// Fixture 1: Karishma Upadhyay (Department: Sales)
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
  department_name: 'Sales',
  department_code: 'SALES',
  department: {
    id: 'dept-sales',
    code: 'SALES',
    name: 'Sales',
  },
  company: {
    id: 'comp-1',
    code: 'GOCOMP',
    name: 'GoCompliance',
  },
  designation: {
    id: 'desig-exec',
    code: 'SR_EXEC',
    name: 'Senior Executive',
  },
};

const salesOnlyModules: AccessibleModule[] = [
  {
    module_id: 'mod-sales',
    module_code: 'SALES',
    module_name: 'Sales',
    display_order: 20,
    is_navigation: true,
    can_view: true,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_approve: false,
    data_scope: 'SELF',
  },
];

// Fixture 2: Deepak Thapliya (Department: Operations)
const deepakUser: CurrentUser = {
  user_id: 'usr-deepak-0005',
  employee_code: 'CG0005',
  first_name: 'Deepak',
  last_name: 'Thapliya',
  official_email: 'deepak.t@gocompliances.in',
  mobile_number: '+919876543211',
  company_id: 'comp-1',
  department_id: 'dept-ops',
  designation_id: 'desig-exec',
  account_status: 'ACTIVE',
  must_change_password: false,
  department_name: 'Operations',
  department_code: 'OPERATIONS',
  department: {
    id: 'dept-ops',
    code: 'OPERATIONS',
    name: 'Operations',
  },
};

const opsOnlyModules: AccessibleModule[] = [
  {
    module_id: 'mod-ops',
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
];

// Fixture 3: Super Admin (Department: Administration)
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
  department_name: 'Administration',
  department_code: 'ADMIN',
  department: {
    id: 'dept-admin',
    code: 'ADMIN',
    name: 'Administration',
  },
};

const adminModules: AccessibleModule[] = [
  {
    module_id: 'mod-admin',
    module_code: 'ADMIN',
    module_name: 'Administration',
    display_order: 10,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: true,
    can_approve: true,
    data_scope: 'ALL',
  },
];

// Fixture 4: Employee with no department assigned
const unassignedDeptUser: CurrentUser = {
  user_id: 'usr-unassigned-0009',
  employee_code: 'CG0009',
  first_name: 'Ravi',
  last_name: 'Kumar',
  official_email: 'ravi.k@gocompliances.in',
  mobile_number: '+919876543299',
  company_id: 'comp-1',
  department_id: null,
  designation_id: 'desig-trainee',
  account_status: 'ACTIVE',
  must_change_password: false,
  department_name: null,
  department_code: null,
  department: null,
};

const renderApp = (initialRoute = '/dashboard') => {
  return render(
    <ThemeProvider>
      <AuthProvider>
        <MemoryRouter initialEntries={[initialRoute]}>
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    </ThemeProvider>
  );
};

describe('Frontend Header Department Subtitle and Access Isolation', () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock-jwt-token');
    vi.restoreAllMocks();
  });

  it('1. Karishma profile with Sales department displays "Sales"', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(salesOnlyModules);

    renderApp();

    await screen.findByRole('heading', { name: 'Sales' });

    // Username and Department in header
    expect(screen.getByTestId('header-user-name')).toHaveTextContent('Karishma Upadhyay');
    expect(screen.getByTestId('header-user-department')).toHaveTextContent('Sales');
    expect(screen.getByTestId('header-user-department')).not.toHaveTextContent('Administration');
  });

  it('2. Deepak profile with Operations department displays "Operations"', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(deepakUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(opsOnlyModules);

    renderApp();

    await screen.findByRole('heading', { name: 'Operations' });

    expect(screen.getByTestId('header-user-name')).toHaveTextContent('Deepak Thapliya');
    expect(screen.getByTestId('header-user-department')).toHaveTextContent('Operations');
    expect(screen.getByTestId('header-user-department')).not.toHaveTextContent('Administration');
  });

  it('3. Super Admin profile displays "Administration"', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(adminModules);

    renderApp();

    await screen.findByRole('heading', { name: 'Admin' });

    expect(screen.getByTestId('header-user-name')).toHaveTextContent('Super Admin');
    expect(screen.getByTestId('header-user-department')).toHaveTextContent('Administration');
  });

  it('4. Missing department displays "Department Not Assigned"', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(unassignedDeptUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(salesOnlyModules);

    renderApp();

    await screen.findByRole('heading', { name: 'Sales' });

    expect(screen.getByTestId('header-user-name')).toHaveTextContent('Ravi Kumar');
    expect(screen.getByTestId('header-user-department')).toHaveTextContent('Department Not Assigned');
    expect(screen.getByTestId('header-user-department')).not.toHaveTextContent('Administration');
  });

  it('5. Missing department does not grant Administration access', async () => {
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(unassignedDeptUser);
    // User has no module permissions
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);

    renderApp();

    await screen.findByText('No Modules Assigned');

    // Admin module should NOT be visible
    expect(screen.queryByRole('heading', { name: 'Admin' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Sales' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Operations' })).not.toBeInTheDocument();
    expect(screen.getByTestId('no-modules-assigned')).toBeInTheDocument();
  });

  it('6. Logout clears the displayed department and user state', async () => {
    const user = userEvent.setup();
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(salesOnlyModules);
    vi.spyOn(authApi, 'logoutApi').mockResolvedValue();

    renderApp();

    await screen.findByRole('heading', { name: 'Sales' });
    expect(screen.getByTestId('header-user-name')).toHaveTextContent('Karishma Upadhyay');
    expect(screen.getByTestId('header-user-department')).toHaveTextContent('Sales');

    const logoutBtn = screen.getByTitle('Sign out of CRM');
    await user.click(logoutBtn);

    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument();
      expect(screen.queryByTestId('header-user-name')).not.toBeInTheDocument();
      expect(screen.queryByTestId('header-user-department')).not.toBeInTheDocument();
    });
  });

  it('7. A second login does not reuse the previous user’s department', async () => {
    // Session 1: Karishma (Sales)
    const fetchUserSpy = vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    const fetchModulesSpy = vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(salesOnlyModules);

    const { unmount } = renderApp();

    await screen.findByRole('heading', { name: 'Sales' });
    expect(screen.getByTestId('header-user-department')).toHaveTextContent('Sales');

    unmount();

    // Session 2: Deepak (Operations)
    fetchUserSpy.mockResolvedValue(deepakUser);
    fetchModulesSpy.mockResolvedValue(opsOnlyModules);

    renderApp();

    await screen.findByRole('heading', { name: 'Operations' });
    expect(screen.getByTestId('header-user-name')).toHaveTextContent('Deepak Thapliya');
    expect(screen.getByTestId('header-user-department')).toHaveTextContent('Operations');
    expect(screen.getByTestId('header-user-department')).not.toHaveTextContent('Sales');
    expect(screen.getByTestId('header-user-department')).not.toHaveTextContent('Administration');
  });

  it('8. Permissions do not overwrite the department label', async () => {
    // Karishma is in Sales department, but has both Sales and Operation permissions granted
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(karishmaUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([
      ...salesOnlyModules,
      {
        module_id: 'mod-ops',
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
    ]);

    renderApp();

    await screen.findByRole('heading', { name: 'Sales' });

    // Both module cards should be visible according to permissions
    expect(screen.getByRole('heading', { name: 'Sales' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Operations' })).toBeInTheDocument();

    // But header department must strictly remain "Sales"
    expect(screen.getByTestId('header-user-name')).toHaveTextContent('Karishma Upadhyay');
    expect(screen.getByTestId('header-user-department')).toHaveTextContent('Sales');
  });
});

describe('DashboardHeader & AdminHeader standalone component fallbacks', () => {
  it('DashboardHeader defaults to Department Not Assigned when no department is given', () => {
    render(
      <DashboardHeader
        session={{
          isAuthenticated: true,
          username: 'Test User',
          userRole: 'Staff',
          employeeCode: 'CG1000',
          email: 'test@example.com',
          department: '',
          designation: '',
          company: '',
        }}
        theme="light"
        onToggleTheme={vi.fn()}
        onOpenPasswordModal={vi.fn()}
        onLogout={vi.fn()}
      />
    );

    expect(screen.getByTestId('header-user-department')).toHaveTextContent('Department Not Assigned');
    expect(screen.queryByText('Administration')).not.toBeInTheDocument();
    expect(screen.queryByText('Admin Department')).not.toBeInTheDocument();
  });

  it('AdminHeader defaults to Department Not Assigned when user department is missing', () => {
    render(
      <AuthProvider>
        <MemoryRouter>
          <AdminHeader
            theme="light"
            onToggleTheme={vi.fn()}
            onOpenPasswordModal={vi.fn()}
            onLogout={vi.fn()}
          />
        </MemoryRouter>
      </AuthProvider>
    );

    expect(screen.getByTestId('header-user-department')).toHaveTextContent('Department Not Assigned');
    expect(screen.queryByText('Administration')).not.toBeInTheDocument();
  });
});

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { DashboardPage } from '../pages/DashboardPage';
import { ChangePasswordRequiredPage } from '../pages/ChangePasswordRequiredPage';
import { LoginCredentialsPage } from '../pages/LoginCredentialsPage';
import { AdminLayout } from '../components/admin/AdminLayout';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import * as authApi from '../api/auth';
import * as employeesApi from '../api/employees';
import * as lookupApi from '../api/lookup';
import { ACCESS_TOKEN_KEY } from '../api/client';

describe('Stage B: Trial Employee Login & Mandatory Password Change', () => {
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

  const mockRestrictedUser = {
    user_id: '22222222-2222-2222-2222-222222222222',
    employee_code: 'CG0002',
    first_name: 'Muskan',
    last_name: 'Gupta',
    official_email: 'muskan.gupta@gocompliances.in',
    mobile_number: '+919876543211',
    company_id: '22222222-2222-2222-2222-222222222222',
    department_id: '33333333-3333-3333-3333-333333333333',
    designation_id: '44444444-4444-4444-4444-444444444444',
    account_status: 'ACTIVE' as const,
    must_change_password: true,
    company_name: 'Gocompliances',
    department_name: 'Compliance',
    designation_name: 'Compliance Associate',
  };

  const mockAdminModules = [
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
      child_modules: [
        {
          module_id: 'm-emp',
          module_code: 'ADMIN_EMPLOYEES',
          module_name: 'Employee Management',
          parent_module_id: 'm-admin',
          display_order: 2,
          is_navigation: true,
          can_view: true,
          can_create: true,
          can_edit: true,
          can_delete: true,
          can_approve: true,
          data_scope: 'ALL' as const,
          child_modules: [],
        },
      ],
    },
  ];

  const mockEmployeesList = {
    items: [
      {
        user_id: '22222222-2222-2222-2222-222222222222',
        employee_code: 'CG0002',
        first_name: 'Muskan',
        last_name: 'Gupta',
        official_email: 'muskan.gupta@gocompliances.in',
        mobile_number: '+919876543211',
        company_id: 'c1',
        department_id: 'd1',
        designation_id: 'des1',
        date_of_joining: '2026-02-01',
        employment_type: 'FULL_TIME' as const,
        account_status: 'ACTIVE' as const,
        company_name: 'Gocompliances Org',
        department_name: 'Compliance',
        designation_name: 'Compliance Associate',
        credentials_initialized: false,
        must_change_password: true,
        login_status: 'Not Initialized',
        credentials_initialized_at: null,
        created_at: '2026-02-01T00:00:00Z',
        updated_at: '2026-02-01T00:00:00Z',
      },
      {
        user_id: '33333333-3333-3333-3333-333333333333',
        employee_code: 'CG0003',
        first_name: 'Rohan',
        last_name: 'Sharma',
        official_email: 'rohan.sharma@gocompliances.in',
        mobile_number: '+919811122233',
        company_id: 'c1',
        department_id: 'd1',
        designation_id: 'des1',
        date_of_joining: '2026-03-01',
        employment_type: 'FULL_TIME' as const,
        account_status: 'ACTIVE' as const,
        company_name: 'Gocompliances Org',
        department_name: 'Engineering',
        designation_name: 'Software Engineer',
        credentials_initialized: true,
        must_change_password: true,
        login_status: 'Password Change Required',
        credentials_initialized_at: '2026-03-01T10:00:00Z',
        created_at: '2026-03-01T00:00:00Z',
        updated_at: '2026-03-01T00:00:00Z',
      },
    ],
    page: 1,
    page_size: 15,
    total: 2,
    pages: 1,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    vi.spyOn(lookupApi, 'getLookupCompaniesApi').mockResolvedValue([
      { company_id: 'c1', company_name: 'Gocompliances Org', company_code: 'GO', employee_code_prefix: 'GO' },
    ]);
    vi.spyOn(lookupApi, 'getLookupDepartmentsApi').mockResolvedValue([
      { department_id: 'd1', company_id: 'c1', department_name: 'Compliance', department_code: 'COMP' },
    ]);
  });

  it('renders Login Credentials management table with badges and Initialize button for uninitialized employee', async () => {
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock-admin-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAdminModules);
    vi.spyOn(employeesApi, 'getEmployeesApi').mockResolvedValue(mockEmployeesList);

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/admin/account-activation']}>
          <Routes>
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                  <AdminLayout />
                </ProtectedRoute>
              }
            >
              <Route path="account-activation" element={<LoginCredentialsPage />} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    // Verify title and notice
    expect(await screen.findByRole('heading', { name: /Login Credentials/i })).toBeInTheDocument();
    expect(screen.getByText(/Trial Phase Credentials Policy/i)).toBeInTheDocument();

    // Verify employees rendered
    expect(await screen.findByText('Muskan Gupta')).toBeInTheDocument();
    expect(screen.getByText('CG0002')).toBeInTheDocument();
    expect(screen.getByText('Rohan Sharma')).toBeInTheDocument();
    expect(screen.getByText('CG0003')).toBeInTheDocument();

    // Verify badges
    expect(screen.getAllByText('Not Initialized').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Password Change Required').length).toBeGreaterThanOrEqual(1);

    // Verify "Initialize Trial Login" button is visible for Muskan (uninitialized)
    const initBtn = screen.getByRole('button', { name: /Initialize Trial Login/i });
    expect(initBtn).toBeInTheDocument();

    // Verify no password or hash is visible in DOM
    expect(screen.queryByText(/12345/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/\$argon2id\$/i)).not.toBeInTheDocument();
  });

  it('opens confirmation modal and initializes trial login for CG0002', async () => {
    const user = userEvent.setup();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock-admin-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAdminModules);
    vi.spyOn(employeesApi, 'getEmployeesApi').mockResolvedValue(mockEmployeesList);
    const initSpy = vi.spyOn(employeesApi, 'initializeTrialLoginApi').mockResolvedValue({
      user_id: '22222222-2222-2222-2222-222222222222',
      employee_code: 'CG0002',
      official_email: 'muskan.gupta@gocompliances.in',
      credentials_initialized: true,
      must_change_password: true,
      login_status: 'Password Change Required',
      credentials_initialized_at: '2026-09-21T00:00:00Z',
      message: 'Trial login credentials have been initialized.',
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/admin/account-activation']}>
          <Routes>
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                  <AdminLayout />
                </ProtectedRoute>
              }
            >
              <Route path="account-activation" element={<LoginCredentialsPage />} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    const initBtn = await screen.findByRole('button', { name: /Initialize Trial Login/i });
    await user.click(initBtn);

    // Modal opens with employee info and warning note
    expect(screen.getByRole('heading', { name: /Initialize Trial Login Credentials/i })).toBeInTheDocument();
    expect(screen.getByText(/Trial Credential Provisioning Note/i)).toBeInTheDocument();

    // Confirm initialization
    const confirmBtn = screen.getByRole('button', { name: /Confirm & Initialize/i });
    await user.click(confirmBtn);

    await waitFor(() => {
      expect(initSpy).toHaveBeenCalledWith('22222222-2222-2222-2222-222222222222');
    });
  });

  it('redirects restricted user with must_change_password=true to /change-password-required and blocks /dashboard', async () => {
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock-restricted-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockRestrictedUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockRejectedValue(new Error('Forbidden'));

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/change-password-required"
              element={<ChangePasswordRequiredPage />}
            />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    // Should redirect from /dashboard to /change-password-required
    expect(await screen.findByText(/Mandatory First-Login Password Setup/i)).toBeInTheDocument();
    expect(screen.getByText(/Muskan Gupta/i)).toBeInTheDocument();
    expect(screen.getByText(/CG0002/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Set New Password & Proceed to Login/i })).toBeInTheDocument();
  });

  it('validates password policy and successfully submits new password on /change-password-required', async () => {
    const user = userEvent.setup();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock-restricted-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockRestrictedUser);
    const changeSpy = vi.spyOn(authApi, 'changeInitialPasswordApi').mockResolvedValue({
      message: 'Password changed successfully',
    });
    vi.spyOn(authApi, 'logoutApi').mockResolvedValue();

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/change-password-required']}>
          <Routes>
            <Route
              path="/change-password-required"
              element={<ChangePasswordRequiredPage />}
            />
            <Route path="/login" element={<div>Login Page Redirected</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    expect(await screen.findByText(/Mandatory First-Login Password Setup/i)).toBeInTheDocument();

    const submitBtn = screen.getByRole('button', { name: /Set New Password & Proceed to Login/i });
    expect(submitBtn).toBeDisabled();

    // Fill in valid strong password
    const newPwdInput = screen.getByPlaceholderText(/Enter new strong password/i);
    const confirmPwdInput = screen.getByPlaceholderText(/Re-type new password/i);

    await user.type(newPwdInput, 'MuskanSecure@2026');
    await user.type(confirmPwdInput, 'MuskanSecure@2026');

    // Submit button becomes enabled
    expect(submitBtn).not.toBeDisabled();

    await user.click(submitBtn);

    await waitFor(() => {
      expect(changeSpy).toHaveBeenCalledWith({
        current_password: undefined,
        new_password: 'MuskanSecure@2026',
        confirm_password: 'MuskanSecure@2026',
      });
    });
  });
});

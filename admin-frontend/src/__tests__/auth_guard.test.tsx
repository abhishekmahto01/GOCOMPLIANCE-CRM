import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ProtectedRoute } from '../components/common/ProtectedRoute';
import * as authApi from '../api/auth';
import { CurrentUser } from '../types/auth';
import { AccessibleModule } from '../types/permission';

const mockUser: CurrentUser = {
  user_id: '11111111-1111-1111-1111-111111111111',
  employee_code: 'CG0001',
  first_name: 'Admin',
  last_name: 'Director',
  official_email: 'director@gocompliances.in',
  mobile_number: '+919876543210',
  company_id: '22222222-2222-2222-2222-222222222222',
  department_id: '33333333-3333-3333-3333-333333333333',
  designation_id: '44444444-4444-4444-4444-444444444444',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const mockModulesWithEmployees: AccessibleModule[] = [
  {
    module_id: '55555555-5555-5555-5555-555555555555',
    module_code: 'ADMIN_EMPLOYEES',
    module_name: 'Employee Management',
    display_order: 1,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: false,
    can_approve: true,
    data_scope: 'ALL',
  },
];

const mockModulesWithoutEmployees: AccessibleModule[] = [
  {
    module_id: '66666666-6666-6666-6666-666666666666',
    module_code: 'SALES',
    module_name: 'Sales Management',
    display_order: 2,
    is_navigation: true,
    can_view: true,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_approve: false,
    data_scope: 'SELF',
  },
];

describe('ProtectedRoute Guard', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it('redirects unauthenticated user to /login', async () => {
    render(
      <MemoryRouter initialEntries={['/employees']}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<div>Login Page Mock</div>} />
            <Route
              path="/employees"
              element={
                <ProtectedRoute moduleCode="ADMIN_EMPLOYEES">
                  <div>Secret Employees Content</div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Login Page Mock')).toBeInTheDocument();
      expect(screen.queryByText('Secret Employees Content')).not.toBeInTheDocument();
    });
  });

  it('redirects authenticated user without ADMIN_EMPLOYEES permission to /unauthorized', async () => {
    localStorage.setItem('gocompliance_admin_access_token', 'mock_jwt_token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModulesWithoutEmployees);

    render(
      <MemoryRouter initialEntries={['/employees']}>
        <AuthProvider>
          <Routes>
            <Route path="/unauthorized" element={<div>Unauthorized Page Mock</div>} />
            <Route
              path="/employees"
              element={
                <ProtectedRoute moduleCode="ADMIN_EMPLOYEES">
                  <div>Secret Employees Content</div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Unauthorized Page Mock')).toBeInTheDocument();
      expect(screen.queryByText('Secret Employees Content')).not.toBeInTheDocument();
    });
  });

  it('allows access to protected route when authenticated and permitted', async () => {
    localStorage.setItem('gocompliance_admin_access_token', 'mock_jwt_token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModulesWithEmployees);

    render(
      <MemoryRouter initialEntries={['/employees']}>
        <AuthProvider>
          <Routes>
            <Route
              path="/employees"
              element={
                <ProtectedRoute moduleCode="ADMIN_EMPLOYEES" requiredAction="view">
                  <div>Secret Employees Content</div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Secret Employees Content')).toBeInTheDocument();
    });
  });
});

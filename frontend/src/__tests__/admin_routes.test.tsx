import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { DashboardPage } from '../pages/DashboardPage';
import { AdminLandingPage } from '../pages/AdminLandingPage';
import { AdminPlaceholderPage } from '../pages/AdminPlaceholderPage';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import { UnauthorizedPage } from '../pages/UnauthorizedPage';
import * as authApi from '../api/auth';
import { ACCESS_TOKEN_KEY } from '../api/client';

describe('Admin Module Routing & Dashboard Card Permission Gates', () => {
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

  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('renders Admin card on Dashboard when user has ADMIN view permission', async () => {
    localStorage.setItem(ACCESS_TOKEN_KEY, 'valid-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
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
      expect(screen.getByText('Admin')).toBeInTheDocument();
      expect(screen.getByText('Sales')).toBeInTheDocument();
      expect(screen.getByText('Operations')).toBeInTheDocument();
    });
  });

  it('hides Admin card on Dashboard when user lacks ADMIN permission', async () => {
    localStorage.setItem(ACCESS_TOKEN_KEY, 'valid-token');
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

  it('redirects to /unauthorized when user directly navigates to /admin without permission', async () => {
    localStorage.setItem(ACCESS_TOKEN_KEY, 'valid-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockSalesUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/admin']}>
          <Routes>
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                  <AdminLandingPage />
                </ProtectedRoute>
              }
            />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    });
  });

  it('renders placeholder pages for upcoming access and activation stages', async () => {
    localStorage.setItem(ACCESS_TOKEN_KEY, 'valid-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
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

    const { unmount } = render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/admin/access']}>
          <Routes>
            <Route
              path="/admin/access"
              element={
                <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                  <AdminPlaceholderPage featureKey="access" />
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/User Module Access/i)).toBeInTheDocument();
      expect(screen.getByText(/Scheduled for Stage 10B/i)).toBeInTheDocument();
    });

    unmount();

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/admin/account-activation']}>
          <Routes>
            <Route
              path="/admin/account-activation"
              element={
                <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                  <AdminPlaceholderPage featureKey="activation" />
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Employee Account Activation/i)).toBeInTheDocument();
      expect(screen.getByText(/Scheduled for Stage 10C/i)).toBeInTheDocument();
    });
  });
});

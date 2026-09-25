import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from '../context/AuthContext';
import * as authApi from '../api/auth';
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from '../api/client';

const TestAuthConsumer: React.FC = () => {
  const { user, modules, isAuthenticated, isLoading, login, logout, hasPermission } = useAuth();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <div data-testid="auth-status">{isAuthenticated ? 'AUTHENTICATED' : 'ANONYMOUS'}</div>
      <div data-testid="user-email">{user?.official_email || 'NO_USER'}</div>
      <div data-testid="user-code">{user?.employee_code || 'NO_CODE'}</div>
      <div data-testid="module-count">{modules.length}</div>
      <div data-testid="can-view-admin">{hasPermission('ADMIN', 'view') ? 'YES' : 'NO'}</div>
      <div data-testid="can-view-emp">{hasPermission('ADMIN_EMPLOYEES', 'view') ? 'YES' : 'NO'}</div>
      <button
        onClick={() =>
          login({ identifier: 'admin@gocompliances.in', password: 'ValidPassword#123', rememberMe: false })
        }
      >
        Trigger Login
      </button>
      <button
        onClick={() =>
          login({ identifier: 'admin@gocompliances.in', password: 'ValidPassword#123', rememberMe: true })
        }
      >
        Trigger Remembered Login
      </button>
      <button onClick={() => logout()}>Trigger Logout</button>
    </div>
  );
};

describe('AuthContext & JWT Authentication Flow', () => {
  const mockUser = {
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

  const mockModules = [
    {
      module_id: 'mod-1',
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
      module_id: 'mod-2',
      module_code: 'ADMIN_EMPLOYEES',
      module_name: 'Employees',
      parent_module_id: 'mod-1',
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
    sessionStorage.clear();
    vi.restoreAllMocks();
  });

  it('initializes in unauthenticated state when no token exists', async () => {
    render(
      <AuthProvider>
        <TestAuthConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('ANONYMOUS');
      expect(screen.getByTestId('user-email')).toHaveTextContent('NO_USER');
    });
  });

  it('performs real login and sets tokens and user profile', async () => {
    vi.spyOn(authApi, 'loginApi').mockImplementation(async () => {
      localStorage.setItem(ACCESS_TOKEN_KEY, 'fake-jwt-access-token');
      localStorage.setItem(REFRESH_TOKEN_KEY, 'fake-jwt-refresh-token');
      return {
        access_token: 'fake-jwt-access-token',
        refresh_token: 'fake-jwt-refresh-token',
        token_type: 'bearer',
        expires_in: 3600,
        must_change_password: false,
      };
    });
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModules);

    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestAuthConsumer />
      </AuthProvider>
    );

    const loginBtn = await screen.findByRole('button', { name: 'Trigger Login' });
    await user.click(loginBtn);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('AUTHENTICATED');
      expect(screen.getByTestId('user-email')).toHaveTextContent('admin@gocompliances.in');
      expect(screen.getByTestId('user-code')).toHaveTextContent('CG0001');
      expect(screen.getByTestId('module-count')).toHaveTextContent('2');
      expect(screen.getByTestId('can-view-admin')).toHaveTextContent('YES');
      expect(screen.getByTestId('can-view-emp')).toHaveTextContent('YES');
    });

    expect(authApi.loginApi).toHaveBeenCalledWith({
      identifier: 'admin@gocompliances.in',
      password: 'ValidPassword#123',
      rememberMe: false,
    });
  });

  it('supports Remember me checked: persists tokens in localStorage', async () => {
    vi.spyOn(authApi, 'loginApi').mockImplementation(async (creds) => {
      if (creds.rememberMe) {
        localStorage.setItem(ACCESS_TOKEN_KEY, 'remembered-access-token');
        localStorage.setItem(REFRESH_TOKEN_KEY, 'remembered-refresh-token');
        sessionStorage.removeItem(ACCESS_TOKEN_KEY);
      }
      return {
        access_token: 'remembered-access-token',
        refresh_token: 'remembered-refresh-token',
        token_type: 'bearer',
        expires_in: 3600,
        must_change_password: false,
      };
    });
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModules);

    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestAuthConsumer />
      </AuthProvider>
    );

    const loginBtn = await screen.findByRole('button', { name: 'Trigger Remembered Login' });
    await user.click(loginBtn);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('AUTHENTICATED');
      expect(localStorage.getItem(ACCESS_TOKEN_KEY)).toBe('remembered-access-token');
      expect(sessionStorage.getItem(ACCESS_TOKEN_KEY)).toBeNull();
    });
  });

  it('supports Remember me unchecked: persists tokens in sessionStorage and clears on logout', async () => {
    vi.spyOn(authApi, 'loginApi').mockImplementation(async (creds) => {
      if (!creds.rememberMe) {
        sessionStorage.setItem(ACCESS_TOKEN_KEY, 'session-access-token');
        sessionStorage.setItem(REFRESH_TOKEN_KEY, 'session-refresh-token');
        localStorage.removeItem(ACCESS_TOKEN_KEY);
      }
      return {
        access_token: 'session-access-token',
        refresh_token: 'session-refresh-token',
        token_type: 'bearer',
        expires_in: 3600,
        must_change_password: false,
      };
    });
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModules);
    vi.spyOn(authApi, 'logoutApi').mockImplementation(async () => {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      sessionStorage.removeItem(ACCESS_TOKEN_KEY);
      sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    });

    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestAuthConsumer />
      </AuthProvider>
    );

    const loginBtn = await screen.findByRole('button', { name: 'Trigger Login' });
    await user.click(loginBtn);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('AUTHENTICATED');
      expect(sessionStorage.getItem(ACCESS_TOKEN_KEY)).toBe('session-access-token');
      expect(localStorage.getItem(ACCESS_TOKEN_KEY)).toBeNull();
    });

    // Logout
    const logoutBtn = await screen.findByRole('button', { name: 'Trigger Logout' });
    await user.click(logoutBtn);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('ANONYMOUS');
      expect(sessionStorage.getItem(ACCESS_TOKEN_KEY)).toBeNull();
      expect(localStorage.getItem(ACCESS_TOKEN_KEY)).toBeNull();
    });
  });
});

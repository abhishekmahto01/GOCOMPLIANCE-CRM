import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ImpersonationBanner } from '../components/common/ImpersonationBanner';
import { ImpersonationUrlHandler } from '../components/auth/ImpersonationUrlHandler';
import * as authApi from '../api/auth';
import type { CurrentUser } from '../types/auth';

const mockSuperAdmin: CurrentUser = {
  user_id: '11111111-1111-1111-1111-111111111111',
  employee_code: 'CG0001',
  first_name: 'Super',
  last_name: 'Admin',
  official_email: 'superadmin@gocompliances.com',
  account_status: 'ACTIVE',
  must_change_password: false,
};

describe('Admin Impersonation ("Login as Employee") UI Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    vi.restoreAllMocks();
  });

  it('renders ImpersonationBanner when user is impersonating and allows returning to Admin', async () => {
    const mockImpersonation = {
      session_id: 'session-123',
      actor_admin_id: '11111111-1111-1111-1111-111111111111',
      actor_name: 'Super Admin',
      actor_employee_code: 'CG0001',
      target_user_id: '44444444-4444-4444-4444-444444444444',
      target_name: 'Rohan Sharma',
      target_employee_code: 'CG0004',
      expires_at: new Date(Date.now() + 1800000).toISOString(),
    };

    // Create a mock token that has is_impersonated: true in JWT payload
    const mockJwtPayload = btoa(JSON.stringify({ is_impersonated: true, sub: '44444444-4444-4444-4444-444444444444' }));
    const mockToken = `header.${mockJwtPayload}.signature`;
    localStorage.setItem('gocompliance_crm_access_token', mockToken);

    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue({
      ...mockSuperAdmin,
      employee_code: 'CG0004',
      first_name: 'Rohan',
      last_name: 'Sharma',
    });
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);
    vi.spyOn(authApi, 'getImpersonationStatusApi').mockResolvedValue({
      is_impersonated: true,
      impersonation: mockImpersonation,
    });
    const returnSpy = vi.spyOn(authApi, 'returnToAdminApi').mockResolvedValue({
      access_token: 'new-admin-token',
      refresh_token: 'new-admin-refresh',
      token_type: 'bearer',
      expires_in: 3600,
      message: 'Restored',
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <ImpersonationBanner />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Logged in as: Rohan Sharma \(CG0004\)/i)).toBeInTheDocument();
    });

    const returnBtn = screen.getByRole('button', { name: /Return to Admin/i });
    expect(returnBtn).toBeInTheDocument();

    await userEvent.click(returnBtn);
    expect(returnSpy).toHaveBeenCalledTimes(1);
  });

  it('processes ?abhilogin=CG0004 for authenticated Super Admin and initiates impersonation', async () => {
    localStorage.setItem('gocompliance_crm_access_token', 'admin-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockSuperAdmin);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);
    vi.spyOn(authApi, 'getImpersonationStatusApi').mockResolvedValue({ is_impersonated: false });

    const startSpy = vi.spyOn(authApi, 'startImpersonationApi').mockResolvedValue({
      access_token: 'impersonated-token',
      refresh_token: 'impersonated-refresh',
      token_type: 'bearer',
      expires_in: 1800,
      is_impersonated: true,
      impersonation: {
        session_id: 'session-456',
        actor_admin_id: mockSuperAdmin.user_id,
        actor_name: 'Super Admin',
        actor_employee_code: 'CG0001',
        target_user_id: '44444444-4444-4444-4444-444444444444',
        target_name: 'Rohan Sharma',
        target_employee_code: 'CG0004',
        expires_at: new Date().toISOString(),
      },
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/?abhilogin=CG0004']}>
          <ImpersonationUrlHandler />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(startSpy).toHaveBeenCalledWith('CG0004');
    });
  });

  it('discards ?abhilogin parameter when user is not authenticated', async () => {
    // No tokens in storage
    const startSpy = vi.spyOn(authApi, 'startImpersonationApi');

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/?abhilogin=CG0004']}>
          <ImpersonationUrlHandler />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(startSpy).not.toHaveBeenCalled();
    });
  });

  it('processes /dashboard?abhilogin=CG0004 with delayed authentication initialization', async () => {
    localStorage.setItem('gocompliance_crm_access_token', 'admin-token');
    
    // Simulate delayed auth check
    vi.spyOn(authApi, 'getCurrentUserApi').mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockSuperAdmin), 50))
    );
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);
    vi.spyOn(authApi, 'getImpersonationStatusApi').mockResolvedValue({ is_impersonated: false });

    const startSpy = vi.spyOn(authApi, 'startImpersonationApi').mockResolvedValue({
      access_token: 'impersonated-token',
      refresh_token: 'impersonated-refresh',
      token_type: 'bearer',
      expires_in: 1800,
      is_impersonated: true,
      impersonation: {
        session_id: 'session-456',
        actor_admin_id: mockSuperAdmin.user_id,
        actor_name: 'Super Admin',
        actor_employee_code: 'CG0001',
        target_user_id: '44444444-4444-4444-4444-444444444444',
        target_name: 'Rohan Sharma',
        target_employee_code: 'CG0004',
        expires_at: new Date().toISOString(),
      },
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard?abhilogin=CG0004']}>
          <ImpersonationUrlHandler />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(startSpy).toHaveBeenCalledWith('CG0004');
    });
  });

  it('displays a visible error toast when impersonation API fails', async () => {
    localStorage.setItem('gocompliance_crm_access_token', 'admin-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockSuperAdmin);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);
    vi.spyOn(authApi, 'getImpersonationStatusApi').mockResolvedValue({ is_impersonated: false });

    vi.spyOn(authApi, 'startImpersonationApi').mockRejectedValue({
      response: {
        status: 404,
        data: { detail: "Employee with code 'INVALID01' was not found." },
      },
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/?abhilogin=INVALID01']}>
          <ImpersonationUrlHandler />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText(/Employee with code 'INVALID01' was not found/i)).toBeInTheDocument();
    });
  });

  it('displays a visible error toast when non-super-admin user attempts impersonation', async () => {
    localStorage.setItem('gocompliance_crm_access_token', 'user-token');
    const regularUser: CurrentUser = {
      ...mockSuperAdmin,
      employee_code: 'CG0005',
      first_name: 'Regular',
      last_name: 'User',
      official_email: 'regular.user@gocompliances.com',
    };
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(regularUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);
    vi.spyOn(authApi, 'getImpersonationStatusApi').mockResolvedValue({ is_impersonated: false });

    const startSpy = vi.spyOn(authApi, 'startImpersonationApi');

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/?abhilogin=CG0004']}>
          <ImpersonationUrlHandler />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(startSpy).not.toHaveBeenCalled();
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText(/Only Super Admin users are authorized to initiate employee impersonation/i)).toBeInTheDocument();
    });
  });
});

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, useLocation, useNavigate } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { AppRoutes } from '../App';
import * as authApi from '../api/auth';
import * as employeesApi from '../api/employees';
import * as lookupApi from '../api/lookup';
import { ACCESS_TOKEN_KEY } from '../api/client';

const Probe = () => {
  const loc = useLocation();
  const nav = useNavigate();
  return (
    <>
      <div data-testid="probe">{loc.pathname}</div>
      <button data-testid="back" onClick={() => nav(-1)}>back</button>
    </>
  );
};

const mod = (id: string, code: string, parent: string | null) => ({
  module_id: id, module_code: code, module_name: code, parent_module_id: parent, display_order: 1,
  is_navigation: true, can_view: true, can_create: true, can_edit: true, can_delete: true, can_approve: true, data_scope: 'ALL',
});

describe('Main dashboard <-> Admin panel navigation flow', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'valid-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue({
      user_id: '1', employee_code: 'GC0001', first_name: 'Super', last_name: 'Admin',
      official_email: 't@x.in', company_id: 'c', department_id: 'd', designation_id: 'g',
      account_status: 'ACTIVE', must_change_password: false, is_super_admin: true,
    } as never);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([
      mod('a', 'ADMIN', null), mod('e', 'ADMIN_EMPLOYEES', 'a'),
      mod('s', 'SALES', null), mod('o', 'OPERATIONS', null), mod('c', 'ACCOUNTS', null),
    ] as never);
    vi.spyOn(employeesApi, 'getEmployeesApi').mockResolvedValue({ items: [], page: 1, page_size: 15, total: 0, pages: 0 } as never);
    vi.spyOn(lookupApi, 'getLookupCompaniesApi').mockResolvedValue([]);
    vi.spyOn(lookupApi, 'getLookupDepartmentsApi').mockResolvedValue([]);
    vi.spyOn(lookupApi, 'getLookupDesignationsApi').mockResolvedValue([]);
  });

  it('root -> main dashboard -> Admin card -> admin panel -> logo / back -> main dashboard', async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/']}>
          <AppRoutes />
          <Probe />
        </MemoryRouter>
      </AuthProvider>
    );
    const path = () => screen.getByTestId('probe').textContent;

    // 1. After login, root lands on main dashboard
    await waitFor(() => expect(path()).toBe('/dashboard'));

    // 2. Click Admin card
    const adminBtn = await screen.findByLabelText('Enter Admin module');
    fireEvent.click(adminBtn);
    await waitFor(() => expect(path()).toBe('/admin/employees'));

    // 3. Browser back -> main dashboard
    fireEvent.click(screen.getByTestId('back'));
    await waitFor(() => expect(path()).toBe('/dashboard'));

    // 4. Admin again, then click GOCOMPLIANCES logo
    fireEvent.click(await screen.findByLabelText('Enter Admin module'));
    await waitFor(() => expect(path()).toBe('/admin/employees'));
    const logo = (await screen.findByRole('banner')).querySelector('a') as HTMLAnchorElement;
    fireEvent.click(logo);
    await waitFor(() => expect(path()).toBe('/dashboard'));
  });
});

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { EmployeeListPage } from '../pages/EmployeeListPage';
import { EmployeeFormPage } from '../pages/EmployeeFormPage';
import { EmployeeDetailPage } from '../pages/EmployeeDetailPage';
import * as employeesApi from '../api/employees';
import * as lookupApi from '../api/lookup';
import * as authApi from '../api/auth';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';
import type { PaginatedEmployees } from '../types/employee';
import { ACCESS_TOKEN_KEY } from '../api/client';

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

const fullPermissionModules: AccessibleModule[] = [
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

const mockPaginatedData: PaginatedEmployees = {
  items: [
    {
      user_id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
      employee_code: 'CG0002',
      first_name: 'Rohit',
      middle_name: null,
      last_name: 'Verma',
      official_email: 'rohit.v@gocompliances.in',
      personal_email: null,
      mobile_number: '+919876543211',
      company_id: '22222222-2222-2222-2222-222222222222',
      department_id: '33333333-3333-3333-3333-333333333333',
      designation_id: '44444444-4444-4444-4444-444444444444',
      company_name: 'Gocompliances',
      company_code: 'GOCOMPLIANCES',
      department_name: 'Sales',
      department_code: 'SALES',
      designation_name: 'Sales Executive',
      designation_code: 'EXECUTIVE',
      manager_name: 'Admin Director',
      manager_employee_code: 'CG0001',
      date_of_joining: '2026-02-01',
      employment_type: 'FULL_TIME',
      account_status: 'ACTIVE',
      created_at: '2026-02-01T10:00:00Z',
      updated_at: '2026-02-01T10:00:00Z',
    },
  ],
  page: 1,
  page_size: 20,
  total: 1,
  pages: 1,
};

describe('Employee Management Canonical Module Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock_jwt_token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullPermissionModules);
    vi.spyOn(lookupApi, 'getLookupCompaniesApi').mockResolvedValue([
      {
        company_id: '22222222-2222-2222-2222-222222222222',
        company_code: 'GOCOMPLIANCES',
        company_name: 'Gocompliances',
        employee_code_prefix: 'CG',
      },
    ]);
    vi.spyOn(lookupApi, 'getLookupDepartmentsApi').mockResolvedValue([]);
    vi.spyOn(lookupApi, 'getLookupDesignationsApi').mockResolvedValue([]);
    vi.spyOn(lookupApi, 'getLookupManagersApi').mockResolvedValue([]);
    vi.spyOn(employeesApi, 'getEmployeesApi').mockResolvedValue(mockPaginatedData);
    vi.spyOn(employeesApi, 'getEmployeeByIdApi').mockResolvedValue(mockPaginatedData.items[0]);
  });

  it('renders employee list with table rows, search and action buttons', async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/admin/employees']}>
          <Routes>
            <Route path="/admin/employees" element={<EmployeeListPage />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Employee Directory' })).toBeInTheDocument();
      expect(screen.getByText('CG0002')).toBeInTheDocument();
      expect(screen.getByText('Rohit Verma')).toBeInTheDocument();
      expect(screen.getByText('rohit.v@gocompliances.in')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Add Employee/i })).toBeInTheDocument();
    });
  });

  it('renders add employee form with required fields and secure password notice', async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/admin/employees/new']}>
          <Routes>
            <Route path="/admin/employees/new" element={<EmployeeFormPage />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Add New Employee' })).toBeInTheDocument();
      expect(
        screen.getByText(/Login access is configured separately through secure account activation/i)
      ).toBeInTheDocument();
      // Ensure NO password input exists
      expect(screen.queryByLabelText(/password/i)).not.toBeInTheDocument();
    });
  });

  it('renders employee detail page with full organizational breakdown', async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/admin/employees/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa']}>
          <Routes>
            <Route path="/admin/employees/:userId" element={<EmployeeDetailPage />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Organizational Structure')).toBeInTheDocument();
      expect(screen.getByText('Contact & Communication')).toBeInTheDocument();
      expect(screen.getByText('Employment Terms')).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Rohit Verma' })).toBeInTheDocument();
      expect(screen.getAllByText('CG0002').length).toBeGreaterThanOrEqual(1);
    });
  });
});

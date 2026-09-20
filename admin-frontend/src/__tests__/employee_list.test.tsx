import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { EmployeeListPage } from '../pages/EmployeeListPage';
import * as employeesApi from '../api/employees';
import * as lookupApi from '../api/lookup';
import * as authApi from '../api/auth';
import { CurrentUser } from '../types/auth';
import { AccessibleModule } from '../types/permission';
import { PaginatedEmployees } from '../types/employee';

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

const viewOnlyModules: AccessibleModule[] = [
  {
    module_id: '55555555-5555-5555-5555-555555555555',
    module_code: 'ADMIN_EMPLOYEES',
    module_name: 'Employee Management',
    display_order: 1,
    is_navigation: true,
    can_view: true,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_approve: false,
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

describe('EmployeeListPage Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.setItem('gocompliance_admin_access_token', 'mock_jwt_token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
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
  });

  it('renders employee table with data, code, name, and status', async () => {
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullPermissionModules);
    vi.spyOn(employeesApi, 'getEmployeesApi').mockResolvedValue(mockPaginatedData);

    render(
      <MemoryRouter initialEntries={['/employees']}>
        <AuthProvider>
          <EmployeeListPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('CG0002')).toBeInTheDocument();
      expect(screen.getByText('Rohit Verma')).toBeInTheDocument();
      expect(screen.getByText('rohit.v@gocompliances.in')).toBeInTheDocument();
      expect(screen.getByText('Sales Executive')).toBeInTheDocument();
      expect(screen.getAllByText('ACTIVE').length).toBeGreaterThan(0);
    });
  });

  it('shows Add Employee, Edit, and Status buttons when user has full permissions', async () => {
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullPermissionModules);
    vi.spyOn(employeesApi, 'getEmployeesApi').mockResolvedValue(mockPaginatedData);

    render(
      <MemoryRouter initialEntries={['/employees']}>
        <AuthProvider>
          <EmployeeListPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Add Employee')).toBeInTheDocument();
      expect(screen.getByTitle('Edit Employee')).toBeInTheDocument();
      expect(screen.getByTitle('Update Account Status')).toBeInTheDocument();
    });
  });

  it('hides Add Employee, Edit, and Status buttons when user has view-only permissions', async () => {
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(viewOnlyModules);
    vi.spyOn(employeesApi, 'getEmployeesApi').mockResolvedValue(mockPaginatedData);

    render(
      <MemoryRouter initialEntries={['/employees']}>
        <AuthProvider>
          <EmployeeListPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('CG0002')).toBeInTheDocument();
      expect(screen.queryByText('Add Employee')).not.toBeInTheDocument();
      expect(screen.queryByTitle('Edit Employee')).not.toBeInTheDocument();
      expect(screen.queryByTitle('Update Account Status')).not.toBeInTheDocument();
      // View Details icon should still be present
      expect(screen.getByTitle('View Details')).toBeInTheDocument();
    });
  });

  it('renders empty state when no employees match filters', async () => {
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullPermissionModules);
    vi.spyOn(employeesApi, 'getEmployeesApi').mockResolvedValue({
      items: [],
      page: 1,
      page_size: 20,
      total: 0,
      pages: 0,
    });

    render(
      <MemoryRouter initialEntries={['/employees']}>
        <AuthProvider>
          <EmployeeListPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('No employees found')).toBeInTheDocument();
    });
  });
});

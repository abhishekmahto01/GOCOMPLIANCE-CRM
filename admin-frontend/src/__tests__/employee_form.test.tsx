import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { EmployeeFormPage } from '../pages/EmployeeFormPage';
import * as employeesApi from '../api/employees';
import * as lookupApi from '../api/lookup';
import * as authApi from '../api/auth';
import { CurrentUser } from '../types/auth';
import { AccessibleModule } from '../types/permission';
import { CompanyLookup, DepartmentLookup, DesignationLookup } from '../types/lookup';
import { Employee } from '../types/employee';

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

const mockModules: AccessibleModule[] = [
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

const mockCompanies: CompanyLookup[] = [
  {
    company_id: '22222222-2222-2222-2222-222222222222',
    company_code: 'GOCOMPLIANCES',
    company_name: 'Gocompliances',
    employee_code_prefix: 'CG',
  },
];

const mockDepartments: DepartmentLookup[] = [
  {
    department_id: '33333333-3333-3333-3333-333333333333',
    company_id: '22222222-2222-2222-2222-222222222222',
    department_code: 'SALES',
    department_name: 'Sales',
  },
];

const mockDesignations: DesignationLookup[] = [
  {
    designation_id: '44444444-4444-4444-4444-444444444444',
    company_id: '22222222-2222-2222-2222-222222222222',
    designation_code: 'MANAGER',
    designation_name: 'Sales Manager',
    level_rank: 5,
    is_managerial: true,
  },
];

const mockExistingEmployee: Employee = {
  user_id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  employee_code: 'CG0002',
  first_name: 'Existing',
  middle_name: null,
  last_name: 'Staff',
  official_email: 'staff@gocompliances.in',
  personal_email: null,
  mobile_number: '+919876543212',
  company_id: '22222222-2222-2222-2222-222222222222',
  department_id: '33333333-3333-3333-3333-333333333333',
  designation_id: '44444444-4444-4444-4444-444444444444',
  company_name: 'Gocompliances',
  company_code: 'GOCOMPLIANCES',
  department_name: 'Sales',
  department_code: 'SALES',
  designation_name: 'Sales Manager',
  designation_code: 'MANAGER',
  date_of_joining: '2026-01-15',
  employment_type: 'FULL_TIME',
  account_status: 'ACTIVE',
  created_at: '2026-01-15T10:00:00Z',
  updated_at: '2026-01-15T10:00:00Z',
};

describe('EmployeeFormPage Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.setItem('gocompliance_admin_access_token', 'mock_jwt_token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModules);
    vi.spyOn(lookupApi, 'getLookupCompaniesApi').mockResolvedValue(mockCompanies);
    vi.spyOn(lookupApi, 'getLookupDepartmentsApi').mockResolvedValue(mockDepartments);
    vi.spyOn(lookupApi, 'getLookupDesignationsApi').mockResolvedValue(mockDesignations);
    vi.spyOn(lookupApi, 'getLookupManagersApi').mockResolvedValue([]);
  });

  it('validates required fields before submitting form in Add mode', async () => {
    render(
      <MemoryRouter initialEntries={['/employees/new']}>
        <AuthProvider>
          <Routes>
            <Route path="/employees/new" element={<EmployeeFormPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Add New Employee')).toBeInTheDocument();
    });

    const submitBtn = screen.getByRole('button', { name: /Create Employee/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('First name is required')).toBeInTheDocument();
      expect(screen.getByText('Last name is required')).toBeInTheDocument();
      expect(screen.getByText('Please select a company')).toBeInTheDocument();
    });
  });

  it('displays read-only employee code in Edit mode', async () => {
    vi.spyOn(employeesApi, 'getEmployeeByIdApi').mockResolvedValue(mockExistingEmployee);

    render(
      <MemoryRouter initialEntries={['/employees/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/edit']}>
        <AuthProvider>
          <Routes>
            <Route path="/employees/:userId/edit" element={<EmployeeFormPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Edit Employee Profile')).toBeInTheDocument();
      expect(screen.getByText('Code: CG0002 (Read-Only)')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Existing')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Staff')).toBeInTheDocument();
      expect(screen.getByDisplayValue('staff@gocompliances.in')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully with alert message', async () => {
    vi.spyOn(employeesApi, 'createEmployeeApi').mockRejectedValue({
      response: {
        data: {
          detail: 'Official email already registered with another active employee.',
        },
      },
    });

    render(
      <MemoryRouter initialEntries={['/employees/new']}>
        <AuthProvider>
          <Routes>
            <Route path="/employees/new" element={<EmployeeFormPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Add New Employee')).toBeInTheDocument();
    });

    // Fill valid inputs
    fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: 'Aman' } });
    fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: 'Singh' } });
    fireEvent.change(screen.getByLabelText(/Official Email/i), {
      target: { value: 'aman.s@gocompliances.in' },
    });
    fireEvent.change(screen.getByLabelText(/Mobile Number/i), {
      target: { value: '9876543210' },
    });
    fireEvent.change(screen.getByLabelText(/Company/i), {
      target: { value: '22222222-2222-2222-2222-222222222222' },
    });

    await waitFor(() => {
      expect(lookupApi.getLookupDepartmentsApi).toHaveBeenCalledWith(
        '22222222-2222-2222-2222-222222222222'
      );
    });

    fireEvent.change(screen.getByLabelText(/Department/i), {
      target: { value: '33333333-3333-3333-3333-333333333333' },
    });
    fireEvent.change(screen.getByLabelText(/Designation/i), {
      target: { value: '44444444-4444-4444-4444-444444444444' },
    });

    const submitBtn = screen.getByRole('button', { name: /Create Employee/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(
        screen.getByText('Official email already registered with another active employee.')
      ).toBeInTheDocument();
    });
  });
});

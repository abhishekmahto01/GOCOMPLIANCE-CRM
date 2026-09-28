import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { DepartmentMasterPage } from '../pages/DepartmentMasterPage';
import { DesignationMasterPage } from '../pages/DesignationMasterPage';
import * as authApi from '../api/auth';
import * as deptApi from '../api/departments';
import * as desigApi from '../api/designations';
import * as lookupApi from '../api/lookup';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { Department } from '../types/department';
import type { Designation } from '../types/designation';
import type { CompanyLookup } from '../types/lookup';

const superAdminUser: CurrentUser = {
  user_id: 'usr-admin-0001',
  employee_code: 'CG0001',
  first_name: 'Super',
  last_name: 'Admin',
  official_email: 'admin@gocompliances.in',
  mobile_number: '+919999999999',
  company_id: 'comp-1',
  department_id: 'dept-admin',
  designation_id: 'desig-dir',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const mockCompanies: CompanyLookup[] = [
  { company_id: 'comp-1', company_code: 'GC', company_name: 'GoCompliances Private Limited', employee_code_prefix: 'GC' },
  { company_id: 'comp-2', company_code: 'BM', company_name: 'Brandmingo Media Works', employee_code_prefix: 'BM' },
];

const mockDepartments: Department[] = [
  {
    department_id: 'dept-1',
    company_id: 'comp-1',
    department_code: 'SALES',
    department_name: 'Sales & BD',
    description: 'Direct sales and business development',
    status: 'ACTIVE',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    department_id: 'dept-2',
    company_id: 'comp-1',
    department_code: 'OPERATIONS',
    department_name: 'Operations & Delivery',
    description: 'Processing and liaison',
    status: 'ACTIVE',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
];

const mockDesignations: Designation[] = [
  {
    designation_id: 'desig-1',
    company_id: 'comp-1',
    designation_code: 'EXECUTIVE',
    designation_name: 'Executive',
    level_rank: 1,
    is_managerial: false,
    description: 'Junior representative',
    status: 'ACTIVE',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    designation_id: 'desig-2',
    company_id: 'comp-1',
    designation_code: 'MANAGER',
    designation_name: 'Operations Manager',
    level_rank: 5,
    is_managerial: true,
    description: 'Team leader and task allocator',
    status: 'ACTIVE',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
];

describe('Department & Designation Master Component Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock-jwt-token');
    vi.clearAllMocks();

    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(superAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);
    vi.spyOn(lookupApi, 'getLookupCompaniesApi').mockResolvedValue(mockCompanies);
  });

  it('1. Department Master renders table with departments and lookup company name', async () => {
    vi.spyOn(deptApi, 'getDepartmentsApi').mockResolvedValue(mockDepartments);

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/admin/departments']}>
            <Routes>
              <Route path="/admin/departments" element={<DepartmentMasterPage />} />
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await screen.findByRole('heading', { name: 'Department Master' });
    expect(screen.getByText('Sales & BD')).toBeInTheDocument();
    expect(screen.getByText('SALES')).toBeInTheDocument();
    expect(screen.getByText('Operations & Delivery')).toBeInTheDocument();
    expect(screen.getByText('OPERATIONS')).toBeInTheDocument();
  });

  it('2. Department Master opens Add Modal and submits createDepartmentApi', async () => {
    vi.spyOn(deptApi, 'getDepartmentsApi').mockResolvedValue(mockDepartments);
    const createSpy = vi.spyOn(deptApi, 'createDepartmentApi').mockResolvedValue({
      department_id: 'dept-3',
      company_id: 'comp-1',
      department_code: 'FINANCE',
      department_name: 'Accounts & Finance',
      description: 'Invoicing and billing',
      status: 'ACTIVE',
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    });

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/admin/departments']}>
            <Routes>
              <Route path="/admin/departments" element={<DepartmentMasterPage />} />
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await screen.findByRole('heading', { name: 'Department Master' });

    // Open Add Modal
    const addBtn = screen.getByRole('button', { name: /Add Department/i });
    await userEvent.click(addBtn);

    expect(screen.getByRole('heading', { name: 'Add New Department' })).toBeInTheDocument();

    // Fill form
    const codeInput = screen.getByPlaceholderText(/e\.g\. SALES, ACCOUNTS/i);
    const nameInput = screen.getByPlaceholderText(/e\.g\. Sales & Marketing/i);

    await userEvent.type(codeInput, 'FINANCE');
    await userEvent.type(nameInput, 'Accounts & Finance');

    const submitBtn = screen.getByRole('button', { name: /Create Department/i });
    await userEvent.click(submitBtn);

    await waitFor(() => {
      expect(createSpy).toHaveBeenCalledWith({
        department_code: 'FINANCE',
        department_name: 'Accounts & Finance',
        description: null,
        status: 'ACTIVE',
      });
    });
  });

  it('3. Designation Master renders table with designations and level rank', async () => {
    vi.spyOn(desigApi, 'getDesignationsApi').mockResolvedValue(mockDesignations);

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/admin/designations']}>
            <Routes>
              <Route path="/admin/designations" element={<DesignationMasterPage />} />
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await screen.findByRole('heading', { name: 'Designation Master' });
    expect(screen.getByText('Executive')).toBeInTheDocument();
    expect(screen.getByText('EXECUTIVE')).toBeInTheDocument();
    expect(screen.getByText('Operations Manager')).toBeInTheDocument();
    expect(screen.getByText('MANAGER')).toBeInTheDocument();
    expect(screen.getByText('Level 1')).toBeInTheDocument();
    expect(screen.getByText('Level 5')).toBeInTheDocument();
    expect(screen.getByText('Managerial')).toBeInTheDocument();
  });

  it('4. Designation Master opens Add Modal and submits createDesignationApi', async () => {
    vi.spyOn(desigApi, 'getDesignationsApi').mockResolvedValue(mockDesignations);
    const createSpy = vi.spyOn(desigApi, 'createDesignationApi').mockResolvedValue({
      designation_id: 'desig-3',
      company_id: null,
      designation_code: 'DIRECTOR',
      designation_name: 'Managing Director',
      level_rank: 10,
      is_managerial: true,
      description: 'Executive leadership',
      status: 'ACTIVE',
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    });

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/admin/designations']}>
            <Routes>
              <Route path="/admin/designations" element={<DesignationMasterPage />} />
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await screen.findByRole('heading', { name: 'Designation Master' });

    const addBtn = screen.getByRole('button', { name: /Add Designation/i });
    await userEvent.click(addBtn);

    expect(screen.getByRole('heading', { name: 'Add New Designation' })).toBeInTheDocument();

    const codeInput = screen.getByPlaceholderText(/e\.g\. EXECUTIVE, MANAGER/i);
    const nameInput = screen.getByPlaceholderText(/e\.g\. Senior Operations Manager/i);
    const managerialCheckbox = screen.getByLabelText(/Is Managerial Position/i);

    await userEvent.type(codeInput, 'DIRECTOR');
    await userEvent.type(nameInput, 'Managing Director');
    await userEvent.click(managerialCheckbox);

    const submitBtn = screen.getByRole('button', { name: /Create Designation/i });
    await userEvent.click(submitBtn);

    await waitFor(() => {
      expect(createSpy).toHaveBeenCalledWith({
        designation_code: 'DIRECTOR',
        designation_name: 'Managing Director',
        level_rank: 1,
        is_managerial: true,
        description: null,
        status: 'ACTIVE',
      });
    });
  });
});

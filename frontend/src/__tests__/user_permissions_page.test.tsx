import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { UserPermissionsPage } from '../pages/UserPermissionsPage';
import * as permissionsApi from '../api/permissions';
import * as lookupApi from '../api/lookup';
import * as employeesApi from '../api/employees';
import * as authApi from '../api/auth';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule, PermissionCatalogResponse, UserPermissionsDetailResponse } from '../types/permission';
import type { PaginatedEmployees } from '../types/employee';
import { ACCESS_TOKEN_KEY } from '../api/client';

const mockAdminUser: CurrentUser = {
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

const mockAdminModules: AccessibleModule[] = [
  {
    module_id: '55555555-5555-5555-5555-555555555555',
    module_code: 'ADMIN',
    module_name: 'Administration',
    display_order: 1,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: true,
    can_approve: true,
    data_scope: 'ALL',
  },
];

const mockCatalog: PermissionCatalogResponse = {
  modules: [
    {
      module_code: 'SALES',
      module_name: 'Sales',
      pages: [
        {
          page_code: 'SALES_DASHBOARD',
          page_name: 'Sales Dashboard',
          display_order: 10,
          supported_actions: ['read', 'export'],
          action_slugs: { read: 'sales.dashboard.read', export: 'sales.dashboard.export' },
        },
        {
          page_code: 'SALES_CONFIRMED_ORDER',
          page_name: 'Create Confirmed Order',
          display_order: 20,
          supported_actions: ['read', 'write', 'update'],
          action_slugs: {
            read: 'sales.confirmed_order.read',
            write: 'sales.confirmed_order.create',
            update: 'sales.confirmed_order.update',
          },
        },
      ],
    },
    {
      module_code: 'OPERATIONS',
      module_name: 'Operation',
      pages: [
        {
          page_code: 'OPERATION_DASHBOARD',
          page_name: 'Operation Dashboard',
          display_order: 10,
          supported_actions: ['read', 'export'],
          action_slugs: { read: 'operation.dashboard.read', export: 'operation.dashboard.export' },
        },
        {
          page_code: 'OPERATION_TASK_ASSIGNMENT',
          page_name: 'Task Assignment',
          display_order: 20,
          supported_actions: ['read', 'assign', 'reassign'],
          action_slugs: {
            read: 'operation.tasks.read',
            assign: 'operation.tasks.assign',
            reassign: 'operation.tasks.reassign',
          },
        },
      ],
    },
  ],
};

const mockEmployeeList: PaginatedEmployees = {
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
    {
      user_id: 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
      employee_code: 'CG0003',
      first_name: 'Anita',
      middle_name: null,
      last_name: 'Sharma',
      official_email: 'anita.s@gocompliances.in',
      personal_email: null,
      mobile_number: '+919876543212',
      company_id: '22222222-2222-2222-2222-222222222222',
      department_id: '33333333-3333-3333-3333-333333333333',
      designation_id: '44444444-4444-4444-4444-444444444444',
      company_name: 'Gocompliances',
      company_code: 'GOCOMPLIANCES',
      department_name: 'Operations',
      department_code: 'OPERATIONS',
      designation_name: 'Operations Lead',
      designation_code: 'OPS_LEAD',
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
  page_size: 100,
  total: 2,
  pages: 1,
};

const mockUserPermissions: UserPermissionsDetailResponse = {
  user_id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  employee_code: 'CG0002',
  first_name: 'Rohit',
  last_name: 'Verma',
  official_email: 'rohit.v@gocompliances.in',
  company_id: '22222222-2222-2222-2222-222222222222',
  department_id: '33333333-3333-3333-3333-333333333333',
  designation_id: '44444444-4444-4444-4444-444444444444',
  is_active: true,
  is_hod: false,
  is_reporting_manager: false,
  manager_user_id: '11111111-1111-1111-1111-111111111111',
  primary_location: 'Delhi Regional Office',
  permissions: [
    {
      page_code: 'SALES_DASHBOARD',
      can_view: true,
      can_create: false,
      can_edit: false,
      can_delete: false,
      can_assign: false,
      can_reassign: false,
      can_export: false,
      can_approve: false,
      data_scope: 'SELF',
      status: 'ACTIVE',
    },
    {
      page_code: 'SALES_CONFIRMED_ORDER',
      can_view: true,
      can_create: true,
      can_edit: false,
      can_delete: false,
      can_assign: false,
      can_reassign: false,
      can_export: false,
      can_approve: false,
      data_scope: 'SELF',
      status: 'ACTIVE',
    },
  ],
};

describe('Frontend UserPermissionsPage Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock_jwt_token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockAdminModules);
    vi.spyOn(permissionsApi, 'getPermissionCatalogApi').mockResolvedValue(mockCatalog);
    vi.spyOn(employeesApi, 'getEmployeesApi').mockResolvedValue(mockEmployeeList);
    vi.spyOn(lookupApi, 'getLookupCompaniesApi').mockResolvedValue([
      {
        company_id: '22222222-2222-2222-2222-222222222222',
        company_code: 'GOCOMPLIANCES',
        company_name: 'Gocompliances',
        employee_code_prefix: 'CG',
      },
    ]);
    vi.spyOn(lookupApi, 'getLookupManagersApi').mockResolvedValue([
      {
        user_id: '11111111-1111-1111-1111-111111111111',
        employee_code: 'CG0001',
        first_name: 'Admin',
        last_name: 'Director',
        official_email: 'director@gocompliances.in',
        designation_name: 'Director',
      },
    ]);
    vi.spyOn(permissionsApi, 'getUserPermissionsApi').mockResolvedValue(mockUserPermissions);
    vi.spyOn(permissionsApi, 'saveUserPermissionsApi').mockResolvedValue(mockUserPermissions);
    vi.spyOn(permissionsApi, 'copyUserPermissionsApi').mockResolvedValue({
      message: 'Successfully copied permissions',
      copied_count: 4,
      source_user_id: 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
      target_user_id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    });
  });

  it('verifies that old placeholder text is completely eliminated', async () => {
    render(
      <MemoryRouter initialEntries={['/admin/access']}>
        <AuthProvider>
          <UserPermissionsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('User Permission')).toBeInTheDocument();
    });

    // Check placeholder texts do NOT exist
    expect(screen.queryByText(/Scheduled for Stage 10B/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Coming Soon/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/interactive management interface/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Return to Employee Directory/i)).not.toBeInTheDocument();
  });

  it('renders top controls, table columns and handles employee selection', async () => {
    render(
      <MemoryRouter initialEntries={['/admin/access']}>
        <AuthProvider>
          <UserPermissionsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByLabelText('Select Employee')).toBeInTheDocument();
    });

    const employeeSelect = screen.getByLabelText('Select Employee');
    fireEvent.change(employeeSelect, {
      target: { value: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa' },
    });

    await waitFor(() => {
      expect(screen.getByText('Sales Module')).toBeInTheDocument();
      expect(screen.getByText('Sales Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Create Confirmed Order')).toBeInTheDocument();
      expect(screen.getByText('Operation Module')).toBeInTheDocument();
      expect(screen.getByText('Task Assignment')).toBeInTheDocument();
    });

    // Verify unsupported actions are not rendered (Sales Dashboard does not have DELETE or ASSIGN)
    expect(screen.queryByTestId('perm-SALES_DASHBOARD-delete')).not.toBeInTheDocument();
    expect(screen.queryByTestId('perm-SALES_DASHBOARD-assign')).not.toBeInTheDocument();

    // Verify settings panel
    expect(screen.getByDisplayValue('rohit.v@gocompliances.in')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Delhi Regional Office')).toBeInTheDocument();
  });

  it('toggles page-level All, module-level Select All and saves permissions', async () => {
    render(
      <MemoryRouter initialEntries={['/admin/access']}>
        <AuthProvider>
          <UserPermissionsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const employeeSelect = await screen.findByLabelText('Select Employee');
    fireEvent.change(employeeSelect, {
      target: { value: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa' },
    });

    await screen.findByText('Create Confirmed Order');

    // Toggle WRITE button on Create Confirmed Order
    const writeBtn = screen.getByRole('button', { name: /WRITE/i });
    fireEvent.click(writeBtn);

    // Save button should be enabled
    const saveBtn = screen.getByRole('button', { name: /Save/i });
    expect(saveBtn).not.toBeDisabled();
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(permissionsApi.saveUserPermissionsApi).toHaveBeenCalledWith(
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        expect.objectContaining({
          permissions: expect.any(Array),
          user_settings: expect.objectContaining({
            primary_location: 'Delhi Regional Office',
          }),
        })
      );
    });
  });

  it('handles copy permissions flow with modal confirmation', async () => {
    render(
      <MemoryRouter initialEntries={['/admin/access']}>
        <AuthProvider>
          <UserPermissionsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const employeeSelect = await screen.findByLabelText('Select Employee');
    fireEvent.change(employeeSelect, {
      target: { value: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa' },
    });

    await screen.findByText('Sales Dashboard');

    const copySelect = screen.getByLabelText('Copy Permissions Source Employee');
    fireEvent.change(copySelect, {
      target: { value: 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb' },
    });

    const copyBtn = screen.getByRole('button', { name: /Copy Sales and Operation Permissions/i });
    expect(copyBtn).not.toBeDisabled();
    fireEvent.click(copyBtn);

    // Modal appears
    await waitFor(() => {
      expect(screen.getByText('Confirm Permission Copy')).toBeInTheDocument();
    });

    const confirmBtn = screen.getByRole('button', { name: /Yes, Copy Permissions/i });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(permissionsApi.copyUserPermissionsApi).toHaveBeenCalledWith(
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        {
          source_user_id: 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        }
      );
    });
  });

  it('renders 403 Forbidden state when user lacks admin access', async () => {
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue([]);

    render(
      <MemoryRouter initialEntries={['/admin/access']}>
        <AuthProvider>
          <UserPermissionsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('403 - Access Forbidden')).toBeInTheDocument();
    });
  });
});

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { UserPermissionsPage } from '../pages/UserPermissionsPage';
import * as permissionsApi from '../api/permissions';
import * as lookupApi from '../api/lookup';
import * as employeesApi from '../api/employees';
import * as authApi from '../api/auth';
import { CurrentUser } from '../types/auth';
import { AccessibleModule, PermissionCatalogResponse, UserPermissionsDetailResponse } from '../types/permission';
import { PaginatedEmployees } from '../types/employee';

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
    module_code: 'ADMIN_EMPLOYEES',
    module_name: 'Employee Management',
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
          display_order: 1,
          supported_actions: ['read'],
          action_slugs: { read: 'sales.dashboard.read' },
        },
        {
          page_code: 'SALES_CONFIRMED_ORDER',
          page_name: 'Confirmed Order',
          display_order: 2,
          supported_actions: ['read', 'write', 'update', 'delete', 'export'],
          action_slugs: {
            read: 'sales.confirmed_order.read',
            write: 'sales.confirmed_order.create',
            update: 'sales.confirmed_order.edit',
            delete: 'sales.confirmed_order.delete',
            export: 'sales.confirmed_order.export',
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
          display_order: 1,
          supported_actions: ['read'],
          action_slugs: { read: 'operation.dashboard.read' },
        },
        {
          page_code: 'OPERATION_TASK_ASSIGNMENT',
          page_name: 'Task Assignment',
          display_order: 2,
          supported_actions: ['read', 'assign', 'reassign', 'export'],
          action_slugs: {
            read: 'operation.tasks.read',
            assign: 'operation.tasks.assign',
            reassign: 'operation.tasks.reassign',
            export: 'operation.tasks.export',
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
      can_edit: true,
      can_delete: false,
      can_assign: false,
      can_reassign: false,
      can_export: true,
      can_approve: false,
      data_scope: 'SELF',
      status: 'ACTIVE',
    },
  ],
};

describe('UserPermissionsPage Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.setItem('gocompliance_admin_access_token', 'mock_jwt_token');
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

  it('renders initial page state with empty selection prompt', async () => {
    render(
      <MemoryRouter initialEntries={['/permissions']}>
        <AuthProvider>
          <UserPermissionsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('User Permission')).toBeInTheDocument();
      expect(screen.getByText('No Employee Selected')).toBeInTheDocument();
    });
  });

  it('loads permissions and populates matrix when employee is selected', async () => {
    render(
      <MemoryRouter initialEntries={['/permissions']}>
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
      expect(screen.getByText('Confirmed Order')).toBeInTheDocument();
      expect(screen.getByText('Operation Module')).toBeInTheDocument();
      expect(screen.getByText('Task Assignment')).toBeInTheDocument();
    });

    // Check user settings panel populated
    expect(screen.getByDisplayValue('rohit.v@gocompliances.in')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Delhi Regional Office')).toBeInTheDocument();
  });

  it('toggles action permissions and enables Save button', async () => {
    render(
      <MemoryRouter initialEntries={['/permissions']}>
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

    // Toggle delete action on Confirmed Order
    const deleteBtn = screen.getByRole('button', { name: /DELETE/i });
    fireEvent.click(deleteBtn);

    // Save button should now trigger API call
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

  it('handles Copy Permissions flow with confirmation modal', async () => {
    render(
      <MemoryRouter initialEntries={['/permissions']}>
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

    // Select source employee for copying
    const copySelect = screen.getByLabelText('Copy Permissions Source Employee');
    fireEvent.change(copySelect, {
      target: { value: 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb' },
    });

    const copyBtn = screen.getByRole('button', { name: /Copy Other Permission/i });
    expect(copyBtn).not.toBeDisabled();
    fireEvent.click(copyBtn);

    // Confirmation Modal should appear
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
});

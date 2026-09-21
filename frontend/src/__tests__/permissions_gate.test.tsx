import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { AuthProvider } from '../context/AuthContext';
import { PermissionGate } from '../components/common/PermissionGate';
import { usePermissions } from '../hooks/usePermissions';
import * as authApi from '../api/auth';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';

import { ACCESS_TOKEN_KEY } from '../api/client';

const mockUser: CurrentUser = {
  user_id: 'user-12345',
  employee_code: 'CG0099',
  first_name: 'Test',
  last_name: 'User',
  official_email: 'test.user@gocompliances.in',
  mobile_number: '+919876543299',
  company_id: 'comp-111',
  department_id: 'dept-222',
  designation_id: 'desig-333',
  account_status: 'ACTIVE',
  must_change_password: false,
  is_hod: true,
  is_reporting_manager: true,
};

const mockModules: AccessibleModule[] = [
  {
    module_id: 'mod-1',
    module_code: 'SALES_DASHBOARD',
    module_name: 'Sales Dashboard',
    display_order: 1,
    is_navigation: true,
    can_view: true,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_approve: false,
    data_scope: 'SELF',
  },
  {
    module_id: 'mod-2',
    module_code: 'OPERATION_TASK_ASSIGNMENT',
    module_name: 'Task Assignment',
    display_order: 2,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: false,
    can_approve: false,
    can_assign: true,
    can_reassign: true,
    can_export: true,
    data_scope: 'DEPARTMENT',
  },
];

const PermissionHookConsumer: React.FC = () => {
  const { can, canSlug, isHod, isReportingManager, getScope } = usePermissions();

  return (
    <div>
      <div data-testid="is-hod">{isHod ? 'YES_HOD' : 'NO_HOD'}</div>
      <div data-testid="is-rm">{isReportingManager ? 'YES_RM' : 'NO_RM'}</div>
      <div data-testid="can-view-sales">{can('SALES_DASHBOARD', 'view') ? 'CAN_VIEW_SALES' : 'NO_SALES'}</div>
      <div data-testid="can-assign-tasks">{can('OPERATION_TASK_ASSIGNMENT', 'assign') ? 'CAN_ASSIGN' : 'NO_ASSIGN'}</div>
      <div data-testid="can-slug-assign">{canSlug('operation.task_assignment.assign') ? 'SLUG_CAN_ASSIGN' : 'SLUG_NO_ASSIGN'}</div>
      <div data-testid="scope-tasks">{getScope('OPERATION_TASK_ASSIGNMENT')}</div>
    </div>
  );
};

describe('Frontend Permission Hook & Gate', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock_jwt');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModules);
  });

  it('evaluates fine-grained permissions and user flags via usePermissions hook', async () => {
    render(
      <AuthProvider>
        <PermissionHookConsumer />
      </AuthProvider>
    );

    await screen.findByText('YES_HOD');
    expect(screen.getByTestId('is-hod').textContent).toBe('YES_HOD');
    expect(screen.getByTestId('is-rm').textContent).toBe('YES_RM');
    expect(screen.getByTestId('can-view-sales').textContent).toBe('CAN_VIEW_SALES');
    expect(screen.getByTestId('can-assign-tasks').textContent).toBe('CAN_ASSIGN');
    expect(screen.getByTestId('can-slug-assign').textContent).toBe('SLUG_CAN_ASSIGN');
    expect(screen.getByTestId('scope-tasks').textContent).toBe('DEPARTMENT');
  });

  it('renders children when PermissionGate condition is met', async () => {
    render(
      <AuthProvider>
        <PermissionGate module="OPERATION_TASK_ASSIGNMENT" action="assign">
          <button id="assign-btn">Assign Task</button>
        </PermissionGate>
      </AuthProvider>
    );

    await screen.findByRole('button', { name: 'Assign Task' });
    expect(screen.getByRole('button', { name: 'Assign Task' })).toBeInTheDocument();
  });

  it('renders fallback or null when PermissionGate condition is not met', async () => {
    render(
      <AuthProvider>
        <PermissionGate
          module="SALES_DASHBOARD"
          action="create"
          fallback={<span>Access Denied</span>}
        >
          <button id="create-order-btn">Create Order</button>
        </PermissionGate>
      </AuthProvider>
    );

    await screen.findByText('Access Denied');
    expect(screen.queryByRole('button', { name: 'Create Order' })).not.toBeInTheDocument();
    expect(screen.getByText('Access Denied')).toBeInTheDocument();
  });
});

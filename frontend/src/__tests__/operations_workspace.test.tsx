import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { OperationsLayout } from '../components/operations/OperationsLayout';
import { OperationsDashboardPage } from '../pages/operations/OperationsDashboardPage';
import { MyTasksPage } from '../pages/operations/MyTasksPage';
import { TaskAssignmentPage } from '../pages/operations/TaskAssignmentPage';
import * as authApi from '../api/auth';
import * as operationsApi from '../api/operations';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';
import type {
  OperationsDashboardResponse,
  OperationApplicationDetail,
  OperationsTaskListResponse,
  AssigneeOption,
} from '../types/operations';

// Mock ResizeObserver for test environment
globalThis.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

const mockDeepakUser: CurrentUser = {
  user_id: 'usr-deepak-0005',
  employee_code: 'CG0005',
  first_name: 'Deepak',
  last_name: 'Kumar',
  official_email: 'deepak.kumar@gocompliances.com',
  mobile_number: '+919876543210',
  company_id: 'comp-1',
  department_id: 'dept-operations',
  designation_id: 'desig-ops-exec',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const mockOperationsModules: AccessibleModule[] = [
  {
    module_id: 'mod-ops',
    module_code: 'OPERATIONS',
    module_name: 'Operations',
    display_order: 20,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: false,
    can_approve: true,
    can_export: true,
    data_scope: 'SELF',
  },
  {
    module_id: 'mod-ops-dash',
    module_code: 'OPERATIONS_DASHBOARD',
    module_name: 'Operations Dashboard',
    display_order: 21,
    is_navigation: true,
    can_view: true,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_approve: false,
    can_export: true,
    data_scope: 'SELF',
  },
  {
    module_id: 'mod-ops-tasks',
    module_code: 'OPS_APPLICATIONS',
    module_name: 'My Tasks',
    display_order: 22,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: false,
    can_approve: true,
    can_export: true,
    data_scope: 'SELF',
  },
];

const mockDashboardData: OperationsDashboardResponse = {
  kpis: {
    total_applications: 12,
    assigned_count: 5,
    in_progress_count: 7,
    pending_documents_count: 2,
    ready_submitted_count: 4,
    authority_query_count: 1,
    approved_count: 25,
    overdue_count: 1,
    unassigned_count: 3,
    sla_adherence_percent: 94.5,
  },
  status_breakdown: [
    { status: 'UNASSIGNED', label: 'Unassigned', count: 3, percentage: 25, color: '#f59e0b' },
    { status: 'ASSIGNED', label: 'Assigned', count: 2, percentage: 16.7, color: '#3b82f6' },
    { status: 'IN_PROGRESS', label: 'In Progress', count: 4, percentage: 33.3, color: '#6366f1' },
    { status: 'APPROVED', label: 'Approved', count: 2, percentage: 16.7, color: '#10b981' },
    { status: 'REJECTED', label: 'Rejected', count: 1, percentage: 8.3, color: '#ef4444' },
  ],
  workload_by_executive: [
    {
      user_id: 'usr-deepak-0005',
      employee_code: 'CG0005',
      full_name: 'Deepak Kumar',
      designation_name: 'Operations Executive',
      active_tasks: 5,
      in_progress_tasks: 3,
      completed_tasks: 10,
      overdue_tasks: 0,
      sla_rating: 98.0,
    },
  ],
  recent_applications: [
    {
      application_id: 'app-kapper-0001',
      application_number: 'AP-2026-0001',
      company_id: 'comp-1',
      sales_order_id: 'ord-kapper-0001',
      sales_order_number: 'SO-2026-0001',
      client_id: 'cli-kapper-0001',
      client_name: 'KAPPER',
      client_phone: '+919876543210',
      service_id: 'srv-clinical-0001',
      service_name: 'Clinical Establishment',
      service_code: 'MED-CE',
      assigned_to_user_id: 'usr-deepak-0005',
      assigned_to_name: 'Deepak Kumar',
      assigned_to_code: 'CG0005',
      salesperson_name: 'Karishma Upadhyay',
      salesperson_code: 'GC0001',
      priority: 'HIGH',
      application_status: 'ASSIGNED',
      target_due_date: '2026-09-30',
      formatted_due_date: '30 Sep 2026',
      documents_completed: 1,
      documents_total: 2,
      is_overdue: false,
      is_due_soon: false,
      created_at: '2026-09-23T10:00:00Z',
      updated_at: '2026-09-23T11:00:00Z',
    },
  ],
  priority_queue: [
    {
      application_id: 'app-kapper-0001',
      application_number: 'AP-2026-0001',
      company_id: 'comp-1',
      sales_order_id: 'ord-kapper-0001',
      sales_order_number: 'SO-2026-0001',
      client_id: 'cli-kapper-0001',
      client_name: 'KAPPER',
      client_phone: '+919876543210',
      service_id: 'srv-clinical-0001',
      service_name: 'Clinical Establishment',
      service_code: 'MED-CE',
      assigned_to_user_id: 'usr-deepak-0005',
      assigned_to_name: 'Deepak Kumar',
      assigned_to_code: 'CG0005',
      salesperson_name: 'Karishma Upadhyay',
      salesperson_code: 'GC0001',
      priority: 'HIGH',
      application_status: 'ASSIGNED',
      target_due_date: '2026-09-30',
      formatted_due_date: '30 Sep 2026',
      documents_completed: 1,
      documents_total: 2,
      is_overdue: false,
      is_due_soon: false,
      created_at: '2026-09-23T10:00:00Z',
      updated_at: '2026-09-23T11:00:00Z',
    },
  ],
  scope: 'SELF',
  company_id: 'comp-1',
  company_name: 'GoCompliance Corp',
};

const mockTaskListResponse: OperationsTaskListResponse = {
  items: [
    {
      application_id: 'app-kapper-0001',
      application_number: 'AP-2026-0001',
      company_id: 'comp-1',
      sales_order_id: 'ord-kapper-0001',
      sales_order_number: 'SO-2026-0001',
      client_id: 'cli-kapper-0001',
      client_name: 'KAPPER',
      client_phone: '+919876543210',
      service_id: 'srv-clinical-0001',
      service_name: 'Clinical Establishment',
      service_code: 'MED-CE',
      assigned_to_user_id: 'usr-deepak-0005',
      assigned_to_name: 'Deepak Kumar',
      assigned_to_code: 'CG0005',
      salesperson_name: 'Karishma Upadhyay',
      salesperson_code: 'GC0001',
      priority: 'HIGH',
      application_status: 'ASSIGNED',
      target_due_date: '2026-09-30',
      formatted_due_date: '30 Sep 2026',
      documents_completed: 1,
      documents_total: 2,
      is_overdue: false,
      is_due_soon: false,
      latest_remark: {
        remark_id: 'rem-1',
        application_id: 'app-kapper-0001',
        author_user_id: 'usr-deepak-0005',
        author_name: 'Deepak Kumar',
        author_employee_code: 'CG0005',
        author_department: 'Operations',
        remark_text: 'Awaiting NOC clearance from state medical board.',
        created_at: '2026-09-23T11:00:00Z',
        formatted_created_at: '23 Sep 2026, 11:00 AM',
      },
      created_at: '2026-09-23T10:00:00Z',
      updated_at: '2026-09-23T11:00:00Z',
    },
  ],
  total_count: 1,
  page: 1,
  limit: 20,
  total_pages: 1,
  summary: {
    total_tasks: 1,
    assigned: 1,
    in_progress: 0,
    pending_docs: 0,
    under_review: 0,
    completed: 0,
    overdue: 0,
  },
};

const mockKapperTask: OperationApplicationDetail = {
  application_id: 'app-kapper-0001',
  application_number: 'AP-2026-0001',
  company_id: 'comp-1',
  sales_order_id: 'ord-kapper-0001',
  sales_order_number: 'SO-2026-0001',
  client_id: 'cli-kapper-0001',
  client_name: 'KAPPER',
  client_phone: '+919876543210',
  client_email: 'contact@kapper.test',
  service_id: 'srv-clinical-0001',
  service_name: 'Clinical Establishment',
  service_code: 'MED-CE',
  assigned_to_user_id: 'usr-deepak-0005',
  assigned_to_name: 'Deepak Kumar',
  assigned_to_code: 'CG0005',
  assigned_by_user_id: 'usr-karishma-0001',
  assigned_by_name: 'Karishma Upadhyay',
  assigned_at: '2026-09-23T10:00:00Z',
  formatted_assigned_at: '23 Sep 2026',
  salesperson_name: 'Karishma Upadhyay',
  salesperson_code: 'GC0001',
  application_status: 'ASSIGNED',
  priority: 'HIGH',
  target_due_date: '2026-09-30',
  formatted_due_date: '30 Sep 2026',
  assignment_notes: 'Priority order from Karishma',
  documents_completed: 1,
  documents_total: 2,
  is_overdue: false,
  is_due_soon: false,
  created_at: '2026-09-23T10:00:00Z',
  updated_at: '2026-09-23T11:00:00Z',
  documents: [
    {
      app_doc_id: 'doc-1',
      application_id: 'app-kapper-0001',
      document_code: 'DOC_TL',
      document_name: 'Trade License',
      is_mandatory: true,
      status: 'PENDING',
      created_at: '2026-09-23T10:00:00Z',
      updated_at: '2026-09-23T10:00:00Z',
    },
    {
      app_doc_id: 'doc-2',
      application_id: 'app-kapper-0001',
      document_code: 'DOC_MSR',
      document_name: 'Medical Staff Registration',
      is_mandatory: true,
      status: 'VERIFIED',
      created_at: '2026-09-23T10:00:00Z',
      updated_at: '2026-09-23T10:00:00Z',
    },
  ],
  assignment_history: [
    {
      history_id: 'hist-1',
      application_id: 'app-kapper-0001',
      assigned_by_user_id: 'usr-karishma-0001',
      previous_assignee_name: null,
      new_assignee_name: 'Deepak Kumar',
      assigned_by_name: 'Karishma Upadhyay',
      reason: 'Initial assignment',
      assigned_at: '2026-09-23T10:00:00Z',
    },
  ],
  activity_logs: [],
  latest_remark: {
    remark_id: 'rem-1',
    application_id: 'app-kapper-0001',
    author_user_id: 'usr-deepak-0005',
    author_name: 'Deepak Kumar',
    author_employee_code: 'CG0005',
    author_department: 'Operations',
    remark_text: 'Awaiting NOC clearance from state medical board.',
    created_at: '2026-09-23T11:00:00Z',
    formatted_created_at: '23 Sep 2026, 11:00 AM',
  },
  remarks: [
    {
      remark_id: 'rem-1',
      application_id: 'app-kapper-0001',
      author_user_id: 'usr-deepak-0005',
      author_name: 'Deepak Kumar',
      author_employee_code: 'CG0005',
      author_department: 'Operations',
      remark_text: 'Awaiting NOC clearance from state medical board.',
      created_at: '2026-09-23T11:00:00Z',
      formatted_created_at: '23 Sep 2026, 11:00 AM',
    },
  ],
};

const mockAssignees: AssigneeOption[] = [
  {
    user_id: 'usr-deepak-0005',
    employee_code: 'CG0005',
    full_name: 'Deepak Kumar',
    name: 'Deepak Kumar',
    department_name: 'Operations',
    designation_name: 'Operations Executive',
  },
  {
    user_id: 'usr-mansi-0002',
    employee_code: 'CG0002',
    full_name: 'Mansi Sharma',
    name: 'Mansi Sharma',
    department_name: 'Operations',
    designation_name: 'Senior Operations Executive',
  },
];

describe('Operations Workspace & Connected Workflow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'fake-token-deepak');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockDeepakUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockOperationsModules);
    vi.spyOn(operationsApi, 'getOperationsDashboardApi').mockResolvedValue(mockDashboardData);
    vi.spyOn(operationsApi, 'getMyOperationsTasksApi').mockResolvedValue(mockTaskListResponse);
    vi.spyOn(operationsApi, 'getOperationTaskDetailApi').mockResolvedValue(mockKapperTask);
    vi.spyOn(operationsApi, 'getOperationsAssigneesApi').mockResolvedValue(mockAssignees);
  });

  it('renders Operations Dashboard with KPIs and recent tasks', async () => {
    render(
      <MemoryRouter initialEntries={['/operations/dashboard']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="dashboard" element={<OperationsDashboardPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    // Wait for Dashboard heading
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /operation dashboard/i })).toBeInTheDocument();
    });

    // Verify KPI numbers
    expect(screen.getByText('12')).toBeInTheDocument(); // Total tasks
    expect(screen.getByText('3')).toBeInTheDocument(); // Unassigned
    expect(screen.getByText('7')).toBeInTheDocument(); // In Progress
    expect(screen.getByText('25')).toBeInTheDocument(); // Approved

    // Verify Recent Applications shows KAPPER
    expect(screen.getAllByText('KAPPER').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Clinical Establishment').length).toBeGreaterThan(0);
  });

  it('displays KAPPER task in Deepak Kumar My Tasks workspace', async () => {
    render(
      <MemoryRouter initialEntries={['/operations/my-tasks']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="my-tasks" element={<MyTasksPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    // Wait for KAPPER row in table
    await waitFor(() => {
      expect(screen.getByText('KAPPER')).toBeInTheDocument();
    });

    // Check KAPPER row details
    expect(screen.getByText('AP-2026-0001')).toBeInTheDocument();
    expect(screen.getByText('SO-2026-0001')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
  });

  it('opens Task Detail Modal and updates document verification and status', async () => {
    const user = userEvent.setup();
    const updateAppStatusSpy = vi.spyOn(operationsApi, 'updateOperationTaskStatusApi').mockResolvedValue({
      ...mockKapperTask,
      application_status: 'IN_PROGRESS',
    });

    render(
      <MemoryRouter initialEntries={['/operations/my-tasks']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="my-tasks" element={<MyTasksPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    // Wait for row and click Open Task button
    await waitFor(() => {
      expect(screen.getByText('KAPPER')).toBeInTheDocument();
    });

    const viewButton = screen.getByRole('button', { name: /open task/i });
    await user.click(viewButton);

    // Verify modal content
    await waitFor(() => {
      expect(screen.getByText('Client & Service Information')).toBeInTheDocument();
    });

    // Verify status action button exists
    const inProgressBtn = screen.getByRole('button', { name: /start work \(in progress\)/i });
    expect(inProgressBtn).toBeInTheDocument();
    await user.click(inProgressBtn);

    expect(updateAppStatusSpy).toHaveBeenCalledWith('app-kapper-0001', {
      new_status: 'IN_PROGRESS',
      comment: undefined,
    });
  });

  it('allows reassigning task in TaskAssignmentPage', async () => {
    const user = userEvent.setup();
    const reassignSpy = vi.spyOn(operationsApi, 'reassignOperationTaskApi').mockResolvedValue({
      ...mockKapperTask,
      assigned_to_user_id: 'usr-mansi-0002',
      assigned_to_name: 'Mansi Sharma',
      assigned_to_code: 'CG0002',
    });
    vi.spyOn(operationsApi, 'getOperationsTasksApi').mockResolvedValue(mockTaskListResponse);

    render(
      <MemoryRouter initialEntries={['/operations/assignment']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="assignment" element={<TaskAssignmentPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    // Wait for table to load KAPPER
    await waitFor(() => {
      expect(screen.getByText('KAPPER')).toBeInTheDocument();
    });

    const reassignBtn = screen.getByRole('button', { name: /reassign/i });
    await user.click(reassignBtn);

    // Modal should open
    await waitFor(() => {
      expect(screen.getByText('Reassign Application AP-2026-0001')).toBeInTheDocument();
    });

    // Choose Mansi
    const selectElem = screen.getByLabelText(/new operations assignee/i);
    await user.selectOptions(selectElem, 'usr-mansi-0002');

    // Fill reason
    const reasonInput = screen.getByLabelText(/mandatory reassignment reason/i);
    await user.type(reasonInput, 'Workload rebalance across team');

    const confirmReassignBtn = screen.getByRole('button', { name: /confirm reassignment/i });
    await user.click(confirmReassignBtn);

    expect(reassignSpy).toHaveBeenCalledWith(
      'app-kapper-0001',
      expect.objectContaining({
        new_assignee_user_id: 'usr-mansi-0002',
        reason: 'Workload rebalance across team',
      })
    );
  });

  it('renders My Assigned Tasks page with correct title, KPI summary, and records', async () => {
    render(
      <MemoryRouter initialEntries={['/operations/my-tasks']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="my-tasks" element={<MyTasksPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /my assigned tasks/i })).toBeInTheDocument();
    });

    expect(screen.getByText('Total Assigned')).toBeInTheDocument();
    expect(screen.getByText('KAPPER')).toBeInTheDocument();
    expect(screen.getByText('AP-2026-0001')).toBeInTheDocument();
  });

  it('renders All Operations Tasks page with assignee filter options and summary counts', async () => {
    render(
      <MemoryRouter initialEntries={['/operations/task-assignment']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="task-assignment" element={<TaskAssignmentPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /all operations tasks & work assignment/i })).toBeInTheDocument();
    });

    expect(screen.getByText('Total Tasks')).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /all assignees/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /deepak kumar/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /mansi sharma/i })).toBeInTheDocument();
  });

  it('renders Operations Remarks on Task Detail modal and allows current assignee to add a remark', async () => {
    const user = userEvent.setup();
    const addRemarkSpy = vi.spyOn(operationsApi, 'addOperationRemarkApi').mockResolvedValue({
      remark_id: 'rem-2',
      application_id: 'app-kapper-0001',
      author_user_id: 'usr-deepak-0005',
      author_name: 'Deepak Kumar',
      author_employee_code: 'CG0005',
      author_department: 'Operations',
      remark_text: 'Authority raised query regarding medical council registration date.',
      created_at: '2026-09-24T14:30:00Z',
      formatted_created_at: '24 Sep 2026, 02:30 PM',
    });

    render(
      <MemoryRouter initialEntries={['/operations/my-tasks']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="my-tasks" element={<MyTasksPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    // Open task modal
    await waitFor(() => {
      expect(screen.getByText('KAPPER')).toBeInTheDocument();
    });
    const viewButton = screen.getByRole('button', { name: /open task/i });
    await user.click(viewButton);

    // Verify Latest Operations Remark banner and Overview section
    await waitFor(() => {
      expect(screen.getByText('Latest Operations Remark')).toBeInTheDocument();
    });
    expect(screen.getAllByText('Awaiting NOC clearance from state medical board.').length).toBeGreaterThan(0);

    // Type new remark
    const remarkTextarea = screen.getByPlaceholderText(/add explanation for delay, blocked status/i);
    await user.type(remarkTextarea, 'Authority raised query regarding medical council registration date.');

    const addRemarkBtn = screen.getByRole('button', { name: /add remark/i });
    expect(addRemarkBtn).not.toBeDisabled();
    await user.click(addRemarkBtn);

    expect(addRemarkSpy).toHaveBeenCalledWith('app-kapper-0001', {
      remark_text: 'Authority raised query regarding medical council registration date.',
    });
  });

  it('shows chronological remarks history and navigates to the dedicated Remarks tab', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/operations/my-tasks']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="my-tasks" element={<MyTasksPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('KAPPER')).toBeInTheDocument();
    });
    await user.click(screen.getByRole('button', { name: /open task/i }));

    // Verify Remarks tab button exists
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /operations remarks/i })).toBeInTheDocument();
    });

    // Click on Remarks tab
    const remarksTabBtn = screen.getByRole('button', { name: /operations remarks/i });
    await user.click(remarksTabBtn);

    // Verify Remarks History header and existing remark content
    expect(screen.getByText('Operations Remarks History')).toBeInTheDocument();
    expect(screen.getAllByText('Awaiting NOC clearance from state medical board.').length).toBeGreaterThan(0);
  });

  it('displays restriction notice on cancelled tasks preventing new remarks', async () => {
    const user = userEvent.setup();
    vi.spyOn(operationsApi, 'getOperationTaskDetailApi').mockResolvedValue({
      ...mockKapperTask,
      application_status: 'CANCELLED',
    });

    render(
      <MemoryRouter initialEntries={['/operations/my-tasks']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="my-tasks" element={<MyTasksPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('KAPPER')).toBeInTheDocument();
    });
    await user.click(screen.getByRole('button', { name: /open task/i }));

    // Check cancellation notice
    await waitFor(() => {
      expect(screen.getByText(/remarks cannot be added to a cancelled or deleted task/i)).toBeInTheDocument();
    });
    expect(screen.queryByPlaceholderText(/add explanation for delay/i)).not.toBeInTheDocument();
  });

  it('renders Latest Remark column in My Assigned Tasks table showing remark preview and author', async () => {
    render(
      <MemoryRouter initialEntries={['/operations/my-tasks']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="my-tasks" element={<MyTasksPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    // Wait for table header and row
    await waitFor(() => {
      expect(screen.getByText('Latest Remark')).toBeInTheDocument();
    });
    expect(screen.getAllByText('Awaiting NOC clearance from state medical board.').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Deepak Kumar').length).toBeGreaterThan(0);
  });

  it('clicking on Latest Remark preview card in table opens task modal directly to remarks tab', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/operations/my-tasks']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="my-tasks" element={<MyTasksPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Latest Remark')).toBeInTheDocument();
    });

    const remarkPreview = screen.getByText('Awaiting NOC clearance from state medical board.');
    await user.click(remarkPreview);

    // Should open modal directly with Operations Remarks History active
    await waitFor(() => {
      expect(screen.getByText('Operations Remarks History')).toBeInTheDocument();
    });
  });

  it('renders "No update yet" in table when task has no latest_remark', async () => {
    vi.spyOn(operationsApi, 'getMyOperationsTasksApi').mockResolvedValue({
      ...mockTaskListResponse,
      items: [
        {
          ...mockTaskListResponse.items[0],
          latest_remark: undefined,
        },
      ],
    });

    render(
      <MemoryRouter initialEntries={['/operations/my-tasks']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="my-tasks" element={<MyTasksPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('No update yet')).toBeInTheDocument();
    });
  });

  it('renders Latest Remark column in All Operations Tasks (TaskAssignmentPage)', async () => {
    vi.spyOn(operationsApi, 'getOperationsTasksApi').mockResolvedValue(mockTaskListResponse);

    render(
      <MemoryRouter initialEntries={['/operations/task-assignment']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/operations" element={<OperationsLayout />}>
                <Route path="task-assignment" element={<TaskAssignmentPage />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Latest Remark')).toBeInTheDocument();
    });
    expect(screen.getAllByText('Awaiting NOC clearance from state medical board.').length).toBeGreaterThan(0);
  });
});

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { InternalTasksPage } from '../pages/operations/InternalTasksPage';
import * as api from '../api/internalTasks';
import type { InternalTask, InternalTaskListResponse } from '../types/internalTask';

const task = (over: Partial<InternalTask> = {}): InternalTask => ({
  task_id: 't1',
  task_number: 'RND-0001',
  company_id: 'c1',
  company_name: 'Gocompliances',
  title: 'Market Research – Fitness Industry',
  description: null,
  task_type: 'RESEARCH',
  priority: 'MEDIUM',
  status: 'IN_PROGRESS',
  assigned_to: { user_id: 'u-riya', name: 'Riya Sharma', employee_code: 'GC0010', department_name: 'R&D' },
  created_by: { user_id: 'u-mgr', name: 'Kishan Singh', employee_code: 'GC0002' },
  due_date: '2026-11-20',
  is_overdue: false,
  completed_at: null,
  created_at: '2026-11-13T10:00:00Z',
  updated_at: '2026-11-13T10:00:00Z',
  message_count: 2,
  can_update_status: true,
  can_edit: true,
  can_reassign: true,
  ...over,
});

const listResponse = (overrides: Partial<InternalTaskListResponse> = {}): InternalTaskListResponse => ({
  items: [
    task(),
    task({ task_id: 't2', task_number: 'RND-0002', title: 'Vendor quotation – Printers', task_type: 'VENDOR', status: 'PENDING' }),
  ],
  total: 2,
  summary: { total: 24, pending: 8, in_progress: 10, completed: 6, cancelled: 1 },
  capabilities: { can_create: true, can_assign: true, is_manager: true, scope: 'COMPANY' },
  ...overrides,
});

const renderPage = () =>
  render(
    <MemoryRouter>
      <InternalTasksPage />
    </MemoryRouter>
  );

describe('R&D / Internal Tasks page', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('shows the 4 summary cards and the task table', async () => {
    vi.spyOn(api, 'getInternalTasksApi').mockResolvedValue(listResponse());
    renderPage();

    expect(await screen.findByText('Market Research – Fitness Industry')).toBeInTheDocument();
    expect(screen.getByText('Vendor quotation – Printers')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Total Tasks\s*24/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /In Progress\s*10/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Pending\s*8/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Completed\s*6/ })).toBeInTheDocument();
    expect(screen.getByText('RND-0001')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Assign Task/ })).toBeInTheDocument();
  });

  it('hides Assign Task for employees who are not managers', async () => {
    vi.spyOn(api, 'getInternalTasksApi').mockResolvedValue(
      listResponse({ capabilities: { can_create: false, can_assign: false, is_manager: false, scope: null } })
    );
    renderPage();
    await screen.findByText('Market Research – Fitness Industry');
    expect(screen.queryByRole('button', { name: /Assign Task/ })).not.toBeInTheDocument();
  });

  it('clicking a summary card filters by that status', async () => {
    const spy = vi.spyOn(api, 'getInternalTasksApi').mockResolvedValue(listResponse());
    renderPage();
    await screen.findByText('Market Research – Fitness Industry');
    fireEvent.click(screen.getByRole('button', { name: /Pending\s*8/ }));
    await waitFor(() => expect(spy).toHaveBeenLastCalledWith(expect.objectContaining({ status: 'PENDING' })));
  });

  it('assigns a new task to any employee', async () => {
    vi.spyOn(api, 'getInternalTasksApi').mockResolvedValue(listResponse());
    vi.spyOn(api, 'getInternalTaskAssigneesApi').mockResolvedValue([
      { user_id: 'u-aman', name: 'Aman Verma', employee_code: 'GC0011', department_name: 'Sales' },
    ]);
    const create = vi.spyOn(api, 'createInternalTaskApi').mockResolvedValue(task({ task_id: 't3' }));
    renderPage();
    await screen.findByText('Market Research – Fitness Industry');

    fireEvent.click(screen.getByRole('button', { name: /Assign Task/ }));
    const dialog = await screen.findByRole('dialog', { name: 'Assign Task' });
    await within(dialog).findByRole('option', { name: /Aman Verma/ });

    fireEvent.change(within(dialog).getByPlaceholderText(/Market Research/), { target: { value: 'Competitor Analysis – CA Services' } });
    fireEvent.change(within(dialog).getByLabelText(/Type/), { target: { value: 'VENDOR' } });
    fireEvent.change(within(dialog).getByLabelText(/Assign to/), { target: { value: 'u-aman' } });
    fireEvent.change(within(dialog).getByLabelText(/Due date/), { target: { value: '2026-11-25' } });
    fireEvent.click(within(dialog).getByRole('button', { name: 'Assign Task' }));

    await waitFor(() =>
      expect(create).toHaveBeenCalledWith({
        title: 'Competitor Analysis – CA Services',
        description: null,
        task_type: 'VENDOR',
        priority: 'MEDIUM',
        assigned_to_user_id: 'u-aman',
        due_date: '2026-11-25',
      })
    );
    await waitFor(() => expect(screen.queryByRole('dialog', { name: 'Assign Task' })).not.toBeInTheDocument());
  });

  it('validates the assign form before calling the API', async () => {
    vi.spyOn(api, 'getInternalTasksApi').mockResolvedValue(listResponse());
    vi.spyOn(api, 'getInternalTaskAssigneesApi').mockResolvedValue([]);
    const create = vi.spyOn(api, 'createInternalTaskApi');
    renderPage();
    await screen.findByText('Market Research – Fitness Industry');
    fireEvent.click(screen.getByRole('button', { name: /Assign Task/ }));
    const dialog = await screen.findByRole('dialog', { name: 'Assign Task' });
    fireEvent.click(within(dialog).getByRole('button', { name: 'Assign Task' }));
    expect(await within(dialog).findByRole('alert')).toHaveTextContent('Please enter a task title.');
    expect(create).not.toHaveBeenCalled();
  });

  it('opens the task chat, shows messages and posts a new update', async () => {
    vi.spyOn(api, 'getInternalTasksApi').mockResolvedValue(listResponse());
    const thread = {
      task: task(),
      can_post: true,
      messages: [
        { message_id: 'm1', task_id: 't1', message_type: 'SYSTEM_EVENT' as const, message_text: 'Task created and assigned to Riya Sharma', is_own: false, created_at: '2026-11-13T10:00:00Z' },
        { message_id: 'm2', task_id: 't1', author_name: 'Riya Sharma', author_employee_code: 'GC0010', message_type: 'COMMENT' as const, message_text: 'Started collecting data', is_own: false, created_at: '2026-11-13T11:00:00Z' },
      ],
    };
    vi.spyOn(api, 'getInternalTaskThreadApi').mockResolvedValue(thread);
    const post = vi.spyOn(api, 'postInternalTaskMessageApi').mockResolvedValue({
      message_id: 'm3', task_id: 't1', message_type: 'COMMENT', message_text: 'Add pricing too', is_own: true, created_at: '2026-11-13T12:00:00Z',
    });
    renderPage();
    await screen.findByText('Market Research – Fitness Industry');

    fireEvent.click(screen.getByRole('button', { name: 'Open chat for RND-0001' }));
    const dialog = await screen.findByRole('dialog');
    expect(await within(dialog).findByText('Started collecting data')).toBeInTheDocument();
    expect(within(dialog).getByText('Task created and assigned to Riya Sharma')).toBeInTheDocument();

    fireEvent.change(within(dialog).getByLabelText('Message'), { target: { value: 'Add pricing too' } });
    fireEvent.click(within(dialog).getByRole('button', { name: 'Send' }));
    await waitFor(() => expect(post).toHaveBeenCalledWith('t1', 'Add pricing too'));
  });

  it('changes task status from the chat window', async () => {
    vi.spyOn(api, 'getInternalTasksApi').mockResolvedValue(listResponse());
    vi.spyOn(api, 'getInternalTaskThreadApi').mockResolvedValue({ task: task(), can_post: true, messages: [] });
    const upd = vi.spyOn(api, 'updateInternalTaskStatusApi').mockResolvedValue(task({ status: 'COMPLETED' }));
    renderPage();
    await screen.findByText('Market Research – Fitness Industry');

    fireEvent.click(screen.getByRole('button', { name: 'Open chat for RND-0001' }));
    const select = await screen.findByLabelText('Change status');
    fireEvent.change(select, { target: { value: 'COMPLETED' } });
    await waitFor(() => expect(upd).toHaveBeenCalledWith('t1', 'COMPLETED'));
  });

  it('reassigns a task to another employee', async () => {
    vi.spyOn(api, 'getInternalTasksApi').mockResolvedValue(listResponse());
    vi.spyOn(api, 'getInternalTaskAssigneesApi').mockResolvedValue([
      { user_id: 'u-riya', name: 'Riya Sharma', employee_code: 'GC0010' },
      { user_id: 'u-neha', name: 'Neha Gupta', employee_code: 'GC0012' },
    ]);
    const reassign = vi.spyOn(api, 'reassignInternalTaskApi').mockResolvedValue(task());
    renderPage();
    await screen.findByText('Market Research – Fitness Industry');

    fireEvent.click(screen.getByRole('button', { name: 'Reassign RND-0001' }));
    const dialog = await screen.findByRole('dialog', { name: /Reassign RND-0001/ });
    const select = within(dialog).getByLabelText(/New assignee/);
    await within(dialog).findByRole('option', { name: /Neha Gupta/ });
    // current assignee is not offered
    expect(within(dialog).queryByRole('option', { name: /Riya Sharma/ })).not.toBeInTheDocument();
    fireEvent.change(select, { target: { value: 'u-neha' } });
    fireEvent.click(within(dialog).getByRole('button', { name: 'Reassign' }));
    await waitFor(() => expect(reassign).toHaveBeenCalledWith('t1', 'u-neha', undefined));
  });
});

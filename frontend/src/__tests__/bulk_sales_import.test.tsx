import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { SalesRegisterPage } from '../pages/SalesRegisterPage';
import { SalesDashboardPage } from '../pages/SalesDashboardPage';
import { BulkSalesImportModal } from '../components/sales/BulkSalesImportModal';
import * as authApi from '../api/auth';
import * as salesApi from '../api/sales';
import * as salesImportApi from '../api/sales_import';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';
import type { SalesEmployeeOption } from '../types/sales';
import type {
  SalesImportPreviewResponse,
  SalesImportExecuteResponse,
} from '../types/sales_import';

// Mock ResizeObserver
globalThis.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock URL.createObjectURL
globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
globalThis.URL.revokeObjectURL = vi.fn();

const mockUser: CurrentUser = {
  user_id: 'b0000000-0000-0000-0000-000000000001',
  employee_code: 'GC0001',
  first_name: 'Karishma',
  last_name: 'Upadhyay',
  official_email: 'karishma@gocompliances.com',
  mobile_number: '+919999900001',
  company_id: 'comp-1',
  department_id: 'dept-sales',
  designation_id: 'desig-mgr',
  account_status: 'ACTIVE',
  must_change_password: false,
};

const mockModules: AccessibleModule[] = [
  {
    module_id: 'mod-sales',
    module_code: 'SALES',
    module_name: 'Sales',
    display_order: 10,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: false,
    can_approve: true,
    can_export: true,
    data_scope: 'ALL',
  },
  {
    module_id: 'mod-sales-reg',
    module_code: 'SALES_REGISTER',
    module_name: 'Sales Register',
    display_order: 20,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: false,
    can_approve: true,
    can_export: true,
    data_scope: 'ALL',
  },
  {
    module_id: 'mod-sales-dash',
    module_code: 'SALES_DASHBOARD',
    module_name: 'Sales Dashboard',
    display_order: 30,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: false,
    can_approve: true,
    can_export: true,
    data_scope: 'ALL',
  },
];

const mockAssignees: SalesEmployeeOption[] = [
  {
    user_id: 'ops-user-1',
    employee_code: 'OP001',
    full_name: 'Omkar Ops Executive',
    department_name: 'Operations',
    designation_name: 'Operations Executive',
    company_id: 'comp-1',
    company_name: 'GoCompliance Corp',
  },
  {
    user_id: 'ops-user-2',
    employee_code: 'OP002',
    full_name: 'Pooja Operations Lead',
    department_name: 'Operations',
    designation_name: 'Team Lead',
    company_id: 'comp-1',
    company_name: 'GoCompliance Corp',
  },
];

const mockPreviewValid: SalesImportPreviewResponse = {
  filename: 'test_orders.xlsx',
  total_rows: 2,
  valid_rows_count: 2,
  error_rows_count: 0,
  duplicate_warnings_count: 0,
  can_import: true,
  rows: [
    {
      row_number: 1,
      sl_no: '1',
      location: 'Delhi - South Ext',
      client_name: 'Acme Global Ltd',
      contact: '09876543210',
      source: 'WEBSITE',
      work: 'Company Registration',
      total_amount: 15000,
      incidental_cost: 500,
      is_valid: true,
      is_duplicate_in_file: false,
      is_duplicate_in_db: false,
      errors: [],
      warnings: [],
      service_id: 'srv-1',
      service_name: 'Company Registration',
    },
    {
      row_number: 2,
      sl_no: '2',
      location: 'Bangalore - Indiranagar',
      client_name: 'TechNova Solutions',
      contact: '9820012345',
      source: 'DIRECT',
      work: 'GST Registration',
      total_amount: 5000,
      incidental_cost: 0,
      is_valid: true,
      is_duplicate_in_file: false,
      is_duplicate_in_db: false,
      errors: [],
      warnings: [],
      service_id: 'srv-2',
      service_name: 'GST Registration',
    },
  ],
};

const mockExecuteResult: SalesImportExecuteResponse = {
  success: true,
  imported_count: 2,
  assignments_count: 2,
  order_numbers: ['SO-2026-0001', 'SO-2026-0002'],
  message: 'Successfully imported and assigned 2 sales orders to Omkar Ops Executive.',
};

describe('Bulk Sales Import & Assignment UI Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'test-access-token');

    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModules);
    vi.spyOn(salesApi, 'getOperationsAssigneesApi').mockResolvedValue(mockAssignees);
    vi.spyOn(salesApi, 'getSalesFormOptionsApi').mockResolvedValue({
      services: [
        { service_id: 'srv-1', service_code: 'CR01', service_name: 'Company Registration', category: 'REG', base_price: 15000, govt_fee: 1000 },
        { service_id: 'srv-2', service_code: 'GST01', service_name: 'GST Registration', category: 'TAX', base_price: 5000, govt_fee: 0 },
        { service_id: 'srv-3', service_code: 'TL01', service_name: 'Trade License', category: 'LIC', base_price: 8000, govt_fee: 500 },
      ],
      salespersons: [],
      clients: [],
      lead_sources: ['DIRECT', 'WEBSITE', 'REFERRAL'],
      company_id: 'comp-1',
      company_name: 'GoCompliance Corp',
      can_select_salesperson: false,
    });
    vi.spyOn(salesApi, 'getSalesRegisterApi').mockResolvedValue({
      items: [],
      total_count: 0,
      page: 1,
      limit: 20,
      total_pages: 1,
      summary: {
        total_orders: 0,
        total_sales: 0,
        total_advance: 0,
        total_pending: 0,
        total_govt_fees: 0,
        total_incidental_cost: 0,
        total_profits: 0,
        formatted_total_sales: '₹0',
        formatted_total_advance: '₹0',
        formatted_total_pending: '₹0',
        formatted_total_govt_fees: '₹0',
        formatted_total_incidental_cost: '₹0',
        formatted_total_profits: '₹0',
      },
    });
  });

  it('renders Import Excel/CSV button on Sales Register and opens BulkSalesImportModal', async () => {
    render(
      <MemoryRouter initialEntries={['/sales/register']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/sales/register" element={<SalesRegisterPage />} />
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    const importBtn = await screen.findByRole('button', { name: /import excel\/csv/i });
    expect(importBtn).toBeInTheDocument();

    fireEvent.click(importBtn);

    // Modal opens
    await waitFor(() => {
      expect(screen.getByText(/bulk sales import \(excel \/ csv\)/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /template \(\.xlsx\)/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /template \(\.csv\)/i })).toBeInTheDocument();
    });
  });

  it('downloads XLSX and CSV master templates when download buttons are clicked', async () => {
    const downloadXlsxSpy = vi
      .spyOn(salesImportApi, 'downloadMasterTemplateXlsxApi')
      .mockResolvedValue({ blob: new Blob(['xlsx-content']), filename: 'sales_import_master_template.xlsx' });
    const downloadCsvSpy = vi
      .spyOn(salesImportApi, 'downloadMasterTemplateCsvApi')
      .mockResolvedValue({ blob: new Blob(['csv-content']), filename: 'sales_import_master_template.csv' });

    render(
      <ThemeProvider>
        <BulkSalesImportModal
          isOpen={true}
          onClose={vi.fn()}
          onSuccess={vi.fn()}
        />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /template \(\.xlsx\)/i })).toBeInTheDocument();
    });

    const xlsxBtn = screen.getByRole('button', { name: /template \(\.xlsx\)/i });
    fireEvent.click(xlsxBtn);
    expect(downloadXlsxSpy).toHaveBeenCalledTimes(1);

    const csvBtn = screen.getByRole('button', { name: /template \(\.csv\)/i });
    fireEvent.click(csvBtn);
    expect(downloadCsvSpy).toHaveBeenCalledTimes(1);
  });

  it('populates Operations assignee dropdown with eligible team members', async () => {
    render(
      <ThemeProvider>
        <BulkSalesImportModal
          isOpen={true}
          onClose={vi.fn()}
          onSuccess={vi.fn()}
        />
      </ThemeProvider>
    );

    await waitFor(() => {
      const select = screen.getByLabelText(/operations assignee/i) as HTMLSelectElement;
      expect(select).toBeInTheDocument();
      expect(select.options.length).toBe(2);
      expect(select.options[0].text).toContain('Omkar Ops Executive (OP001)');
      expect(select.options[1].text).toContain('Pooja Operations Lead (OP002)');
    });
  });

  it('validates uploaded file and renders preview table with stats and import confirmation', async () => {
    const previewSpy = vi
      .spyOn(salesImportApi, 'previewSalesImportApi')
      .mockResolvedValue(mockPreviewValid);
    const executeSpy = vi
      .spyOn(salesImportApi, 'executeBulkImportApi')
      .mockResolvedValue(mockExecuteResult);
    const onSuccessMock = vi.fn();

    render(
      <ThemeProvider>
        <BulkSalesImportModal
          isOpen={true}
          onClose={vi.fn()}
          onSuccess={onSuccessMock}
        />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/browse file/i)).toBeInTheDocument();
    });

    // Simulate file selection
    const file = new File(['mock content'], 'test_orders.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    Object.defineProperty(fileInput, 'files', { value: [file] });
    fireEvent.change(fileInput);

    // Click Validate & Preview
    const validateBtn = screen.getByRole('button', { name: /validate & preview/i });
    expect(validateBtn).not.toBeDisabled();
    fireEvent.click(validateBtn);

    await waitFor(() => {
      expect(previewSpy).toHaveBeenCalledTimes(1);
      expect(screen.getByText(/total data rows/i)).toBeInTheDocument();
      expect(screen.getByText('Acme Global Ltd')).toBeInTheDocument();
      expect(screen.getByText('TechNova Solutions')).toBeInTheDocument();
      expect(screen.getByText('Delhi - South Ext')).toBeInTheDocument();
      expect(screen.getByText('Bangalore - Indiranagar')).toBeInTheDocument();
      expect(screen.getByText('09876543210')).toBeInTheDocument();
    });

    // Click Import All Entries
    const importBtn = screen.getByRole('button', { name: /import all entries \(2\)/i });
    expect(importBtn).not.toBeDisabled();
    fireEvent.click(importBtn);

    await waitFor(() => {
      expect(executeSpy).toHaveBeenCalledTimes(1);
      expect(onSuccessMock).toHaveBeenCalledTimes(1);
      expect(screen.getByText(/bulk import completed successfully!/i)).toBeInTheDocument();
      expect(screen.getByText('SO-2026-0001')).toBeInTheDocument();
      expect(screen.getByText('SO-2026-0002')).toBeInTheDocument();
    });
  });

  it('shows error banner and disables import button when validation fails', async () => {
    const mockPreviewError: SalesImportPreviewResponse = {
      filename: 'error_orders.xlsx',
      total_rows: 1,
      valid_rows_count: 0,
      error_rows_count: 1,
      duplicate_warnings_count: 0,
      can_import: false,
      rows: [
        {
          row_number: 1,
          sl_no: '1',
          location: 'Delhi',
          client_name: null,
          contact: '123',
          source: 'INVALID',
          work: 'Bad Work',
          total_amount: null,
          incidental_cost: 0,
          is_valid: false,
          is_duplicate_in_file: false,
          is_duplicate_in_db: false,
          errors: ['Client Name is required', 'Invalid Contact number', 'Total Amount is required'],
          warnings: [],
        },
      ],
    };
    vi.spyOn(salesImportApi, 'previewSalesImportApi').mockResolvedValue(mockPreviewError);

    render(
      <ThemeProvider>
        <BulkSalesImportModal
          isOpen={true}
          onClose={vi.fn()}
          onSuccess={vi.fn()}
        />
      </ThemeProvider>
    );

    const file = new File(['mock content'], 'error_orders.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    Object.defineProperty(fileInput, 'files', { value: [file] });
    fireEvent.change(fileInput);

    const validateBtn = screen.getByRole('button', { name: /validate & preview/i });
    fireEvent.click(validateBtn);

    await waitFor(() => {
      expect(screen.getByText(/validation errors detected/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /error report \(csv\)/i })).toBeInTheDocument();
      const importBtn = screen.getByRole('button', { name: /import all entries/i });
      expect(importBtn).toBeDisabled();
    });
  });

  it('renders Import Excel/CSV button on Sales Dashboard Page', async () => {
    vi.spyOn(salesApi, 'getSalesDashboardApi').mockResolvedValue({
      date_range: {
        preset: 'this_month',
        from_date: '2026-10-01',
        to_date: '2026-10-31',
        formatted_from: '01/10/2026',
        formatted_to: '31/10/2026',
        comparison_label: 'vs last month',
      },
      kpis: {
        total_sales: { value: 100000, formatted_value: '₹1,00,000', previous_value: 90000, percentage_change: 10, is_positive: true, comparison_label: 'vs last month' },
        confirmed_orders: { value: 10, formatted_value: '10', previous_value: 8, percentage_change: 25, is_positive: true, comparison_label: 'vs last month' },
        amount_received: { value: 50000, formatted_value: '₹50,000', previous_value: 40000, percentage_change: 25, is_positive: true, comparison_label: 'vs last month' },
        outstanding: { value: 50000, formatted_value: '₹50,000', previous_value: 50000, percentage_change: 0, is_positive: false, comparison_label: 'vs last month' },
        avg_order_value: { value: 10000, formatted_value: '₹10,000', previous_value: 10000, percentage_change: 0, is_positive: true, comparison_label: 'vs last month' },
        total_clients: { value: 8, formatted_value: '8', previous_value: 6, percentage_change: 33, is_positive: true, comparison_label: 'vs last month' },
      },
      sales_trend: [],
      payment_status: {
        total_orders: 10,
        items: [
          { status: 'FULLY_PAID', label: 'Fully Paid', count: 5, percentage: 50, amount: 50000 },
          { status: 'PENDING', label: 'Pending', count: 5, percentage: 50, amount: 50000 },
        ],
      },
      service_sales: [],
      lead_sources: {
        total_leads: 10,
        items: [
          { source: 'WEBSITE', label: 'Website', count: 6, percentage: 60 },
          { source: 'DIRECT', label: 'Direct', count: 4, percentage: 40 },
        ],
      },
      team_performance: [],
      recent_orders: [],
      filter_options: { employees: [], services: [], lead_sources: [], payment_statuses: [], can_filter_employees: true },
    } as any);

    render(
      <MemoryRouter initialEntries={['/sales/dashboard']}>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/sales/dashboard" element={<SalesDashboardPage />} />
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    );

    const importBtn = await screen.findByRole('button', { name: /import excel\/csv/i });
    expect(importBtn).toBeInTheDocument();

    fireEvent.click(importBtn);

    await waitFor(() => {
      expect(screen.getByText(/bulk sales import \(excel \/ csv\)/i)).toBeInTheDocument();
    });
  });

  it('allows inline quick-fix of service mismatch from cell dropdown and enables import when all rows valid', async () => {
    const mockPreviewWithWorkError: SalesImportPreviewResponse = {
      filename: 'sales_import.xlsx',
      total_rows: 2,
      valid_rows_count: 1,
      error_rows_count: 1,
      duplicate_warnings_count: 0,
      can_import: false,
      rows: [
        {
          row_number: 1,
          sl_no: '1.0',
          location: 'Delhi',
          client_name: 'Acme Corp',
          contact: '9876543210',
          source: 'WEBSITE',
          work: 'Company Registration',
          total_amount: 15000,
          incidental_cost: 0,
          is_valid: true,
          is_duplicate_in_file: false,
          is_duplicate_in_db: false,
          errors: [],
          warnings: [],
          service_id: 'srv-1',
          service_name: 'Company Registration',
        },
        {
          row_number: 2,
          sl_no: '2.0',
          location: 'Mumbai',
          client_name: 'Beta LLC',
          contact: '9876543211',
          source: 'WEBSITE',
          work: 'Trade licese',
          total_amount: 30000,
          incidental_cost: 0,
          is_valid: false,
          is_duplicate_in_file: false,
          is_duplicate_in_db: false,
          errors: ["Work 'Trade licese' does not match any active service in the system."],
          warnings: [],
        },
      ],
    };

    vi.spyOn(salesImportApi, 'previewSalesImportApi').mockResolvedValue(mockPreviewWithWorkError);
    const executeSpy = vi
      .spyOn(salesImportApi, 'executeBulkImportApi')
      .mockResolvedValue(mockExecuteResult);

    render(
      <ThemeProvider>
        <BulkSalesImportModal isOpen={true} onClose={vi.fn()} onSuccess={vi.fn()} />
      </ThemeProvider>
    );

    const file = new File(['content'], 'sales_import.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    Object.defineProperty(fileInput, 'files', { value: [file] });
    fireEvent.change(fileInput);

    const validateBtn = screen.getByRole('button', { name: /validate & preview/i });
    fireEvent.click(validateBtn);

    // Initial state: 1 valid, 1 error, can_import is false
    await waitFor(() => {
      expect(screen.getByText(/validation errors detected \(1 row\)/i)).toBeInTheDocument();
      expect(screen.getByText('Trade licese')).toBeInTheDocument();
    });

    const importBtn = screen.getByRole('button', { name: /import all entries/i });
    expect(importBtn).toBeDisabled();

    // Find the quick-fix service dropdown for row 2
    const quickFixSelect = screen.getByLabelText(/fix service for row 2/i) as HTMLSelectElement;
    expect(quickFixSelect).toBeInTheDocument();

    // Select Trade License (srv-3)
    fireEvent.change(quickFixSelect, { target: { value: 'srv-3' } });

    // After quick-fix: error is cleared, row is valid, banner shows all rows valid, import button enabled!
    await waitFor(() => {
      expect(screen.getByText(/all rows valid & ready to import/i)).toBeInTheDocument();
      expect(screen.getByText('Trade License')).toBeInTheDocument();
      expect(importBtn).not.toBeDisabled();
    });

    // Click Import All Entries
    fireEvent.click(importBtn);

    await waitFor(() => {
      expect(executeSpy).toHaveBeenCalledTimes(1);
      const callArg = executeSpy.mock.calls[0][0];
      expect(callArg.rows[1].work).toBe('Trade License');
      expect(callArg.rows[1].service_id).toBe('srv-3');
      expect(callArg.rows[1].is_valid).toBe(true);
    });
  });

  it('allows inline editing of row details and saves updated values', async () => {
    const mockPreviewSingle: SalesImportPreviewResponse = {
      filename: 'sales_import.xlsx',
      total_rows: 1,
      valid_rows_count: 1,
      error_rows_count: 0,
      duplicate_warnings_count: 0,
      can_import: true,
      rows: [
        {
          row_number: 1,
          sl_no: '1',
          location: 'Delhi',
          client_name: 'Old Client Name',
          contact: '9876543210',
          source: 'WEBSITE',
          work: 'Company Registration',
          total_amount: 15000,
          incidental_cost: 0,
          is_valid: true,
          is_duplicate_in_file: false,
          is_duplicate_in_db: false,
          errors: [],
          warnings: [],
          service_id: 'srv-1',
          service_name: 'Company Registration',
        },
      ],
    };

    vi.spyOn(salesImportApi, 'previewSalesImportApi').mockResolvedValue(mockPreviewSingle);

    render(
      <ThemeProvider>
        <BulkSalesImportModal isOpen={true} onClose={vi.fn()} onSuccess={vi.fn()} />
      </ThemeProvider>
    );

    const file = new File(['content'], 'sales_import.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    Object.defineProperty(fileInput, 'files', { value: [file] });
    fireEvent.change(fileInput);

    const validateBtn = screen.getByRole('button', { name: /validate & preview/i });
    fireEvent.click(validateBtn);

    await waitFor(() => {
      expect(screen.getByText('Old Client Name')).toBeInTheDocument();
    });

    // Click Edit row button
    const editBtn = screen.getByLabelText(/edit row 1/i);
    fireEvent.click(editBtn);

    // Client name input appears
    const clientInput = screen.getByPlaceholderText('Client Name') as HTMLInputElement;
    expect(clientInput).toBeInTheDocument();
    expect(clientInput.value).toBe('Old Client Name');

    // Change client name
    fireEvent.change(clientInput, { target: { value: 'New Updated Client' } });

    // Click Save
    const saveBtn = screen.getByLabelText(/save row 1/i);
    fireEvent.click(saveBtn);

    // Verify row updated in UI
    await waitFor(() => {
      expect(screen.getByText('New Updated Client')).toBeInTheDocument();
      expect(screen.queryByPlaceholderText('Client Name')).not.toBeInTheDocument();
    });
  });

  it('displays Advance Amount column in preview and validates advance <= total when editing', async () => {
    const mockPreviewWithAdvance: SalesImportPreviewResponse = {
      filename: 'sales_import.xlsx',
      total_rows: 1,
      valid_rows_count: 1,
      error_rows_count: 0,
      duplicate_warnings_count: 0,
      can_import: true,
      rows: [
        {
          row_number: 1,
          sl_no: '1',
          location: 'Delhi',
          client_name: 'Advance Test Client',
          contact: '9876543210',
          source: 'DIRECT',
          work: 'Company Registration',
          total_amount: 20000,
          advance_amount: 5000,
          incidental_cost: 0,
          is_valid: true,
          is_duplicate_in_file: false,
          is_duplicate_in_db: false,
          errors: [],
          warnings: [],
          service_id: 'srv-1',
          service_name: 'Company Registration',
        },
      ],
    };

    vi.spyOn(salesImportApi, 'previewSalesImportApi').mockResolvedValue(mockPreviewWithAdvance);

    render(
      <ThemeProvider>
        <BulkSalesImportModal isOpen={true} onClose={vi.fn()} onSuccess={vi.fn()} />
      </ThemeProvider>
    );

    const file = new File(['content'], 'sales_import.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    Object.defineProperty(fileInput, 'files', { value: [file] });
    fireEvent.change(fileInput);

    const validateBtn = screen.getByRole('button', { name: /validate & preview/i });
    fireEvent.click(validateBtn);

    await waitFor(() => {
      expect(screen.getByRole('columnheader', { name: /advance/i })).toBeInTheDocument();
      expect(screen.getByText('Advance Test Client')).toBeInTheDocument();
    });

    // Advance amount ₹5,000 is rendered
    expect(screen.getByText('₹5,000')).toBeInTheDocument();

    // Click Edit row button
    const editBtn = screen.getByLabelText(/edit row 1/i);
    fireEvent.click(editBtn);

    // Look for inputs: total_amount and advance_amount
    const inputs = screen.getAllByRole('spinbutton');
    const advanceInput = inputs.find((inp) => (inp as HTMLInputElement).value === '5000') as HTMLInputElement;
    expect(advanceInput).toBeDefined();

    // Set advance higher than total amount (e.g. 25000 > 20000)
    fireEvent.change(advanceInput, { target: { value: '25000' } });

    // Click Save
    const saveBtn = screen.getByLabelText(/save row 1/i);
    fireEvent.click(saveBtn);

    // Verify error message for advance amount exceeding total
    await waitFor(() => {
      expect(screen.getByText(/advance amount cannot exceed total amount/i)).toBeInTheDocument();
    });
  });

  it('supports GST 18% auto-calculation checklist/radio toggle, renders Base Amount + GST columns, and submits apply_gst: true', async () => {
    const mockPreviewWithGst: SalesImportPreviewResponse = {
      filename: 'sales_import.xlsx',
      total_rows: 1,
      valid_rows_count: 1,
      error_rows_count: 0,
      duplicate_warnings_count: 0,
      can_import: true,
      apply_gst: true,
      total_base_amount: 10000,
      total_gst_amount: 1800,
      rows: [
        {
          row_number: 1,
          sl_no: '1',
          location: 'Delhi',
          client_name: 'GST Client Private Ltd',
          contact: '9876543210',
          source: 'WEBSITE',
          work: 'Company Registration',
          base_amount: 10000,
          gst_amount: 1800,
          gst_rate: 18,
          total_amount: 11800,
          advance_amount: 2000,
          incidental_cost: 0,
          gst_invoice_required: true,
          is_valid: true,
          is_duplicate_in_file: false,
          is_duplicate_in_db: false,
          errors: [],
          warnings: [],
          service_id: 'srv-1',
          service_name: 'Company Registration',
        },
      ],
    };

    const previewSpy = vi
      .spyOn(salesImportApi, 'previewSalesImportApi')
      .mockResolvedValue(mockPreviewWithGst);
    const executeSpy = vi
      .spyOn(salesImportApi, 'executeBulkImportApi')
      .mockResolvedValue(mockExecuteResult);

    render(
      <ThemeProvider>
        <BulkSalesImportModal isOpen={true} onClose={vi.fn()} onSuccess={vi.fn()} />
      </ThemeProvider>
    );

    // Verify GST options exist
    const gstRadio = screen.getByLabelText(/add 18% gst \(auto calculation\)/i) as HTMLInputElement;
    expect(gstRadio).toBeInTheDocument();
    expect(gstRadio.checked).toBe(false);

    // Select Add 18% GST
    fireEvent.click(gstRadio);
    expect(gstRadio.checked).toBe(true);

    const file = new File(['content'], 'sales_import.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    Object.defineProperty(fileInput, 'files', { value: [file] });
    fireEvent.change(fileInput);

    const validateBtn = screen.getByRole('button', { name: /validate & preview/i });
    fireEvent.click(validateBtn);

    // Verify preview API was called with applyGst: true
    await waitFor(() => {
      expect(previewSpy).toHaveBeenCalledWith(file, true);
    });

    // Check table headers for GST breakdown
    await waitFor(() => {
      expect(screen.getByRole('columnheader', { name: /base amount/i })).toBeInTheDocument();
      expect(screen.getByRole('columnheader', { name: /gst \(18%\)/i })).toBeInTheDocument();
      expect(screen.getByRole('columnheader', { name: /total amount/i })).toBeInTheDocument();
    });

    // Verify amounts displayed
    expect(screen.getByText('₹10,000')).toBeInTheDocument(); // Base
    expect(screen.getByText('₹1,800')).toBeInTheDocument();  // 18% GST
    expect(screen.getByText('₹11,800')).toBeInTheDocument(); // Total

    // Click Import
    const importBtn = screen.getByRole('button', { name: /import all entries \(1\)/i });
    fireEvent.click(importBtn);

    // Verify execute API payload has apply_gst: true
    await waitFor(() => {
      expect(executeSpy).toHaveBeenCalledTimes(1);
      const executeCall = executeSpy.mock.calls[0][0];
      expect(executeCall.apply_gst).toBe(true);
      expect(executeCall.rows[0].total_amount).toBe(11800);
      expect(executeCall.rows[0].gst_invoice_required).toBe(true);
    });
  });
});



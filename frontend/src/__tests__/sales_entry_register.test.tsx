import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { SalesEntryPage } from '../pages/SalesEntryPage';
import { SalesRegisterPage } from '../pages/SalesRegisterPage';
import { SalesLayout } from '../components/sales/SalesLayout';
import * as authApi from '../api/auth';
import * as salesApi from '../api/sales';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';
import type {
  SalesFormOptionsResponse,
  SalesRegisterResponse,
} from '../types/sales';

// Mock ResizeObserver
globalThis.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

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
];

const mockFormOptions: SalesFormOptionsResponse = {
  company_id: 'comp-1',
  company_name: 'GoCompliance Solutions Pvt Ltd',
  services: [
    {
      service_id: 'a0000000-0000-0000-0000-000000000001',
      service_code: 'FSSAI_NEW',
      service_name: 'FSSAI Registration - New License',
      category: 'Food Safety',
      base_price: 15000,
      govt_fee: 5000,
    },
    {
      service_id: 'a0000000-0000-0000-0000-000000000002',
      service_code: 'GST_REG',
      service_name: 'GST Registration',
      category: 'Taxation',
      base_price: 5000,
      govt_fee: 0,
    },
  ],
  salespersons: [
    {
      user_id: 'b0000000-0000-0000-0000-000000000001',
      employee_code: 'GC0001',
      full_name: 'Karishma Upadhyay',
      department_name: 'Sales',
      designation_name: 'Sales Director',
    },
    {
      user_id: 'b0000000-0000-0000-0000-000000000002',
      employee_code: 'GC0002',
      full_name: 'Rajesh Sharma',
      department_name: 'Sales',
      designation_name: 'Sales Executive',
    },
  ],
  clients: [
    {
      client_id: 'c0000000-0000-0000-0000-000000000001',
      client_name: 'Acme Agro Foods Pvt Ltd',
      contact_phone: '9876543210',
      contact_email: 'compliance@acme.com',
      contact_person: 'Ramesh Gupta',
      entity_type: 'PRIVATE_LIMITED',
    },
  ],
  lead_sources: ['WEBSITE', 'REFERRAL', 'DIRECT', 'JUSTDIAL', 'INDIAMART', 'OTHERS'],
  operations_assignees: [
    {
      user_id: 'b0000000-0000-0000-0000-000000000003',
      employee_code: 'GC0003',
      full_name: 'Mansi Sharma',
      department_name: 'Operations',
      designation_name: 'Operations Executive',
    },
    {
      user_id: 'b0000000-0000-0000-0000-000000000001',
      employee_code: 'GC0001',
      full_name: 'Karishma Upadhyay',
      department_name: 'Operations',
      designation_name: 'Operations Head',
    },
  ],
  default_salesperson_id: 'b0000000-0000-0000-0000-000000000001',
  can_select_salesperson: true,
};

const mockRegisterData: SalesRegisterResponse = {
  items: [
    {
      s_no: 1,
      order_id: 'ord-001',
      order_number: 'SO-2026-0001',
      company_id: 'comp-1',
      client_id: 'c0000000-0000-0000-0000-000000000001',
      service_id: 'a0000000-0000-0000-0000-000000000001',
      salesperson_user_id: 'b0000000-0000-0000-0000-000000000001',
      order_date: '2026-09-23',
      formatted_date: '23 Sep 2026',
      client_name: 'Acme Agro Foods Pvt Ltd',
      contact_no: '9876543210',
      lead_source: 'Website',
      service_name: 'FSSAI Registration - New License',
      service_code: 'FSSAI_NEW',
      salesperson_name: 'Karishma Upadhyay',
      salesperson_code: 'GC0001',
      assigned_to_name: 'Vikram Mehta',
      assigned_to_code: 'GC0005',
      assigned_to_user_id: 'usr-vikram-0005',
      work_status: 'IN_PROGRESS',
      order_value: 50000,
      amount_received: 20000,
      balance_amount: 30000,
      payment_status: 'PARTIALLY_PAID',
      proforma_invoice_no: 'PI-2026-001',
      tax_invoice_no: 'INV-2026-001',
      reimbursement_note: 'Challan fee 5000 included',
      govt_fees: 5000,
      incidental_cost: 1000,
      profit_amount: 44000,
      notes: 'Express completion request',
      remarks: 'Express completion request',
      confirmation_status: 'CONFIRMED',
      operation_status: 'IN_PROGRESS',
      application_number: 'APP-2026-001',
    },
    {
      s_no: 2,
      order_id: 'ord-002',
      order_number: 'SO-2026-0002',
      company_id: 'comp-1',
      client_id: 'c0000000-0000-0000-0000-000000000001',
      service_id: 'a0000000-0000-0000-0000-000000000002',
      salesperson_user_id: 'b0000000-0000-0000-0000-000000000002',
      order_date: '2026-09-23',
      formatted_date: '23 Sep 2026',
      client_name: 'Beta Biotech Pvt Ltd',
      contact_no: '9811122233',
      lead_source: 'Direct',
      service_name: 'GST Registration',
      service_code: 'GST_REG',
      salesperson_name: 'Rajesh Sharma',
      salesperson_code: 'GC0002',
      assigned_to_name: undefined,
      assigned_to_code: undefined,
      assigned_to_user_id: null,
      work_status: 'UNASSIGNED',
      order_value: 15000,
      amount_received: 15000,
      balance_amount: 0,
      payment_status: 'FULLY_PAID',
      proforma_invoice_no: undefined,
      tax_invoice_no: undefined,
      reimbursement_note: undefined,
      govt_fees: 0,
      incidental_cost: 0,
      profit_amount: 15000,
      notes: undefined,
      remarks: undefined,
      confirmation_status: 'CONFIRMED',
      operation_status: 'UNASSIGNED',
      application_number: 'APP-2026-002',
    },
  ],
  total_count: 2,
  page: 1,
  limit: 25,
  total_pages: 1,
  summary: {
    total_orders: 2,
    total_sales: 65000,
    total_advance: 35000,
    total_pending: 30000,
    total_govt_fees: 5000,
    total_incidental_cost: 1000,
    total_profits: 59000,
    formatted_total_sales: '₹65,000',
    formatted_total_advance: '₹35,000',
    formatted_total_pending: '₹30,000',
    formatted_total_govt_fees: '₹5,000',
    formatted_total_incidental_cost: '₹1,000',
    formatted_total_profits: '₹59,000',
  },
};

describe('Sales Entry & Sales Register Module Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'test-access-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModules);
    vi.spyOn(salesApi, 'getSalesFormOptionsApi').mockResolvedValue(mockFormOptions);
    vi.spyOn(salesApi, 'getSalesRegisterApi').mockResolvedValue(mockRegisterData);
  });

  it('renders Sales Entry form with 2 sections (no Invoicing section or Assigned To selector)', async () => {
    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/entry']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="entry" element={<SalesEntryPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    // Wait for form options to load and heading to appear
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    // Check presence of Section 1 & 2
    expect(screen.getByText(/1\. Client & Engagement Details/i)).toBeInTheDocument();
    expect(screen.getByText(/2\. Financials & Cost Analysis/i)).toBeInTheDocument();

    // Check absence of Section 3 (Invoicing & Operational Notes)
    expect(screen.queryByText(/3\. Invoicing & Operational Notes/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Proforma Invoice No/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Tax Invoice No/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Reimbursement Note/i)).not.toBeInTheDocument();

    // Verify Converted By label is present, but NO "Assigned To" input exists
    expect(screen.getByText(/Converted By \(Sales Employee\)/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/^Assigned To$/i)).not.toBeInTheDocument();

    // Verify key fields exist
    expect(screen.getByLabelText(/Date/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Acme Legal Solutions/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/9876543210/i)).toBeInTheDocument();
    expect(screen.getByText(/-- Select Service \/ Work --/i)).toBeInTheDocument();

    // Verify live calculation cards
    expect(screen.getByText('Total Amount')).toBeInTheDocument();
    expect(screen.getByText('Pending Balance')).toBeInTheDocument();
    expect(screen.getByText(/Calculated Profit/i)).toBeInTheDocument();
  });

  it('validates Advance Amount cannot exceed Total Amount', async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/entry']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="entry" element={<SalesEntryPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    // Fill Total Amount = 10000, Advance = 15000 (invalid)
    const totalInput = screen.getByLabelText(/Total Amount \(₹\)/i);
    const advanceInput = screen.getByLabelText(/Advance Amount \(₹\)/i);

    await user.clear(totalInput);
    await user.type(totalInput, '10000');

    await user.clear(advanceInput);
    await user.type(advanceInput, '15000');

    // Click "Save & Confirm Order"
    const confirmBtn = screen.getByRole('button', { name: /Save & Confirm Order/i });
    await user.click(confirmBtn);

    // Error message should appear
    await waitFor(() => {
      expect(screen.getByText(/Advance amount cannot exceed total amount/i)).toBeInTheDocument();
    });
  });

  it('submits valid Sales Entry and invokes createSalesEntryApi', async () => {
    const user = userEvent.setup();
    const createSpy = vi.spyOn(salesApi, 'createSalesEntryApi').mockResolvedValue(mockRegisterData.items[0]);

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/entry']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="entry" element={<SalesEntryPage />} />
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    // Fill form fields
    const clientInput = screen.getByPlaceholderText(/Acme Legal Solutions/i);
    await user.type(clientInput, 'Tata Steel Limited');

    const contactInput = screen.getByPlaceholderText(/9876543210/i);
    await user.type(contactInput, '9811223344');

    // Select Service
    const serviceSelect = screen.getByLabelText(/Work \/ Service/i);
    fireEvent.change(serviceSelect, {
      target: { value: 'a0000000-0000-0000-0000-000000000001' },
    });

    // Fill Total Amount = 50000, Advance = 20000
    const totalInput = screen.getByLabelText(/Total Amount \(₹\)/i);
    await user.clear(totalInput);
    await user.type(totalInput, '50000');

    const advanceInput = screen.getByLabelText(/Advance Amount \(₹\)/i);
    await user.clear(advanceInput);
    await user.type(advanceInput, '20000');

    // Click "Save & Confirm Order"
    const confirmBtn = screen.getByRole('button', { name: /Save & Confirm Order/i });
    await user.click(confirmBtn);

    await waitFor(() => {
      expect(createSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          client_name: 'Tata Steel Limited',
          contact_no: '9811223344',
          service_id: 'a0000000-0000-0000-0000-000000000001',
          order_value: 50000,
          amount_received: 20000,
          auto_confirm: true,
        })
      );
    });
  });

  it('renders Sales Register with 20 columns, displays Unassigned for unassigned orders, and preserves clean columns', async () => {
    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/register']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    // Wait for register heading to load
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales register/i })).toBeInTheDocument();
    });

    // Check KPI strip values
    expect(screen.getByText('Total Orders')).toBeInTheDocument();
    expect(screen.getAllByText('₹65,000').length).toBeGreaterThanOrEqual(1);

    // Check 20 Columns in Table Header
    expect(screen.getByText('1. S.No')).toBeInTheDocument();
    expect(screen.getByText('2. Date')).toBeInTheDocument();
    expect(screen.getByText('3. Client Name')).toBeInTheDocument();
    expect(screen.getByText('4. Contact No')).toBeInTheDocument();
    expect(screen.getByText('5. Source')).toBeInTheDocument();
    expect(screen.getByText('6. Work')).toBeInTheDocument();
    expect(screen.getByText('7. Converted By')).toBeInTheDocument();
    expect(screen.getByText('8. Assigned To')).toBeInTheDocument();
    expect(screen.getByText('9. Work Status')).toBeInTheDocument();
    expect(screen.getByText('10. Total Amount')).toBeInTheDocument();
    expect(screen.getByText('11. Advance Amount')).toBeInTheDocument();
    expect(screen.getByText('12. Pending Amount')).toBeInTheDocument();
    expect(screen.getByText('13. Payment Status')).toBeInTheDocument();
    expect(screen.getByText('14. Proforma Inv. No.')).toBeInTheDocument();
    expect(screen.getByText('15. Tax Inv. No.')).toBeInTheDocument();
    expect(screen.getByText('16. Reimbursement Note')).toBeInTheDocument();
    expect(screen.getByText('17. Govt Fees')).toBeInTheDocument();
    expect(screen.getByText('18. Incidental Cost')).toBeInTheDocument();
    expect(screen.getByText('19. Profits')).toBeInTheDocument();
    expect(screen.getByText('20. Remarks')).toBeInTheDocument();

    // Check Row 1 Data
    expect(screen.getByText('Acme Agro Foods Pvt Ltd')).toBeInTheDocument();
    expect(screen.getByText('9876543210')).toBeInTheDocument();
    expect(screen.getAllByText('Karishma Upadhyay').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Vikram Mehta')).toBeInTheDocument();
    expect(screen.getAllByText('Partially Paid').length).toBeGreaterThanOrEqual(1);

    // Check Row 2 Data (Unassigned)
    expect(screen.getByText('Beta Biotech Pvt Ltd')).toBeInTheDocument();
    expect(screen.getAllByText('Rajesh Sharma').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Unassigned').length).toBeGreaterThanOrEqual(1);
  });

  it('allows Operations Manager to assign order to Operations assignee via modal', async () => {
    const user = userEvent.setup();
    const assignSpy = vi.spyOn(salesApi, 'assignSalesOrderApi').mockResolvedValue(mockRegisterData.items[0]);

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/register']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales register/i })).toBeInTheDocument();
    });

    // Find the "Assign" button for the unassigned item (Row 2)
    const assignButtons = screen.getAllByRole('button', { name: /Assign/i });
    expect(assignButtons.length).toBeGreaterThanOrEqual(1);
    await user.click(assignButtons[0]);

    // Modal should open
    await waitFor(() => {
      expect(screen.getByText(/Assign Operations Work:/i)).toBeInTheDocument();
    });

    // Select Mansi Sharma from Operations Assignees
    const assigneeSelect = screen.getByLabelText(/Eligible Operations Team Member/i);
    expect(assigneeSelect).toBeInTheDocument();
    fireEvent.change(assigneeSelect, {
      target: { value: 'b0000000-0000-0000-0000-000000000003' },
    });

    // Add handover notes
    const notesInput = screen.getByPlaceholderText(/Assigned to Mansi/i);
    await user.type(notesInput, 'Please expedite processing');

    // Submit assignment
    const submitBtn = screen.getByRole('button', { name: /Confirm Assignment/i });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(assignSpy).toHaveBeenCalledWith(
        'ord-002',
        expect.objectContaining({
          assignee_user_id: 'b0000000-0000-0000-0000-000000000003',
          notes: 'Please expedite processing',
        })
      );
    });
  });

  it('triggers CSV export on clicking Export CSV button in Sales Register', async () => {
    const user = userEvent.setup();
    const exportSpy = vi.spyOn(salesApi, 'exportSalesRegisterCsvApi').mockResolvedValue({
      blob: new Blob(['s_no,order_date\n1,2026-09-23'], { type: 'text/csv' }),
      filename: 'sales_register_export.csv',
    });

    // Mock URL object methods
    const createObjectURLMock = vi.fn(() => 'blob:http://localhost/mock-blob-url');
    const revokeObjectURLMock = vi.fn();
    window.URL.createObjectURL = createObjectURLMock;
    window.URL.revokeObjectURL = revokeObjectURLMock;

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/register']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales register/i })).toBeInTheDocument();
    });

    const exportBtn = screen.getByRole('button', { name: /Export CSV/i });
    await user.click(exportBtn);

    await waitFor(() => {
      expect(exportSpy).toHaveBeenCalled();
    });
  });

  it('renders service dropdown with service name only and does not auto-fill/overwrite pricing on selection', async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/entry']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="entry" element={<SalesEntryPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    // Verify service options only show service_name (no "Base: ₹" text)
    const serviceSelect = screen.getByLabelText(/Work \/ Service/i) as HTMLSelectElement;
    const optionTexts = Array.from(serviceSelect.options).map((o) => o.text);
    expect(optionTexts).toContain('FSSAI Registration - New License');
    expect(optionTexts).toContain('GST Registration');
    expect(optionTexts.every((txt) => !txt.includes('Base: ₹'))).toBe(true);

    // Enter a custom quote of 45,000 and govt fee 2,500
    const totalInput = screen.getByLabelText(/Total Amount \(₹\)/i) as HTMLInputElement;
    const govtFeeInput = screen.getByLabelText(/Govt Fees \(₹\)/i) as HTMLInputElement;

    await user.clear(totalInput);
    await user.type(totalInput, '45000');
    await user.clear(govtFeeInput);
    await user.type(govtFeeInput, '2500');

    // Change service selection
    fireEvent.change(serviceSelect, {
      target: { value: 'a0000000-0000-0000-0000-000000000001' },
    });

    // Verify custom quote is NOT overwritten
    expect(totalInput.value).toBe('45000');
    expect(govtFeeInput.value).toBe('2500');

    // Change to another service
    fireEvent.change(serviceSelect, {
      target: { value: 'a0000000-0000-0000-0000-000000000002' },
    });
    expect(totalInput.value).toBe('45000');
    expect(govtFeeInput.value).toBe('2500');
  });

  it('renders lead sources including JUSTDIAL and INDIAMART in the Sales Source dropdown', async () => {
    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/entry']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="entry" element={<SalesEntryPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const sourceSelect = screen.getByLabelText(/Source/i) as HTMLSelectElement;
    const options = Array.from(sourceSelect.options).map((o) => o.value.toUpperCase());
    expect(options).toContain('JUSTDIAL');
    expect(options).toContain('INDIAMART');
    expect(options).toContain('WEBSITE');
  });

  it('renders Actions column with Edit button and opens Edit Sales Order modal with populated values', async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/register']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales register/i })).toBeInTheDocument();
    });

    // Check Actions header is present
    expect(screen.getByText(/21\. Actions/i)).toBeInTheDocument();

    // Find and click the Edit button for the first row
    const editButtons = screen.getAllByRole('button', { name: /Edit/i });
    expect(editButtons.length).toBeGreaterThan(0);
    await user.click(editButtons[0]);

    // Verify modal is open with title and pre-filled fields
    await waitFor(() => {
      expect(screen.getByText(/Edit Sales Order:/i)).toBeInTheDocument();
    });

    const totalInput = screen.getByLabelText(/Total Amount \(₹\)/i) as HTMLInputElement;
    expect(totalInput).toBeInTheDocument();
    expect(Number(totalInput.value)).toBe(50000);
  });

  it('updates sales order amounts and calls updateSalesOrderApi on submit', async () => {
    const user = userEvent.setup();
    const updateSpy = vi.spyOn(salesApi, 'updateSalesOrderApi').mockResolvedValue({
      ...mockRegisterData.items[0],
      order_value: 30000,
      amount_received: 30000,
      balance_amount: 0,
      payment_status: 'FULLY_PAID',
    });

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/register']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales register/i })).toBeInTheDocument();
    });

    // Click Edit button on first row
    const editButtons = screen.getAllByRole('button', { name: /Edit/i });
    await user.click(editButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Edit Sales Order:/i)).toBeInTheDocument();
    });

    const totalInput = screen.getByLabelText(/Total Amount \(₹\)/i) as HTMLInputElement;
    const advanceInput = screen.getByLabelText(/Advance \/ Recvd \(₹\)/i) as HTMLInputElement;

    await user.clear(totalInput);
    await user.type(totalInput, '30000');
    await user.clear(advanceInput);
    await user.type(advanceInput, '30000');

    const saveBtn = screen.getByRole('button', { name: /Save Changes/i });
    await user.click(saveBtn);

    await waitFor(() => {
      expect(updateSpy).toHaveBeenCalledWith(
        mockRegisterData.items[0].order_id,
        expect.objectContaining({
          order_value: 30000,
          amount_received: 30000,
        })
      );
    });
  });

  it('populates Converted By filter with only Sales department employees and All', async () => {
    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/register']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales register/i })).toBeInTheDocument();
    });

    // Converted By filter dropdown
    const convertedByFilter = screen.getByDisplayValue('Converted By: All') as HTMLSelectElement;
    expect(convertedByFilter).toBeInTheDocument();

    const options = Array.from(convertedByFilter.options).map((opt) => opt.text);
    expect(options).toContain('Converted By: All');
    expect(options).toContain('Karishma Upadhyay');
    expect(options).toContain('Rajesh Sharma');
    expect(options).not.toContain('Mansi Singhal');
    expect(options).not.toContain('Deepak Kumar');
  });

  it('allows updating Converted By in Edit modal to a Sales department employee', async () => {
    const user = userEvent.setup();
    const updateSpy = vi.spyOn(salesApi, 'updateSalesOrderApi').mockResolvedValue({
      ...mockRegisterData.items[0],
      salesperson_user_id: 'b0000000-0000-0000-0000-000000000002',
      salesperson_name: 'Rajesh Sharma',
    });

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/register']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales register/i })).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole('button', { name: /Edit/i });
    await user.click(editButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Edit Sales Order:/i)).toBeInTheDocument();
    });

    const spSelect = screen.getByLabelText(/Converted By \(Sales Employee\)/i) as HTMLSelectElement;
    expect(spSelect).toBeInTheDocument();

    const spOptions = Array.from(spSelect.options).map((o) => o.text);
    expect(spOptions.some((t) => t.includes('Karishma Upadhyay'))).toBe(true);
    expect(spOptions.some((t) => t.includes('Rajesh Sharma'))).toBe(true);
    expect(spOptions.some((t) => t.includes('Mansi Singhal'))).toBe(false);

    // Select Rajesh Sharma
    await user.selectOptions(spSelect, 'b0000000-0000-0000-0000-000000000002');

    const saveBtn = screen.getByRole('button', { name: /Save Changes/i });
    await user.click(saveBtn);

    await waitFor(() => {
      expect(updateSpy).toHaveBeenCalledWith(
        mockRegisterData.items[0].order_id,
        expect.objectContaining({
          salesperson_user_id: 'b0000000-0000-0000-0000-000000000002',
        })
      );
    });
  });

  it('renders Delete button beside Edit in each row and opens confirmation modal', async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/register']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales register/i })).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole('button', { name: /Delete/i });
    expect(deleteButtons.length).toBeGreaterThan(0);

    // Click Delete button on first row
    await user.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Delete Sales Entry: SO-2026-0001/i)).toBeInTheDocument();
    });

    // Check modal displays client, work, amount and warning
    expect(screen.getAllByText('Acme Agro Foods Pvt Ltd').length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText('FSSAI Registration - New License').length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText(/Are you sure you want to delete this entry\?/i)).toBeInTheDocument();
    expect(screen.getByText(/immediately remove the linked task from the Operations assignee's active task list/i)).toBeInTheDocument();

    // Cancel button closes modal
    const cancelBtn = screen.getByRole('button', { name: /Cancel/i });
    await user.click(cancelBtn);

    await waitFor(() => {
      expect(screen.queryByText(/Delete Sales Entry: SO-2026-0001/i)).not.toBeInTheDocument();
    });
  });

  it('successfully deletes sales order when Delete Entry is confirmed', async () => {
    const user = userEvent.setup();
    const deleteSpy = vi.spyOn(salesApi, 'deleteSalesOrderApi').mockResolvedValue({
      ...mockRegisterData.items[0],
      confirmation_status: 'CANCELLED',
      work_status: 'CANCELLED',
    });

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/register']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales register/i })).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole('button', { name: /Delete/i });
    await user.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Delete Sales Entry: SO-2026-0001/i)).toBeInTheDocument();
    });

    // Click confirm "Delete Entry"
    const confirmDeleteBtn = screen.getByRole('button', { name: /^Delete Entry$/i });
    await user.click(confirmDeleteBtn);

    await waitFor(() => {
      expect(deleteSpy).toHaveBeenCalledWith(mockRegisterData.items[0].order_id);
    });
  });

  it('displays server rejection error when Operations has completed the task', async () => {
    const user = userEvent.setup();
    vi.spyOn(salesApi, 'deleteSalesOrderApi').mockRejectedValue({
      response: {
        status: 400,
        data: {
          detail: 'This entry cannot be deleted because Operations has completed the task.',
        },
      },
    });

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/sales/register']}>
            <Routes>
              <Route path="/sales" element={<SalesLayout />}>
                <Route path="register" element={<SalesRegisterPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /sales register/i })).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole('button', { name: /Delete/i });
    await user.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Delete Sales Entry: SO-2026-0001/i)).toBeInTheDocument();
    });

    const confirmDeleteBtn = screen.getByRole('button', { name: /^Delete Entry$/i });
    fireEvent.click(confirmDeleteBtn);

    await waitFor(() => {
      expect(document.body.textContent).toContain('This entry cannot be deleted because Operations has completed the task.');
    });
  });
});



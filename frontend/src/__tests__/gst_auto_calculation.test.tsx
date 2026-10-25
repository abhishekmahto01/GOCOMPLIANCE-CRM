import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ThemeProvider } from '../context/ThemeContext';
import { SalesEntryPage } from '../pages/SalesEntryPage';
import { SalesLayout } from '../components/sales/SalesLayout';
import * as authApi from '../api/auth';
import * as salesApi from '../api/sales';
import { ACCESS_TOKEN_KEY } from '../api/client';
import type { CurrentUser } from '../types/auth';
import type { AccessibleModule } from '../types/permission';
import type { SalesFormOptionsResponse, SalesRegisterResponse } from '../types/sales';

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
  ],
  salespersons: [
    {
      user_id: 'b0000000-0000-0000-0000-000000000001',
      employee_code: 'GC0001',
      full_name: 'Karishma Upadhyay',
      department_name: 'Sales',
      designation_name: 'Sales Director',
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
  lead_sources: ['WEBSITE', 'REFERRAL', 'DIRECT'],
  operations_assignees: [],
  default_salesperson_id: 'b0000000-0000-0000-0000-000000000001',
  can_select_salesperson: true,
};

const mockRegisterData: SalesRegisterResponse = {
  items: [],
  total_count: 0,
  page: 1,
  limit: 25,
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
};

function renderSalesEntry() {
  return render(
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
}

describe('GST Auto-Calculation in Sales Entry Form', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'test-access-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(mockModules);
    vi.spyOn(salesApi, 'getSalesFormOptionsApi').mockResolvedValue(mockFormOptions);
    vi.spyOn(salesApi, 'getSalesRegisterApi').mockResolvedValue(mockRegisterData);
  });

  it('Case 1: GST Yes with ₹10,000 base amount produces ₹1,800.00 GST and ₹11,800.00 final amount', async () => {
    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const baseInput = screen.getByTestId('base-amount-input');
    const gstYesRadio = screen.getByTestId('gst-yes-radio');

    // Select GST Yes
    fireEvent.click(gstYesRadio);
    expect(gstYesRadio).toBeChecked();

    // Enter ₹10,000
    fireEvent.change(baseInput, { target: { value: '10000' } });

    // Verify GST breakdown panel
    await waitFor(() => {
      expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹10,000.00');
      expect(screen.getByTestId('summary-gst-rate')).toHaveTextContent('18%');
      expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹1,800.00');
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹11,800.00');
    });

    // Verify KPI card
    expect(screen.getByTestId('kpi-total-amount')).toHaveTextContent('₹11,800.00');
  });

  it('Case 2: GST No with ₹10,000 base amount produces ₹0.00 GST and ₹10,000.00 final amount', async () => {
    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const baseInput = screen.getByTestId('base-amount-input');
    const gstNoRadio = screen.getByTestId('gst-no-radio');

    // Select GST No
    fireEvent.click(gstNoRadio);
    expect(gstNoRadio).toBeChecked();

    // Enter ₹10,000
    fireEvent.change(baseInput, { target: { value: '10000' } });

    // Verify GST breakdown panel
    await waitFor(() => {
      expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹10,000.00');
      expect(screen.getByTestId('summary-gst-rate')).toHaveTextContent('0%');
      expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹0.00');
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹10,000.00');
    });

    // Verify KPI card
    expect(screen.getByTestId('kpi-total-amount')).toHaveTextContent('₹10,000.00');
  });

  it('Case 3: Switching from GST Yes to GST No removes the GST component without changing the base amount', async () => {
    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const baseInput = screen.getByTestId('base-amount-input');
    const gstYesRadio = screen.getByTestId('gst-yes-radio');
    const gstNoRadio = screen.getByTestId('gst-no-radio');

    // Start with GST Yes and 10000
    fireEvent.click(gstYesRadio);
    fireEvent.change(baseInput, { target: { value: '10000' } });

    await waitFor(() => {
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹11,800.00');
    });

    // Switch to GST No
    fireEvent.click(gstNoRadio);

    await waitFor(() => {
      // Base amount unchanged
      expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹10,000.00');
      expect(baseInput).toHaveValue(10000);
      // GST removed
      expect(screen.getByTestId('summary-gst-rate')).toHaveTextContent('0%');
      expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹0.00');
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹10,000.00');
    });
  });

  it('Case 4: Switching from GST No to GST Yes adds GST exactly once without compounding repeatedly', async () => {
    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const baseInput = screen.getByTestId('base-amount-input');
    const gstYesRadio = screen.getByTestId('gst-yes-radio');
    const gstNoRadio = screen.getByTestId('gst-no-radio');

    // Start with GST No and 10000
    fireEvent.click(gstNoRadio);
    fireEvent.change(baseInput, { target: { value: '10000' } });

    await waitFor(() => {
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹10,000.00');
    });

    // Switch to GST Yes
    fireEvent.click(gstYesRadio);
    await waitFor(() => {
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹11,800.00');
    });

    // Click GST Yes again (simulating repeated clicks)
    fireEvent.click(gstYesRadio);
    expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹11,800.00');
    expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹10,000.00');

    // Switch to GST No, then back to GST Yes
    fireEvent.click(gstNoRadio);
    await waitFor(() => {
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹10,000.00');
    });

    fireEvent.click(gstYesRadio);
    await waitFor(() => {
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹11,800.00');
      expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹1,800.00');
      expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹10,000.00');
    });
  });

  it('Case 5: Changing the amount recalculates the GST and final amount correctly', async () => {
    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const baseInput = screen.getByTestId('base-amount-input');
    const gstYesRadio = screen.getByTestId('gst-yes-radio');

    fireEvent.click(gstYesRadio);
    fireEvent.change(baseInput, { target: { value: '10000' } });

    await waitFor(() => {
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹11,800.00');
    });

    // Change amount to ₹25,000
    fireEvent.change(baseInput, { target: { value: '25000' } });

    await waitFor(() => {
      expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹25,000.00');
      expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹4,500.00');
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹29,500.00');
    });

    // Change amount to ₹50,000
    fireEvent.change(baseInput, { target: { value: '50000' } });

    await waitFor(() => {
      expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹50,000.00');
      expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹9,000.00');
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹59,000.00');
    });
  });

  it('Case 6: Empty amount is handled according to existing form validation rules', async () => {
    const user = userEvent.setup();
    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const baseInput = screen.getByTestId('base-amount-input');
    fireEvent.change(baseInput, { target: { value: '' } });

    // Breakdown should show ₹0.00 safely without NaN
    expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹0.00');
    expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹0.00');
    expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹0.00');

    // Attempt form submit
    const submitBtn = screen.getByRole('button', { name: /save & confirm order/i });
    await user.click(submitBtn);

    // Form validation error should display
    await waitFor(() => {
      expect(screen.getByText(/Amount must be a number/i)).toBeInTheDocument();
    });
  });

  it('Case 7: Zero amount is handled correctly', async () => {
    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const baseInput = screen.getByTestId('base-amount-input');
    const gstYesRadio = screen.getByTestId('gst-yes-radio');
    fireEvent.click(gstYesRadio);
    fireEvent.change(baseInput, { target: { value: '0' } });

    await waitFor(() => {
      expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹0.00');
      expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹0.00');
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹0.00');
    });
  });

  it('Case 8: Negative amounts are rejected by validation', async () => {
    const user = userEvent.setup();
    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const baseInput = screen.getByTestId('base-amount-input');
    fireEvent.change(baseInput, { target: { value: '-500' } });

    const submitBtn = screen.getByRole('button', { name: /save & confirm order/i });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Amount must be greater than or equal to 0/i)).toBeInTheDocument();
    });
  });

  it('Case 9: Invalid numeric input cannot produce a misleading final amount', async () => {
    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const baseInput = screen.getByTestId('base-amount-input');
    fireEvent.change(baseInput, { target: { value: 'invalid_text' } });

    // Should gracefully display ₹0.00 rather than NaN or undefined
    expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹0.00');
    expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹0.00');
    expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹0.00');
    expect(screen.getByTestId('summary-final-amount').textContent).not.toContain('NaN');
  });

  it('Case 10: Decimal amounts are rounded consistently to two decimal places', async () => {
    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    const baseInput = screen.getByTestId('base-amount-input');
    const gstYesRadio = screen.getByTestId('gst-yes-radio');
    fireEvent.click(gstYesRadio);

    // Test with 10000.55: 18% of 10000.55 = 1800.099 -> 1800.10, final = 11800.65
    fireEvent.change(baseInput, { target: { value: '10000.55' } });

    await waitFor(() => {
      expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹10,000.55');
      expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹1,800.10');
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹11,800.65');
    });

    // Test with 100.33: 18% of 100.33 = 18.0594 -> 18.06, final = 118.39
    fireEvent.change(baseInput, { target: { value: '100.33' } });

    await waitFor(() => {
      expect(screen.getByTestId('summary-base-amount')).toHaveTextContent('₹100.33');
      expect(screen.getByTestId('summary-gst-amount')).toHaveTextContent('₹18.06');
      expect(screen.getByTestId('summary-final-amount')).toHaveTextContent('₹118.39');
    });
  });

  it('Submits correct financial fields payload on form submission', async () => {
    const user = userEvent.setup();
    const createSpy = vi.spyOn(salesApi, 'createSalesEntryApi').mockResolvedValue({
      order_id: 'ord-new',
      order_number: 'SO-2026-9999',
      s_no: 1,
      company_id: 'comp-1',
      client_id: 'c0000000-0000-0000-0000-000000000001',
      service_id: 'a0000000-0000-0000-0000-000000000001',
      salesperson_user_id: 'b0000000-0000-0000-0000-000000000001',
      order_date: '2026-10-24',
      formatted_date: '24 Oct 2026',
      client_name: 'Acme Agro Foods Pvt Ltd',
      location: 'Mumbai',
      contact_no: '9876543210',
      lead_source: 'WEBSITE',
      service_name: 'FSSAI Registration',
      salesperson_name: 'Karishma Upadhyay',
      work_status: 'PENDING',
      order_value: 11800,
      base_amount: 10000,
      gst_amount: 1800,
      gst_rate: 18,
      gst_invoice_required: true,
      amount_received: 0,
      balance_amount: 11800,
      payment_status: 'PENDING',
      govt_fees: 0,
      incidental_cost: 0,
      profit_amount: 11800,
      confirmation_status: 'PENDING_APPROVAL',
      operation_status: 'UNASSIGNED',
    });

    renderSalesEntry();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /new sales entry/i })).toBeInTheDocument();
    });

    // Select service
    const serviceSelect = screen.getByLabelText(/Work \/ Service/i);
    fireEvent.change(serviceSelect, {
      target: { value: 'a0000000-0000-0000-0000-000000000001' },
    });

    // Fill Client Info
    const clientInput = screen.getByPlaceholderText(/Acme Legal Solutions/i);
    await user.type(clientInput, 'Acme Agro Foods Pvt Ltd');

    const phoneInput = screen.getByPlaceholderText(/9876543210/i);
    await user.type(phoneInput, '9876543210');

    // GST Yes and Base Amount 10000
    const gstYesRadio = screen.getByTestId('gst-yes-radio');
    await user.click(gstYesRadio);

    const baseInput = screen.getByTestId('base-amount-input');
    await user.clear(baseInput);
    await user.type(baseInput, '10000');

    const submitBtn = screen.getByRole('button', { name: /save & confirm order/i });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(createSpy).toHaveBeenCalled();
    });

    const submittedData = createSpy.mock.calls[0][0];
    expect(submittedData.base_amount).toBe(10000);
    expect(submittedData.gst_rate).toBe(18);
    expect(submittedData.gst_amount).toBe(1800);
    expect(submittedData.order_value).toBe(11800);
    expect(submittedData.gst_invoice_required).toBe(true);
  });
});

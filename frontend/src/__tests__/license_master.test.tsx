import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { LicenseMasterPage } from '../pages/LicenseMasterPage';
import { AuthProvider } from '../context/AuthContext';
import * as licensesApi from '../api/licenses';
import * as authApi from '../api/auth';
import type { License } from '../types/license';
import { ACCESS_TOKEN_KEY } from '../api/client';

const mockAdminUser = {
  user_id: '11111111-1111-1111-1111-111111111111',
  employee_code: 'CG0001',
  first_name: 'Super',
  last_name: 'Admin',
  official_email: 'admin@gocompliances.in',
  mobile_number: '+919876543210',
  company_id: '22222222-2222-2222-2222-222222222222',
  department_id: '33333333-3333-3333-3333-333333333333',
  designation_id: '44444444-4444-4444-4444-444444444444',
  account_status: 'ACTIVE' as const,
  must_change_password: false,
  company_name: 'Gocompliances',
  department_name: 'Administration',
  designation_name: 'Super Administrator',
};

const fullAdminModules = [
  {
    module_id: 'm-admin',
    module_code: 'ADMIN',
    module_name: 'Administration',
    parent_module_id: null,
    display_order: 1,
    is_navigation: true,
    can_view: true,
    can_create: true,
    can_edit: true,
    can_delete: true,
    can_approve: true,
    data_scope: 'ALL' as const,
  },
];

const mockLicenses: License[] = [
  {
    service_id: '11111111-1111-1111-1111-111111111111',
    service_code: 'FSSAI_REG',
    service_name: 'FSSAI Food Registration',
    category: 'LICENCE',
    description: 'Food Safety and Standards Authority registration',
    base_price: 3500,
    govt_fee: 500,
    standard_turnaround_days: 15,
    status: 'ACTIVE',
    created_at: '2026-09-01T00:00:00Z',
    updated_at: '2026-09-01T00:00:00Z',
  },
  {
    service_id: '22222222-2222-2222-2222-222222222222',
    service_code: 'TRADE_LIC',
    service_name: 'Trade License',
    category: 'LICENCE',
    description: 'Municipal trade license permit',
    base_price: 4500,
    govt_fee: 1000,
    standard_turnaround_days: 20,
    status: 'ACTIVE',
    created_at: '2026-09-01T00:00:00Z',
    updated_at: '2026-09-01T00:00:00Z',
  },
  {
    service_id: '33333333-3333-3333-3333-333333333333',
    service_code: 'OLD_LIC',
    service_name: 'Discontinued License',
    category: 'LICENCE',
    description: 'Old inactive license',
    base_price: 2000,
    govt_fee: 0,
    standard_turnaround_days: 30,
    status: 'INACTIVE',
    created_at: '2026-09-01T00:00:00Z',
    updated_at: '2026-09-01T00:00:00Z',
  },
];

describe('LicenseMasterPage Component Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'mock-valid-token');
    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullAdminModules);

    vi.spyOn(licensesApi, 'getLicensesApi').mockImplementation(async (params) => {
      let filtered = [...mockLicenses];
      if (params?.search) {
        const s = params.search.toLowerCase();
        filtered = filtered.filter(
          (l) =>
            l.service_name.toLowerCase().includes(s) ||
            l.service_code.toLowerCase().includes(s)
        );
      }
      if (params?.category && params.category !== 'ALL') {
        filtered = filtered.filter((l) => l.category === params.category);
      }
      if (params?.status && params.status !== 'ALL') {
        filtered = filtered.filter((l) => l.status === params.status);
      }
      return filtered;
    });
  });

  const renderWithProviders = (component: React.ReactNode) => {
    return render(
      <MemoryRouter>
        <AuthProvider>{component}</AuthProvider>
      </MemoryRouter>
    );
  };

  it('renders license master page header, summary stats, and license list', async () => {
    renderWithProviders(<LicenseMasterPage />);

    expect(screen.getByText('License Master')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('FSSAI Food Registration')).toBeInTheDocument();
      expect(screen.getByText('Trade License')).toBeInTheDocument();
      expect(screen.getByText('Discontinued License')).toBeInTheDocument();
    });

    // Check stats badges
    expect(screen.getByText('Active Offerings')).toBeInTheDocument();
    expect(screen.getByText('Categories')).toBeInTheDocument();
  });

  it('filters licenses by search term', async () => {
    renderWithProviders(<LicenseMasterPage />);

    await waitFor(() => {
      expect(screen.getByText('FSSAI Food Registration')).toBeInTheDocument();
      expect(screen.getByText('Trade License')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/Search license name, code, category, or description/i);
    fireEvent.change(searchInput, { target: { value: 'FSSAI' } });

    await waitFor(() => {
      expect(screen.getByText('FSSAI Food Registration')).toBeInTheDocument();
      expect(screen.queryByText('Trade License')).not.toBeInTheDocument();
    });
  });

  it('opens Add License modal, submits form and calls createLicenseApi', async () => {
    const createdLicense: License = {
      service_id: '44444444-4444-4444-4444-444444444444',
      service_code: 'FIRE_NOC',
      service_name: 'Fire Department NOC',
      category: 'LICENCE',
      description: 'Fire safety clearance certificate',
      base_price: 12000,
      govt_fee: 2500,
      standard_turnaround_days: 25,
      status: 'ACTIVE',
      created_at: '2026-09-01T00:00:00Z',
      updated_at: '2026-09-01T00:00:00Z',
    };

    const createSpy = vi.spyOn(licensesApi, 'createLicenseApi').mockResolvedValue(createdLicense);

    renderWithProviders(<LicenseMasterPage />);

    await waitFor(() => {
      expect(screen.getByText('FSSAI Food Registration')).toBeInTheDocument();
    });

    // Click "Add License" button
    const addBtn = screen.getByRole('button', { name: /Add License/i });
    fireEvent.click(addBtn);

    // Verify modal appears
    await waitFor(() => {
      expect(screen.getByText('Register New License / Service')).toBeInTheDocument();
    });

    // Fill form
    const codeInput = screen.getByPlaceholderText(/e\.g\. FSSAI_LICENSE/i);
    const nameInput = screen.getByPlaceholderText(/e\.g\. FSSAI Food Safety License, Trade License/i);

    fireEvent.change(codeInput, { target: { value: 'FIRE_NOC' } });
    fireEvent.change(nameInput, { target: { value: 'Fire Department NOC' } });

    // Submit
    const submitBtn = screen.getByRole('button', { name: /Create License/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(createSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          service_code: 'FIRE_NOC',
          service_name: 'Fire Department NOC',
        })
      );
    });
  });

  it('opens Edit License modal and calls updateLicenseApi', async () => {
    const updatedLicense: License = {
      ...mockLicenses[0],
      service_name: 'FSSAI Food Central License',
    };

    const updateSpy = vi.spyOn(licensesApi, 'updateLicenseApi').mockResolvedValue(updatedLicense);

    renderWithProviders(<LicenseMasterPage />);

    await waitFor(() => {
      expect(screen.getByText('FSSAI Food Registration')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.queryByText('Loading license records...')).not.toBeInTheDocument();
      expect(screen.getAllByRole('button', { name: /^Edit$/i }).length).toBeGreaterThan(0);
    });

    const editButtons = screen.getAllByRole('button', { name: /^Edit$/i });
    fireEvent.click(editButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Edit License Details')).toBeInTheDocument();
    });

    const nameInput = screen.getByDisplayValue('FSSAI Food Registration');
    fireEvent.change(nameInput, { target: { value: 'FSSAI Food Central License' } });

    const updateBtn = screen.getByRole('button', { name: /Save Changes/i });
    fireEvent.click(updateBtn);

    await waitFor(() => {
      expect(updateSpy).toHaveBeenCalledWith(
        mockLicenses[0].service_id,
        expect.objectContaining({
          service_name: 'FSSAI Food Central License',
        })
      );
    });
  });

  it('opens Delete License modal and calls deleteLicenseApi', async () => {
    const deleteSpy = vi.spyOn(licensesApi, 'deleteLicenseApi').mockResolvedValue({
      message: 'Deleted successfully',
      license_id: mockLicenses[1].service_id,
    });

    renderWithProviders(<LicenseMasterPage />);

    await waitFor(() => {
      expect(screen.getByText('Trade License')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.queryByText('Loading license records...')).not.toBeInTheDocument();
      expect(screen.getAllByRole('button', { name: /^Delete$/i }).length).toBeGreaterThan(0);
    });

    const deleteButtons = screen.getAllByRole('button', { name: /^Delete$/i });
    fireEvent.click(deleteButtons[1]); // Trade license delete button

    await waitFor(() => {
      expect(screen.getByText('Delete License / Service')).toBeInTheDocument();
    });

    const confirmBtn = screen.getByRole('button', { name: /Delete License/i });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(deleteSpy).toHaveBeenCalledWith(mockLicenses[1].service_id);
    });
  });
});

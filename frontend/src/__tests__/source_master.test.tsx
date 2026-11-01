import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { SourceMasterPage } from '../pages/SourceMasterPage';
import { AuthProvider } from '../context/AuthContext';
import * as sourcesApi from '../api/sources';
import * as authApi from '../api/auth';
import type { SourceMaster } from '../types/source';
import { ACCESS_TOKEN_KEY } from '../api/client';
import { ADMIN_NAV_GROUPS } from '../components/admin/adminNavConfig';

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

const mockSources: SourceMaster[] = [
  {
    source_id: '11111111-1111-1111-1111-111111111111',
    source_code: 'WEBSITE',
    source_name: 'Website',
    description: 'Direct enquiries from company website',
    status: 'ACTIVE',
    is_system: true,
    created_at: '2026-09-01T00:00:00Z',
    updated_at: '2026-09-01T00:00:00Z',
  },
  {
    source_id: '22222222-2222-2222-2222-222222222222',
    source_code: 'GOOGLE_ADS',
    source_name: 'Google Ads',
    description: 'PPC Search and display network ads',
    status: 'ACTIVE',
    is_system: false,
    created_at: '2026-09-02T00:00:00Z',
    updated_at: '2026-09-02T00:00:00Z',
  },
  {
    source_id: '33333333-3333-3333-3333-333333333333',
    source_code: 'JUSTDIAL',
    source_name: 'Justdial',
    description: 'Lead acquisition via Justdial platform',
    status: 'INACTIVE',
    is_system: true,
    created_at: '2026-09-03T00:00:00Z',
    updated_at: '2026-09-03T00:00:00Z',
  },
];

describe('SourceMasterPage and Navigation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem(ACCESS_TOKEN_KEY, 'test-access-token');

    vi.spyOn(authApi, 'getCurrentUserApi').mockResolvedValue(mockAdminUser);
    vi.spyOn(authApi, 'getAccessibleModulesApi').mockResolvedValue(fullAdminModules);
    vi.spyOn(sourcesApi, 'getSourcesApi').mockResolvedValue(mockSources);
  });

  const renderComponent = () =>
    render(
      <MemoryRouter>
        <AuthProvider>
          <SourceMasterPage />
        </AuthProvider>
      </MemoryRouter>
    );

  it('renders Source Master in adminNavConfig under Common Master', () => {
    const commonMasterGroup = ADMIN_NAV_GROUPS.find((g) => g.id === 'common_master');
    expect(commonMasterGroup).toBeDefined();

    const sourceMasterNav = commonMasterGroup?.children.find((c) => c.id === 'source_master');
    expect(sourceMasterNav).toBeDefined();
    expect(sourceMasterNav?.title).toBe('Source Master');
    expect(sourceMasterNav?.route).toBe('/admin/sources');
  });

  it('renders Source Master header, KPI counts, and lists source rows', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Source Master')).toBeInTheDocument();
      expect(screen.getByText('3 Registered')).toBeInTheDocument();
    });

    expect(screen.getByText('Website')).toBeInTheDocument();
    expect(screen.getByText('Google Ads')).toBeInTheDocument();
    expect(screen.getByText('Justdial')).toBeInTheDocument();
    expect(screen.getByText('WEBSITE')).toBeInTheDocument();
    expect(screen.getByText('GOOGLE_ADS')).toBeInTheDocument();
  });

  it('filters sources when searching in search input', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Website')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/Search source name, code, or description/i);
    fireEvent.change(searchInput, { target: { value: 'Google' } });

    await waitFor(() => {
      expect(sourcesApi.getSourcesApi).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'Google' })
      );
    });
  });

  it('opens Add Source modal, inputs data, and invokes createSourceApi', async () => {
    const createMock = vi.spyOn(sourcesApi, 'createSourceApi').mockResolvedValue({
      source_id: '44444444-4444-4444-4444-444444444444',
      source_code: 'FACEBOOK_ADS',
      source_name: 'Facebook Ads',
      description: 'Meta campaigns',
      status: 'ACTIVE',
      is_system: false,
      created_at: '2026-09-04T00:00:00Z',
      updated_at: '2026-09-04T00:00:00Z',
    });

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Add Source')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Add Source'));

    expect(screen.getByText('Add New Lead Source')).toBeInTheDocument();

    const nameInput = screen.getByPlaceholderText(/e\.g\. Google Ads, Facebook, Trade Fair/i);
    fireEvent.change(nameInput, { target: { value: 'Facebook Ads' } });

    const codeInput = screen.getByPlaceholderText(/e\.g\. GOOGLE_ADS/i);
    fireEvent.change(codeInput, { target: { value: 'FACEBOOK_ADS' } });

    const saveButton = screen.getByRole('button', { name: /Save Source/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(createMock).toHaveBeenCalledWith(
        expect.objectContaining({
          source_name: 'Facebook Ads',
          source_code: 'FACEBOOK_ADS',
        })
      );
    });
  });

  it('opens Edit Source modal and updates source via updateSourceApi', async () => {
    const updateMock = vi.spyOn(sourcesApi, 'updateSourceApi').mockResolvedValue({
      ...mockSources[1],
      source_name: 'Google PPC Ads',
    });

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Google Ads')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByTitle('Edit Source');
    fireEvent.click(editButtons[1]); // Edit second item (Google Ads)

    await waitFor(() => {
      expect(screen.getByText(/Edit Source: Google Ads/i)).toBeInTheDocument();
    });

    const nameInput = screen.getByDisplayValue('Google Ads');
    fireEvent.change(nameInput, { target: { value: 'Google PPC Ads' } });

    const updateButton = screen.getByRole('button', { name: /Update Source/i });
    fireEvent.click(updateButton);

    await waitFor(() => {
      expect(updateMock).toHaveBeenCalledWith(
        mockSources[1].source_id,
        expect.objectContaining({
          source_name: 'Google PPC Ads',
        })
      );
    });
  });
});

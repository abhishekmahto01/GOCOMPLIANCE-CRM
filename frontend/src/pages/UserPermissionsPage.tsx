import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  ShieldCheck,
  Search,
  Save,
  Copy,
  ChevronDown,
  ChevronRight,
  Mail,
  MapPin,
  Users,
  AlertTriangle,
  Loader2,
  CheckCircle2,
  XCircle,
  ShieldAlert,
} from 'lucide-react';
import { clsx } from 'clsx';
import {
  getPermissionCatalogApi,
  getUserPermissionsApi,
  saveUserPermissionsApi,
  copyUserPermissionsApi,
} from '../api/permissions';
import { getLookupCompaniesApi, getLookupManagersApi } from '../api/lookup';
import { getEmployeesApi } from '../api/employees';
import { extractErrorMessage } from '../api/client';
import { useAuth } from '../context/AuthContext';
import type {
  CatalogModuleItem,
  CatalogPageItem,
  PageActionPermission,
  UserPermissionsDetailResponse,
  UserPermissionsSaveRequest,
  DataScope,
} from '../types/permission';
import type { CompanyLookup, ManagerLookup } from '../types/lookup';
import type { Employee } from '../types/employee';
import { ConfirmationModal } from '../components/common/ConfirmationModal';

// Action pill display labels & color themes
const ACTION_DISPLAY_CONFIG: Record<string, { label: string; activeColor: string; inactiveColor: string }> = {
  read: {
    label: 'READ',
    activeColor: 'border-indigo-600 bg-indigo-600 text-white',
    inactiveColor: 'border-indigo-300 text-indigo-700 bg-indigo-50/60 hover:bg-indigo-100 dark:border-indigo-500 dark:text-indigo-300 dark:bg-indigo-950/30',
  },
  write: {
    label: 'WRITE',
    activeColor: 'border-purple-600 bg-purple-600 text-white',
    inactiveColor: 'border-purple-300 text-purple-700 bg-purple-50/60 hover:bg-purple-100 dark:border-purple-500 dark:text-purple-300 dark:bg-purple-950/30',
  },
  update: {
    label: 'UPDATE',
    activeColor: 'border-blue-600 bg-blue-600 text-white',
    inactiveColor: 'border-blue-300 text-blue-700 bg-blue-50/60 hover:bg-blue-100 dark:border-blue-500 dark:text-blue-300 dark:bg-blue-950/30',
  },
  delete: {
    label: 'DELETE',
    activeColor: 'border-rose-600 bg-rose-600 text-white',
    inactiveColor: 'border-rose-300 text-rose-700 bg-rose-50/60 hover:bg-rose-100 dark:border-rose-500 dark:text-rose-300 dark:bg-rose-950/30',
  },
  assign: {
    label: 'ASSIGN',
    activeColor: 'border-amber-600 bg-amber-600 text-white',
    inactiveColor: 'border-amber-300 text-amber-700 bg-amber-50/60 hover:bg-amber-100 dark:border-amber-500 dark:text-amber-300 dark:bg-amber-950/30',
  },
  reassign: {
    label: 'REASSIGN',
    activeColor: 'border-cyan-600 bg-cyan-600 text-white',
    inactiveColor: 'border-cyan-300 text-cyan-700 bg-cyan-50/60 hover:bg-cyan-100 dark:border-cyan-500 dark:text-cyan-300 dark:bg-cyan-950/30',
  },
  export: {
    label: 'EXPORT',
    activeColor: 'border-emerald-600 bg-emerald-600 text-white',
    inactiveColor: 'border-emerald-300 text-emerald-700 bg-emerald-50/60 hover:bg-emerald-100 dark:border-emerald-500 dark:text-emerald-300 dark:bg-emerald-950/30',
  },
};

export const UserPermissionsPage: React.FC = () => {
  const { hasPermission } = useAuth();
  const canManageAccess = hasPermission('ADMIN', 'view') || hasPermission('ADMIN_EMPLOYEES', 'view');

  const [searchParams] = useSearchParams();
  const initialUserId = searchParams.get('userId') || searchParams.get('user_id') || '';

  // Master Lookups & Catalog
  const [catalog, setCatalog] = useState<CatalogModuleItem[]>([]);
  const [companies, setCompanies] = useState<CompanyLookup[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [managers, setManagers] = useState<ManagerLookup[]>([]);

  // Selection Filters
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('');
  const [selectedUserId, setSelectedUserId] = useState<string>(initialUserId);
  const [moduleFilter, setModuleFilter] = useState<string>('ALL');

  // Active Employee State
  const [currentUserDetail, setCurrentUserDetail] = useState<UserPermissionsDetailResponse | null>(null);
  const [permissionsState, setPermissionsState] = useState<Record<string, PageActionPermission>>({});
  const [isHod, setIsHod] = useState<boolean>(false);
  const [isReportingManager, setIsReportingManager] = useState<boolean>(false);
  const [isActive, setIsActive] = useState<boolean>(true);
  const [selectedManagerId, setSelectedManagerId] = useState<string>('');
  const [primaryLocation, setPrimaryLocation] = useState<string>('');

  // Copy Permissions
  const [copySourceUserId, setCopySourceUserId] = useState<string>('');
  const [isCopyModalOpen, setIsCopyModalOpen] = useState<boolean>(false);

  // UI state
  const [collapsedModules, setCollapsedModules] = useState<Record<string, boolean>>({});
  const [isDirty, setIsDirty] = useState<boolean>(false);
  const [isLoadingCatalog, setIsLoadingCatalog] = useState<boolean>(true);
  const [isLoadingPermissions, setIsLoadingPermissions] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isCopying, setIsCopying] = useState<boolean>(false);

  // Toast feedback
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Prompt before navigating away with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);

  // Load initial catalog & company lookups
  useEffect(() => {
    const loadInitialData = async () => {
      setIsLoadingCatalog(true);
      try {
        const [catalogRes, companiesRes] = await Promise.all([
          getPermissionCatalogApi(),
          getLookupCompaniesApi(),
        ]);
        setCatalog(catalogRes.modules || []);
        setCompanies(companiesRes || []);
      } catch (err) {
        setToast({
          message: `Failed to load catalog metadata: ${extractErrorMessage(err)}`,
          type: 'error',
        });
      } finally {
        setIsLoadingCatalog(false);
      }
    };
    loadInitialData();
  }, []);

  // Load employees when company filter changes (only ACTIVE employees by default)
  useEffect(() => {
    const loadEmployees = async () => {
      try {
        const res = await getEmployeesApi({
          company_id: selectedCompanyId || undefined,
          account_status: 'ACTIVE',
          page_size: 100,
        });
        setEmployees(res.items || []);
      } catch (err) {
        console.error('Failed to load employees for dropdown:', err);
      }
    };
    loadEmployees();
  }, [selectedCompanyId]);

  // Load managers lookup
  useEffect(() => {
    const loadManagers = async () => {
      try {
        const mgrs = await getLookupManagersApi(selectedCompanyId || undefined, selectedUserId || undefined);
        setManagers(mgrs || []);
      } catch (err) {
        console.error('Failed to load managers lookup:', err);
      }
    };
    loadManagers();
  }, [selectedCompanyId, selectedUserId]);

  // Fetch permissions for selected employee
  const fetchEmployeePermissions = useCallback(async (userId: string) => {
    if (!userId) return;
    setIsLoadingPermissions(true);
    try {
      const res = await getUserPermissionsApi(userId);
      setCurrentUserDetail(res);

      // Map permissions by page_code
      const permMap: Record<string, PageActionPermission> = {};
      (res.permissions || []).forEach((p) => {
        permMap[p.page_code] = { ...p };
      });
      setPermissionsState(permMap);

      // Populate user settings
      setIsHod(Boolean(res.is_hod));
      setIsReportingManager(Boolean(res.is_reporting_manager));
      setIsActive(Boolean(res.is_active));
      setSelectedManagerId(res.manager_user_id || '');
      setPrimaryLocation(res.primary_location || '');
      setIsDirty(false);
    } catch (err) {
      setToast({
        message: `Failed to load permissions: ${extractErrorMessage(err)}`,
        type: 'error',
      });
    } finally {
      setIsLoadingPermissions(false);
    }
  }, []);

  // Auto-fetch if initialUserId is present in query parameters
  useEffect(() => {
    if (initialUserId) {
      fetchEmployeePermissions(initialUserId);
    }
  }, [initialUserId, fetchEmployeePermissions]);

  // Handle employee dropdown selection
  const handleSelectEmployee = (newUserId: string) => {
    if (isDirty) {
      const confirmChange = window.confirm(
        'You have unsaved permission changes. Switching employees will discard them. Proceed?'
      );
      if (!confirmChange) return;
    }
    setSelectedUserId(newUserId);
    if (newUserId) {
      fetchEmployeePermissions(newUserId);
    } else {
      setCurrentUserDetail(null);
      setPermissionsState({});
      setIsDirty(false);
    }
  };

  // Filtered employee list for dropdown
  const filteredEmployees = useMemo(() => {
    return employees.filter((emp) => {
      if (selectedCompanyId && emp.company_id !== selectedCompanyId) return false;
      return true;
    });
  }, [employees, selectedCompanyId]);

  // Selected employee metadata object
  const selectedEmployeeObj = useMemo(() => {
    return employees.find((e) => e.user_id === selectedUserId) || currentUserDetail;
  }, [employees, selectedUserId, currentUserDetail]);

  // Filtered catalog modules
  const filteredCatalog = useMemo(() => {
    if (moduleFilter === 'ALL') return catalog;
    return catalog.filter((m) => m.module_code.toUpperCase() === moduleFilter.toUpperCase());
  }, [catalog, moduleFilter]);

  // Check if a specific action is active for a page
  const isActionActive = (pageCode: string, action: string): boolean => {
    const perm = permissionsState[pageCode];
    if (!perm || !perm.can_view) return false;
    switch (action.toLowerCase()) {
      case 'read':
        return perm.can_view;
      case 'write':
        return perm.can_create;
      case 'update':
        return perm.can_edit;
      case 'delete':
        return perm.can_delete;
      case 'assign':
        return perm.can_assign;
      case 'reassign':
        return perm.can_reassign;
      case 'export':
        return perm.can_export;
      default:
        return false;
    }
  };

  // Check if 'All' supported actions are active for a page
  const isPageAllActive = (page: CatalogPageItem): boolean => {
    const perm = permissionsState[page.page_code];
    if (!perm || !perm.can_view) return false;
    return page.supported_actions.every((act) => isActionActive(page.page_code, act));
  };

  // Check if all pages in a module have all actions active
  const isModuleAllActive = (mod: CatalogModuleItem): boolean => {
    if (!mod.pages || mod.pages.length === 0) return false;
    return mod.pages.every((p) => isPageAllActive(p));
  };

  // Toggle individual action permission
  const handleToggleAction = (pageCode: string, action: string) => {
    setIsDirty(true);
    setPermissionsState((prev) => {
      const current = prev[pageCode] || {
        page_code: pageCode,
        can_view: false,
        can_create: false,
        can_edit: false,
        can_delete: false,
        can_assign: false,
        can_reassign: false,
        can_export: false,
        can_approve: false,
        data_scope: 'SELF' as DataScope,
        status: 'ACTIVE' as const,
      };

      const next = { ...current };
      const actNorm = action.toLowerCase();

      if (actNorm === 'read') {
        const nextRead = !current.can_view;
        next.can_view = nextRead;
        // If read is unchecked, uncheck all dependent actions
        if (!nextRead) {
          next.can_create = false;
          next.can_edit = false;
          next.can_delete = false;
          next.can_assign = false;
          next.can_reassign = false;
          next.can_export = false;
        }
      } else {
        // Checking any action requires read (can_view) to be enabled
        switch (actNorm) {
          case 'write':
            next.can_create = !current.can_create;
            if (next.can_create) next.can_view = true;
            break;
          case 'update':
            next.can_edit = !current.can_edit;
            if (next.can_edit) next.can_view = true;
            break;
          case 'delete':
            next.can_delete = !current.can_delete;
            if (next.can_delete) next.can_view = true;
            break;
          case 'assign':
            next.can_assign = !current.can_assign;
            if (next.can_assign) next.can_view = true;
            break;
          case 'reassign':
            next.can_reassign = !current.can_reassign;
            if (next.can_reassign) next.can_view = true;
            break;
          case 'export':
            next.can_export = !current.can_export;
            if (next.can_export) next.can_view = true;
            break;
        }
      }

      return {
        ...prev,
        [pageCode]: next,
      };
    });
  };

  // Toggle 'All' on a single page
  const handleTogglePageAll = (page: CatalogPageItem) => {
    setIsDirty(true);
    const currentlyAll = isPageAllActive(page);
    const targetState = !currentlyAll;

    setPermissionsState((prev) => {
      const current = prev[page.page_code] || {
        page_code: page.page_code,
        can_view: false,
        can_create: false,
        can_edit: false,
        can_delete: false,
        can_assign: false,
        can_reassign: false,
        can_export: false,
        can_approve: false,
        data_scope: 'SELF' as DataScope,
        status: 'ACTIVE' as const,
      };

      const supported = new Set(page.supported_actions.map((a) => a.toLowerCase()));
      const next = {
        ...current,
        can_view: targetState,
        can_create: targetState && supported.has('write'),
        can_edit: targetState && supported.has('update'),
        can_delete: targetState && supported.has('delete'),
        can_assign: targetState && supported.has('assign'),
        can_reassign: targetState && supported.has('reassign'),
        can_export: targetState && supported.has('export'),
      };

      return {
        ...prev,
        [page.page_code]: next,
      };
    });
  };

  // Toggle 'Select All' on an entire module
  const handleToggleModuleAll = (mod: CatalogModuleItem) => {
    setIsDirty(true);
    const currentlyAll = isModuleAllActive(mod);
    const targetState = !currentlyAll;

    setPermissionsState((prev) => {
      const updated = { ...prev };
      mod.pages.forEach((page) => {
        const supported = new Set(page.supported_actions.map((a) => a.toLowerCase()));
        updated[page.page_code] = {
          page_code: page.page_code,
          can_view: targetState,
          can_create: targetState && supported.has('write'),
          can_edit: targetState && supported.has('update'),
          can_delete: targetState && supported.has('delete'),
          can_assign: targetState && supported.has('assign'),
          can_reassign: targetState && supported.has('reassign'),
          can_export: targetState && supported.has('export'),
          can_approve: false,
          data_scope: prev[page.page_code]?.data_scope || 'SELF',
          status: 'ACTIVE',
        };
      });
      return updated;
    });
  };

  // Toggle collapse state of a module group
  const toggleCollapse = (moduleCode: string) => {
    setCollapsedModules((prev) => ({
      ...prev,
      [moduleCode]: !prev[moduleCode],
    }));
  };

  // Save permissions & user settings
  const handleSave = async () => {
    if (!selectedUserId) {
      setToast({ message: 'Please select an employee first.', type: 'error' });
      return;
    }

    setIsSaving(true);
    try {
      const permissionsList: PageActionPermission[] = Object.values(permissionsState);

      const payload: UserPermissionsSaveRequest = {
        permissions: permissionsList,
        user_settings: {
          is_active: isActive,
          is_hod: isHod,
          is_reporting_manager: isReportingManager,
          manager_user_id: selectedManagerId || null,
          primary_location: primaryLocation.trim() || null,
        },
      };

      const updated = await saveUserPermissionsApi(selectedUserId, payload);
      setCurrentUserDetail(updated);
      setIsDirty(false);
      setToast({
        message: `Permissions for ${updated.employee_code} (${updated.first_name} ${updated.last_name}) saved successfully!`,
        type: 'success',
      });
    } catch (err) {
      setToast({
        message: `Failed to save permissions: ${extractErrorMessage(err)}`,
        type: 'error',
      });
    } finally {
      setIsSaving(false);
    }
  };

  // Confirm copy permissions
  const handleConfirmCopy = async () => {
    if (!copySourceUserId || !selectedUserId) return;
    setIsCopying(true);
    try {
      const res = await copyUserPermissionsApi(selectedUserId, {
        source_user_id: copySourceUserId,
      });
      setToast({
        message: res.message || 'Permissions copied successfully!',
        type: 'success',
      });
      setIsCopyModalOpen(false);
      setCopySourceUserId('');
      await fetchEmployeePermissions(selectedUserId);
    } catch (err) {
      setToast({
        message: `Copy failed: ${extractErrorMessage(err)}`,
        type: 'error',
      });
    } finally {
      setIsCopying(false);
    }
  };

  const copySourceEmployee = employees.find((e) => e.user_id === copySourceUserId);

  // Access check guard
  if (!canManageAccess) {
    return (
      <div className="w-full max-w-4xl mx-auto px-4 py-16 flex items-center justify-center">
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 border border-rose-200 dark:border-rose-900 text-center shadow-xl space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-rose-100 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 mx-auto flex items-center justify-center">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">
            403 - Access Forbidden
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md">
            You do not have permission to view or manage user access permissions. Contact your system administrator if you believe this is an error.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
      {/* Toast notification banner */}
      {toast && (
        <div
          className={clsx(
            'p-4 rounded-xl border flex items-center justify-between shadow-md transition-all animate-fade-in',
            toast.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-950/50 dark:border-emerald-800 dark:text-emerald-200'
              : 'bg-rose-50 border-rose-200 text-rose-800 dark:bg-rose-950/50 dark:border-rose-800 dark:text-rose-200'
          )}
        >
          <div className="flex items-center gap-3">
            {toast.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
            ) : (
              <XCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0" />
            )}
            <span className="text-sm font-semibold">{toast.message}</span>
          </div>
          <button
            type="button"
            onClick={() => setToast(null)}
            className="text-xs font-bold uppercase tracking-wider hover:opacity-75"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Copy Confirmation Modal */}
      <ConfirmationModal
        isOpen={isCopyModalOpen}
        title="Confirm Permission Copy"
        description={
          copySourceEmployee && selectedEmployeeObj
            ? `Are you sure you want to copy Sales and Operation permissions from ${copySourceEmployee.employee_code} (${copySourceEmployee.first_name} ${copySourceEmployee.last_name}) to ${selectedEmployeeObj.employee_code} (${selectedEmployeeObj.first_name} ${selectedEmployeeObj.last_name})? This will replace existing permissions.`
            : 'Are you sure you want to copy permissions to this employee?'
        }
        confirmText={isCopying ? 'Copying...' : 'Yes, Copy Permissions'}
        cancelText="Cancel"
        isLoading={isCopying}
        onConfirm={handleConfirmCopy}
        onClose={() => setIsCopyModalOpen(false)}
      />

      {/* Top Header Controls Bar (Faithfully matching Reference Screenshot) */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-xs p-5 transition-colors">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          {/* Title and Description */}
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-blue-50 dark:bg-blue-950/50 border border-blue-200 dark:border-blue-800 flex items-center justify-center text-blue-600 dark:text-blue-400 shadow-xs shrink-0">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-[#0a2569] dark:text-white tracking-tight">
                User Permission
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Manage user-wise, module-wise and page-wise granular action rights
              </p>
            </div>
          </div>

          {/* Action & Filter Controls */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Company Dropdown */}
            <div className="w-48 sm:w-56">
              <select
                aria-label="Filter by Company"
                value={selectedCompanyId}
                onChange={(e) => {
                  setSelectedCompanyId(e.target.value);
                  setSelectedUserId('');
                }}
                className="w-full h-10 px-3 text-xs sm:text-sm font-medium rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-blue-500 transition-all"
              >
                <option value="">-- All Companies --</option>
                {companies.map((c) => (
                  <option key={c.company_id} value={c.company_id}>
                    {c.company_code} – {c.company_name}
                  </option>
                ))}
              </select>
            </div>

            {/* Employee Dropdown: EMPLOYEE_CODE – NAME */}
            <div className="w-64 sm:w-72">
              <select
                aria-label="Select Employee"
                value={selectedUserId}
                onChange={(e) => handleSelectEmployee(e.target.value)}
                className="w-full h-10 px-3 text-xs sm:text-sm font-bold rounded-xl border-2 border-blue-500 dark:border-blue-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 shadow-xs transition-all"
              >
                <option value="">- Select Employee -</option>
                {filteredEmployees.map((emp) => (
                  <option key={emp.user_id} value={emp.user_id}>
                    {emp.employee_code} – {emp.first_name} {emp.last_name}
                  </option>
                ))}
              </select>
            </div>

            {/* Department / Module Filter */}
            <div className="w-36 sm:w-44">
              <select
                aria-label="Module Filter"
                value={moduleFilter}
                onChange={(e) => setModuleFilter(e.target.value)}
                className="w-full h-10 px-3 text-xs sm:text-sm font-medium rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-blue-500 transition-all"
              >
                <option value="ALL">All Modules</option>
                <option value="SALES">Sales</option>
                <option value="OPERATIONS">Operation</option>
              </select>
            </div>

            {/* Search / Load Permissions Button (Blue) */}
            <button
              type="button"
              id="search-permissions-btn"
              onClick={() => selectedUserId && fetchEmployeePermissions(selectedUserId)}
              disabled={!selectedUserId || isLoadingPermissions}
              className="h-10 px-5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs sm:text-sm font-bold flex items-center gap-2 shadow-sm transition-all cursor-pointer disabled:cursor-not-allowed"
            >
              {isLoadingPermissions ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              <span>Search</span>
            </button>

            {/* Save Button (Green) */}
            <button
              type="button"
              id="save-permissions-btn"
              onClick={handleSave}
              disabled={!selectedUserId || !isDirty || isSaving || isLoadingPermissions}
              className="h-10 px-6 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-xs sm:text-sm font-bold flex items-center gap-2 shadow-sm transition-all cursor-pointer disabled:cursor-not-allowed"
            >
              {isSaving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              <span>Save</span>
            </button>
          </div>
        </div>

        {/* Unsaved changes indicator */}
        {isDirty && (
          <div className="mt-4 flex items-center gap-2 text-xs font-semibold text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/40 px-3.5 py-2 rounded-xl border border-amber-200 dark:border-amber-800">
            <AlertTriangle className="w-4 h-4 shrink-0 text-amber-600" />
            <span>You have unsaved changes. Click Save to persist them to the database.</span>
          </div>
        )}
      </div>

      {/* Main Content Grid: Left Table & Right User Settings Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Permission Matrix Table */}
        <div className="lg:col-span-8 space-y-6">
          {isLoadingCatalog || isLoadingPermissions ? (
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-12 flex flex-col items-center justify-center gap-3 text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <p className="text-sm font-medium">Loading permissions catalog...</p>
            </div>
          ) : !selectedUserId ? (
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-12 text-center">
              <div className="w-16 h-16 rounded-2xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 flex items-center justify-center mx-auto mb-4 border border-blue-100 dark:border-blue-900">
                <Users className="w-8 h-8" />
              </div>
              <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">
                No Employee Selected
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto mt-1">
                Please select an employee from the dropdown above to inspect and configure page-level permissions.
              </p>
            </div>
          ) : (
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse" id="permissions-table">
                  <thead>
                    <tr className="bg-slate-100/90 dark:bg-slate-800/90 border-b border-slate-200 dark:border-slate-700 text-[11px] font-extrabold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                      <th className="py-3 px-3 w-12 text-center">SR</th>
                      <th className="py-3 px-4 w-36">Module</th>
                      <th className="py-3 px-4 w-48">Page</th>
                      <th className="py-3 px-4">Permissions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
                    {filteredCatalog.map((modGroup) => {
                      const isCollapsed = collapsedModules[modGroup.module_code];
                      const isModAll = isModuleAllActive(modGroup);

                      return (
                        <React.Fragment key={modGroup.module_code}>
                          {/* Module Header Row */}
                          <tr className="bg-slate-50 dark:bg-slate-800/50 font-bold border-t-2 border-slate-200 dark:border-slate-700">
                            <td colSpan={3} className="py-2.5 px-4">
                              <button
                                type="button"
                                onClick={() => toggleCollapse(modGroup.module_code)}
                                className="flex items-center gap-2 text-slate-800 dark:text-slate-200 hover:text-blue-600 transition-colors"
                              >
                                {isCollapsed ? (
                                  <ChevronRight className="w-4 h-4 text-slate-400" />
                                ) : (
                                  <ChevronDown className="w-4 h-4 text-slate-400" />
                                )}
                                <span className="font-extrabold text-sm tracking-tight">
                                  {modGroup.module_name} Module
                                </span>
                                <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-mono font-medium">
                                  {modGroup.pages.length} Pages
                                </span>
                              </button>
                            </td>
                            <td className="py-2.5 px-4 text-right">
                              <label className="inline-flex items-center gap-2 cursor-pointer select-none">
                                <input
                                  type="checkbox"
                                  checked={isModAll}
                                  onChange={() => handleToggleModuleAll(modGroup)}
                                  className="w-4 h-4 rounded-md border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                                />
                                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                                  Select All {modGroup.module_name}
                                </span>
                              </label>
                            </td>
                          </tr>

                          {/* Page Rows */}
                          {!isCollapsed &&
                            modGroup.pages.map((page, idx) => {
                              const isAll = isPageAllActive(page);

                              return (
                                <tr
                                  key={page.page_code}
                                  className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors"
                                >
                                  {/* SR */}
                                  <td className="py-3 px-3 text-center font-bold text-slate-500 dark:text-slate-400">
                                    {idx + 1}
                                  </td>

                                  {/* Module */}
                                  <td className="py-3 px-4 font-semibold text-slate-700 dark:text-slate-300 whitespace-nowrap">
                                    {modGroup.module_name}
                                  </td>

                                  {/* Page */}
                                  <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">
                                    {page.page_name}
                                  </td>

                                  {/* Action Permissions Pills */}
                                  <td className="py-3 px-4">
                                    <div className="flex flex-wrap items-center gap-2">
                                      {/* Page-level 'All' Checkbox Pill */}
                                      <button
                                        type="button"
                                        id={`page-${page.page_code}-all`}
                                        onClick={() => handleTogglePageAll(page)}
                                        className={clsx(
                                          'px-2.5 py-1 rounded-full text-[11px] font-extrabold border-2 transition-all flex items-center gap-1.5 shadow-2xs cursor-pointer select-none',
                                          isAll
                                            ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs'
                                            : 'border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:border-emerald-500 hover:text-emerald-600'
                                        )}
                                      >
                                        <div
                                          className={clsx(
                                            'w-3.5 h-3.5 rounded-full border flex items-center justify-center text-[9px] font-bold',
                                            isAll
                                              ? 'border-white bg-white text-emerald-600'
                                              : 'border-slate-400 bg-white dark:bg-slate-800'
                                          )}
                                        >
                                          {isAll && '✓'}
                                        </div>
                                        <span>All</span>
                                      </button>

                                      {/* Supported Action Badges */}
                                      {page.supported_actions.map((act) => {
                                        const actKey = act.toLowerCase();
                                        const config = ACTION_DISPLAY_CONFIG[actKey] || {
                                          label: act.toUpperCase(),
                                          activeColor: 'border-blue-600 bg-blue-600 text-white',
                                          inactiveColor: 'border-slate-300 text-slate-700',
                                        };
                                        const active = isActionActive(page.page_code, actKey);

                                        return (
                                          <button
                                            key={actKey}
                                            type="button"
                                            id={`perm-${page.page_code}-${actKey}`}
                                            onClick={() => handleToggleAction(page.page_code, actKey)}
                                            className={clsx(
                                              'px-2.5 py-1 rounded-full text-[11px] font-bold border-2 transition-all flex items-center gap-1.5 shadow-2xs cursor-pointer select-none',
                                              active ? config.activeColor : config.inactiveColor
                                            )}
                                          >
                                            <div
                                              className={clsx(
                                                'w-3.5 h-3.5 rounded-full border flex items-center justify-center text-[9px] font-bold',
                                                active
                                                  ? 'border-white bg-white text-blue-600'
                                                  : 'border-slate-400 bg-white dark:bg-slate-800'
                                              )}
                                            >
                                              {active && '✓'}
                                            </div>
                                            <span>{config.label}</span>
                                          </button>
                                        );
                                      })}
                                    </div>
                                  </td>
                                </tr>
                              );
                            })}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: User Settings Panel ("Other Permission") */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs p-5 space-y-5">
            {/* Panel Title */}
            <div className="border-b border-slate-100 dark:border-slate-800 pb-3">
              <h2 className="text-sm font-extrabold text-slate-900 dark:text-white uppercase tracking-wider">
                Other Permission
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Role designations and organizational settings
              </p>
            </div>

            {/* Checkbox Toggles */}
            <div className="space-y-3">
              {/* Set as Reporting Manager */}
              <label className="flex items-center gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-all">
                <input
                  type="checkbox"
                  id="set-reporting-manager-toggle"
                  checked={isReportingManager}
                  disabled={!selectedUserId}
                  onChange={(e) => {
                    setIsDirty(true);
                    setIsReportingManager(e.target.checked);
                  }}
                  className="w-4 h-4 rounded-md border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
                <div>
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">
                    Set as Reporting Manager
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400">
                    Eligible to have subordinates report to them
                  </span>
                </div>
              </label>

              {/* Set as HOD */}
              <label className="flex items-center gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-all">
                <input
                  type="checkbox"
                  id="set-hod-toggle"
                  checked={isHod}
                  disabled={!selectedUserId}
                  onChange={(e) => {
                    setIsDirty(true);
                    setIsHod(e.target.checked);
                  }}
                  className="w-4 h-4 rounded-md border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
                <div>
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">
                    Set as HOD
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400">
                    Designated as Head of Department
                  </span>
                </div>
              </label>

              {/* Set as Active */}
              <label className="flex items-center gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-all">
                <input
                  type="checkbox"
                  id="set-active-toggle"
                  checked={isActive}
                  disabled={!selectedUserId}
                  onChange={(e) => {
                    setIsDirty(true);
                    setIsActive(e.target.checked);
                  }}
                  className="w-4 h-4 rounded-md border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
                <div>
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">
                    Active Employee
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400">
                    Allow account login and module operations
                  </span>
                </div>
              </label>
            </div>

            {/* Email Field (Readonly) */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Employee Email ID
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  readOnly
                  value={selectedEmployeeObj?.official_email || ''}
                  placeholder="Employee Email ID"
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 cursor-not-allowed font-mono"
                />
              </div>
            </div>

            {/* Reporting Manager Dropdown */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Reporting To
              </label>
              <select
                aria-label="Reporting To Manager"
                value={selectedManagerId}
                disabled={!selectedUserId}
                onChange={(e) => {
                  setIsDirty(true);
                  setSelectedManagerId(e.target.value);
                }}
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Reporting To --</option>
                {managers.map((m) => (
                  <option key={m.user_id} value={m.user_id}>
                    {m.employee_code} – {m.first_name} {m.last_name} ({m.designation_name || 'Staff'})
                  </option>
                ))}
              </select>
            </div>

            {/* Primary Location */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Primary Location *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <MapPin className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={primaryLocation}
                  disabled={!selectedUserId}
                  onChange={(e) => {
                    setIsDirty(true);
                    setPrimaryLocation(e.target.value);
                  }}
                  placeholder="e.g. Head Office / Delhi Hub"
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Copy Permission Section */}
            <div className="border-t border-slate-100 dark:border-slate-800 pt-4 space-y-3">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
                Copy Permission from:
              </label>
              <select
                aria-label="Copy Permissions Source Employee"
                value={copySourceUserId}
                disabled={!selectedUserId}
                onChange={(e) => setCopySourceUserId(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-blue-500"
              >
                <option value="">- Select Source Employee -</option>
                {employees
                  .filter((e) => e.user_id !== selectedUserId)
                  .map((e) => (
                    <option key={e.user_id} value={e.user_id}>
                      {e.employee_code} – {e.first_name} {e.last_name}
                    </option>
                  ))}
              </select>

              <button
                type="button"
                id="copy-permissions-btn"
                disabled={!selectedUserId || !copySourceUserId}
                onClick={() => setIsCopyModalOpen(true)}
                className="w-full py-2.5 px-4 rounded-xl bg-[#0a2569] hover:bg-blue-900 dark:bg-blue-600 dark:hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-xs cursor-pointer disabled:cursor-not-allowed"
              >
                <Copy className="w-3.5 h-3.5" />
                <span>Copy Sales and Operation Permissions</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserPermissionsPage;

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { getEmployeesApi, initializeTrialLoginApi } from '../api/employees';
import { getLookupCompaniesApi, getLookupDepartmentsApi } from '../api/lookup';
import { extractErrorMessage } from '../api/client';
import type { Employee, EmployeeFilterParams, PaginatedEmployees } from '../types/employee';
import type { CompanyLookup, DepartmentLookup } from '../types/lookup';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Modal } from '../components/ui/modal';
import { ToastContainer } from '../components/ui/toast';
import type { ToastMessage } from '../components/ui/toast';
import {
  KeyRound,
  Search,
  RefreshCw,
  ShieldAlert,
  CheckCircle2,
  AlertCircle,
  Clock,
  Lock,
  UserCheck,
  Building,
  Briefcase,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

export const LoginCredentialsPage: React.FC = () => {
  const { hasPermission } = useAuth();
  const canApprove = hasPermission('ADMIN_EMPLOYEES', 'approve');

  // State
  const [employeesData, setEmployeesData] = useState<PaginatedEmployees>({
    items: [],
    page: 1,
    page_size: 15,
    total: 0,
    pages: 0,
  });

  const [companies, setCompanies] = useState<CompanyLookup[]>([]);
  const [departments, setDepartments] = useState<DepartmentLookup[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Filters
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('');
  const [selectedDeptId, setSelectedDeptId] = useState<string>('');
  const [selectedStatusFilter, setSelectedStatusFilter] = useState<string>('ALL');
  const [currentPage, setCurrentPage] = useState<number>(1);

  // Initialize Modal State
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isInitializing, setIsInitializing] = useState<boolean>(false);

  const addToast = (type: 'success' | 'error' | 'info', title: string, message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Load Companies & Departments
  useEffect(() => {
    async function loadMasters() {
      try {
        const [cList, dList] = await Promise.all([
          getLookupCompaniesApi(),
          getLookupDepartmentsApi(),
        ]);
        setCompanies(cList);
        setDepartments(dList);
      } catch (err) {
        console.error('Failed to load lookup masters:', err);
      }
    }
    loadMasters();
  }, []);

  // Fetch Employees with filters
  const fetchEmployees = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const params: EmployeeFilterParams = {
        page: currentPage,
        page_size: 15,
        search: searchTerm.trim() || undefined,
        company_id: selectedCompanyId || undefined,
        department_id: selectedDeptId || undefined,
      };

      const res = await getEmployeesApi(params);
      
      // Client-side filter by computed login_status if specific filter chosen
      if (selectedStatusFilter !== 'ALL') {
        const filteredItems = res.items.filter((emp) => {
          const status = emp.login_status || (emp.credentials_initialized ? (emp.must_change_password ? 'Password Change Required' : 'Active Login') : 'Not Initialized');
          if (selectedStatusFilter === 'NOT_INITIALIZED') return status === 'Not Initialized';
          if (selectedStatusFilter === 'PASSWORD_CHANGE_REQUIRED') return status === 'Password Change Required';
          if (selectedStatusFilter === 'ACTIVE_LOGIN') return status === 'Active Login';
          if (selectedStatusFilter === 'DISABLED') return status === 'Disabled';
          return true;
        });
        setEmployeesData({
          ...res,
          items: filteredItems,
          total: filteredItems.length,
        });
      } else {
        setEmployeesData(res);
      }
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      setErrorMessage(msg);
      addToast('error', 'Failed to load credentials list', msg);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, searchTerm, selectedCompanyId, selectedDeptId, selectedStatusFilter]);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  // Handle Initialize Click
  const handleOpenInitModal = (emp: Employee) => {
    setSelectedEmployee(emp);
    setIsModalOpen(true);
  };

  const handleConfirmInitialize = async () => {
    if (!selectedEmployee) return;

    setIsInitializing(true);
    try {
      const res = await initializeTrialLoginApi(selectedEmployee.user_id);
      addToast(
        'success',
        'Trial Login Initialized',
        `Temporary credentials provisioned for ${res.employee_code} (${res.official_email}). Mandatory password change is active.`
      );
      setIsModalOpen(false);
      setSelectedEmployee(null);
      await fetchEmployees();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Initialization Failed', msg);
    } finally {
      setIsInitializing(false);
    }
  };

  // Status Badge Helper
  const renderLoginStatusBadge = (emp: Employee) => {
    const status =
      emp.login_status ||
      (emp.account_status === 'INACTIVE' || emp.account_status === 'SUSPENDED'
        ? 'Disabled'
        : !emp.credentials_initialized
        ? 'Not Initialized'
        : emp.must_change_password
        ? 'Password Change Required'
        : 'Active Login');

    switch (status) {
      case 'Active Login':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            Active Login
          </span>
        );
      case 'Password Change Required':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
            <Clock className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
            Password Change Required
          </span>
        );
      case 'Disabled':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
            <Lock className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" />
            Disabled
          </span>
        );
      case 'Not Initialized':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
            <AlertCircle className="w-3.5 h-3.5 text-slate-500" />
            Not Initialized
          </span>
        );
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-900">
              <KeyRound className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
                Login Credentials
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
                Manage trial employee login provisioning and first-login security enforcement.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchEmployees()}
            isLoading={isLoading}
            className="flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Trial Security Notice */}
      <div className="p-4 rounded-xl bg-blue-50/70 dark:bg-blue-950/40 border border-blue-200/80 dark:border-blue-800/60 flex items-start gap-3">
        <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
        <div className="text-xs text-blue-900 dark:text-blue-200 space-y-1">
          <p className="font-semibold text-blue-950 dark:text-blue-100">
            Trial Phase Credentials Policy
          </p>
          <p className="leading-relaxed">
            During local testing, newly created employees receive temporary trial credentials managed through local environment settings. Initialized employees must change their password on first login before accessing CRM modules. Plaintext passwords and hashes are never exposed.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-4 bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Search */}
          <div className="relative">
            <Input
              placeholder="Search code, name, email..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              leftIcon={<Search className="w-4 h-4 text-slate-400" />}
            />
          </div>

          {/* Login Status Filter */}
          <div>
            <select
              value={selectedStatusFilter}
              onChange={(e) => {
                setSelectedStatusFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Credential Statuses</option>
              <option value="NOT_INITIALIZED">Not Initialized</option>
              <option value="PASSWORD_CHANGE_REQUIRED">Password Change Required</option>
              <option value="ACTIVE_LOGIN">Active Login</option>
              <option value="DISABLED">Disabled / Suspended</option>
            </select>
          </div>

          {/* Company Filter */}
          <div>
            <select
              value={selectedCompanyId}
              onChange={(e) => {
                setSelectedCompanyId(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Companies</option>
              {companies.map((c) => (
                <option key={c.company_id} value={c.company_id}>
                  {c.company_name} ({c.company_code})
                </option>
              ))}
            </select>
          </div>

          {/* Department Filter */}
          <div>
            <select
              value={selectedDeptId}
              onChange={(e) => {
                setSelectedDeptId(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Departments</option>
              {departments.map((d) => (
                <option key={d.department_id} value={d.department_id}>
                  {d.department_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="py-16 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
              Loading employee credentials...
            </span>
          </div>
        ) : errorMessage ? (
          <div className="py-12 flex flex-col items-center justify-center gap-3 text-center px-4">
            <AlertCircle className="w-10 h-10 text-red-500" />
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{errorMessage}</p>
            <Button variant="outline" size="sm" onClick={() => fetchEmployees()}>
              Retry
            </Button>
          </div>
        ) : employeesData.items.length === 0 ? (
          <div className="py-16 flex flex-col items-center justify-center gap-2 text-center px-4">
            <KeyRound className="w-10 h-10 text-slate-300 dark:text-slate-600" />
            <h3 className="text-base font-semibold text-slate-800 dark:text-slate-200">
              No employee credentials found
            </h3>
            <p className="text-xs text-slate-500 max-w-sm">
              No employee records match the current search term or credential status filter.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/75 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 font-semibold">
                  <th className="py-3 px-4">Employee</th>
                  <th className="py-3 px-4">Official Email</th>
                  <th className="py-3 px-4">Organization</th>
                  <th className="py-3 px-4">Employment</th>
                  <th className="py-3 px-4">Credential Status</th>
                  <th className="py-3 px-4">Initialized At</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {employeesData.items.map((emp) => {
                  const isInitialized = !!emp.credentials_initialized;
                  const isInactive = emp.account_status !== 'ACTIVE';

                  return (
                    <tr
                      key={emp.user_id}
                      className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      {/* Employee Info */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-300 font-bold flex items-center justify-center text-xs shrink-0">
                            {emp.first_name[0]}
                            {emp.last_name[0]}
                          </div>
                          <div>
                            <div className="font-semibold text-slate-900 dark:text-white">
                              {emp.first_name} {emp.last_name}
                            </div>
                            <div className="text-xs text-slate-400 font-mono">
                              {emp.employee_code}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Official Email */}
                      <td className="py-3.5 px-4 text-slate-700 dark:text-slate-300 font-mono text-xs">
                        {emp.official_email}
                      </td>

                      {/* Organization */}
                      <td className="py-3.5 px-4 text-slate-600 dark:text-slate-400 text-xs">
                        <div className="flex items-center gap-1 font-medium text-slate-800 dark:text-slate-200">
                          <Building className="w-3 h-3 text-slate-400" />
                          <span>{emp.company_name || '—'}</span>
                        </div>
                        <div className="flex items-center gap-1 text-slate-500">
                          <Briefcase className="w-3 h-3 text-slate-400" />
                          <span>{emp.department_name || '—'}</span>
                        </div>
                      </td>

                      {/* Employment Status */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold ${
                            emp.account_status === 'ACTIVE'
                              ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300'
                              : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
                          }`}
                        >
                          {emp.account_status}
                        </span>
                      </td>

                      {/* Credential Status */}
                      <td className="py-3.5 px-4">{renderLoginStatusBadge(emp)}</td>

                      {/* Initialized At */}
                      <td className="py-3.5 px-4 text-slate-500 dark:text-slate-400 text-xs">
                        {emp.credentials_initialized_at
                          ? new Date(emp.credentials_initialized_at).toLocaleDateString(undefined, {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })
                          : isInitialized
                          ? 'Pre-existing'
                          : 'Not yet initialized'}
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right">
                        {!isInitialized && !isInactive ? (
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => handleOpenInitModal(emp)}
                            disabled={!canApprove}
                            title={!canApprove ? 'Requires Approve permission' : 'Initialize trial login credentials'}
                            className="text-xs h-8 shadow-sm"
                          >
                            <UserCheck className="w-3.5 h-3.5 mr-1" />
                            Initialize Trial Login
                          </Button>
                        ) : isInitialized ? (
                          <span className="text-xs text-slate-400 italic">Initialized</span>
                        ) : (
                          <span className="text-xs text-slate-400 italic">Inactive Employee</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {employeesData.pages > 1 && (
          <div className="p-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2 text-xs text-slate-600 dark:text-slate-400">
            <span>
              Showing page <strong>{employeesData.page}</strong> of <strong>{employeesData.pages}</strong> ({employeesData.total} total employees)
            </span>
            <div className="flex items-center gap-1.5">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage <= 1 || isLoading}
                className="h-8 px-2.5"
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.min(employeesData.pages, p + 1))}
                disabled={currentPage >= employeesData.pages || isLoading}
                className="h-8 px-2.5"
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          if (!isInitializing) {
            setIsModalOpen(false);
            setSelectedEmployee(null);
          }
        }}
        title="Initialize Trial Login Credentials"
        description="Provision temporary login access for this employee profile."
      >
        {selectedEmployee && (
          <div className="space-y-4 text-xs sm:text-sm text-slate-600 dark:text-slate-300">
            {/* Employee Card */}
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 space-y-1.5">
              <div className="font-semibold text-slate-900 dark:text-white text-sm">
                {selectedEmployee.first_name} {selectedEmployee.last_name} ({selectedEmployee.employee_code})
              </div>
              <div className="text-xs text-slate-500 font-mono">
                Official Email: {selectedEmployee.official_email}
              </div>
              <div className="text-xs text-slate-500">
                Department: {selectedEmployee.department_name} • Designation: {selectedEmployee.designation_name}
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-amber-900 dark:text-amber-200 text-xs leading-relaxed space-y-1">
              <p className="font-semibold flex items-center gap-1 text-amber-950 dark:text-amber-100">
                <ShieldAlert className="w-4 h-4 text-amber-600" />
                Trial Credential Provisioning Note
              </p>
              <p>
                This action will provision the approved temporary trial password hash for <strong>{selectedEmployee.first_name} {selectedEmployee.last_name}</strong>.
              </p>
              <p>
                The employee will be required to set their own strong permanent password immediately upon first login.
              </p>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2">
              <Button
                variant="outline"
                onClick={() => {
                  setIsModalOpen(false);
                  setSelectedEmployee(null);
                }}
                disabled={isInitializing}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleConfirmInitialize}
                isLoading={isInitializing}
              >
                Confirm & Initialize
              </Button>
            </div>
          </div>
        )}
      </Modal>

      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

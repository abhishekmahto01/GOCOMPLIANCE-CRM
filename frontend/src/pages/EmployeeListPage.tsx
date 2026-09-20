import React, { useEffect, useState, useCallback } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import {
  Users,
  UserPlus,
  Search,
  RotateCcw,
  Eye,
  Edit2,
  SlidersHorizontal,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getEmployeesApi, updateEmployeeStatusApi } from '../api/employees';
import {
  getLookupCompaniesApi,
  getLookupDepartmentsApi,
  getLookupDesignationsApi,
  getLookupManagersApi,
} from '../api/lookup';
import type { Employee, PaginatedEmployees, AccountStatus } from '../types/employee';
import type {
  CompanyLookup,
  DepartmentLookup,
  DesignationLookup,
  ManagerLookup,
} from '../types/lookup';
import { StatusBadge } from '../components/common/StatusBadge';
import { Pagination } from '../components/common/Pagination';
import { ConfirmationModal } from '../components/common/ConfirmationModal';
import { AdminHeader } from '../components/dashboard/AdminHeader';
import { ChangePasswordModal } from '../components/dashboard/ChangePasswordModal';
import { ToastContainer, type ToastMessage } from '../components/ui/toast';
import { useDebounce } from '../hooks/useDebounce';
import { extractErrorMessage } from '../api/client';

export const EmployeeListPage: React.FC = () => {
  const { hasPermission, logout } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // Dark / Light Theme state
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    try {
      const saved = localStorage.getItem('gocompliances-theme');
      return saved === 'dark' ? 'dark' : 'light';
    } catch {
      return 'light';
    }
  });

  useEffect(() => {
    try {
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        localStorage.setItem('gocompliances-theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch (err) {
      console.error('Error persisting theme:', err);
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Toast notifications
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const addToast = (type: 'success' | 'error' | 'info', title: string, message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };
  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);

  // Permissions
  const canCreate = hasPermission('ADMIN_EMPLOYEES', 'create');
  const canEdit = hasPermission('ADMIN_EMPLOYEES', 'edit');
  const canApprove = hasPermission('ADMIN_EMPLOYEES', 'approve');

  // Filter & Pagination States (backed by URL SearchParams)
  const pageParam = Number(searchParams.get('page')) || 1;
  const pageSizeParam = Number(searchParams.get('page_size')) || 20;
  const searchParam = searchParams.get('search') || '';
  const companyParam = searchParams.get('company_id') || '';
  const departmentParam = searchParams.get('department_id') || '';
  const designationParam = searchParams.get('designation_id') || '';
  const managerParam = searchParams.get('manager_user_id') || '';
  const statusParam = searchParams.get('account_status') || '';

  const [searchInput, setSearchInput] = useState(searchParam);
  const debouncedSearch = useDebounce(searchInput, 350);

  // Lookups Data
  const [companies, setCompanies] = useState<CompanyLookup[]>([]);
  const [departments, setDepartments] = useState<DepartmentLookup[]>([]);
  const [designations, setDesignations] = useState<DesignationLookup[]>([]);
  const [managers, setManagers] = useState<ManagerLookup[]>([]);

  // Employee Data & Loading
  const [data, setData] = useState<PaginatedEmployees | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Status Change Dialog State
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [targetStatus, setTargetStatus] = useState<AccountStatus>('ACTIVE');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  // Synchronize debounced search with URL searchParams
  useEffect(() => {
    const currentSearch = searchParams.get('search') || '';
    if (debouncedSearch !== currentSearch) {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (debouncedSearch.trim()) {
          next.set('search', debouncedSearch.trim());
        } else {
          next.delete('search');
        }
        next.set('page', '1');
        return next;
      });
    }
  }, [debouncedSearch, searchParams, setSearchParams]);

  // Load Companies lookup
  useEffect(() => {
    getLookupCompaniesApi()
      .then(setCompanies)
      .catch((err) => console.error('Failed to load companies lookup:', err));
  }, []);

  // Load dependent lookups when companyParam changes
  useEffect(() => {
    getLookupDepartmentsApi(companyParam || undefined)
      .then(setDepartments)
      .catch((err) => console.error('Failed to load departments lookup:', err));

    getLookupDesignationsApi(companyParam || undefined)
      .then(setDesignations)
      .catch((err) => console.error('Failed to load designations lookup:', err));

    getLookupManagersApi(companyParam || undefined)
      .then(setManagers)
      .catch((err) => console.error('Failed to load managers lookup:', err));
  }, [companyParam]);

  // Fetch Employees List from API
  const fetchEmployees = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await getEmployeesApi({
        page: pageParam,
        page_size: pageSizeParam,
        search: searchParam,
        company_id: companyParam || undefined,
        department_id: departmentParam || undefined,
        designation_id: designationParam || undefined,
        manager_user_id: managerParam || undefined,
        account_status: statusParam || undefined,
      });
      setData(res);
    } catch (err) {
      const msg = extractErrorMessage(err);
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  }, [
    pageParam,
    pageSizeParam,
    searchParam,
    companyParam,
    departmentParam,
    designationParam,
    managerParam,
    statusParam,
  ]);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  // Filter Update Handler
  const updateFilter = (key: string, value: string) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (value) {
        next.set(key, value);
      } else {
        next.delete(key);
      }
      // If company changed, reset department and designation filters
      if (key === 'company_id') {
        next.delete('department_id');
        next.delete('designation_id');
        next.delete('manager_user_id');
      }
      next.set('page', '1');
      return next;
    });
  };

  // Reset Filters Handler
  const resetFilters = () => {
    setSearchInput('');
    setSearchParams({ page: '1', page_size: String(pageSizeParam) });
  };

  // Open Status Dialog
  const handleOpenStatusModal = (emp: Employee) => {
    setSelectedEmployee(emp);
    setTargetStatus(emp.account_status);
    setStatusModalOpen(true);
  };

  // Confirm Status Update
  const handleConfirmStatusUpdate = async () => {
    if (!selectedEmployee) return;
    setIsUpdatingStatus(true);
    try {
      await updateEmployeeStatusApi(selectedEmployee.user_id, {
        account_status: targetStatus,
      });
      addToast(
        'success',
        'Status Updated',
        `Employee ${selectedEmployee.employee_code} status set to ${targetStatus}`
      );
      setStatusModalOpen(false);
      fetchEmployees();
    } catch (err) {
      addToast('error', 'Update Failed', extractErrorMessage(err));
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const hasActiveFilters =
    Boolean(searchParam) ||
    Boolean(companyParam) ||
    Boolean(departmentParam) ||
    Boolean(designationParam) ||
    Boolean(managerParam) ||
    Boolean(statusParam);

  return (
    <div
      className={`min-h-screen w-full flex flex-col font-sans transition-colors duration-300 relative overflow-x-hidden ${
        theme === 'dark' ? 'dark bg-slate-950 text-slate-100' : 'bg-[#f8faff] text-slate-800'
      }`}
    >
      {/* Background Ambience */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/3 w-[800px] h-[500px] rounded-full bg-gradient-to-b from-blue-300/20 via-sky-200/10 to-transparent dark:from-blue-900/15 dark:via-indigo-950/10 blur-3xl" />
        <div className="absolute top-1/3 -left-32 w-[550px] h-[550px] rounded-full bg-cyan-200/15 dark:bg-cyan-900/10 blur-3xl" />
        <div className="absolute top-1/2 -right-32 w-[550px] h-[550px] rounded-full bg-blue-300/15 dark:bg-indigo-900/10 blur-3xl" />
      </div>

      {/* Header */}
      <div className="relative z-20 shrink-0">
        <AdminHeader
          breadcrumbs={[
            { label: 'Administration', href: '/admin' },
            { label: 'Employee Directory' },
          ]}
          theme={theme}
          onToggleTheme={toggleTheme}
          onOpenPasswordModal={() => setIsPasswordModalOpen(true)}
          onLogout={handleLogout}
        />
      </div>

      {/* Main Container */}
      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        {/* Top Title & Actions Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0a2569] dark:text-white tracking-tight">
                Employee Directory
              </h1>
              {data && (
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                  {data.total} Total
                </span>
              )}
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
              Browse, filter, and manage CRM workforce profiles within your authorized data scope.
            </p>
          </div>

          <div className="flex items-center gap-2.5 w-full sm:w-auto">
            <button
              type="button"
              onClick={fetchEmployees}
              className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition shadow-2xs"
              title="Refresh Data"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>

            {canCreate && (
              <Link to="/admin/employees/new">
                <button
                  type="button"
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-sm hover:shadow-md transition active:scale-95"
                >
                  <UserPlus className="w-4 h-4" />
                  <span>Add Employee</span>
                </button>
              </Link>
            )}
          </div>
        </div>

        {/* Global Notifications */}
        {errorMessage && (
          <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300 flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              type="button"
              onClick={() => setErrorMessage(null)}
              className="text-xs font-bold underline ml-4 hover:text-rose-950"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Filters Card */}
        <div className="p-4 sm:p-5 rounded-3xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              <SlidersHorizontal className="w-3.5 h-3.5 text-blue-600" />
              <span>Filters & Search</span>
            </div>

            {hasActiveFilters && (
              <button
                type="button"
                onClick={resetFilters}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-600 dark:text-rose-400 hover:underline"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset Filters</span>
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
            {/* Search Input */}
            <div className="lg:col-span-2 relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search code, name, email..."
                className="w-full pl-9 pr-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Company Filter */}
            <div>
              <select
                value={companyParam}
                onChange={(e) => updateFilter('company_id', e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Companies</option>
                {companies.map((c) => (
                  <option key={c.company_id} value={c.company_id}>
                    {c.company_name} ({c.employee_code_prefix})
                  </option>
                ))}
              </select>
            </div>

            {/* Department Filter */}
            <div>
              <select
                value={departmentParam}
                onChange={(e) => updateFilter('department_id', e.target.value)}
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

            {/* Designation Filter */}
            <div>
              <select
                value={designationParam}
                onChange={(e) => updateFilter('designation_id', e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Designations</option>
                {designations.map((desig) => (
                  <option key={desig.designation_id} value={desig.designation_id}>
                    {desig.designation_name}
                  </option>
                ))}
              </select>
            </div>

            {/* Manager Filter */}
            <div>
              <select
                value={managerParam}
                onChange={(e) => updateFilter('manager_user_id', e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Managers</option>
                {managers.map((m) => (
                  <option key={m.user_id} value={m.user_id}>
                    {m.first_name} {m.last_name} ({m.employee_code})
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <select
                value={statusParam}
                onChange={(e) => updateFilter('account_status', e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="ACTIVE">ACTIVE</option>
                <option value="PENDING">PENDING</option>
                <option value="INACTIVE">INACTIVE</option>
                <option value="SUSPENDED">SUSPENDED</option>
              </select>
            </div>
          </div>
        </div>

        {/* Employees Table Card */}
        <div className="rounded-3xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 shadow-xl overflow-hidden">
          <div className="overflow-x-auto min-h-[300px]">
            <table className="w-full text-left text-xs sm:text-sm border-collapse">
              <thead>
                <tr className="bg-slate-50/80 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Code</th>
                  <th className="py-3 px-4">Employee Name</th>
                  <th className="py-3 px-4">Company & Dept</th>
                  <th className="py-3 px-4">Designation</th>
                  <th className="py-3 px-4">Reporting Manager</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="py-16 text-center text-slate-400">
                      <div className="flex flex-col items-center justify-center gap-3">
                        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
                        <span className="text-xs">Loading employee records...</span>
                      </div>
                    </td>
                  </tr>
                ) : !data || data.items.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-16 text-center text-slate-400">
                      <div className="flex flex-col items-center justify-center gap-2">
                        <Users className="w-10 h-10 text-slate-300 dark:text-slate-700" />
                        <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                          No employees found
                        </span>
                        <span className="text-xs text-slate-500 max-w-xs">
                          {hasActiveFilters
                            ? 'Try modifying your search keywords or filter criteria.'
                            : 'No employee accounts exist in the CRM directory within your scope.'}
                        </span>
                      </div>
                    </td>
                  </tr>
                ) : (
                  data.items.map((emp) => (
                    <tr
                      key={emp.user_id}
                      className="hover:bg-blue-50/40 dark:hover:bg-slate-800/40 transition group"
                    >
                      {/* Code */}
                      <td className="py-3.5 px-4 font-mono font-bold text-blue-600 dark:text-blue-400 whitespace-nowrap">
                        <Link
                          to={`/admin/employees/${emp.user_id}`}
                          className="hover:underline"
                        >
                          {emp.employee_code}
                        </Link>
                      </td>

                      {/* Name & Contact */}
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-slate-900 dark:text-white">
                          {[emp.first_name, emp.middle_name, emp.last_name].filter(Boolean).join(' ')}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">
                          {emp.official_email}
                        </div>
                      </td>

                      {/* Company & Department */}
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <div className="font-medium text-slate-800 dark:text-slate-200">
                          {emp.company_name || '—'}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">
                          {emp.department_name || '—'}
                        </div>
                      </td>

                      {/* Designation */}
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <div className="font-medium text-slate-800 dark:text-slate-200">
                          {emp.designation_name || '—'}
                        </div>
                        <div className="text-xs text-slate-400">
                          {emp.employment_type}
                        </div>
                      </td>

                      {/* Reporting Manager */}
                      <td className="py-3.5 px-4 whitespace-nowrap text-xs text-slate-600 dark:text-slate-300">
                        {emp.manager_name ? (
                          <span>
                            {emp.manager_name} ({emp.manager_employee_code})
                          </span>
                        ) : (
                          <span className="text-slate-400 italic">None (Self/Top)</span>
                        )}
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <StatusBadge status={emp.account_status} />
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* View Detail */}
                          <Link
                            to={`/admin/employees/${emp.user_id}`}
                            className="p-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                            title="View Employee Detail"
                          >
                            <Eye className="w-4 h-4" />
                          </Link>

                          {/* Edit Profile */}
                          {canEdit && (
                            <Link
                              to={`/admin/employees/${emp.user_id}/edit`}
                              className="p-1.5 rounded-lg text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/50 transition"
                              title="Edit Employee Profile"
                            >
                              <Edit2 className="w-4 h-4" />
                            </Link>
                          )}

                          {/* Status Management */}
                          {canApprove && (
                            <button
                              type="button"
                              onClick={() => handleOpenStatusModal(emp)}
                              className="px-2 py-1 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                              title="Update Account Status"
                            >
                              Status
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          {data && (
            <Pagination
              currentPage={data.page}
              totalPages={data.pages}
              pageSize={data.page_size}
              totalItems={data.total}
              onPageChange={(p) => updateFilter('page', String(p))}
              onPageSizeChange={(sz) => updateFilter('page_size', String(sz))}
            />
          )}
        </div>
      </main>

      {/* Status Management Modal */}
      <ConfirmationModal
        isOpen={statusModalOpen}
        onClose={() => setStatusModalOpen(false)}
        onConfirm={handleConfirmStatusUpdate}
        title="Update Account Operational Status"
        confirmText="Save Status"
        isLoading={isUpdatingStatus}
      >
        <div className="space-y-4 text-left">
          {selectedEmployee && (
            <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300 space-y-1">
              <div>
                <strong>Employee:</strong> {selectedEmployee.first_name}{' '}
                {selectedEmployee.last_name} ({selectedEmployee.employee_code})
              </div>
              <div>
                <strong>Current Status:</strong>{' '}
                <StatusBadge status={selectedEmployee.account_status} size="sm" />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
              Select New Operational Status:
            </label>
            <select
              value={targetStatus}
              onChange={(e) => setTargetStatus(e.target.value as AccountStatus)}
              className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            >
              <option value="ACTIVE">ACTIVE (Authorized CRM Access)</option>
              <option value="PENDING">PENDING (Awaiting Activation)</option>
              <option value="INACTIVE">INACTIVE (Deactivated Employee)</option>
              <option value="SUSPENDED">SUSPENDED (Temporarily Locked)</option>
            </select>
          </div>

          <p className="text-xs text-slate-500 dark:text-slate-400">
            Note: Changing account status to INACTIVE or SUSPENDED prevents login and revokes active token sessions.
          </p>
        </div>
      </ConfirmationModal>

      {/* Password Modal */}
      <ChangePasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        onSuccessToast={(title, msg) => addToast('success', title, msg)}
      />

      {/* Toasts */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

import React, { useEffect, useState, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
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
  CheckCircle2,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getEmployeesApi, updateEmployeeStatusApi } from '../api/employees';
import {
  getLookupCompaniesApi,
  getLookupDepartmentsApi,
  getLookupDesignationsApi,
  getLookupManagersApi,
} from '../api/lookup';
import { Employee, PaginatedEmployees, AccountStatus } from '../types/employee';
import {
  CompanyLookup,
  DepartmentLookup,
  DesignationLookup,
  ManagerLookup,
} from '../types/lookup';
import { StatusBadge } from '../components/common/StatusBadge';
import { Pagination } from '../components/common/Pagination';
import { ConfirmationModal } from '../components/common/ConfirmationModal';
import { useDebounce } from '../hooks/useDebounce';
import { extractErrorMessage } from '../api/client';

export const EmployeeListPage: React.FC = () => {
  const { hasPermission } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

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
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

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
        search: searchParam || undefined,
        company_id: companyParam || undefined,
        department_id: departmentParam || undefined,
        designation_id: designationParam || undefined,
        manager_user_id: managerParam || undefined,
        account_status: statusParam || undefined,
      });
      setData(res);
    } catch (err) {
      setErrorMessage(extractErrorMessage(err));
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

  // Handle Filter Changes
  const updateFilter = (key: string, value: string) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (value) {
        next.set(key, value);
      } else {
        next.delete(key);
      }
      // If company changed, reset dependent filter params
      if (key === 'company_id') {
        next.delete('department_id');
        next.delete('designation_id');
        next.delete('manager_user_id');
      }
      next.set('page', '1');
      return next;
    });
  };

  const clearAllFilters = () => {
    setSearchInput('');
    setSearchParams(new URLSearchParams({ page: '1', page_size: String(pageSizeParam) }));
  };

  // Status Change Actions
  const handleOpenStatusModal = (employee: Employee) => {
    setSelectedEmployee(employee);
    setTargetStatus(employee.account_status);
    setStatusModalOpen(true);
  };

  const handleConfirmStatusUpdate = async () => {
    if (!selectedEmployee) return;
    setIsUpdatingStatus(true);
    setErrorMessage(null);
    try {
      await updateEmployeeStatusApi(selectedEmployee.user_id, {
        account_status: targetStatus,
      });
      setSuccessMessage(
        `Successfully updated status for ${selectedEmployee.first_name} ${selectedEmployee.last_name} (${selectedEmployee.employee_code}) to ${targetStatus}.`
      );
      setStatusModalOpen(false);
      await fetchEmployees();
    } catch (err) {
      setErrorMessage(extractErrorMessage(err));
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const hasActiveFilters =
    searchParam ||
    companyParam ||
    departmentParam ||
    designationParam ||
    managerParam ||
    statusParam;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <Users className="w-6 h-6 text-brand-600" />
            <span>Employee Directory</span>
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Manage organization staff, view profiles, and update operational statuses.
          </p>
        </div>

        {canCreate && (
          <Link
            to="/employees/new"
            className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white font-semibold text-sm shadow-button-glow transition-all"
          >
            <UserPlus className="w-4 h-4" />
            <span>Add Employee</span>
          </Link>
        )}
      </div>

      {/* Feedback Alerts */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start justify-between gap-3 animate-fade-in">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Unable to complete request</p>
              <p className="text-xs text-rose-700 mt-0.5">{errorMessage}</p>
            </div>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-rose-500 hover:text-rose-700 text-xs font-bold"
          >
            Dismiss
          </button>
        </div>
      )}

      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-start justify-between gap-3 animate-fade-in">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <span className="font-medium">{successMessage}</span>
          </div>
          <button
            onClick={() => setSuccessMessage(null)}
            className="text-emerald-600 hover:text-emerald-800 text-xs font-bold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Search & Filter Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-4 sm:p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-700">
            <SlidersHorizontal className="w-4 h-4 text-brand-600" />
            <span>Filter Records</span>
          </div>

          {hasActiveFilters && (
            <button
              onClick={clearAllFilters}
              className="flex items-center gap-1.5 text-xs text-brand-600 hover:text-brand-800 font-semibold transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Clear Filters</span>
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
          {/* Search Box */}
          <div className="xl:col-span-2">
            <label htmlFor="search-input" className="block text-xs font-medium text-slate-600 mb-1">
              Search Text
            </label>
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                id="search-input"
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Code, name, or email..."
                className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all"
              />
            </div>
          </div>

          {/* Company Filter */}
          <div>
            <label htmlFor="company-filter" className="block text-xs font-medium text-slate-600 mb-1">
              Company
            </label>
            <select
              id="company-filter"
              value={companyParam}
              onChange={(e) => updateFilter('company_id', e.target.value)}
              className="w-full py-2 px-2.5 text-xs border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-700"
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
            <label htmlFor="department-filter" className="block text-xs font-medium text-slate-600 mb-1">
              Department
            </label>
            <select
              id="department-filter"
              value={departmentParam}
              onChange={(e) => updateFilter('department_id', e.target.value)}
              className="w-full py-2 px-2.5 text-xs border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-700"
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
            <label htmlFor="designation-filter" className="block text-xs font-medium text-slate-600 mb-1">
              Designation
            </label>
            <select
              id="designation-filter"
              value={designationParam}
              onChange={(e) => updateFilter('designation_id', e.target.value)}
              className="w-full py-2 px-2.5 text-xs border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-700"
            >
              <option value="">All Designations</option>
              {designations.map((d) => (
                <option key={d.designation_id} value={d.designation_id}>
                  {d.designation_name}
                </option>
              ))}
            </select>
          </div>

          {/* Manager Filter */}
          <div>
            <label htmlFor="manager-filter" className="block text-xs font-medium text-slate-600 mb-1">
              Manager
            </label>
            <select
              id="manager-filter"
              value={managerParam}
              onChange={(e) => updateFilter('manager_user_id', e.target.value)}
              className="w-full py-2 px-2.5 text-xs border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-700"
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
            <label htmlFor="status-filter" className="block text-xs font-medium text-slate-600 mb-1">
              Status
            </label>
            <select
              id="status-filter"
              value={statusParam}
              onChange={(e) => updateFilter('account_status', e.target.value)}
              className="w-full py-2 px-2.5 text-xs border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-700"
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
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-600">
                <th className="py-3.5 px-4">Code</th>
                <th className="py-3.5 px-4">Employee</th>
                <th className="py-3.5 px-4">Company</th>
                <th className="py-3.5 px-4">Department & Designation</th>
                <th className="py-3.5 px-4">Manager</th>
                <th className="py-3.5 px-4">Joining Date</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-200/80 text-sm">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="py-16 text-center text-slate-500">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <RefreshCw className="w-6 h-6 text-brand-600 animate-spin" />
                      <span className="text-sm font-medium text-slate-600">
                        Loading employee records...
                      </span>
                    </div>
                  </td>
                </tr>
              ) : data && data.items.length > 0 ? (
                data.items.map((emp) => (
                  <tr
                    key={emp.user_id}
                    className="hover:bg-slate-50/80 transition-colors group"
                  >
                    {/* Employee Code */}
                    <td className="py-3.5 px-4 font-mono font-bold text-xs text-brand-700">
                      {emp.employee_code}
                    </td>

                    {/* Name & Contact */}
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-900 leading-tight">
                        {emp.first_name} {emp.middle_name ? `${emp.middle_name} ` : ''}
                        {emp.last_name}
                      </div>
                      <div className="text-xs text-slate-500 font-mono mt-0.5">
                        {emp.official_email}
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        {emp.mobile_number}
                      </div>
                    </td>

                    {/* Company */}
                    <td className="py-3.5 px-4 text-xs font-medium text-slate-700">
                      {emp.company_name || '—'}
                    </td>

                    {/* Department & Designation */}
                    <td className="py-3.5 px-4">
                      <div className="text-xs font-semibold text-slate-800">
                        {emp.designation_name || '—'}
                      </div>
                      <div className="text-xs text-slate-500">
                        {emp.department_name || '—'}
                      </div>
                    </td>

                    {/* Manager */}
                    <td className="py-3.5 px-4 text-xs text-slate-700">
                      {emp.manager_name ? (
                        <div>
                          <div className="font-medium text-slate-800">
                            {emp.manager_name}
                          </div>
                          <div className="text-[10px] font-mono text-slate-400">
                            {emp.manager_employee_code}
                          </div>
                        </div>
                      ) : (
                        <span className="text-slate-400 italic">None</span>
                      )}
                    </td>

                    {/* Joining Date */}
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-600">
                      {emp.date_of_joining}
                    </td>

                    {/* Status Badge */}
                    <td className="py-3.5 px-4">
                      <StatusBadge status={emp.account_status} size="sm" />
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {/* View Details */}
                        <Link
                          to={`/employees/${emp.user_id}`}
                          className="p-1.5 text-slate-500 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>

                        {/* Edit Profile */}
                        {canEdit && (
                          <Link
                            to={`/employees/${emp.user_id}/edit`}
                            className="p-1.5 text-slate-500 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-colors"
                            title="Edit Employee"
                          >
                            <Edit2 className="w-4 h-4" />
                          </Link>
                        )}

                        {/* Change Status */}
                        {canApprove && (
                          <button
                            onClick={() => handleOpenStatusModal(emp)}
                            className="px-2 py-1 text-xs font-semibold rounded-md border border-slate-300 text-slate-700 hover:bg-slate-100 transition-colors"
                            title="Update Account Status"
                          >
                            Status
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-16 text-center text-slate-500">
                    <div className="flex flex-col items-center justify-center max-w-sm mx-auto">
                      <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-3">
                        <Users className="w-6 h-6" />
                      </div>
                      <h3 className="text-base font-bold text-slate-800">
                        No employees found
                      </h3>
                      <p className="text-xs text-slate-500 mt-1">
                        {hasActiveFilters
                          ? 'No matching employees match your filter criteria. Try clearing or adjusting filters.'
                          : 'No employee records are available in your authorized data scope.'}
                      </p>
                      {hasActiveFilters && (
                        <button
                          onClick={clearAllFilters}
                          className="mt-4 px-3 py-1.5 text-xs font-semibold text-brand-600 border border-brand-200 rounded-lg hover:bg-brand-50 transition-colors"
                        >
                          Reset Filters
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        {data && (
          <Pagination
            currentPage={data.page}
            totalPages={data.pages}
            totalItems={data.total}
            pageSize={data.page_size}
            onPageChange={(p) => updateFilter('page', String(p))}
            onPageSizeChange={(sz) => updateFilter('page_size', String(sz))}
          />
        )}
      </div>

      {/* Status Management Confirmation Modal */}
      {statusModalOpen && selectedEmployee && (
        <ConfirmationModal
          isOpen={statusModalOpen}
          title="Update Account Status"
          message={
            <div className="space-y-4">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1">
                <div className="text-slate-500">Target Employee:</div>
                <div className="font-bold text-slate-900 text-sm">
                  {selectedEmployee.first_name} {selectedEmployee.last_name} (
                  {selectedEmployee.employee_code})
                </div>
                <div className="text-slate-600">{selectedEmployee.official_email}</div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Current Status:
                </label>
                <div className="mb-3">
                  <StatusBadge status={selectedEmployee.account_status} />
                </div>

                <label
                  htmlFor="target-status"
                  className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
                >
                  New Target Status <span className="text-rose-500">*</span>
                </label>
                <select
                  id="target-status"
                  value={targetStatus}
                  onChange={(e) => setTargetStatus(e.target.value as AccountStatus)}
                  className="w-full p-2.5 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-brand-500 focus:outline-none"
                >
                  <option value="ACTIVE">ACTIVE (Full access)</option>
                  <option value="PENDING">PENDING (Awaiting activation)</option>
                  <option value="INACTIVE">INACTIVE (Deactivated / offboarded)</option>
                  <option value="SUSPENDED">SUSPENDED (Temporarily locked)</option>
                </select>
              </div>
            </div>
          }
          confirmLabel="Update Status"
          cancelLabel="Cancel"
          variant={targetStatus === 'SUSPENDED' || targetStatus === 'INACTIVE' ? 'warning' : 'primary'}
          isLoading={isUpdatingStatus}
          onConfirm={handleConfirmStatusUpdate}
          onClose={() => setStatusModalOpen(false)}
        />
      )}
    </div>
  );
};

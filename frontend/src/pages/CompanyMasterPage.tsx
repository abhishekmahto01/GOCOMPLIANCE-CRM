import React, { useState, useEffect, useCallback } from 'react';
import {
  Building2,
  Plus,
  Search,
  RefreshCw,
  Edit2,
  CheckCircle2,
  AlertCircle,
  Building,
  Hash,
  Save,
  Trash2,
  Settings2,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  getCompaniesApi,
  createCompanyApi,
  updateCompanyApi,
  deleteCompanyApi,
} from '../api/companies';
import { extractErrorMessage } from '../api/client';
import type {
  Company,
  CompanyCreatePayload,
  CompanyUpdatePayload,
  CompanyStatus,
} from '../types/company';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Modal } from '../components/ui/modal';
import { ConfirmationModal } from '../components/common/ConfirmationModal';
import { ToastContainer, type ToastMessage } from '../components/ui/toast';
import { OperationsCoordinatorModal } from '../components/admin/OperationsCoordinatorModal';

export const CompanyMasterPage: React.FC = () => {
  const { hasPermission, isSuperAdmin } = useAuth();
  const canCreate = hasPermission('ADMIN', 'create');
  const canEdit = hasPermission('ADMIN', 'edit');
  const canDelete = isSuperAdmin;

  // State
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Delete State
  const [companyToDelete, setCompanyToDelete] = useState<Company | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Filters
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  // Operations Coordinator Modal State
  const [isCoordinatorModalOpen, setIsCoordinatorModalOpen] = useState<boolean>(false);

  // Add Company Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [isSubmittingAdd, setIsSubmittingAdd] = useState<boolean>(false);
  const [addForm, setAddForm] = useState<CompanyCreatePayload>({
    company_name: '',
    company_code: '',
    employee_code_prefix: '',
    legal_name: '',
    next_employee_number: 1,
    status: 'ACTIVE',
  });
  const [addFormErrors, setAddFormErrors] = useState<Record<string, string>>({});

  // Edit Company Modal State
  const [isEditModalOpen, setIsEditModalOpen] = useState<boolean>(false);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [isSubmittingEdit, setIsSubmittingEdit] = useState<boolean>(false);
  const [editForm, setEditForm] = useState<CompanyUpdatePayload>({
    company_name: '',
    legal_name: '',
    status: 'ACTIVE',
  });
  const [editFormErrors, setEditFormErrors] = useState<Record<string, string>>({});

  // Toast Helpers
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

  // Fetch Companies
  const fetchCompanies = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await getCompaniesApi({
        search: searchTerm.trim() || undefined,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
      });
      setCompanies(data);
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      setErrorMessage(msg);
      addToast('error', 'Failed to load companies', msg);
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, statusFilter]);

  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  // Open Add Modal
  const handleOpenAddModal = () => {
    setAddForm({
      company_name: '',
      company_code: '',
      employee_code_prefix: '',
      legal_name: '',
      next_employee_number: 1,
      status: 'ACTIVE',
    });
    setAddFormErrors({});
    setIsAddModalOpen(true);
  };

  // Open Edit Modal
  const handleOpenEditModal = (comp: Company) => {
    setSelectedCompany(comp);
    setEditForm({
      company_name: comp.company_name,
      legal_name: comp.legal_name || '',
      status: comp.status,
    });
    setEditFormErrors({});
    setIsEditModalOpen(true);
  };

  // Validate Add Form
  const validateAddForm = (): boolean => {
    const errors: Record<string, string> = {};
    if (!addForm.company_name.trim()) {
      errors.company_name = 'Company display name is required.';
    }
    if (!addForm.company_code.trim()) {
      errors.company_code = 'Company identifier code is required.';
    } else if (!/^[A-Za-z0-9_-]{2,20}$/.test(addForm.company_code.trim())) {
      errors.company_code = 'Company code must be 2-20 alphanumeric characters.';
    }
    if (!addForm.employee_code_prefix.trim()) {
      errors.employee_code_prefix = 'Employee code prefix is required.';
    } else if (!/^[A-Za-z]{2,5}$/.test(addForm.employee_code_prefix.trim())) {
      errors.employee_code_prefix = 'Prefix must be 2-5 alphabetic letters (e.g. CG, EP, BM).';
    }
    setAddFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle Create Company Submit
  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateAddForm()) return;

    setIsSubmittingAdd(true);
    try {
      const payload: CompanyCreatePayload = {
        company_name: addForm.company_name.trim(),
        company_code: addForm.company_code.trim().toUpperCase(),
        employee_code_prefix: addForm.employee_code_prefix.trim().toUpperCase(),
        legal_name: addForm.legal_name?.trim() || null,
        next_employee_number: 1,
        status: addForm.status || 'ACTIVE',
      };

      const created = await createCompanyApi(payload);
      addToast(
        'success',
        'Company Created',
        `Company "${created.company_name}" (${created.employee_code_prefix}) successfully registered.`
      );
      setIsAddModalOpen(false);
      await fetchCompanies();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Creation Failed', msg);
    } finally {
      setIsSubmittingAdd(false);
    }
  };

  // Handle Edit Company Submit
  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCompany) return;

    if (!editForm.company_name?.trim()) {
      setEditFormErrors({ company_name: 'Company display name is required.' });
      return;
    }

    setIsSubmittingEdit(true);
    try {
      const payload: CompanyUpdatePayload = {
        company_name: editForm.company_name.trim(),
        legal_name: editForm.legal_name?.trim() || null,
        status: editForm.status,
      };

      const updated = await updateCompanyApi(selectedCompany.company_id, payload);
      addToast(
        'success',
        'Company Updated',
        `Company "${updated.company_name}" was successfully updated.`
      );
      setIsEditModalOpen(false);
      setSelectedCompany(null);
      await fetchCompanies();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Update Failed', msg);
    } finally {
      setIsSubmittingEdit(false);
    }
  };

  // Handle Delete Company
  const handleConfirmDelete = async () => {
    if (!companyToDelete) return;

    setIsDeleting(true);
    try {
      const res = await deleteCompanyApi(companyToDelete.company_id);
      addToast(
        'success',
        'Company Deleted',
        res.message || `Company "${companyToDelete.company_name}" has been deleted.`
      );
      setCompanyToDelete(null);
      await fetchCompanies();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Deletion Blocked', msg);
    } finally {
      setIsDeleting(false);
    }
  };

  // Stats
  const totalCompanies = companies.length;
  const activeCompanies = companies.filter((c) => c.status === 'ACTIVE').length;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 text-white shadow-md">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl sm:text-2xl font-extrabold text-[#0a2569] dark:text-white tracking-tight">
                Company Master
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                {totalCompanies} Registered
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
              Configure corporate entities, edit company display names, and manage employee code prefixes.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchCompanies()}
            isLoading={isLoading}
            className="flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>

          {canEdit && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsCoordinatorModalOpen(true)}
              className="flex items-center gap-1.5 border-purple-200 text-purple-700 hover:bg-purple-50 dark:border-purple-800 dark:text-purple-300 dark:hover:bg-purple-950/50"
            >
              <Settings2 className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span>Operations Coordinators</span>
            </Button>
          )}

          {canCreate && (
            <Button
              variant="primary"
              size="sm"
              onClick={handleOpenAddModal}
              className="flex items-center gap-1.5 shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Add Company</span>
            </Button>
          )}
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 sm:p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Total Companies
            </span>
            <div className="text-2xl font-black text-slate-900 dark:text-white mt-1">
              {totalCompanies}
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center">
            <Building className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 sm:p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Active Entities
            </span>
            <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
              {activeCompanies}
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 sm:p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Code Prefixes
            </span>
            <div className="text-xs font-mono font-bold text-slate-700 dark:text-slate-300 mt-2 flex flex-wrap gap-1.5">
              {companies.map((c) => (
                <span
                  key={c.company_id}
                  className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
                >
                  {c.employee_code_prefix}
                </span>
              ))}
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0">
            <Hash className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="sm:col-span-2 relative">
            <Input
              placeholder="Search company name, code, prefix, legal entity..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="w-4 h-4 text-slate-400" />}
            />
          </div>

          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="ACTIVE">ACTIVE</option>
              <option value="INACTIVE">INACTIVE</option>
            </select>
          </div>
        </div>
      </div>

      {/* Companies Table Container */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="py-16 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
              Loading company records...
            </span>
          </div>
        ) : errorMessage ? (
          <div className="py-12 flex flex-col items-center justify-center gap-3 text-center px-4">
            <AlertCircle className="w-10 h-10 text-red-500" />
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{errorMessage}</p>
            <Button variant="outline" size="sm" onClick={() => fetchCompanies()}>
              Retry
            </Button>
          </div>
        ) : companies.length === 0 ? (
          <div className="py-16 flex flex-col items-center justify-center gap-2 text-center px-4">
            <Building2 className="w-10 h-10 text-slate-300 dark:text-slate-600" />
            <h3 className="text-base font-semibold text-slate-800 dark:text-slate-200">
              No companies found
            </h3>
            <p className="text-xs text-slate-500 max-w-sm">
              {searchTerm || statusFilter !== 'ALL'
                ? 'Try adjusting your search query or status filter.'
                : 'No companies are currently registered. Click "Add Company" to register one.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/75 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Company</th>
                  <th className="py-3 px-4">Company Code</th>
                  <th className="py-3 px-4">Code Prefix</th>
                  <th className="py-3 px-4">Next Emp #</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {companies.map((comp) => {
                  return (
                    <tr
                      key={comp.company_id}
                      className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      {/* Company Name & Legal Name */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white font-bold flex items-center justify-center text-xs shrink-0 shadow-xs">
                            {comp.company_name.substring(0, 2).toUpperCase()}
                          </div>
                          <div>
                            <div className="font-bold text-slate-900 dark:text-white text-sm">
                              {comp.company_name}
                            </div>
                            <div className="text-xs text-slate-400">
                              {comp.legal_name || 'No legal name specified'}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Company Code */}
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-700 dark:text-slate-300 text-xs">
                        {comp.company_code}
                      </td>

                      {/* Employee Code Prefix */}
                      <td className="py-3.5 px-4">
                        <span className="inline-flex items-center gap-1 font-mono font-bold text-xs px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300 border border-blue-200/70 dark:border-blue-800">
                          {comp.employee_code_prefix}
                          <span className="text-blue-400 font-normal">-XXXX</span>
                        </span>
                      </td>

                      {/* Next Sequential Employee Number */}
                      <td className="py-3.5 px-4 font-mono text-xs text-slate-600 dark:text-slate-400">
                        #{comp.next_employee_number.toString().padStart(4, '0')}
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                            comp.status === 'ACTIVE'
                              ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                              : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              comp.status === 'ACTIVE' ? 'bg-emerald-500' : 'bg-slate-400'
                            }`}
                          />
                          {comp.status}
                        </span>
                      </td>

                      {/* Created Date */}
                      <td className="py-3.5 px-4 text-slate-500 dark:text-slate-400 text-xs">
                        {comp.created_at
                          ? new Date(comp.created_at).toLocaleDateString(undefined, {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                            })
                          : '—'}
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {canEdit && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleOpenEditModal(comp)}
                              className="inline-flex items-center gap-1.5 text-xs h-8 text-blue-600 hover:text-blue-700"
                            >
                              <Edit2 className="w-3.5 h-3.5 text-blue-600" />
                              <span>Edit</span>
                            </Button>
                          )}
                          {canDelete && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setCompanyToDelete(comp)}
                              className="inline-flex items-center gap-1.5 text-xs h-8 text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/40 border-slate-200 dark:border-slate-700"
                              title={`Delete ${comp.company_name}`}
                            >
                              <Trash2 className="w-3.5 h-3.5 text-rose-500" />
                              <span>Delete</span>
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Company Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => {
          if (!isSubmittingAdd) setIsAddModalOpen(false);
        }}
        title="Register New Company"
        description="Add a new business entity to Gocompliances CRM."
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs sm:text-sm">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
              Company Display Name <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              placeholder="e.g. BrandMingo or Entrepreneur"
              value={addForm.company_name}
              onChange={(e) =>
                setAddForm((prev) => ({ ...prev, company_name: e.target.value }))
              }
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
            {addFormErrors.company_name && (
              <p className="text-xs text-rose-600 mt-1">{addFormErrors.company_name}</p>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Company Code <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder="e.g. BRANDMINGO"
                value={addForm.company_code}
                onChange={(e) =>
                  setAddForm((prev) => ({
                    ...prev,
                    company_code: e.target.value.toUpperCase(),
                  }))
                }
                className="w-full px-3 py-2 font-mono uppercase bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              />
              {addFormErrors.company_code && (
                <p className="text-xs text-rose-600 mt-1">{addFormErrors.company_code}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Employee Code Prefix <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder="e.g. BM (2-5 letters)"
                maxLength={5}
                value={addForm.employee_code_prefix}
                onChange={(e) =>
                  setAddForm((prev) => ({
                    ...prev,
                    employee_code_prefix: e.target.value.toUpperCase(),
                  }))
                }
                className="w-full px-3 py-2 font-mono uppercase bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              />
              {addFormErrors.employee_code_prefix && (
                <p className="text-xs text-rose-600 mt-1">
                  {addFormErrors.employee_code_prefix}
                </p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
              Legal Corporate Name <span className="text-slate-400 font-normal">(Optional)</span>
            </label>
            <input
              type="text"
              placeholder="e.g. BrandMingo Technologies Pvt Ltd"
              value={addForm.legal_name || ''}
              onChange={(e) =>
                setAddForm((prev) => ({ ...prev, legal_name: e.target.value }))
              }
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
              Operational Status
            </label>
            <select
              value={addForm.status}
              onChange={(e) =>
                setAddForm((prev) => ({
                  ...prev,
                  status: e.target.value as CompanyStatus,
                }))
              }
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            >
              <option value="ACTIVE">ACTIVE</option>
              <option value="INACTIVE">INACTIVE</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-slate-200 dark:border-slate-800">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsAddModalOpen(false)}
              disabled={isSubmittingAdd}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              isLoading={isSubmittingAdd}
              className="flex items-center gap-1.5"
            >
              <Save className="w-4 h-4" />
              <span>Create Company</span>
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Company Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          if (!isSubmittingEdit) {
            setIsEditModalOpen(false);
            setSelectedCompany(null);
          }
        }}
        title="Edit Company Details"
        description="Update display name, legal registered title, or status."
      >
        {selectedCompany && (
          <form onSubmit={handleEditSubmit} className="space-y-4 text-xs sm:text-sm">
            {/* Readonly Identifier Bar */}
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">
                  Company Code
                </span>
                <span className="font-mono font-bold text-slate-900 dark:text-white">
                  {selectedCompany.company_code}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">
                  Prefix
                </span>
                <span className="font-mono font-bold text-blue-600 dark:text-blue-400">
                  {selectedCompany.employee_code_prefix}-XXXX
                </span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Company Display Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                value={editForm.company_name}
                onChange={(e) =>
                  setEditForm((prev) => ({ ...prev, company_name: e.target.value }))
                }
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              />
              {editFormErrors.company_name && (
                <p className="text-xs text-rose-600 mt-1">
                  {editFormErrors.company_name}
                </p>
              )}
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Legal Corporate Name
              </label>
              <input
                type="text"
                value={editForm.legal_name || ''}
                onChange={(e) =>
                  setEditForm((prev) => ({ ...prev, legal_name: e.target.value }))
                }
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Operational Status
              </label>
              <select
                value={editForm.status}
                onChange={(e) =>
                  setEditForm((prev) => ({
                    ...prev,
                    status: e.target.value as CompanyStatus,
                  }))
                }
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              >
                <option value="ACTIVE">ACTIVE</option>
                <option value="INACTIVE">INACTIVE</option>
              </select>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-slate-200 dark:border-slate-800">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setIsEditModalOpen(false);
                  setSelectedCompany(null);
                }}
                disabled={isSubmittingEdit}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                isLoading={isSubmittingEdit}
                className="flex items-center gap-1.5"
              >
                <Save className="w-4 h-4" />
                <span>Save Changes</span>
              </Button>
            </div>
          </form>
        )}
      </Modal>

      {/* Delete Company Confirmation Modal */}
      <ConfirmationModal
        isOpen={!!companyToDelete}
        onClose={() => {
          if (!isDeleting) setCompanyToDelete(null);
        }}
        onConfirm={handleConfirmDelete}
        title="Delete Company Entity"
        description="Are you sure you want to delete this company entity?"
        confirmText="Delete Company"
        variant="danger"
        isLoading={isDeleting}
      >
        {companyToDelete && (
          <div className="p-3.5 bg-rose-50/70 dark:bg-rose-950/40 border border-rose-200/80 dark:border-rose-800 rounded-xl space-y-2 text-xs">
            <div className="font-bold text-rose-800 dark:text-rose-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>You are deleting {companyToDelete.company_name} ({companyToDelete.company_code})</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400">
              This action permanently removes the company master record from CRM.
              If any active employees, departments, or sales records are assigned to this company, the system will block deletion for data integrity.
            </p>
          </div>
        )}
      </ConfirmationModal>

      {/* Operations Coordinator Settings Modal */}
      <OperationsCoordinatorModal
        isOpen={isCoordinatorModalOpen}
        onClose={() => setIsCoordinatorModalOpen(false)}
        onSaved={() => {
          addToast('success', 'Coordinator Settings Updated', 'Default Operations coordinators saved successfully.');
        }}
      />

      {/* Interactive Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

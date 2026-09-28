import React, { useState, useEffect, useCallback } from 'react';
import {
  FileBadge,
  Plus,
  Search,
  RefreshCw,
  Edit2,
  Trash2,
  AlertCircle,
  Save,
  Clock,
  Layers,
  Award,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  getLicensesApi,
  createLicenseApi,
  updateLicenseApi,
  deleteLicenseApi,
} from '../api/licenses';
import { extractErrorMessage } from '../api/client';
import type {
  License,
  LicenseCreatePayload,
  LicenseUpdatePayload,
  LicenseStatus,
} from '../types/license';
import { Button } from '../components/ui/button';
import { Modal } from '../components/ui/modal';
import { ConfirmationModal } from '../components/common/ConfirmationModal';
import { ToastContainer, type ToastMessage } from '../components/ui/toast';

const CATEGORIES = [
  'LICENCE',
  'REGISTRATION',
  'INCORPORATION',
  'COMPLIANCE',
  'OTHER',
];

export const LicenseMasterPage: React.FC = () => {
  const { hasPermission } = useAuth();
  const canCreate = hasPermission('ADMIN', 'create');
  const canEdit = hasPermission('ADMIN', 'edit');
  const canDelete = hasPermission('ADMIN', 'delete');

  // State
  const [licenses, setLicenses] = useState<License[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Filters
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  // Add License Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [isSubmittingAdd, setIsSubmittingAdd] = useState<boolean>(false);
  const [addForm, setAddForm] = useState<LicenseCreatePayload>({
    service_name: '',
    service_code: '',
    category: 'LICENCE',
    description: '',
    base_price: 0,
    govt_fee: 0,
    standard_turnaround_days: 15,
    status: 'ACTIVE',
  });
  const [addFormErrors, setAddFormErrors] = useState<Record<string, string>>({});

  // Edit License Modal State
  const [isEditModalOpen, setIsEditModalOpen] = useState<boolean>(false);
  const [selectedLicense, setSelectedLicense] = useState<License | null>(null);
  const [isSubmittingEdit, setIsSubmittingEdit] = useState<boolean>(false);
  const [editForm, setEditForm] = useState<LicenseUpdatePayload>({
    service_name: '',
    category: 'LICENCE',
    description: '',
    base_price: 0,
    govt_fee: 0,
    standard_turnaround_days: 15,
    status: 'ACTIVE',
  });
  const [editFormErrors, setEditFormErrors] = useState<Record<string, string>>({});

  // Delete State
  const [licenseToDelete, setLicenseToDelete] = useState<License | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

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

  // Fetch Licenses
  const fetchLicenses = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await getLicensesApi({
        search: searchTerm.trim() || undefined,
        category: categoryFilter !== 'ALL' ? categoryFilter : undefined,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
      });
      setLicenses(data);
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      setErrorMessage(msg);
      addToast('error', 'Failed to load licenses', msg);
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, categoryFilter, statusFilter]);

  useEffect(() => {
    fetchLicenses();
  }, [fetchLicenses]);

  // Open Add Modal
  const handleOpenAddModal = () => {
    setAddForm({
      service_name: '',
      service_code: '',
      category: 'LICENCE',
      description: '',
      base_price: 0,
      govt_fee: 0,
      standard_turnaround_days: 15,
      status: 'ACTIVE',
    });
    setAddFormErrors({});
    setIsAddModalOpen(true);
  };

  // Open Edit Modal
  const handleOpenEditModal = (lic: License) => {
    setSelectedLicense(lic);
    setEditForm({
      service_name: lic.service_name,
      category: lic.category,
      description: lic.description || '',
      base_price: Number(lic.base_price) || 0,
      govt_fee: Number(lic.govt_fee) || 0,
      standard_turnaround_days: lic.standard_turnaround_days || 15,
      status: lic.status,
    });
    setEditFormErrors({});
    setIsEditModalOpen(true);
  };

  // Auto-generate code from name
  const handleNameChangeForAdd = (nameVal: string) => {
    const autoCode = nameVal
      .toUpperCase()
      .replace(/[^A-Z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '')
      .substring(0, 40);

    setAddForm((prev) => ({
      ...prev,
      service_name: nameVal,
      service_code: prev.service_code && prev.service_code !== autoCode.slice(0, -1) ? prev.service_code : autoCode,
    }));
  };

  // Validate Add Form
  const validateAddForm = (): boolean => {
    const errors: Record<string, string> = {};
    if (!addForm.service_name.trim()) {
      errors.service_name = 'License display name is required.';
    }
    if (!addForm.service_code.trim()) {
      errors.service_code = 'License code is required.';
    } else if (!/^[A-Z0-9_]{2,50}$/.test(addForm.service_code.trim())) {
      errors.service_code = 'License code must be uppercase alphanumeric and underscores (e.g. TRADE_LICENSE).';
    }
    if (!addForm.category.trim()) {
      errors.category = 'Category is required.';
    }
    setAddFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle Create License Submit
  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateAddForm()) return;

    setIsSubmittingAdd(true);
    try {
      const payload: LicenseCreatePayload = {
        service_name: addForm.service_name.trim(),
        service_code: addForm.service_code.trim().toUpperCase(),
        category: addForm.category.trim().toUpperCase(),
        description: addForm.description?.trim() || null,
        base_price: Number(addForm.base_price) || 0,
        govt_fee: Number(addForm.govt_fee) || 0,
        standard_turnaround_days: Number(addForm.standard_turnaround_days) || 15,
        status: addForm.status || 'ACTIVE',
      };

      const created = await createLicenseApi(payload);
      addToast(
        'success',
        'License Created',
        `License "${created.service_name}" (${created.service_code}) successfully registered in Master.`
      );
      setIsAddModalOpen(false);
      await fetchLicenses();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Creation Failed', msg);
    } finally {
      setIsSubmittingAdd(false);
    }
  };

  // Handle Edit License Submit
  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLicense) return;

    if (!editForm.service_name?.trim()) {
      setEditFormErrors({ service_name: 'License display name is required.' });
      return;
    }

    setIsSubmittingEdit(true);
    try {
      const payload: LicenseUpdatePayload = {
        service_name: editForm.service_name.trim(),
        category: editForm.category?.trim().toUpperCase(),
        description: editForm.description?.trim() || null,
        base_price: Number(editForm.base_price) || 0,
        govt_fee: Number(editForm.govt_fee) || 0,
        standard_turnaround_days: Number(editForm.standard_turnaround_days) || 15,
        status: editForm.status,
      };

      const updated = await updateLicenseApi(selectedLicense.service_id, payload);
      addToast(
        'success',
        'License Updated',
        `License "${updated.service_name}" was successfully updated.`
      );
      setIsEditModalOpen(false);
      setSelectedLicense(null);
      await fetchLicenses();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Update Failed', msg);
    } finally {
      setIsSubmittingEdit(false);
    }
  };

  // Handle Delete License
  const handleConfirmDelete = async () => {
    if (!licenseToDelete) return;

    setIsDeleting(true);
    try {
      const res = await deleteLicenseApi(licenseToDelete.service_id);
      addToast(
        'success',
        'License Deleted',
        res.message || `License "${licenseToDelete.service_name}" has been removed.`
      );
      setLicenseToDelete(null);
      await fetchLicenses();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Deletion Blocked', msg);
    } finally {
      setIsDeleting(false);
    }
  };

  // Stats
  const totalLicenses = licenses.length;
  const activeLicenses = licenses.filter((l) => l.status === 'ACTIVE').length;
  const categoriesCount = new Set(licenses.map((l) => l.category)).size;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-gradient-to-br from-indigo-600 to-blue-700 text-white shadow-md">
            <FileBadge className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl sm:text-2xl font-extrabold text-[#0a2569] dark:text-white tracking-tight">
                License Master
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                {totalLicenses} Registered
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
              Configure statutory compliance services and licences available across Sales and Operations workflows.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchLicenses()}
            isLoading={isLoading}
            className="flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>

          {canCreate && (
            <Button
              variant="primary"
              size="sm"
              onClick={handleOpenAddModal}
              className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white shadow-md"
            >
              <Plus className="w-4 h-4" />
              <span>Add License</span>
            </Button>
          )}
        </div>
      </div>

      {/* KPI Stats Ribbon */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Total Licenses
            </span>
            <div className="text-2xl font-black text-slate-900 dark:text-white mt-1">
              {totalLicenses}
            </div>
          </div>
          <div className="p-2 rounded-xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400">
            <Award className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Active Offerings
            </span>
            <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
              {activeLicenses}
            </div>
          </div>
          <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400">
            <Layers className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Categories
            </span>
            <div className="text-2xl font-black text-indigo-600 dark:text-indigo-400 mt-1">
              {categoriesCount}
            </div>
          </div>
          <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
            <FileBadge className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search license name, code, category, or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs sm:text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Categories</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="INACTIVE">INACTIVE</option>
          </select>
        </div>
      </div>

      {/* Licenses Table Container */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="py-16 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
              Loading license records...
            </span>
          </div>
        ) : errorMessage ? (
          <div className="py-12 flex flex-col items-center justify-center gap-3 text-center px-4">
            <AlertCircle className="w-10 h-10 text-red-500" />
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{errorMessage}</p>
            <Button variant="outline" size="sm" onClick={() => fetchLicenses()}>
              Retry
            </Button>
          </div>
        ) : licenses.length === 0 ? (
          <div className="py-16 flex flex-col items-center justify-center gap-2 text-center px-4">
            <FileBadge className="w-10 h-10 text-slate-300 dark:text-slate-600" />
            <h3 className="text-base font-semibold text-slate-800 dark:text-slate-200">
              No licenses found
            </h3>
            <p className="text-xs text-slate-500 max-w-sm">
              {searchTerm || categoryFilter !== 'ALL' || statusFilter !== 'ALL'
                ? 'Try adjusting your search query or filters.'
                : 'No statutory licenses are currently registered. Click "Add License" to create one.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/75 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">License / Service</th>
                  <th className="py-3 px-4">Code</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">SLA Turnaround</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {licenses.map((lic) => {
                  return (
                    <tr
                      key={lic.service_id}
                      className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      {/* License Name & Description */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 text-white font-bold flex items-center justify-center text-xs shrink-0 shadow-xs">
                            <FileBadge className="w-4 h-4" />
                          </div>
                          <div>
                            <div className="font-bold text-slate-900 dark:text-white text-sm">
                              {lic.service_name}
                            </div>
                            <div className="text-xs text-slate-400 max-w-md truncate">
                              {lic.description || 'No description provided'}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* License Code */}
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-700 dark:text-slate-300 text-xs">
                        <span className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                          {lic.service_code}
                        </span>
                      </td>

                      {/* Category */}
                      <td className="py-3.5 px-4">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-lg text-xs font-semibold bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 border border-indigo-200/70 dark:border-indigo-800">
                          {lic.category}
                        </span>
                      </td>

                      {/* SLA Turnaround */}
                      <td className="py-3.5 px-4 text-xs text-slate-600 dark:text-slate-400">
                        <span className="inline-flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-slate-400" />
                          <span>{lic.standard_turnaround_days} Days</span>
                        </span>
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                            lic.status === 'ACTIVE'
                              ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                              : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              lic.status === 'ACTIVE' ? 'bg-emerald-500' : 'bg-slate-400'
                            }`}
                          />
                          {lic.status}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {canEdit && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleOpenEditModal(lic)}
                              className="inline-flex items-center gap-1.5 text-xs h-8 text-blue-600 hover:text-blue-700"
                              title="Edit License"
                            >
                              <Edit2 className="w-3.5 h-3.5 text-blue-600" />
                              <span>Edit</span>
                            </Button>
                          )}
                          {canDelete && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setLicenseToDelete(lic)}
                              className="inline-flex items-center gap-1.5 text-xs h-8 text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/40 border-slate-200 dark:border-slate-700"
                              title="Delete License"
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

      {/* Add License Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => {
          if (!isSubmittingAdd) setIsAddModalOpen(false);
        }}
        title="Register New License / Service"
        description="Add a new statutory compliance licence or service offering to CRM."
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs sm:text-sm">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
              License Display Name <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              placeholder="e.g. FSSAI Food Safety License, Trade License"
              value={addForm.service_name}
              onChange={(e) => handleNameChangeForAdd(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
            {addFormErrors.service_name && (
              <p className="text-xs text-rose-600 mt-1">{addFormErrors.service_name}</p>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                License Code <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder="e.g. FSSAI_LICENSE"
                value={addForm.service_code}
                onChange={(e) =>
                  setAddForm((prev) => ({
                    ...prev,
                    service_code: e.target.value.toUpperCase().replace(/\s+/g, '_'),
                  }))
                }
                className="w-full px-3 py-2 font-mono bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 uppercase"
              />
              {addFormErrors.service_code && (
                <p className="text-xs text-rose-600 mt-1">{addFormErrors.service_code}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Category <span className="text-rose-500">*</span>
              </label>
              <select
                value={addForm.category}
                onChange={(e) =>
                  setAddForm((prev) => ({
                    ...prev,
                    category: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
              Estimated SLA Turnaround (Days)
            </label>
            <input
              type="number"
              min={1}
              max={365}
              value={addForm.standard_turnaround_days}
              onChange={(e) =>
                setAddForm((prev) => ({
                  ...prev,
                  standard_turnaround_days: parseInt(e.target.value, 10) || 15,
                }))
              }
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
              Description / Statutory Scope
            </label>
            <textarea
              rows={2}
              placeholder="e.g. State municipal licence requirement for commercial retail..."
              value={addForm.description || ''}
              onChange={(e) =>
                setAddForm((prev) => ({ ...prev, description: e.target.value }))
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
                  status: e.target.value as LicenseStatus,
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
              className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Save className="w-4 h-4" />
              <span>Create License</span>
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit License Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          if (!isSubmittingEdit) {
            setIsEditModalOpen(false);
            setSelectedLicense(null);
          }
        }}
        title="Edit License Details"
        description="Update display name, category, SLA turnaround days, or status."
      >
        {selectedLicense && (
          <form onSubmit={handleEditSubmit} className="space-y-4 text-xs sm:text-sm">
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">
                  License Code
                </span>
                <span className="font-mono font-bold text-slate-900 dark:text-white">
                  {selectedLicense.service_code}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">
                  Category
                </span>
                <span className="font-bold text-indigo-600 dark:text-indigo-400">
                  {selectedLicense.category}
                </span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                License Display Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                value={editForm.service_name}
                onChange={(e) =>
                  setEditForm((prev) => ({ ...prev, service_name: e.target.value }))
                }
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
              />
              {editFormErrors.service_name && (
                <p className="text-xs text-rose-600 mt-1">
                  {editFormErrors.service_name}
                </p>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Category
                </label>
                <select
                  value={editForm.category}
                  onChange={(e) =>
                    setEditForm((prev) => ({
                      ...prev,
                      category: e.target.value,
                    }))
                  }
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  SLA Turnaround (Days)
                </label>
                <input
                  type="number"
                  min={1}
                  max={365}
                  value={editForm.standard_turnaround_days}
                  onChange={(e) =>
                    setEditForm((prev) => ({
                      ...prev,
                      standard_turnaround_days: parseInt(e.target.value, 10) || 15,
                    }))
                  }
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Description / Statutory Scope
              </label>
              <textarea
                rows={2}
                value={editForm.description || ''}
                onChange={(e) =>
                  setEditForm((prev) => ({ ...prev, description: e.target.value }))
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
                    status: e.target.value as LicenseStatus,
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
                  setSelectedLicense(null);
                }}
                disabled={isSubmittingEdit}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                isLoading={isSubmittingEdit}
                className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Save className="w-4 h-4" />
                <span>Save Changes</span>
              </Button>
            </div>
          </form>
        )}
      </Modal>

      {/* Delete License Confirmation Modal */}
      <ConfirmationModal
        isOpen={!!licenseToDelete}
        onClose={() => {
          if (!isDeleting) setLicenseToDelete(null);
        }}
        onConfirm={handleConfirmDelete}
        title="Delete License / Service"
        description="Are you sure you want to delete this statutory license?"
        confirmText="Delete License"
        variant="danger"
        isLoading={isDeleting}
      >
        {licenseToDelete && (
          <div className="p-3.5 bg-rose-50/70 dark:bg-rose-950/40 border border-rose-200/80 dark:border-rose-800 rounded-xl space-y-2 text-xs">
            <div className="font-bold text-rose-800 dark:text-rose-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>You are deleting {licenseToDelete.service_name} ({licenseToDelete.service_code})</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400">
              This action will remove the license from master offerings.
              If any active sales orders or operations applications are linked to this license, the system will prevent deletion.
            </p>
          </div>
        )}
      </ConfirmationModal>

      {/* Interactive Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

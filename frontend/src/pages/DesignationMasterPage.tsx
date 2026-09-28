import React, { useState, useEffect, useCallback } from 'react';
import {
  Award,
  Plus,
  Search,
  RefreshCw,
  Edit2,
  AlertCircle,
  Save,
  Trash2,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  getDesignationsApi,
  createDesignationApi,
  updateDesignationApi,
  deleteDesignationApi,
} from '../api/designations';
import { extractErrorMessage } from '../api/client';
import type {
  Designation,
  DesignationCreatePayload,
  DesignationUpdatePayload,
  DesignationStatus,
} from '../types/designation';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Modal } from '../components/ui/modal';
import { ConfirmationModal } from '../components/common/ConfirmationModal';
import { ToastContainer, type ToastMessage } from '../components/ui/toast';

export const DesignationMasterPage: React.FC = () => {
  const { hasPermission } = useAuth();
  const canCreate = hasPermission('ADMIN', 'create');
  const canEdit = hasPermission('ADMIN', 'edit');
  const canDelete = hasPermission('ADMIN', 'delete');

  // State
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Delete State
  const [desigToDelete, setDesigToDelete] = useState<Designation | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Filters
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  // Add Designation Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [isSubmittingAdd, setIsSubmittingAdd] = useState<boolean>(false);
  const [addForm, setAddForm] = useState<DesignationCreatePayload>({
    designation_code: '',
    designation_name: '',
    level_rank: 1,
    is_managerial: false,
    description: '',
    status: 'ACTIVE',
  });
  const [addFormErrors, setAddFormErrors] = useState<Record<string, string>>({});

  // Edit Designation Modal State
  const [isEditModalOpen, setIsEditModalOpen] = useState<boolean>(false);
  const [selectedDesig, setSelectedDesig] = useState<Designation | null>(null);
  const [isSubmittingEdit, setIsSubmittingEdit] = useState<boolean>(false);
  const [editForm, setEditForm] = useState<DesignationUpdatePayload>({
    designation_name: '',
    level_rank: 1,
    is_managerial: false,
    description: '',
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

  // Fetch Designations
  const fetchDesignations = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await getDesignationsApi({
        search: searchTerm.trim() || undefined,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
      });
      setDesignations(data);
    } catch (err: unknown) {
      setErrorMessage(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, statusFilter]);

  useEffect(() => {
    fetchDesignations();
  }, [fetchDesignations]);

  // Open Add Modal
  const handleOpenAddModal = () => {
    setAddForm({
      designation_code: '',
      designation_name: '',
      level_rank: 1,
      is_managerial: false,
      description: '',
      status: 'ACTIVE',
    });
    setAddFormErrors({});
    setIsAddModalOpen(true);
  };

  // Submit Add Form
  const handleSubmitAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    const errors: Record<string, string> = {};

    if (!addForm.designation_code.trim()) {
      errors.designation_code = 'Designation code is required';
    } else if (!/^[A-Z_]+$/.test(addForm.designation_code.trim().toUpperCase())) {
      errors.designation_code = 'Code must contain only uppercase letters and underscores (A-Z, _)';
    }

    if (!addForm.designation_name.trim()) {
      errors.designation_name = 'Designation title is required';
    }

    if (!addForm.level_rank || addForm.level_rank <= 0) {
      errors.level_rank = 'Rank must be greater than 0';
    }

    if (Object.keys(errors).length > 0) {
      setAddFormErrors(errors);
      return;
    }

    setIsSubmittingAdd(true);
    setAddFormErrors({});

    try {
      const newDesig = await createDesignationApi({
        designation_code: addForm.designation_code.trim().toUpperCase(),
        designation_name: addForm.designation_name.trim(),
        level_rank: Number(addForm.level_rank),
        is_managerial: !!addForm.is_managerial,
        description: addForm.description?.trim() || null,
        status: addForm.status || 'ACTIVE',
      });

      addToast(
        'success',
        'Designation Created',
        `Designation "${newDesig.designation_name}" (${newDesig.designation_code}) has been created successfully.`
      );
      setIsAddModalOpen(false);
      fetchDesignations();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Creation Failed', msg);
      setAddFormErrors({ general: msg });
    } finally {
      setIsSubmittingAdd(false);
    }
  };

  // Open Edit Modal
  const handleOpenEditModal = (desig: Designation) => {
    setSelectedDesig(desig);
    setEditForm({
      designation_name: desig.designation_name,
      level_rank: desig.level_rank,
      is_managerial: desig.is_managerial,
      description: desig.description || '',
      status: desig.status,
    });
    setEditFormErrors({});
    setIsEditModalOpen(true);
  };

  // Submit Edit Form
  const handleSubmitEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDesig) return;

    const errors: Record<string, string> = {};
    if (!editForm.designation_name?.trim()) {
      errors.designation_name = 'Designation title cannot be empty';
    }
    if (editForm.level_rank !== undefined && editForm.level_rank <= 0) {
      errors.level_rank = 'Rank must be greater than 0';
    }

    if (Object.keys(errors).length > 0) {
      setEditFormErrors(errors);
      return;
    }

    setIsSubmittingEdit(true);
    setEditFormErrors({});

    try {
      const updated = await updateDesignationApi(selectedDesig.designation_id, {
        designation_name: editForm.designation_name?.trim(),
        level_rank: editForm.level_rank ? Number(editForm.level_rank) : undefined,
        is_managerial: editForm.is_managerial,
        description: editForm.description?.trim() || null,
        status: editForm.status,
      });

      addToast(
        'success',
        'Designation Updated',
        `Designation "${updated.designation_name}" has been updated successfully.`
      );
      setIsEditModalOpen(false);
      fetchDesignations();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Update Failed', msg);
      setEditFormErrors({ general: msg });
    } finally {
      setIsSubmittingEdit(false);
    }
  };

  // Delete Designation Handler
  const handleConfirmDelete = async () => {
    if (!desigToDelete) return;
    setIsDeleting(true);
    try {
      await deleteDesignationApi(desigToDelete.designation_id);
      addToast(
        'success',
        'Designation Deleted',
        `Designation "${desigToDelete.designation_name}" was successfully removed.`
      );
      setDesigToDelete(null);
      fetchDesignations();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Delete Failed', msg);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white/70 dark:bg-slate-900/70 p-6 rounded-3xl backdrop-blur-md border border-slate-200/80 dark:border-slate-800 shadow-xs">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
            <Award className="w-5 h-5" />
            <span className="text-xs font-bold uppercase tracking-wider">Common Master</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Designation Master
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 max-w-2xl">
            Configure common employee job titles, seniority levels, managerial status, and organizational hierarchy across all companies.
          </p>
        </div>

        {canCreate && (
          <Button
            onClick={handleOpenAddModal}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/20 px-5 py-2.5 rounded-xl font-semibold text-xs sm:text-sm shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>Add Designation</span>
          </Button>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white/80 dark:bg-slate-900/80 p-4 sm:p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col sm:flex-row items-center gap-3">
        {/* Search Input */}
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <Input
            type="text"
            placeholder="Search by designation title, code, or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9.5 text-xs sm:text-sm rounded-xl border-slate-200 dark:border-slate-700"
          />
        </div>

        {/* Status Filter */}
        <div className="w-full sm:w-44 shrink-0">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full h-10 px-3 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="ALL">All Status</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
          </select>
        </div>

        {/* Reset / Refresh Button */}
        <button
          type="button"
          onClick={() => {
            setSearchTerm('');
            setStatusFilter('ALL');
          }}
          className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition"
          title="Reset Filters"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Error Alert State */}
      {errorMessage && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 flex items-center justify-between text-xs sm:text-sm text-rose-700 dark:text-rose-300">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            onClick={fetchDesignations}
            className="underline font-bold hover:text-rose-900 cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {/* Designations Table */}
      <div className="bg-white/90 dark:bg-slate-900/90 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="p-12 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs text-slate-500">Loading designation records...</span>
          </div>
        ) : designations.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 mx-auto flex items-center justify-center">
              <Award className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">
              No Designations Found
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
              {searchTerm || statusFilter !== 'ALL'
                ? 'No designations match your active search filters.'
                : 'Get started by adding your first designation record.'}
            </p>
            {canCreate && (
              <Button
                onClick={handleOpenAddModal}
                size="sm"
                className="mt-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs"
              >
                Add Designation
              </Button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50/75 dark:bg-slate-800/40 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                  <th className="py-3.5 px-4 sm:px-6">Designation Title & Code</th>
                  <th className="py-3.5 px-4 text-center">Seniority Level</th>
                  <th className="py-3.5 px-4">Role Type</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-xs sm:text-sm">
                {designations.map((desig) => (
                  <tr
                    key={desig.designation_id}
                    className="hover:bg-slate-50/60 dark:hover:bg-slate-800/30 transition-colors"
                  >
                    {/* Designation Title & Code */}
                    <td className="py-3.5 px-4 sm:px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0">
                          <Award className="w-4 h-4" />
                        </div>
                        <div>
                          <span className="font-bold text-slate-900 dark:text-white block">
                            {desig.designation_name}
                          </span>
                          <span className="text-[11px] font-mono text-slate-400">
                            {desig.designation_code}
                          </span>
                        </div>
                      </div>
                    </td>

                    {/* Seniority Level */}
                    <td className="py-3.5 px-4 text-center">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold text-xs">
                        <TrendingUp className="w-3 h-3 text-indigo-500" />
                        Level {desig.level_rank}
                      </span>
                    </td>

                    {/* Role Type / Managerial */}
                    <td className="py-3.5 px-4">
                      {desig.is_managerial ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-50 text-purple-700 border border-purple-200 dark:bg-purple-950/60 dark:text-purple-300 dark:border-purple-800">
                          <ShieldCheck className="w-3 h-3 text-purple-500" />
                          Managerial
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium text-slate-500 bg-slate-100 dark:bg-slate-800 dark:text-slate-400">
                          Individual
                        </span>
                      )}
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                          desig.status === 'ACTIVE'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800'
                            : 'bg-slate-100 text-slate-600 border border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            desig.status === 'ACTIVE' ? 'bg-emerald-500' : 'bg-slate-400'
                          }`}
                        />
                        {desig.status}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right space-x-1 whitespace-nowrap">
                      {canEdit && (
                        <button
                          type="button"
                          onClick={() => handleOpenEditModal(desig)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-slate-800 dark:hover:text-indigo-400 transition"
                          title="Edit Designation"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                      )}
                      {canDelete && (
                        <button
                          type="button"
                          onClick={() => setDesigToDelete(desig)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-slate-800 dark:hover:text-rose-400 transition"
                          title="Delete Designation"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Designation Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => !isSubmittingAdd && setIsAddModalOpen(false)}
        title="Add New Designation"
        description="Configure a common master job title and seniority rank applicable across all companies."
      >
        <form onSubmit={handleSubmitAdd} className="space-y-4 pt-2">
          {addFormErrors.general && (
            <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-xs text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-900">
              {addFormErrors.general}
            </div>
          )}

          {/* Designation Code & Title */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Designation Code <span className="text-rose-500">*</span>
              </label>
              <Input
                placeholder="e.g. EXECUTIVE, MANAGER"
                value={addForm.designation_code}
                onChange={(e) =>
                  setAddForm({ ...addForm, designation_code: e.target.value.toUpperCase() })
                }
                className="text-xs sm:text-sm rounded-xl uppercase"
              />
              {addFormErrors.designation_code && (
                <p className="text-[11px] text-rose-500">{addFormErrors.designation_code}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Designation Title <span className="text-rose-500">*</span>
              </label>
              <Input
                placeholder="e.g. Senior Operations Manager"
                value={addForm.designation_name}
                onChange={(e) => setAddForm({ ...addForm, designation_name: e.target.value })}
                className="text-xs sm:text-sm rounded-xl"
              />
              {addFormErrors.designation_name && (
                <p className="text-[11px] text-rose-500">{addFormErrors.designation_name}</p>
              )}
            </div>
          </div>

          {/* Level Rank & Managerial Flag */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 items-center">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Seniority Level Rank <span className="text-rose-500">*</span>
              </label>
              <Input
                type="number"
                min={1}
                max={20}
                placeholder="1 (Entry) to 10 (Director)"
                value={addForm.level_rank}
                onChange={(e) =>
                  setAddForm({ ...addForm, level_rank: Number(e.target.value) })
                }
                className="text-xs sm:text-sm rounded-xl"
              />
              {addFormErrors.level_rank && (
                <p className="text-[11px] text-rose-500">{addFormErrors.level_rank}</p>
              )}
            </div>

            <div className="pt-5 flex items-center gap-2">
              <input
                type="checkbox"
                id="add_is_managerial"
                checked={addForm.is_managerial}
                onChange={(e) =>
                  setAddForm({ ...addForm, is_managerial: e.target.checked })
                }
                className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
              />
              <label
                htmlFor="add_is_managerial"
                className="text-xs font-semibold text-slate-700 dark:text-slate-300 cursor-pointer"
              >
                Is Managerial Position
              </label>
            </div>
          </div>

          {/* Description */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Description (Optional)
            </label>
            <textarea
              rows={2}
              placeholder="Brief description of designation responsibilities..."
              value={addForm.description || ''}
              onChange={(e) => setAddForm({ ...addForm, description: e.target.value })}
              className="w-full p-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Status */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Operational Status
            </label>
            <select
              value={addForm.status}
              onChange={(e) =>
                setAddForm({ ...addForm, status: e.target.value as DesignationStatus })
              }
              className="w-full h-10 px-3 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-100 dark:border-slate-800">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsAddModalOpen(false)}
              disabled={isSubmittingAdd}
              className="rounded-xl text-xs"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmittingAdd}
              className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5"
            >
              {isSubmittingAdd ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Create Designation</span>
                </>
              )}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Designation Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => !isSubmittingEdit && setIsEditModalOpen(false)}
        title="Edit Designation"
        description={`Modify configuration for designation "${selectedDesig?.designation_code}".`}
      >
        <form onSubmit={handleSubmitEdit} className="space-y-4 pt-2">
          {editFormErrors.general && (
            <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-xs text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-900">
              {editFormErrors.general}
            </div>
          )}

          {/* Designation Title */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Designation Title <span className="text-rose-500">*</span>
            </label>
            <Input
              placeholder="e.g. Senior Operations Manager"
              value={editForm.designation_name || ''}
              onChange={(e) => setEditForm({ ...editForm, designation_name: e.target.value })}
              className="text-xs sm:text-sm rounded-xl"
            />
            {editFormErrors.designation_name && (
              <p className="text-[11px] text-rose-500">{editFormErrors.designation_name}</p>
            )}
          </div>

          {/* Level Rank & Managerial Flag */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 items-center">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Seniority Level Rank <span className="text-rose-500">*</span>
              </label>
              <Input
                type="number"
                min={1}
                max={20}
                placeholder="1 (Entry) to 10 (Director)"
                value={editForm.level_rank || 1}
                onChange={(e) =>
                  setEditForm({ ...editForm, level_rank: Number(e.target.value) })
                }
                className="text-xs sm:text-sm rounded-xl"
              />
              {editFormErrors.level_rank && (
                <p className="text-[11px] text-rose-500">{editFormErrors.level_rank}</p>
              )}
            </div>

            <div className="pt-5 flex items-center gap-2">
              <input
                type="checkbox"
                id="edit_is_managerial"
                checked={editForm.is_managerial || false}
                onChange={(e) =>
                  setEditForm({ ...editForm, is_managerial: e.target.checked })
                }
                className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
              />
              <label
                htmlFor="edit_is_managerial"
                className="text-xs font-semibold text-slate-700 dark:text-slate-300 cursor-pointer"
              >
                Is Managerial Position
              </label>
            </div>
          </div>

          {/* Description */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Description
            </label>
            <textarea
              rows={2}
              placeholder="Brief description of responsibilities..."
              value={editForm.description || ''}
              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              className="w-full p-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Status */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Operational Status
            </label>
            <select
              value={editForm.status}
              onChange={(e) =>
                setEditForm({ ...editForm, status: e.target.value as DesignationStatus })
              }
              className="w-full h-10 px-3 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-100 dark:border-slate-800">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsEditModalOpen(false)}
              disabled={isSubmittingEdit}
              className="rounded-xl text-xs"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmittingEdit}
              className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5"
            >
              {isSubmittingEdit ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Updating...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Save Changes</span>
                </>
              )}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={!!desigToDelete}
        onClose={() => !isDeleting && setDesigToDelete(null)}
        onConfirm={handleConfirmDelete}
        title="Delete Designation"
        description={`Are you sure you want to delete designation "${desigToDelete?.designation_name}" (${desigToDelete?.designation_code})? This action cannot be undone.`}
        confirmText={isDeleting ? 'Deleting...' : 'Delete Designation'}
        variant="danger"
        isLoading={isDeleting}
      />

      {/* Global Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

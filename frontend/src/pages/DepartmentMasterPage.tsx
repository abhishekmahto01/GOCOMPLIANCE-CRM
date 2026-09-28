import React, { useState, useEffect, useCallback } from 'react';
import {
  Network,
  Plus,
  Search,
  RefreshCw,
  Edit2,
  AlertCircle,
  Save,
  Trash2,
  Briefcase,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  getDepartmentsApi,
  createDepartmentApi,
  updateDepartmentApi,
  deleteDepartmentApi,
} from '../api/departments';
import { extractErrorMessage } from '../api/client';
import type {
  Department,
  DepartmentCreatePayload,
  DepartmentUpdatePayload,
  DepartmentStatus,
} from '../types/department';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Modal } from '../components/ui/modal';
import { ConfirmationModal } from '../components/common/ConfirmationModal';
import { ToastContainer, type ToastMessage } from '../components/ui/toast';

export const DepartmentMasterPage: React.FC = () => {
  const { hasPermission } = useAuth();
  const canCreate = hasPermission('ADMIN', 'create');
  const canEdit = hasPermission('ADMIN', 'edit');
  const canDelete = hasPermission('ADMIN', 'delete');

  // State
  const [departments, setDepartments] = useState<Department[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Delete State
  const [deptToDelete, setDeptToDelete] = useState<Department | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Filters
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  // Add Department Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [isSubmittingAdd, setIsSubmittingAdd] = useState<boolean>(false);
  const [addForm, setAddForm] = useState<DepartmentCreatePayload>({
    department_code: '',
    department_name: '',
    description: '',
    status: 'ACTIVE',
  });
  const [addFormErrors, setAddFormErrors] = useState<Record<string, string>>({});

  // Edit Department Modal State
  const [isEditModalOpen, setIsEditModalOpen] = useState<boolean>(false);
  const [selectedDept, setSelectedDept] = useState<Department | null>(null);
  const [isSubmittingEdit, setIsSubmittingEdit] = useState<boolean>(false);
  const [editForm, setEditForm] = useState<DepartmentUpdatePayload>({
    department_name: '',
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

  // Fetch Departments
  const fetchDepartments = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await getDepartmentsApi({
        search: searchTerm.trim() || undefined,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
      });
      setDepartments(data);
    } catch (err: unknown) {
      setErrorMessage(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, statusFilter]);

  useEffect(() => {
    fetchDepartments();
  }, [fetchDepartments]);

  // Open Add Modal
  const handleOpenAddModal = () => {
    setAddForm({
      department_code: '',
      department_name: '',
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

    if (!addForm.department_code.trim()) {
      errors.department_code = 'Department code is required';
    } else if (!/^[A-Z_]+$/.test(addForm.department_code.trim().toUpperCase())) {
      errors.department_code = 'Code must contain only uppercase letters and underscores (A-Z, _)';
    }

    if (!addForm.department_name.trim()) {
      errors.department_name = 'Department name is required';
    }

    if (Object.keys(errors).length > 0) {
      setAddFormErrors(errors);
      return;
    }

    setIsSubmittingAdd(true);
    setAddFormErrors({});

    try {
      const newDept = await createDepartmentApi({
        department_code: addForm.department_code.trim().toUpperCase(),
        department_name: addForm.department_name.trim(),
        description: addForm.description?.trim() || null,
        status: addForm.status || 'ACTIVE',
      });

      addToast(
        'success',
        'Department Created',
        `Department "${newDept.department_name}" (${newDept.department_code}) has been created successfully.`
      );
      setIsAddModalOpen(false);
      fetchDepartments();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Creation Failed', msg);
      setAddFormErrors({ general: msg });
    } finally {
      setIsSubmittingAdd(false);
    }
  };

  // Open Edit Modal
  const handleOpenEditModal = (dept: Department) => {
    setSelectedDept(dept);
    setEditForm({
      department_name: dept.department_name,
      description: dept.description || '',
      status: dept.status,
    });
    setEditFormErrors({});
    setIsEditModalOpen(true);
  };

  // Submit Edit Form
  const handleSubmitEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDept) return;

    const errors: Record<string, string> = {};
    if (!editForm.department_name?.trim()) {
      errors.department_name = 'Department name cannot be empty';
    }

    if (Object.keys(errors).length > 0) {
      setEditFormErrors(errors);
      return;
    }

    setIsSubmittingEdit(true);
    setEditFormErrors({});

    try {
      const updated = await updateDepartmentApi(selectedDept.department_id, {
        department_name: editForm.department_name?.trim(),
        description: editForm.description?.trim() || null,
        status: editForm.status,
      });

      addToast(
        'success',
        'Department Updated',
        `Department "${updated.department_name}" has been updated successfully.`
      );
      setIsEditModalOpen(false);
      fetchDepartments();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Update Failed', msg);
      setEditFormErrors({ general: msg });
    } finally {
      setIsSubmittingEdit(false);
    }
  };

  // Delete Department Handler
  const handleConfirmDelete = async () => {
    if (!deptToDelete) return;
    setIsDeleting(true);
    try {
      await deleteDepartmentApi(deptToDelete.department_id);
      addToast(
        'success',
        'Department Deleted',
        `Department "${deptToDelete.department_name}" was successfully removed.`
      );
      setDeptToDelete(null);
      fetchDepartments();
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
          <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
            <Network className="w-5 h-5" />
            <span className="text-xs font-bold uppercase tracking-wider">Common Master</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Department Master
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 max-w-2xl">
            Configure enterprise-wide master departments (e.g. Sales, Operations, Administration, Accounts) for user organization and workflows.
          </p>
        </div>

        {canCreate && (
          <Button
            onClick={handleOpenAddModal}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/20 px-5 py-2.5 rounded-xl font-semibold text-xs sm:text-sm shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>Add Department</span>
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
            placeholder="Search by department name, code, or description..."
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
            className="w-full h-10 px-3 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            onClick={fetchDepartments}
            className="underline font-bold hover:text-rose-900 cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {/* Departments Table */}
      <div className="bg-white/90 dark:bg-slate-900/90 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="p-12 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs text-slate-500">Loading department records...</span>
          </div>
        ) : departments.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 mx-auto flex items-center justify-center">
              <Briefcase className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">
              No Departments Found
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
              {searchTerm || statusFilter !== 'ALL'
                ? 'No departments match your active search filters.'
                : 'Get started by creating your first department master record.'}
            </p>
            {canCreate && (
              <Button
                onClick={handleOpenAddModal}
                size="sm"
                className="mt-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs"
              >
                Add Department
              </Button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50/75 dark:bg-slate-800/40 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                  <th className="py-3.5 px-4 sm:px-6">Department Name & Code</th>
                  <th className="py-3.5 px-4">Description</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-xs sm:text-sm">
                {departments.map((dept) => (
                  <tr
                    key={dept.department_id}
                    className="hover:bg-slate-50/60 dark:hover:bg-slate-800/30 transition-colors"
                  >
                    {/* Department Name & Code */}
                    <td className="py-3.5 px-4 sm:px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
                          <Network className="w-4 h-4" />
                        </div>
                        <div>
                          <span className="font-bold text-slate-900 dark:text-white block">
                            {dept.department_name}
                          </span>
                          <span className="text-[11px] font-mono text-slate-400">
                            {dept.department_code}
                          </span>
                        </div>
                      </div>
                    </td>

                    {/* Description */}
                    <td className="py-3.5 px-4 text-xs text-slate-500 dark:text-slate-400 max-w-xs truncate">
                      {dept.description || '—'}
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                          dept.status === 'ACTIVE'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800'
                            : 'bg-slate-100 text-slate-600 border border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            dept.status === 'ACTIVE' ? 'bg-emerald-500' : 'bg-slate-400'
                          }`}
                        />
                        {dept.status}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right space-x-1 whitespace-nowrap">
                      {canEdit && (
                        <button
                          type="button"
                          onClick={() => handleOpenEditModal(dept)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-slate-800 dark:hover:text-blue-400 transition"
                          title="Edit Department"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                      )}
                      {canDelete && (
                        <button
                          type="button"
                          onClick={() => setDeptToDelete(dept)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-slate-800 dark:hover:text-rose-400 transition"
                          title="Delete Department"
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

      {/* Add Department Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => !isSubmittingAdd && setIsAddModalOpen(false)}
        title="Add New Department"
        description="Register a common master department applicable across all companies."
      >
        <form onSubmit={handleSubmitAdd} className="space-y-4 pt-2">
          {addFormErrors.general && (
            <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-xs text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-900">
              {addFormErrors.general}
            </div>
          )}

          {/* Department Code & Name */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Department Code <span className="text-rose-500">*</span>
              </label>
              <Input
                placeholder="e.g. SALES, ACCOUNTS"
                value={addForm.department_code}
                onChange={(e) =>
                  setAddForm({ ...addForm, department_code: e.target.value.toUpperCase() })
                }
                className="text-xs sm:text-sm rounded-xl uppercase"
              />
              {addFormErrors.department_code && (
                <p className="text-[11px] text-rose-500">{addFormErrors.department_code}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Department Name <span className="text-rose-500">*</span>
              </label>
              <Input
                placeholder="e.g. Sales & Marketing"
                value={addForm.department_name}
                onChange={(e) => setAddForm({ ...addForm, department_name: e.target.value })}
                className="text-xs sm:text-sm rounded-xl"
              />
              {addFormErrors.department_name && (
                <p className="text-[11px] text-rose-500">{addFormErrors.department_name}</p>
              )}
            </div>
          </div>

          {/* Description */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Description (Optional)
            </label>
            <textarea
              rows={2}
              placeholder="Brief description of department scope and functions..."
              value={addForm.description || ''}
              onChange={(e) => setAddForm({ ...addForm, description: e.target.value })}
              className="w-full p-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                setAddForm({ ...addForm, status: e.target.value as DepartmentStatus })
              }
              className="w-full h-10 px-3 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5"
            >
              {isSubmittingAdd ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Create Department</span>
                </>
              )}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Department Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => !isSubmittingEdit && setIsEditModalOpen(false)}
        title="Edit Department"
        description={`Modify configuration for department "${selectedDept?.department_code}".`}
      >
        <form onSubmit={handleSubmitEdit} className="space-y-4 pt-2">
          {editFormErrors.general && (
            <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-xs text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-900">
              {editFormErrors.general}
            </div>
          )}

          {/* Department Name */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Department Name <span className="text-rose-500">*</span>
            </label>
            <Input
              placeholder="e.g. Sales & Marketing"
              value={editForm.department_name || ''}
              onChange={(e) => setEditForm({ ...editForm, department_name: e.target.value })}
              className="text-xs sm:text-sm rounded-xl"
            />
            {editFormErrors.department_name && (
              <p className="text-[11px] text-rose-500">{editFormErrors.department_name}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Description
            </label>
            <textarea
              rows={2}
              placeholder="Brief description of department scope..."
              value={editForm.description || ''}
              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              className="w-full p-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                setEditForm({ ...editForm, status: e.target.value as DepartmentStatus })
              }
              className="w-full h-10 px-3 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5"
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
        isOpen={!!deptToDelete}
        onClose={() => !isDeleting && setDeptToDelete(null)}
        onConfirm={handleConfirmDelete}
        title="Delete Department"
        description={`Are you sure you want to delete department "${deptToDelete?.department_name}" (${deptToDelete?.department_code})? This action cannot be undone.`}
        confirmText={isDeleting ? 'Deleting...' : 'Delete Department'}
        variant="danger"
        isLoading={isDeleting}
      />

      {/* Global Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

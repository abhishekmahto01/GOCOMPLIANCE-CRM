import React, { useState, useEffect, useCallback } from 'react';
import {
  Share2,
  Plus,
  Search,
  RefreshCw,
  Edit2,
  Trash2,
  AlertCircle,
  Save,
  CheckCircle2,
  XCircle,
  ShieldAlert,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  getSourcesApi,
  createSourceApi,
  updateSourceApi,
  deleteSourceApi,
} from '../api/sources';
import { extractErrorMessage } from '../api/client';
import type {
  SourceMaster,
  SourceCreatePayload,
  SourceUpdatePayload,
  SourceStatus,
} from '../types/source';
import { Button } from '../components/ui/button';
import { Modal } from '../components/ui/modal';
import { ConfirmationModal } from '../components/common/ConfirmationModal';
import { ToastContainer, type ToastMessage } from '../components/ui/toast';

export const SourceMasterPage: React.FC = () => {
  const { hasPermission, isSuperAdmin } = useAuth();
  const canCreate = hasPermission('ADMIN', 'create');
  const canEdit = hasPermission('ADMIN', 'edit');
  const canDelete = isSuperAdmin;

  // State
  const [sources, setSources] = useState<SourceMaster[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Filters
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  // Add Source Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [isSubmittingAdd, setIsSubmittingAdd] = useState<boolean>(false);
  const [addForm, setAddForm] = useState<SourceCreatePayload>({
    source_name: '',
    source_code: '',
    description: '',
    status: 'ACTIVE',
  });
  const [addFormErrors, setAddFormErrors] = useState<Record<string, string>>({});

  // Edit Source Modal State
  const [isEditModalOpen, setIsEditModalOpen] = useState<boolean>(false);
  const [selectedSource, setSelectedSource] = useState<SourceMaster | null>(null);
  const [isSubmittingEdit, setIsSubmittingEdit] = useState<boolean>(false);
  const [editForm, setEditForm] = useState<SourceUpdatePayload>({
    source_name: '',
    description: '',
    status: 'ACTIVE',
  });
  const [editFormErrors, setEditFormErrors] = useState<Record<string, string>>({});

  // Delete State
  const [sourceToDelete, setSourceToDelete] = useState<SourceMaster | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Toast Helpers
  const addToast = (type: 'success' | 'error' | 'info', title: string, message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  };

  // Fetch Sources
  const fetchSources = useCallback(async () => {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      const data = await getSourcesApi({
        search: searchTerm.trim() || undefined,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
      });
      setSources(data);
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      setErrorMessage(msg);
      addToast('error', 'Error Loading Sources', msg);
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, statusFilter]);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  // Handle Add Form Changes
  const handleAddChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setAddForm((prev) => {
      const updated = { ...prev, [name]: value };
      // Auto-format source code uppercase with underscores if typing source_name and code wasn't manually edited
      if (name === 'source_name' && !prev.source_code) {
        updated.source_code = value.trim().toUpperCase().replace(/[^A-Z0-9]/g, '_');
      }
      return updated;
    });

    if (addFormErrors[name]) {
      setAddFormErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const handleOpenAddModal = () => {
    setAddForm({
      source_name: '',
      source_code: '',
      description: '',
      status: 'ACTIVE',
    });
    setAddFormErrors({});
    setIsAddModalOpen(true);
  };

  const handleCreateSource = async (e: React.FormEvent) => {
    e.preventDefault();
    const errors: Record<string, string> = {};

    if (!addForm.source_name.trim()) {
      errors.source_name = 'Source name is required';
    }
    if (!addForm.source_code.trim()) {
      errors.source_code = 'Source code is required';
    } else if (!/^[A-Za-z0-9_]+$/.test(addForm.source_code.trim())) {
      errors.source_code = 'Code must contain only letters, numbers, and underscores';
    }

    if (Object.keys(errors).length > 0) {
      setAddFormErrors(errors);
      return;
    }

    try {
      setIsSubmittingAdd(true);
      const created = await createSourceApi({
        source_name: addForm.source_name.trim(),
        source_code: addForm.source_code.trim().toUpperCase(),
        description: addForm.description?.trim() || undefined,
        status: addForm.status as SourceStatus,
      });
      addToast('success', 'Source Added', `Source '${created.source_name}' was successfully created.`);
      setIsAddModalOpen(false);
      await fetchSources();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Creation Failed', msg);
    } finally {
      setIsSubmittingAdd(false);
    }
  };

  // Handle Edit
  const handleOpenEditModal = (src: SourceMaster) => {
    setSelectedSource(src);
    setEditForm({
      source_name: src.source_name,
      description: src.description || '',
      status: src.status,
    });
    setEditFormErrors({});
    setIsEditModalOpen(true);
  };

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setEditForm((prev) => ({ ...prev, [name]: value }));
    if (editFormErrors[name]) {
      setEditFormErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const handleUpdateSource = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSource) return;

    const errors: Record<string, string> = {};
    if (!editForm.source_name?.trim()) {
      errors.source_name = 'Source name is required';
    }

    if (Object.keys(errors).length > 0) {
      setEditFormErrors(errors);
      return;
    }

    try {
      setIsSubmittingEdit(true);
      const updated = await updateSourceApi(selectedSource.source_id, {
        source_name: editForm.source_name?.trim(),
        description: editForm.description?.trim() || undefined,
        status: editForm.status as SourceStatus,
      });
      addToast('success', 'Source Updated', `Source '${updated.source_name}' has been updated.`);
      setIsEditModalOpen(false);
      setSelectedSource(null);
      await fetchSources();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Update Failed', msg);
    } finally {
      setIsSubmittingEdit(false);
    }
  };

  // Handle Delete
  const handleDeleteSource = async () => {
    if (!sourceToDelete) return;
    try {
      setIsDeleting(true);
      await deleteSourceApi(sourceToDelete.source_id);
      addToast('success', 'Source Removed', `Source '${sourceToDelete.source_name}' was successfully removed.`);
      setSourceToDelete(null);
      await fetchSources();
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      addToast('error', 'Deletion Blocked', msg);
    } finally {
      setIsDeleting(false);
    }
  };

  // Stats
  const totalSources = sources.length;
  const activeSources = sources.filter((s) => s.status === 'ACTIVE').length;
  const systemSources = sources.filter((s) => s.is_system).length;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-gradient-to-br from-teal-600 to-emerald-700 text-white shadow-md">
            <Share2 className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl sm:text-2xl font-extrabold text-[#0a2569] dark:text-white tracking-tight">
                Source Master
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-teal-100 text-teal-800 dark:bg-teal-950/60 dark:text-teal-300 border border-teal-200 dark:border-teal-800">
                {totalSources} Registered
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
              Configure statutory and marketing lead acquisition sources available across Sales workflows.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchSources()}
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
              <span>Add Source</span>
            </Button>
          )}
        </div>
      </div>

      {/* KPI Stats Ribbon */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Total Sources
            </span>
            <p className="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">
              {totalSources}
            </p>
          </div>
          <div className="p-2.5 rounded-xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400">
            <Share2 className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Active Offerings
            </span>
            <p className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">
              {activeSources}
            </p>
          </div>
          <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Core System Channels
            </span>
            <p className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400 mt-0.5">
              {systemSources}
            </p>
          </div>
          <div className="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="flex flex-col md:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search source name, code, or description..."
            className="w-full pl-10 pr-4 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-xs"
          />
        </div>

        <div className="w-full md:w-48">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-xs"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active Only</option>
            <option value="INACTIVE">Inactive Only</option>
          </select>
        </div>
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900 flex items-center gap-3 text-rose-700 dark:text-rose-300">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <p className="text-sm font-medium">{errorMessage}</p>
        </div>
      )}

      {/* Sources Table / List */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="p-12 flex flex-col items-center justify-center gap-3 text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
            <span className="text-sm">Loading lead sources...</span>
          </div>
        ) : sources.length === 0 ? (
          <div className="p-12 text-center text-slate-400 dark:text-slate-500 space-y-2">
            <Share2 className="w-8 h-8 mx-auto text-slate-300 dark:text-slate-600 mb-2" />
            <p className="text-base font-semibold text-slate-700 dark:text-slate-300">
              No sources found
            </p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              {searchTerm || statusFilter !== 'ALL'
                ? 'Try adjusting your search criteria or filter to see more sources.'
                : 'Click "Add Source" above to configure your first lead acquisition channel.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/75 dark:bg-slate-800/50 text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  <th className="py-3.5 px-4 sm:px-6">Source / Channel</th>
                  <th className="py-3.5 px-4">Code</th>
                  <th className="py-3.5 px-4">Description</th>
                  <th className="py-3.5 px-4">Channel Type</th>
                  <th className="py-3.5 px-4 text-center">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-sm">
                {sources.map((src) => (
                  <tr
                    key={src.source_id}
                    className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    <td className="py-3.5 px-4 sm:px-6">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl bg-teal-50 dark:bg-teal-950/50 text-teal-600 dark:text-teal-400 shrink-0">
                          <Share2 className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900 dark:text-white">
                            {src.source_name}
                          </p>
                        </div>
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="font-mono text-xs px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium border border-slate-200 dark:border-slate-700">
                        {src.source_code}
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-xs text-slate-500 dark:text-slate-400 max-w-xs truncate">
                      {src.description || '—'}
                    </td>

                    <td className="py-3.5 px-4">
                      {src.is_system ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                          System Core
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                          Custom
                        </span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          src.status === 'ACTIVE'
                            ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
                        }`}
                      >
                        {src.status === 'ACTIVE' ? (
                          <>
                            <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                            Active
                          </>
                        ) : (
                          <>
                            <XCircle className="w-3 h-3 text-slate-400" />
                            Inactive
                          </>
                        )}
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {canEdit && (
                          <button
                            onClick={() => handleOpenEditModal(src)}
                            className="p-1.5 rounded-lg text-slate-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950/50 transition-colors"
                            title="Edit Source"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                        )}

                        {canDelete && !src.is_system && (
                          <button
                            onClick={() => setSourceToDelete(src)}
                            className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/50 transition-colors"
                            title="Delete Source"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Source Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => !isSubmittingAdd && setIsAddModalOpen(false)}
        title="Add New Lead Source"
      >
        <form onSubmit={handleCreateSource} className="space-y-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Source Name <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              name="source_name"
              value={addForm.source_name}
              onChange={handleAddChange}
              placeholder="e.g. Google Ads, Facebook, Trade Fair"
              className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {addFormErrors.source_name && (
              <p className="text-xs text-rose-500 mt-1">{addFormErrors.source_name}</p>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Source Code <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              name="source_code"
              value={addForm.source_code}
              onChange={handleAddChange}
              placeholder="e.g. GOOGLE_ADS"
              className="w-full px-3.5 py-2 text-sm font-mono uppercase rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-[11px] text-slate-400 mt-0.5">
              Uppercase identifier used internally and in sales reporting (e.g. GOOGLE_ADS).
            </p>
            {addFormErrors.source_code && (
              <p className="text-xs text-rose-500 mt-1">{addFormErrors.source_code}</p>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Description (Optional)
            </label>
            <textarea
              name="description"
              rows={3}
              value={addForm.description}
              onChange={handleAddChange}
              placeholder="Details or notes about how leads from this channel are acquired..."
              className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Status
            </label>
            <select
              name="status"
              value={addForm.status}
              onChange={handleAddChange}
              className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ACTIVE">ACTIVE (Available immediately in Sales)</option>
              <option value="INACTIVE">INACTIVE</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsAddModalOpen(false)}
              disabled={isSubmittingAdd}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              isLoading={isSubmittingAdd}
              className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-1.5"
            >
              <Save className="w-4 h-4" />
              <span>Save Source</span>
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Source Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => !isSubmittingEdit && setIsEditModalOpen(false)}
        title={`Edit Source: ${selectedSource?.source_name || ''}`}
      >
        <form onSubmit={handleUpdateSource} className="space-y-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Source Code (Read-Only)
            </label>
            <input
              type="text"
              disabled
              value={selectedSource?.source_code || ''}
              className="w-full px-3.5 py-2 text-sm font-mono rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-slate-500 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Source Name <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              name="source_name"
              value={editForm.source_name}
              onChange={handleEditChange}
              placeholder="e.g. Google Ads"
              className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {editFormErrors.source_name && (
              <p className="text-xs text-rose-500 mt-1">{editFormErrors.source_name}</p>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Description (Optional)
            </label>
            <textarea
              name="description"
              rows={3}
              value={editForm.description}
              onChange={handleEditChange}
              placeholder="Details or notes about how leads from this channel are acquired..."
              className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Status
            </label>
            <select
              name="status"
              value={editForm.status}
              onChange={handleEditChange}
              className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ACTIVE">ACTIVE</option>
              <option value="INACTIVE">INACTIVE</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsEditModalOpen(false)}
              disabled={isSubmittingEdit}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              isLoading={isSubmittingEdit}
              className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-1.5"
            >
              <Save className="w-4 h-4" />
              <span>Update Source</span>
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={!!sourceToDelete}
        onClose={() => !isDeleting && setSourceToDelete(null)}
        onConfirm={handleDeleteSource}
        title="Delete Lead Source"
        description={`Are you sure you want to remove the source '${sourceToDelete?.source_name}'? This action cannot be undone.`}
        confirmText="Delete Source"
        variant="danger"
        isLoading={isDeleting}
      />

      {/* Toast Feedback */}
      <ToastContainer toasts={toasts} onDismiss={(id: string) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </div>
  );
};

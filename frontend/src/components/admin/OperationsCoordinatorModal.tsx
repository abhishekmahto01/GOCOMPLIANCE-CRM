import React, { useEffect, useState } from 'react';
import {
  X,
  Settings2,
  Building2,
  UserCheck,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  Info,
  ShieldAlert,
  Save,
} from 'lucide-react';
import {
  getCoordinatorConfigsApi,
  getEligibleCoordinatorsApi,
  updateCoordinatorConfigApi,
} from '../../api/coordinatorConfig';
import { extractErrorMessage } from '../../api/client';
import type {
  EligibleCoordinatorOption,
  OperationsCoordinatorConfigItem,
} from '../../types/coordinatorConfig';

export interface OperationsCoordinatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaved?: () => void;
}

export const OperationsCoordinatorModal: React.FC<OperationsCoordinatorModalProps> = ({
  isOpen,
  onClose,
  onSaved,
}) => {
  const [configs, setConfigs] = useState<OperationsCoordinatorConfigItem[]>([]);
  const [eligibleList, setEligibleList] = useState<EligibleCoordinatorOption[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [savingCompanyId, setSavingCompanyId] = useState<string | null>(null);
  const [selectedUsers, setSelectedUsers] = useState<Record<string, string>>({});
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const [configsData, eligibleData] = await Promise.all([
        getCoordinatorConfigsApi(),
        getEligibleCoordinatorsApi(),
      ]);
      setConfigs(configsData);
      setEligibleList(eligibleData);

      // Prepopulate selection map
      const initialMap: Record<string, string> = {};
      configsData.forEach((cfg) => {
        initialMap[cfg.company_id] = cfg.coordinator_user_id || '';
      });
      setSelectedUsers(initialMap);
    } catch (err: any) {
      setErrorMsg(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const handleSelectChange = (companyId: string, userId: string) => {
    setSelectedUsers((prev) => ({
      ...prev,
      [companyId]: userId,
    }));
  };

  const handleSave = async (companyId: string) => {
    setSavingCompanyId(companyId);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      const userId = selectedUsers[companyId] || null;
      const updated = await updateCoordinatorConfigApi({
        company_id: companyId,
        coordinator_user_id: userId,
      });

      setConfigs((prev) =>
        prev.map((item) => (item.company_id === companyId ? updated : item))
      );
      setSuccessMsg(`Default Operations coordinator for ${updated.company_name} updated successfully.`);
      if (onSaved) onSaved();
    } catch (err: any) {
      setErrorMsg(extractErrorMessage(err));
    } finally {
      setSavingCompanyId(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-md animate-fade-in"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200/90 dark:border-slate-800 overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="coordinator-modal-title"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200/80 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-600 text-white flex items-center justify-center shadow-md shadow-purple-500/20">
              <Settings2 className="w-5 h-5" />
            </div>
            <div>
              <h3 id="coordinator-modal-title" className="text-base font-bold text-slate-900 dark:text-white">
                Operations Coordinator Settings
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Configure default Operations coordinator mapping per company
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 dark:hover:text-slate-200 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Notice Strip */}
        <div className="px-6 py-2.5 bg-blue-50/70 dark:bg-blue-950/40 border-b border-blue-100 dark:border-blue-900/60 flex items-start gap-2.5 text-xs text-blue-800 dark:text-blue-300">
          <Info className="w-4 h-4 shrink-0 mt-0.5 text-blue-600 dark:text-blue-400" />
          <span>
            <strong>Note:</strong> When a new Sales entry is confirmed, it is automatically routed to that company's configured coordinator. Changing this setting affects <strong>NEW entries only</strong>; existing task assignments remain intact.
          </span>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-4 flex-1">
          {errorMsg && (
            <div className="p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/80 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-900/80 text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2.5">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-400">
              <RefreshCw className="w-6 h-6 animate-spin text-purple-600" />
              <span className="text-xs font-medium">Loading coordinator configurations...</span>
            </div>
          ) : configs.length === 0 ? (
            <div className="py-10 text-center text-slate-500 text-xs">
              No active companies found.
            </div>
          ) : (
            <div className="space-y-4">
              {configs.map((cfg) => {
                const currentSelection = selectedUsers[cfg.company_id] || '';
                const isSaving = savingCompanyId === cfg.company_id;
                const hasChanged = currentSelection !== (cfg.coordinator_user_id || '');

                return (
                  <div
                    key={cfg.company_id}
                    className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm hover:border-slate-300 dark:hover:border-slate-700 transition-all space-y-3"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-2 min-w-0">
                        <Building2 className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0" />
                        <span className="font-semibold text-sm text-slate-900 dark:text-white truncate">
                          {cfg.company_name}
                        </span>
                        <span className="font-mono text-xs font-bold text-slate-500 dark:text-slate-400 uppercase bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-md border border-slate-200 dark:border-slate-700">
                          {cfg.company_code}
                        </span>
                      </div>

                      {cfg.coordinator_user_id ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800 shrink-0">
                          <UserCheck className="w-3 h-3" />
                          Configured
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 px-2 py-0.5 rounded-full border border-amber-200 dark:border-amber-800 shrink-0">
                          <ShieldAlert className="w-3 h-3" />
                          Unassigned
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-center">
                      <div className="sm:col-span-8">
                        <label className="block text-[11px] font-medium text-slate-500 dark:text-slate-400 mb-1">
                          Default Operations Coordinator:
                        </label>
                        <select
                          value={currentSelection}
                          onChange={(e) => handleSelectChange(cfg.company_id, e.target.value)}
                          className="w-full text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white py-2 px-3 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                        >
                          <option value="">-- No Coordinator (Leaves new tasks unassigned) --</option>
                          {eligibleList.map((cand) => (
                            <option key={cand.user_id} value={cand.user_id}>
                              {cand.full_name} ({cand.employee_code}) - {cand.company_name} ({cand.designation_name || 'Operations'})
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="sm:col-span-4 flex items-end justify-end">
                        <button
                          type="button"
                          onClick={() => handleSave(cfg.company_id)}
                          disabled={isSaving || !hasChanged}
                          className={`w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                            hasChanged
                              ? 'bg-purple-600 hover:bg-purple-700 text-white shadow-md shadow-purple-500/20'
                              : 'bg-slate-100 dark:bg-slate-800 text-slate-400 cursor-not-allowed border border-slate-200 dark:border-slate-700'
                          }`}
                        >
                          {isSaving ? (
                            <>
                              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                              Saving...
                            </>
                          ) : (
                            <>
                              <Save className="w-3.5 h-3.5" />
                              Save Mapping
                            </>
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Metadata Footer */}
                    {cfg.coordinator_name && (
                      <div className="text-[11px] text-slate-500 dark:text-slate-400 pt-1 border-t border-slate-100 dark:border-slate-800/60 flex flex-wrap items-center justify-between gap-2">
                        <div>
                          Active Coordinator: <strong className="text-slate-700 dark:text-slate-200">{cfg.coordinator_name}</strong>
                          {cfg.coordinator_employee_code && ` (${cfg.coordinator_employee_code})`}
                          {cfg.coordinator_email && ` • ${cfg.coordinator_email}`}
                        </div>
                        {cfg.updated_by_name && (
                          <div className="text-[10px] text-slate-400">
                            Updated by {cfg.updated_by_name}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

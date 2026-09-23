import React, { useState, useEffect } from 'react';
import {
  X,
  FileText,
  Clock,
  UserCheck,
  CheckCircle2,
  AlertCircle,
  Building2,
  Phone,
  Mail,
  User,
  History,
  Check,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';
import type {
  AssigneeOption,
  OperationApplicationDetail,
} from '../../types/operations';
import {
  getOperationTaskDetailApi,
  reassignOperationTaskApi,
  updateOperationTaskStatusApi,
  updateApplicationDocStatusApi,
  getOperationsAssigneesApi,
} from '../../api/operations';

import { useAuth } from '../../context/AuthContext';

export interface TaskDetailModalProps {
  applicationId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onRefresh?: () => void;
  onShowToast?: (type: 'success' | 'error' | 'info', title: string, message: string) => void;
}

export const TaskDetailModal: React.FC<TaskDetailModalProps> = ({
  applicationId,
  isOpen,
  onClose,
  onRefresh,
  onShowToast,
}) => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'overview' | 'documents' | 'history' | 'reassign'>('overview');
  const [taskDetail, setTaskDetail] = useState<OperationApplicationDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Status change state
  const [statusComment, setStatusComment] = useState('');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  // Reassignment form state
  const [eligibleAssignees, setEligibleAssignees] = useState<AssigneeOption[]>([]);
  const [reassignTargetUserId, setReassignTargetUserId] = useState('');
  const [reassignReason, setReassignReason] = useState('');
  const [reassignPriority, setReassignPriority] = useState('MEDIUM');
  const [reassignDueDate, setReassignDueDate] = useState('');
  const [isReassigning, setIsReassigning] = useState(false);

  // Document rejection modal state
  const [rejectingDocId, setRejectingDocId] = useState<string | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');

  const loadDetail = async (appId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await getOperationTaskDetailApi(appId);
      setTaskDetail(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load task details.');
    } finally {
      setLoading(false);
    }
  };

  const loadAssignees = async () => {
    try {
      const data = await getOperationsAssigneesApi();
      setEligibleAssignees(data);
    } catch (err) {
      console.error('Failed to load assignees', err);
    }
  };

  useEffect(() => {
    if (isOpen && applicationId) {
      loadDetail(applicationId);
      loadAssignees();
      setActiveTab('overview');
      setStatusComment('');
      setReassignReason('');
    } else {
      setTaskDetail(null);
    }
  }, [isOpen, applicationId]);

  if (!isOpen || !applicationId) return null;

  const handleStatusTransition = async (newStatus: string) => {
    if (!taskDetail) return;
    try {
      setIsUpdatingStatus(true);
      const updated = await updateOperationTaskStatusApi(taskDetail.application_id, {
        new_status: newStatus,
        comment: statusComment.trim() || undefined,
      });
      setTaskDetail(updated);
      setStatusComment('');
      if (onShowToast) {
        onShowToast('success', 'Status Updated', `Task status transitioned to ${newStatus.replace(/_/g, ' ')}.`);
      }
      if (onRefresh) onRefresh();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to update status.';
      if (onShowToast) onShowToast('error', 'Update Failed', msg);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleReassignSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskDetail || !reassignTargetUserId || !reassignReason.trim()) return;
    if (taskDetail.assigned_to_user_id && reassignTargetUserId === taskDetail.assigned_to_user_id) {
      if (onShowToast) {
        onShowToast('error', 'Invalid Assignee', 'Cannot reassign task to the current assignee.');
      }
      return;
    }
    if (user?.user_id && reassignTargetUserId === user.user_id) {
      if (onShowToast) {
        onShowToast('error', 'Invalid Assignee', 'Cannot reassign task to yourself.');
      }
      return;
    }
    try {
      setIsReassigning(true);
      const updated = await reassignOperationTaskApi(taskDetail.application_id, {
        new_assignee_user_id: reassignTargetUserId,
        reason: reassignReason.trim(),
        priority: reassignPriority,
        target_due_date: reassignDueDate || undefined,
      });
      setTaskDetail(updated);
      setActiveTab('overview');
      setReassignReason('');
      if (onShowToast) {
        onShowToast('success', 'Task Reassigned', 'Task has been reassigned successfully.');
      }
      if (onRefresh) onRefresh();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to reassign task.';
      if (onShowToast) onShowToast('error', 'Reassignment Failed', msg);
    } finally {
      setIsReassigning(false);
    }
  };

  const handleDocStatus = async (appDocId: string, status: string, reason?: string) => {
    try {
      await updateApplicationDocStatusApi(appDocId, {
        status,
        rejection_reason: reason,
      });
      if (taskDetail) {
        loadDetail(taskDetail.application_id);
      }
      setRejectingDocId(null);
      setRejectionReason('');
      if (onShowToast) {
        onShowToast('success', 'Document Updated', `Document marked as ${status}.`);
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to update document status.';
      if (onShowToast) onShowToast('error', 'Document Error', msg);
    }
  };

  const getPriorityBadge = (p: string) => {
    switch (p?.toUpperCase()) {
      case 'URGENT':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-300">URGENT</span>;
      case 'HIGH':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">HIGH</span>;
      case 'LOW':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">LOW</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">MEDIUM</span>;
    }
  };

  const getStatusBadge = (s: string) => {
    switch (s?.toUpperCase()) {
      case 'APPROVED':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">Approved</span>;
      case 'IN_PROGRESS':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300">In Progress</span>;
      case 'PENDING_DOCUMENTS':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">Pending Docs</span>;
      case 'READY_FOR_SUBMISSION':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-cyan-100 text-cyan-700 dark:bg-cyan-950/60 dark:text-cyan-300">Ready to Submit</span>;
      case 'SUBMITTED':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300">Submitted</span>;
      case 'AUTHORITY_QUERY':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300">Authority Query</span>;
      case 'CANCELLED':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300">Cancelled</span>;
      case 'UNASSIGNED':
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">Unassigned</span>;
      default:
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">Assigned</span>;
    }
  };

  // Next available status options based on current status
  const getNextStatusActions = (currentStatus: string) => {
    switch (currentStatus) {
      case 'ASSIGNED':
        return [{ target: 'IN_PROGRESS', label: 'Start Work (In Progress)', color: 'bg-indigo-600 hover:bg-indigo-700' }];
      case 'IN_PROGRESS':
        return [
          { target: 'PENDING_DOCUMENTS', label: 'Need Client Documents', color: 'bg-amber-600 hover:bg-amber-700' },
          { target: 'READY_FOR_SUBMISSION', label: 'Ready for Submission', color: 'bg-cyan-600 hover:bg-cyan-700' },
          { target: 'SUBMITTED', label: 'Submit to Authority', color: 'bg-purple-600 hover:bg-purple-700' },
        ];
      case 'PENDING_DOCUMENTS':
        return [
          { target: 'IN_PROGRESS', label: 'Documents Received (Resume Work)', color: 'bg-indigo-600 hover:bg-indigo-700' },
          { target: 'READY_FOR_SUBMISSION', label: 'Ready for Submission', color: 'bg-cyan-600 hover:bg-cyan-700' },
        ];
      case 'READY_FOR_SUBMISSION':
        return [
          { target: 'SUBMITTED', label: 'Mark as Submitted to Authority', color: 'bg-purple-600 hover:bg-purple-700' },
          { target: 'IN_PROGRESS', label: 'Return to In Progress', color: 'bg-slate-600 hover:bg-slate-700' },
        ];
      case 'SUBMITTED':
        return [
          { target: 'APPROVED', label: 'Mark as Approved (Completed)', color: 'bg-emerald-600 hover:bg-emerald-700' },
          { target: 'AUTHORITY_QUERY', label: 'Record Authority Query', color: 'bg-rose-600 hover:bg-rose-700' },
        ];
      case 'AUTHORITY_QUERY':
        return [
          { target: 'SUBMITTED', label: 'Query Answered & Resubmitted', color: 'bg-purple-600 hover:bg-purple-700' },
          { target: 'IN_PROGRESS', label: 'Work on Query Resolution', color: 'bg-indigo-600 hover:bg-indigo-700' },
        ];
      default:
        return [];
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200/80 dark:border-slate-800 flex flex-col max-h-[90vh] overflow-hidden text-slate-800 dark:text-slate-100">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200/80 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-slate-900/70">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                  {taskDetail ? taskDetail.application_number : 'Application Details'}
                </h2>
                {taskDetail && getStatusBadge(taskDetail.application_status)}
                {taskDetail && getPriorityBadge(taskDetail.priority)}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Sales Order:{' '}
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {taskDetail?.sales_order_number || '—'}
                </span>{' '}
                • Client:{' '}
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {taskDetail?.client_name || '—'}
                </span>
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Tabs */}
        <div className="flex border-b border-slate-200 dark:border-slate-800 px-6 bg-white dark:bg-slate-900 text-xs font-semibold">
          <button
            type="button"
            onClick={() => setActiveTab('overview')}
            className={`py-3 px-4 border-b-2 transition flex items-center gap-2 ${
              activeTab === 'overview'
                ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            <Building2 className="w-4 h-4" />
            <span>Overview & Client</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('documents')}
            className={`py-3 px-4 border-b-2 transition flex items-center gap-2 ${
              activeTab === 'documents'
                ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>
              Required Documents{' '}
              {taskDetail && (
                <span className="ml-1 px-1.5 py-0.5 rounded-full text-[10px] bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300">
                  {taskDetail.documents_completed}/{taskDetail.documents_total}
                </span>
              )}
            </span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('history')}
            className={`py-3 px-4 border-b-2 transition flex items-center gap-2 ${
              activeTab === 'history'
                ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            <History className="w-4 h-4" />
            <span>Timeline & Audit Logs</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('reassign')}
            className={`py-3 px-4 border-b-2 transition flex items-center gap-2 ${
              activeTab === 'reassign'
                ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            <UserCheck className="w-4 h-4" />
            <span>Reassign Task</span>
          </button>
        </div>

        {/* Modal Body Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading && (
            <div className="py-12 flex flex-col items-center justify-center text-slate-400 space-y-2">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
              <p className="text-sm">Loading task details...</p>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!loading && taskDetail && (
            <>
              {/* TAB 1: OVERVIEW */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Grid 1: Core Details */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Client & Service Info */}
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 space-y-3">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                        <Building2 className="w-4 h-4 text-blue-600" />
                        Client & Service Information
                      </h3>
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-slate-500">Client Name:</span>
                          <span className="font-semibold text-slate-900 dark:text-white">{taskDetail.client_name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Primary Contact:</span>
                          <span className="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-1">
                            <Phone className="w-3 h-3 text-slate-400" />
                            {taskDetail.client_phone || '—'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Email:</span>
                          <span className="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-1">
                            <Mail className="w-3 h-3 text-slate-400" />
                            {taskDetail.client_email || '—'}
                          </span>
                        </div>
                        <div className="flex justify-between pt-1 border-t border-slate-200/60 dark:border-slate-700/60">
                          <span className="text-slate-500">Service:</span>
                          <span className="font-semibold text-blue-600 dark:text-blue-400">{taskDetail.service_name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Service Code:</span>
                          <span className="font-mono text-slate-700 dark:text-slate-300">{taskDetail.service_code || '—'}</span>
                        </div>
                      </div>
                    </div>

                    {/* Assignment & Sales Info */}
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 space-y-3">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                        <User className="w-4 h-4 text-indigo-600" />
                        Assignment & Ownership
                      </h3>
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-slate-500">Assigned To:</span>
                          <span className="font-semibold text-slate-900 dark:text-white">
                            {taskDetail.assigned_to_name ? (
                              <span className="text-blue-600 dark:text-blue-400 font-bold">
                                {taskDetail.assigned_to_name} ({taskDetail.assigned_to_code})
                              </span>
                            ) : (
                              <span className="text-amber-600 font-medium">Unassigned</span>
                            )}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Assigned By:</span>
                          <span className="font-medium text-slate-700 dark:text-slate-300">{taskDetail.assigned_by_name || '—'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Assigned Date:</span>
                          <span className="font-medium text-slate-700 dark:text-slate-300">{taskDetail.formatted_assigned_at || '—'}</span>
                        </div>
                        <div className="flex justify-between pt-1 border-t border-slate-200/60 dark:border-slate-700/60">
                          <span className="text-slate-500">Converted By (Sales):</span>
                          <span className="font-medium text-slate-700 dark:text-slate-300">
                            {taskDetail.salesperson_name || '—'} ({taskDetail.salesperson_code || '—'})
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Target Due Date:</span>
                          <span className={`font-semibold ${taskDetail.is_overdue ? 'text-red-600' : 'text-slate-700 dark:text-slate-300'}`}>
                            {taskDetail.formatted_due_date || 'No Target Date'}
                            {taskDetail.is_overdue && ' (OVERDUE)'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Internal Assignment Notes */}
                  {taskDetail.assignment_notes && (
                    <div className="p-3.5 rounded-xl bg-blue-50/70 dark:bg-blue-950/40 border border-blue-200/70 dark:border-blue-900 text-xs">
                      <span className="font-bold text-blue-800 dark:text-blue-300">Assignment Notes:</span>
                      <p className="mt-1 text-slate-700 dark:text-slate-300">{taskDetail.assignment_notes}</p>
                    </div>
                  )}

                  {/* Lifecycle Status Transition Controls */}
                  <div className="p-4 rounded-xl bg-gradient-to-r from-blue-50/50 to-indigo-50/50 dark:from-slate-800/80 dark:to-slate-800/80 border border-blue-200/70 dark:border-slate-700 space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
                      <ArrowRight className="w-4 h-4 text-blue-600" />
                      Lifecycle Action & Status Progression
                    </h3>
                    
                    <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
                      <div className="flex-1 w-full">
                        <input
                          type="text"
                          value={statusComment}
                          onChange={(e) => setStatusComment(e.target.value)}
                          placeholder="Add comment, submission note, or filing reference..."
                          className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-blue-500 outline-hidden"
                        />
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {getNextStatusActions(taskDetail.application_status).map((act) => (
                          <button
                            key={act.target}
                            type="button"
                            disabled={isUpdatingStatus}
                            onClick={() => handleStatusTransition(act.target)}
                            className={`px-3 py-2 rounded-lg text-xs font-bold text-white shadow-xs transition flex items-center gap-1.5 ${act.color} disabled:opacity-50`}
                          >
                            <Check className="w-3.5 h-3.5" />
                            <span>{act.label}</span>
                          </button>
                        ))}
                        {getNextStatusActions(taskDetail.application_status).length === 0 && (
                          <span className="text-xs text-slate-500 py-2">
                            {taskDetail.application_status === 'APPROVED'
                              ? 'Task is completed and approved.'
                              : 'No forward status transitions available.'}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: REQUIRED DOCUMENTS */}
              {activeTab === 'documents' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white">Document Checklist</h3>
                      <p className="text-xs text-slate-500">Track and verify statutory documents required for filing.</p>
                    </div>
                    <span className="text-xs font-bold text-slate-600 dark:text-slate-400">
                      Verified: {taskDetail.documents_completed} / {taskDetail.documents_total}
                    </span>
                  </div>

                  {taskDetail.documents.length === 0 ? (
                    <div className="p-8 text-center bg-slate-50 dark:bg-slate-800/40 rounded-xl text-slate-500 text-xs">
                      No mandatory document checklist configured for this service.
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-200/80 dark:divide-slate-800 border border-slate-200/80 dark:border-slate-800 rounded-xl overflow-hidden">
                      {taskDetail.documents.map((doc) => (
                        <div key={doc.app_doc_id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold text-slate-900 dark:text-white">{doc.document_name}</span>
                              {doc.is_mandatory && (
                                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300">
                                  Required
                                </span>
                              )}
                            </div>
                            <p className="text-[11px] font-mono text-slate-500">Code: {doc.document_code}</p>
                            {doc.rejection_reason && (
                              <p className="text-xs text-red-600 dark:text-red-400 font-medium">
                                Rejection Note: {doc.rejection_reason}
                              </p>
                            )}
                            {doc.verified_by_name && (
                              <p className="text-[11px] text-emerald-600 dark:text-emerald-400">
                                Verified by {doc.verified_by_name}
                              </p>
                            )}
                          </div>

                          <div className="flex items-center gap-2 shrink-0">
                            {doc.status === 'VERIFIED' ? (
                              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 flex items-center gap-1">
                                <CheckCircle2 className="w-3.5 h-3.5" /> Verified
                              </span>
                            ) : doc.status === 'REJECTED' ? (
                              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300 flex items-center gap-1">
                                <AlertCircle className="w-3.5 h-3.5" /> Rejected
                              </span>
                            ) : doc.status === 'RECEIVED' ? (
                              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 flex items-center gap-1">
                                <Clock className="w-3.5 h-3.5" /> Received
                              </span>
                            ) : (
                              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                                Pending
                              </span>
                            )}

                            {/* Action Buttons */}
                            <button
                              type="button"
                              onClick={() => handleDocStatus(doc.app_doc_id, 'VERIFIED')}
                              className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 transition"
                            >
                              Verify
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setRejectingDocId(doc.app_doc_id);
                                setRejectionReason('');
                              }}
                              className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-red-50 text-red-700 hover:bg-red-100 dark:bg-red-950/40 dark:text-red-300 border border-red-200 dark:border-red-800 transition"
                            >
                              Reject
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Reject Document Reason Modal */}
                  {rejectingDocId && (
                    <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 space-y-3">
                      <h4 className="text-xs font-bold text-red-800 dark:text-red-200">Specify Rejection Reason</h4>
                      <input
                        type="text"
                        value={rejectionReason}
                        onChange={(e) => setRejectionReason(e.target.value)}
                        placeholder="e.g. Signature missing, blur scan, expired validity..."
                        className="w-full px-3 py-2 text-xs rounded-lg border border-red-300 dark:border-red-700 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-red-500 outline-hidden"
                      />
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => setRejectingDocId(null)}
                          className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDocStatus(rejectingDocId, 'REJECTED', rejectionReason)}
                          className="px-3 py-1.5 text-xs font-bold rounded-lg bg-red-600 text-white hover:bg-red-700"
                        >
                          Confirm Rejection
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: TIMELINE & AUDIT LOGS */}
              {activeTab === 'history' && (
                <div className="space-y-4">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">Audit Trail & Assignment History</h3>
                  
                  {/* Assignment History Sub-section */}
                  {taskDetail.assignment_history.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Assignment History</h4>
                      <div className="space-y-2">
                        {taskDetail.assignment_history.map((h) => (
                          <div key={h.history_id} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700/60 text-xs">
                            <div className="flex justify-between font-semibold">
                              <span>
                                {h.previous_assignee_name || 'Unassigned'} ➔{' '}
                                <span className="text-blue-600 dark:text-blue-400">{h.new_assignee_name}</span>
                              </span>
                              <span className="text-slate-400">{new Date(h.assigned_at).toLocaleString()}</span>
                            </div>
                            <p className="text-slate-500 mt-1">
                              Assigned by: <span className="font-medium text-slate-700 dark:text-slate-300">{h.assigned_by_name}</span> • Reason: {h.reason || '—'}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Activity Logs Timeline */}
                  <div className="space-y-2 pt-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Activity Log</h4>
                    <div className="space-y-2">
                      {taskDetail.activity_logs.map((log) => (
                        <div key={log.activity_id} className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800 text-xs flex items-start gap-3">
                          <div className="p-1.5 rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400 shrink-0 mt-0.5">
                            <Clock className="w-3.5 h-3.5" />
                          </div>
                          <div className="flex-1">
                            <div className="flex justify-between">
                              <span className="font-semibold text-slate-900 dark:text-white">{log.action_type.replace(/_/g, ' ')}</span>
                              <span className="text-slate-400 text-[11px]">{new Date(log.created_at).toLocaleString()}</span>
                            </div>
                            <p className="text-slate-600 dark:text-slate-300 mt-0.5">{log.comment}</p>
                            <p className="text-[11px] text-slate-400 mt-0.5">Actor: {log.actor_name || 'System'}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: REASSIGN TASK */}
              {activeTab === 'reassign' && (
                <form onSubmit={handleReassignSubmit} className="space-y-4 max-w-lg mx-auto py-2">
                  <div className="p-4 rounded-xl bg-blue-50/60 dark:bg-blue-950/30 border border-blue-200/70 dark:border-blue-900/60 text-xs text-slate-700 dark:text-slate-300">
                    <p className="font-semibold text-blue-800 dark:text-blue-300">Task Reassignment</p>
                    <p className="mt-0.5">Reassign this application to another Operations team member. A reason is required for compliance auditing.</p>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                      New Assignee <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={reassignTargetUserId}
                      onChange={(e) => setReassignTargetUserId(e.target.value)}
                      required
                      className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-blue-500 outline-hidden"
                    >
                      <option value="">-- Select Operations Team Member --</option>
                      {eligibleAssignees
                        .filter((emp) => {
                          if (taskDetail.assigned_to_user_id && emp.user_id === taskDetail.assigned_to_user_id) return false;
                          if (user?.user_id && emp.user_id === user.user_id) return false;
                          const dept = (emp.department_name || '').toLowerCase();
                          const desig = (emp.designation_name || '').toLowerCase();
                          if (dept.includes('sale') || desig.includes('sale')) return false;
                          if (dept.includes('admin') || desig.includes('admin')) return false;
                          if (desig.includes('director') || desig.includes('ceo') || desig.includes('super admin')) return false;
                          if (emp.employee_code === 'CG0001') return false;
                          return true;
                        })
                        .map((emp) => (
                          <option key={emp.user_id} value={emp.user_id}>
                            {emp.full_name || emp.name} ({emp.employee_code})
                          </option>
                        ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                      Mandatory Reason for Reassignment <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      value={reassignReason}
                      onChange={(e) => setReassignReason(e.target.value)}
                      required
                      rows={3}
                      placeholder="e.g. Employee on leave, workload balancing, client requested specialist..."
                      className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-blue-500 outline-hidden"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Priority</label>
                      <select
                        value={reassignPriority}
                        onChange={(e) => setReassignPriority(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-blue-500 outline-hidden"
                      >
                        <option value="LOW">Low</option>
                        <option value="MEDIUM">Medium</option>
                        <option value="HIGH">High</option>
                        <option value="URGENT">Urgent</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Target Due Date</label>
                      <input
                        type="date"
                        value={reassignDueDate}
                        onChange={(e) => setReassignDueDate(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-blue-500 outline-hidden"
                      />
                    </div>
                  </div>

                  <div className="pt-2 flex justify-end gap-3">
                    <button
                      type="button"
                      onClick={() => setActiveTab('overview')}
                      className="px-4 py-2 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isReassigning}
                      className="px-5 py-2 text-xs font-bold rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-md disabled:opacity-50"
                    >
                      {isReassigning ? 'Reassigning...' : 'Confirm Reassignment'}
                    </button>
                  </div>
                </form>
              )}
            </>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-200/80 dark:border-slate-800 flex justify-between items-center bg-slate-50/50 dark:bg-slate-900/50 text-xs">
          <span className="text-slate-400">
            Last Updated: {taskDetail ? new Date(taskDetail.updated_at).toLocaleString() : '—'}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-200 hover:bg-slate-300 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

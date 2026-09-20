import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Edit2,
  Building2,
  Briefcase,
  Calendar,
  Mail,
  Phone,
  Clock,
  ShieldAlert,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getEmployeeByIdApi, updateEmployeeStatusApi } from '../api/employees';
import type { Employee, AccountStatus } from '../types/employee';
import { StatusBadge } from '../components/common/StatusBadge';
import { ConfirmationModal } from '../components/common/ConfirmationModal';
import { Button } from '../components/ui/button';
import { ToastContainer, type ToastMessage } from '../components/ui/toast';
import { extractErrorMessage } from '../api/client';

export const EmployeeDetailPage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const { hasPermission } = useAuth();

  // Toast state
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

  // Permissions
  const canEdit = hasPermission('ADMIN_EMPLOYEES', 'edit');
  const canApprove = hasPermission('ADMIN_EMPLOYEES', 'approve');

  // Employee data state
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isNotFound, setIsNotFound] = useState<boolean>(false);
  const [isForbidden, setIsForbidden] = useState<boolean>(false);

  // Status Dialog state
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [targetStatus, setTargetStatus] = useState<AccountStatus>('ACTIVE');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  // Fetch employee details
  const fetchEmployee = async () => {
    if (!userId) return;
    setIsLoading(true);
    setErrorMessage(null);
    setIsNotFound(false);
    setIsForbidden(false);

    try {
      const data = await getEmployeeByIdApi(userId);
      setEmployee(data);
      setTargetStatus(data.account_status);
    } catch (err: any) {
      const status = err?.response?.status;
      if (status === 404) {
        setIsNotFound(true);
      } else if (status === 403) {
        setIsForbidden(true);
      } else {
        setErrorMessage(extractErrorMessage(err));
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployee();
  }, [userId]);

  // Handle status update
  const handleConfirmStatusUpdate = async () => {
    if (!employee) return;
    setIsUpdatingStatus(true);
    try {
      const updated = await updateEmployeeStatusApi(employee.user_id, {
        account_status: targetStatus,
      });
      setEmployee(updated);
      addToast(
        'success',
        'Status Updated',
        `Employee status changed to ${targetStatus}`
      );
      setStatusModalOpen(false);
    } catch (err) {
      addToast('error', 'Update Failed', extractErrorMessage(err));
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[300px] w-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
            Loading employee profile...
          </span>
        </div>
      </div>
    );
  }

  if (isNotFound) {
    return (
      <div className="min-h-[300px] w-full flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-slate-900 rounded-3xl p-8 border border-slate-200 dark:border-slate-800 shadow-xl text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-rose-500 mx-auto" />
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            Employee Record Not Found
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            The requested employee identifier does not exist in the CRM directory.
          </p>
          <div className="pt-2">
            <Link to="/admin/employees">
              <Button variant="primary" className="w-full">
                Back to Employee Directory
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (isForbidden) {
    return (
      <div className="min-h-[300px] w-full flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-slate-900 rounded-3xl p-8 border border-slate-200 dark:border-slate-800 shadow-xl text-center space-y-4">
          <ShieldAlert className="w-12 h-12 text-amber-500 mx-auto" />
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            Out of Scope Access
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            This employee profile is outside your assigned data scope (SELF, TEAM, DEPARTMENT, or COMPANY).
          </p>
          <div className="pt-2">
            <Link to="/admin/employees">
              <Button variant="primary" className="w-full">
                Back to Employee Directory
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="min-h-[300px] w-full flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-slate-900 rounded-3xl p-8 border border-slate-200 dark:border-slate-800 shadow-xl text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-rose-500 mx-auto" />
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            Failed to Load Profile
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {errorMessage}
          </p>
          <div className="pt-2">
            <Link to="/admin/employees">
              <Button variant="primary" className="w-full">
                Back to Employee Directory
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!employee) return null;

  return (
    <div className="max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
      {/* Top Profile Summary Card */}
      <div className="p-6 sm:p-8 rounded-3xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="flex items-center gap-4 sm:gap-6">
            <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-3xl bg-gradient-to-br from-blue-600 to-indigo-700 text-white flex items-center justify-center font-extrabold text-2xl sm:text-3xl shadow-lg shrink-0">
              {employee.first_name.charAt(0)}
            </div>

            <div className="space-y-1 text-left">
              <div className="flex flex-wrap items-center gap-2.5">
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-[#0a2569] dark:text-white tracking-tight">
                  {[employee.first_name, employee.middle_name, employee.last_name].filter(Boolean).join(' ')}
                </h1>
                <StatusBadge status={employee.account_status} size="sm" />
              </div>

              <div className="flex flex-wrap items-center gap-3 text-xs sm:text-sm text-slate-500 dark:text-slate-400 font-medium">
                <span className="font-mono font-bold text-blue-600 dark:text-blue-400">
                  {employee.employee_code}
                </span>
                <span>•</span>
                <span>{employee.designation_name || 'Staff'}</span>
                <span>•</span>
                <span>{employee.company_name}</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 w-full sm:w-auto">
            {canApprove && (
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setTargetStatus(employee.account_status);
                  setStatusModalOpen(true);
                }}
                className="text-xs font-semibold"
              >
                Change Status
              </Button>
            )}

            {canEdit && (
              <Link to={`/admin/employees/${employee.user_id}/edit`}>
                <Button variant="primary" className="flex items-center gap-2 text-xs font-semibold">
                  <Edit2 className="w-3.5 h-3.5" />
                  <span>Edit Profile</span>
                </Button>
              </Link>
            )}
          </div>
        </div>

        {/* Detailed Information Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Card 1: Organizational Affiliation */}
          <div className="p-6 rounded-3xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-800 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              <Building2 className="w-4 h-4 text-blue-600" />
              <span>Organizational Structure</span>
            </div>

            <dl className="grid grid-cols-1 gap-3 text-xs sm:text-sm">
              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Company</dt>
                <dd className="font-semibold text-slate-900 dark:text-white mt-0.5">
                  {employee.company_name} ({employee.company_code})
                </dd>
              </div>

              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Department</dt>
                <dd className="font-semibold text-slate-900 dark:text-white mt-0.5">
                  {employee.department_name} ({employee.department_code})
                </dd>
              </div>

              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Designation & Rank</dt>
                <dd className="font-semibold text-slate-900 dark:text-white mt-0.5">
                  {employee.designation_name} ({employee.designation_code})
                </dd>
              </div>

              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Reporting Manager</dt>
                <dd className="font-semibold text-slate-900 dark:text-white mt-0.5">
                  {employee.manager_name ? (
                    <span>
                      {employee.manager_name} ({employee.manager_employee_code})
                    </span>
                  ) : (
                    <span className="text-slate-400 italic">No Direct Manager (Top Hierarchy)</span>
                  )}
                </dd>
              </div>
            </dl>
          </div>

          {/* Card 2: Contact Information */}
          <div className="p-6 rounded-3xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-800 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              <Mail className="w-4 h-4 text-blue-600" />
              <span>Contact & Communication</span>
            </div>

            <dl className="grid grid-cols-1 gap-3 text-xs sm:text-sm">
              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Official Work Email</dt>
                <dd className="font-semibold text-slate-900 dark:text-white mt-0.5 flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <a href={`mailto:${employee.official_email}`} className="hover:underline">
                    {employee.official_email}
                  </a>
                </dd>
              </div>

              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Personal Email</dt>
                <dd className="font-medium text-slate-700 dark:text-slate-300 mt-0.5">
                  {employee.personal_email || '—'}
                </dd>
              </div>

              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Primary Mobile Number</dt>
                <dd className="font-semibold text-slate-900 dark:text-white mt-0.5 flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <a href={`tel:${employee.mobile_number}`} className="hover:underline">
                    {employee.mobile_number}
                  </a>
                </dd>
              </div>
            </dl>
          </div>

          {/* Card 3: Employment Terms */}
          <div className="p-6 rounded-3xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-800 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              <Briefcase className="w-4 h-4 text-blue-600" />
              <span>Employment Terms</span>
            </div>

            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs sm:text-sm">
              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Date of Joining</dt>
                <dd className="font-semibold text-slate-900 dark:text-white mt-0.5 flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-slate-400" />
                  <span>{employee.date_of_joining}</span>
                </dd>
              </div>

              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Employment Type</dt>
                <dd className="font-semibold text-slate-900 dark:text-white mt-0.5">
                  {employee.employment_type}
                </dd>
              </div>
            </dl>
          </div>

          {/* Card 4: Audit & System Metadata */}
          <div className="p-6 rounded-3xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-800 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              <Clock className="w-4 h-4 text-blue-600" />
              <span>System Record Metadata</span>
            </div>

            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs sm:text-sm">
              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Record Created</dt>
                <dd className="font-medium text-slate-700 dark:text-slate-300 mt-0.5">
                  {new Date(employee.created_at).toLocaleString()}
                </dd>
              </div>

              <div>
                <dt className="text-slate-400 font-medium text-[11px]">Last Updated</dt>
                <dd className="font-medium text-slate-700 dark:text-slate-300 mt-0.5">
                  {new Date(employee.updated_at).toLocaleString()}
                </dd>
              </div>
            </dl>
          </div>
        </div>

      {/* Status Modal */}
      <ConfirmationModal
        isOpen={statusModalOpen}
        onClose={() => setStatusModalOpen(false)}
        onConfirm={handleConfirmStatusUpdate}
        title="Change Employee Operational Status"
        confirmText="Save Status"
        isLoading={isUpdatingStatus}
      >
        <div className="space-y-4 text-left">
          <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300 space-y-1">
            <div>
              <strong>Employee:</strong> {employee.first_name} {employee.last_name} ({employee.employee_code})
            </div>
            <div>
              <strong>Current Status:</strong>{' '}
              <StatusBadge status={employee.account_status} size="sm" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
              Select Target Status:
            </label>
            <select
              value={targetStatus}
              onChange={(e) => setTargetStatus(e.target.value as AccountStatus)}
              className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            >
              <option value="ACTIVE">ACTIVE</option>
              <option value="PENDING">PENDING</option>
              <option value="INACTIVE">INACTIVE</option>
              <option value="SUSPENDED">SUSPENDED</option>
            </select>
          </div>
        </div>
      </ConfirmationModal>

      {/* Toasts */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

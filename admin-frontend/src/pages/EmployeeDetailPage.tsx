import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  User,
  Building2,
  Clock,
  ArrowLeft,
  Edit2,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getEmployeeByIdApi, updateEmployeeStatusApi } from '../api/employees';
import { Employee, AccountStatus } from '../types/employee';
import { StatusBadge } from '../components/common/StatusBadge';
import { ConfirmationModal } from '../components/common/ConfirmationModal';
import { extractErrorMessage } from '../api/client';

export const EmployeeDetailPage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const { hasPermission } = useAuth();

  const canEdit = hasPermission('ADMIN_EMPLOYEES', 'edit');
  const canApprove = hasPermission('ADMIN_EMPLOYEES', 'approve');

  const [employee, setEmployee] = useState<Employee | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [errorCode, setErrorCode] = useState<number | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Status Modal
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [targetStatus, setTargetStatus] = useState<AccountStatus>('ACTIVE');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  const fetchEmployee = useCallback(async () => {
    if (!userId) return;
    setIsLoading(true);
    setErrorMessage(null);
    setErrorCode(null);
    try {
      const data = await getEmployeeByIdApi(userId);
      setEmployee(data);
      setTargetStatus(data.account_status);
    } catch (err: unknown) {
      setErrorMessage(extractErrorMessage(err));
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const axErr = err as { response?: { status?: number } };
        if (axErr.response?.status) {
          setErrorCode(axErr.response.status);
        }
      }
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchEmployee();
  }, [fetchEmployee]);

  const handleConfirmStatusUpdate = async () => {
    if (!employee) return;
    setIsUpdatingStatus(true);
    setErrorMessage(null);
    try {
      const updated = await updateEmployeeStatusApi(employee.user_id, {
        account_status: targetStatus,
      });
      setEmployee(updated);
      setSuccessMessage(`Account status updated to ${targetStatus} successfully.`);
      setStatusModalOpen(false);
    } catch (err) {
      setErrorMessage(extractErrorMessage(err));
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  if (isLoading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-3">
        <RefreshCw className="w-8 h-8 text-brand-600 animate-spin" />
        <p className="text-sm font-medium text-slate-600">Loading employee profile...</p>
      </div>
    );
  }

  if (errorMessage && !employee) {
    return (
      <div className="max-w-xl mx-auto py-12 px-4 animate-fade-in">
        <div className="p-6 bg-white rounded-2xl border border-rose-200 shadow-card-soft text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">
            {errorCode === 404
              ? 'Employee Record Not Found'
              : errorCode === 403
              ? 'Access Forbidden'
              : 'Error Loading Employee'}
          </h2>
          <p className="text-sm text-slate-600">{errorMessage}</p>
          <div className="pt-2">
            <Link
              to="/employees"
              className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded-lg hover:bg-slate-800 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Employee List</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!employee) return null;

  const fullName = `${employee.first_name} ${
    employee.middle_name ? `${employee.middle_name} ` : ''
  }${employee.last_name}`;

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl mx-auto">
      {/* Navigation & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/employees')}
            className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100 transition-colors"
            title="Back to List"
            aria-label="Back to List"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                {fullName}
              </h1>
              <span className="px-2.5 py-0.5 rounded font-mono font-bold text-xs bg-brand-50 text-brand-700 border border-brand-200">
                {employee.employee_code}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5 font-mono">
              User ID: {employee.user_id}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {canApprove && (
            <button
              onClick={() => {
                setTargetStatus(employee.account_status);
                setStatusModalOpen(true);
              }}
              className="px-3.5 py-2 text-xs font-bold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-100 transition-colors"
            >
              Change Status
            </button>
          )}

          {canEdit && (
            <Link
              to={`/employees/${employee.user_id}/edit`}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs shadow-button-glow transition-all"
            >
              <Edit2 className="w-3.5 h-3.5" />
              <span>Edit Profile</span>
            </Link>
          )}
        </div>
      </div>

      {/* Success / Error Alerts */}
      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center justify-between animate-fade-in">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <span className="font-medium">{successMessage}</span>
          </div>
          <button
            onClick={() => setSuccessMessage(null)}
            className="text-emerald-700 hover:text-emerald-900 text-xs font-bold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Profile Overview Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card-soft overflow-hidden">
        {/* Banner Header */}
        <div className="bg-gradient-to-r from-slate-900 to-brand-950 p-6 text-white flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-cyan-400 flex items-center justify-center text-white font-extrabold text-2xl shadow-brand-glow">
              {employee.first_name[0]}
              {employee.last_name[0]}
            </div>
            <div>
              <h2 className="text-xl font-bold">{fullName}</h2>
              <p className="text-xs text-brand-200 font-mono mt-0.5">
                {employee.official_email}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:self-start">
            <StatusBadge status={employee.account_status} />
            <StatusBadge status={employee.employment_type} />
          </div>
        </div>

        {/* Detailed Info Grid */}
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8 divide-y md:divide-y-0 md:divide-x divide-slate-100">
          {/* Organizational Info */}
          <div className="space-y-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-brand-600" />
              <span>Organizational Placement</span>
            </h3>

            <div className="space-y-4 text-sm">
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Company:</span>
                <span className="font-semibold text-slate-800">
                  {employee.company_name} ({employee.company_code})
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Department:</span>
                <span className="font-semibold text-slate-800">
                  {employee.department_name} ({employee.department_code})
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Designation:</span>
                <span className="font-semibold text-slate-800">
                  {employee.designation_name} ({employee.designation_code})
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Reporting Manager:</span>
                <span className="font-semibold text-slate-800">
                  {employee.manager_name ? (
                    <span>
                      {employee.manager_name} (
                      <span className="font-mono text-xs text-slate-500">
                        {employee.manager_employee_code}
                      </span>
                      )
                    </span>
                  ) : (
                    <span className="text-slate-400 italic font-normal">None Assigned</span>
                  )}
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Date of Joining:</span>
                <span className="font-semibold font-mono text-slate-800">
                  {employee.date_of_joining}
                </span>
              </div>
            </div>
          </div>

          {/* Contact & Personal Info */}
          <div className="space-y-5 md:pl-8 pt-6 md:pt-0">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <User className="w-4 h-4 text-brand-600" />
              <span>Contact & Personal Details</span>
            </h3>

            <div className="space-y-4 text-sm">
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Official Email:</span>
                <span className="font-semibold font-mono text-slate-800">
                  {employee.official_email}
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Personal Email:</span>
                <span className="font-medium font-mono text-slate-800">
                  {employee.personal_email || <span className="text-slate-400 italic">Not Provided</span>}
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Mobile Number:</span>
                <span className="font-semibold font-mono text-slate-800">
                  {employee.mobile_number}
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Employment Type:</span>
                <span className="font-semibold text-slate-800">
                  {employee.employment_type.replace(/_/g, ' ')}
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Operational Status:</span>
                <span className="font-semibold text-slate-800">
                  {employee.account_status}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Audit Footer */}
        <div className="bg-slate-50 px-6 py-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center sm:justify-between text-xs text-slate-500 gap-2">
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>Created At: {new Date(employee.created_at).toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>Last Updated: {new Date(employee.updated_at).toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Status Modal */}
      {statusModalOpen && (
        <ConfirmationModal
          isOpen={statusModalOpen}
          title="Update Account Status"
          message={
            <div className="space-y-4">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1">
                <div className="text-slate-500">Target Employee:</div>
                <div className="font-bold text-slate-900 text-sm">
                  {fullName} ({employee.employee_code})
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Current Status:
                </label>
                <div className="mb-3">
                  <StatusBadge status={employee.account_status} />
                </div>

                <label
                  htmlFor="target-status-detail"
                  className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
                >
                  New Target Status <span className="text-rose-500">*</span>
                </label>
                <select
                  id="target-status-detail"
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

import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Save,
  ArrowLeft,
  Building2,
  Briefcase,
  UserCheck,
  Calendar,
  Mail,
  Phone,
  Info,
  AlertCircle,
} from 'lucide-react';
import {
  createEmployeeApi,
  getEmployeeByIdApi,
  updateEmployeeApi,
} from '../api/employees';
import {
  getLookupCompaniesApi,
  getLookupDepartmentsApi,
  getLookupDesignationsApi,
  getLookupManagersApi,
} from '../api/lookup';
import type {
  CompanyLookup,
  DepartmentLookup,
  DesignationLookup,
  ManagerLookup,
} from '../types/lookup';
import { Button } from '../components/ui/button';
import { ToastContainer, type ToastMessage } from '../components/ui/toast';
import { extractErrorMessage } from '../api/client';

const employeeFormSchema = z.object({
  first_name: z.string().trim().min(1, 'First name is required').max(50),
  middle_name: z.string().trim().max(50).optional().nullable(),
  last_name: z.string().trim().min(1, 'Last name is required').max(50),
  official_email: z.string().trim().email('Enter a valid official email address').max(100),
  personal_email: z
    .string()
    .trim()
    .email('Enter a valid personal email address')
    .max(100)
    .optional()
    .nullable()
    .or(z.literal('')),
  mobile_number: z
    .string()
    .trim()
    .regex(/^(\+91)?[6-9]\d{9}$/, 'Enter a valid 10-digit Indian mobile number (+91 optional)'),
  company_id: z.string().uuid('Please select a company'),
  department_id: z.string().uuid('Please select a department'),
  designation_id: z.string().uuid('Please select a designation'),
  manager_user_id: z.string().uuid().optional().nullable().or(z.literal('')),
  date_of_joining: z.string().min(1, 'Date of joining is required'),
  employment_type: z.enum(['FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERN', 'CONSULTANT']),
  account_status: z.enum(['ACTIVE', 'PENDING', 'INACTIVE', 'SUSPENDED']),
});

type EmployeeFormData = z.infer<typeof employeeFormSchema>;

export const EmployeeFormPage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const isEditMode = Boolean(userId);
  const navigate = useNavigate();

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

  // Lookups state
  const [companies, setCompanies] = useState<CompanyLookup[]>([]);
  const [departments, setDepartments] = useState<DepartmentLookup[]>([]);
  const [designations, setDesignations] = useState<DesignationLookup[]>([]);
  const [managers, setManagers] = useState<ManagerLookup[]>([]);

  // Loading & Error states
  const [isLoading, setIsLoading] = useState<boolean>(isEditMode);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [employeeCode, setEmployeeCode] = useState<string>('');

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<EmployeeFormData>({
    resolver: zodResolver(employeeFormSchema),
    defaultValues: {
      first_name: '',
      middle_name: '',
      last_name: '',
      official_email: '',
      personal_email: '',
      mobile_number: '',
      company_id: '',
      department_id: '',
      designation_id: '',
      manager_user_id: '',
      date_of_joining: new Date().toISOString().split('T')[0],
      employment_type: 'FULL_TIME',
      account_status: 'ACTIVE',
    },
  });

  const selectedCompanyId = watch('company_id');

  // Load Companies Lookup on mount
  useEffect(() => {
    getLookupCompaniesApi()
      .then(setCompanies)
      .catch((err) => console.error('Failed to load companies:', err));
  }, []);

  // When Company changes, update dependent lookups
  useEffect(() => {
    if (selectedCompanyId) {
      getLookupDepartmentsApi(selectedCompanyId)
        .then(setDepartments)
        .catch((err) => console.error('Failed to load departments:', err));

      getLookupDesignationsApi(selectedCompanyId)
        .then(setDesignations)
        .catch((err) => console.error('Failed to load designations:', err));

      getLookupManagersApi(selectedCompanyId, userId)
        .then(setManagers)
        .catch((err) => console.error('Failed to load managers:', err));
    } else {
      setDepartments([]);
      setDesignations([]);
      setManagers([]);
    }
  }, [selectedCompanyId, userId]);

  // Load existing employee data in Edit Mode
  useEffect(() => {
    if (isEditMode && userId) {
      setIsLoading(true);
      getEmployeeByIdApi(userId)
        .then((emp) => {
          setEmployeeCode(emp.employee_code);
          reset({
            first_name: emp.first_name,
            middle_name: emp.middle_name || '',
            last_name: emp.last_name,
            official_email: emp.official_email,
            personal_email: emp.personal_email || '',
            mobile_number: emp.mobile_number,
            company_id: emp.company_id,
            department_id: emp.department_id,
            designation_id: emp.designation_id,
            manager_user_id: emp.manager_user_id || '',
            date_of_joining: emp.date_of_joining,
            employment_type: emp.employment_type,
            account_status: emp.account_status,
          });
        })
        .catch((err) => {
          const msg = extractErrorMessage(err);
          setErrorMessage(msg);
          addToast('error', 'Error Loading Employee', msg);
        })
        .finally(() => setIsLoading(false));
    }
  }, [isEditMode, userId, reset]);

  // Submit Handler
  const onSubmit = async (data: EmployeeFormData) => {
    setIsSubmitting(true);
    setErrorMessage(null);

    const payload = {
      ...data,
      middle_name: data.middle_name?.trim() || null,
      personal_email: data.personal_email?.trim() || null,
      manager_user_id: data.manager_user_id?.trim() || null,
    };

    try {
      if (isEditMode && userId) {
        await updateEmployeeApi(userId, payload);
        addToast('success', 'Profile Updated', 'Employee record was successfully updated.');
        setTimeout(() => navigate(`/admin/employees/${userId}`), 600);
      } else {
        const created = await createEmployeeApi(payload);
        addToast(
          'success',
          'Employee Created',
          `Employee assigned code: ${created.employee_code}`
        );
        setTimeout(() => navigate(`/admin/employees/${created.user_id}`), 600);
      }
    } catch (err) {
      const msg = extractErrorMessage(err);
      setErrorMessage(msg);
      addToast('error', isEditMode ? 'Update Failed' : 'Creation Failed', msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[300px] w-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
            Loading employee record...
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0a2569] dark:text-white tracking-tight">
              {isEditMode ? `Edit Employee (${employeeCode})` : 'Add New Employee'}
            </h1>
          </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
              {isEditMode
                ? 'Update organizational assignments, contact information, and reporting details.'
                : 'Create an employee profile. Employee code and credentials will be generated automatically.'}
            </p>
          </div>

          <Link
            to={isEditMode && userId ? `/admin/employees/${userId}` : '/admin/employees'}
          >
            <Button variant="outline" className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              <span>Cancel</span>
            </Button>
          </Link>
        </div>

        {/* Global Error Banner */}
        {errorMessage && (
          <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300 flex items-center gap-3 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Security / Provisioning Notice */}
        {!isEditMode && (
          <div className="p-4 rounded-2xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900 text-blue-900 dark:text-blue-300 flex items-start gap-3 text-xs sm:text-sm">
            <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold block mb-0.5">Secure Credential Provisioning</span>
              <span>
                Employee codes are atomically generated on save based on company prefix. Login access is configured separately through secure account activation.
              </span>
            </div>
          </div>
        )}

        {/* Form Container */}
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="rounded-3xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 shadow-xl p-6 sm:p-8 space-y-8"
        >
          {/* Section 1: Organizational Assignment */}
          <div>
            <div className="flex items-center gap-2 pb-3 mb-4 border-b border-slate-200 dark:border-slate-800 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              <Building2 className="w-4 h-4 text-blue-600" />
              <span>1. Company & Department Assignment</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              {/* Company Selection */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Company <span className="text-rose-500">*</span>
                </label>
                <select
                  {...register('company_id')}
                  onChange={(e) => {
                    setValue('company_id', e.target.value);
                    setValue('department_id', '');
                    setValue('designation_id', '');
                    setValue('manager_user_id', '');
                  }}
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Company</option>
                  {companies.map((c) => (
                    <option key={c.company_id} value={c.company_id}>
                      {c.company_name} ({c.employee_code_prefix})
                    </option>
                  ))}
                </select>
                {errors.company_id && (
                  <p className="text-xs text-rose-600 mt-1">{errors.company_id.message}</p>
                )}
              </div>

              {/* Department Selection */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Department <span className="text-rose-500">*</span>
                </label>
                <select
                  {...register('department_id')}
                  disabled={!selectedCompanyId}
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <option value="">
                    {selectedCompanyId ? 'Select Department' : 'Select Company First'}
                  </option>
                  {departments.map((d) => (
                    <option key={d.department_id} value={d.department_id}>
                      {d.department_name} ({d.department_code})
                    </option>
                  ))}
                </select>
                {errors.department_id && (
                  <p className="text-xs text-rose-600 mt-1">{errors.department_id.message}</p>
                )}
              </div>

              {/* Designation Selection */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Designation <span className="text-rose-500">*</span>
                </label>
                <select
                  {...register('designation_id')}
                  disabled={!selectedCompanyId}
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <option value="">
                    {selectedCompanyId ? 'Select Designation' : 'Select Company First'}
                  </option>
                  {designations.map((desig) => (
                    <option key={desig.designation_id} value={desig.designation_id}>
                      {desig.designation_name} ({desig.designation_code})
                    </option>
                  ))}
                </select>
                {errors.designation_id && (
                  <p className="text-xs text-rose-600 mt-1">{errors.designation_id.message}</p>
                )}
              </div>

              {/* Direct Reporting Manager Selection */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Reporting Manager <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <select
                  {...register('manager_user_id')}
                  disabled={!selectedCompanyId}
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <option value="">No Direct Manager (Top Level / Self)</option>
                  {managers.map((m) => (
                    <option key={m.user_id} value={m.user_id}>
                      {m.first_name} {m.last_name} ({m.employee_code}) - {m.designation_name || 'Staff'}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Section 2: Personal Profile */}
          <div>
            <div className="flex items-center gap-2 pb-3 mb-4 border-b border-slate-200 dark:border-slate-800 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              <UserCheck className="w-4 h-4 text-blue-600" />
              <span>2. Personal & Contact Details</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* First Name */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  First Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  {...register('first_name')}
                  placeholder="e.g. Rohan"
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                />
                {errors.first_name && (
                  <p className="text-xs text-rose-600 mt-1">{errors.first_name.message}</p>
                )}
              </div>

              {/* Middle Name */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Middle Name <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <input
                  type="text"
                  {...register('middle_name')}
                  placeholder="e.g. Kumar"
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Last Name */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Last Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  {...register('last_name')}
                  placeholder="e.g. Verma"
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                />
                {errors.last_name && (
                  <p className="text-xs text-rose-600 mt-1">{errors.last_name.message}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
              {/* Official Email */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Official Email <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="email"
                    {...register('official_email')}
                    placeholder="name@gocompliances.in"
                    className="w-full pl-9 pr-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                {errors.official_email && (
                  <p className="text-xs text-rose-600 mt-1">{errors.official_email.message}</p>
                )}
              </div>

              {/* Personal Email */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Personal Email <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="email"
                    {...register('personal_email')}
                    placeholder="name@example.com"
                    className="w-full pl-9 pr-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                {errors.personal_email && (
                  <p className="text-xs text-rose-600 mt-1">{errors.personal_email.message}</p>
                )}
              </div>

              {/* Mobile Number */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Mobile Number <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <Phone className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="tel"
                    {...register('mobile_number')}
                    placeholder="+919876543210"
                    className="w-full pl-9 pr-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                {errors.mobile_number && (
                  <p className="text-xs text-rose-600 mt-1">{errors.mobile_number.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Section 3: Employment Terms & Status */}
          <div>
            <div className="flex items-center gap-2 pb-3 mb-4 border-b border-slate-200 dark:border-slate-800 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              <Briefcase className="w-4 h-4 text-blue-600" />
              <span>3. Employment Terms & Status</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Date of Joining */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Date of Joining <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <Calendar className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="date"
                    {...register('date_of_joining')}
                    className="w-full pl-9 pr-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                {errors.date_of_joining && (
                  <p className="text-xs text-rose-600 mt-1">{errors.date_of_joining.message}</p>
                )}
              </div>

              {/* Employment Type */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Employment Type <span className="text-rose-500">*</span>
                </label>
                <select
                  {...register('employment_type')}
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                >
                  <option value="FULL_TIME">Full Time</option>
                  <option value="PART_TIME">Part Time</option>
                  <option value="CONTRACT">Contract</option>
                  <option value="INTERN">Intern</option>
                  <option value="CONSULTANT">Consultant</option>
                </select>
              </div>

              {/* Account Status */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Account Status <span className="text-rose-500">*</span>
                </label>
                <select
                  {...register('account_status')}
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="PENDING">PENDING</option>
                  <option value="INACTIVE">INACTIVE</option>
                  <option value="SUSPENDED">SUSPENDED</option>
                </select>
              </div>
            </div>
          </div>

          {/* Form Action Buttons */}
          <div className="flex items-center justify-end gap-3 pt-6 border-t border-slate-200 dark:border-slate-800">
            <Link to="/admin/employees">
              <Button type="button" variant="outline" disabled={isSubmitting}>
                Cancel
              </Button>
            </Link>

            <Button
              type="submit"
              variant="primary"
              isLoading={isSubmitting}
              className="flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              <span>{isEditMode ? 'Save Changes' : 'Create Employee'}</span>
            </Button>
          </div>
        </form>

      {/* Toasts */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

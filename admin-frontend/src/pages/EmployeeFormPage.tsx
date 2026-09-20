import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  ArrowLeft,
  Save,
  Building2,
  User,
  AlertCircle,
  RefreshCw,
  Info,
  ShieldCheck,
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
import {
  CompanyLookup,
  DepartmentLookup,
  DesignationLookup,
  ManagerLookup,
} from '../types/lookup';
import { extractErrorMessage } from '../api/client';

const mobileRegex = /^(\+91[\-\s]?)?[6-9]\d{9}$/;

const employeeFormSchema = z.object({
  first_name: z.string().trim().min(1, 'First name is required').max(100),
  middle_name: z.string().trim().max(100).optional().or(z.literal('')),
  last_name: z.string().trim().min(1, 'Last name is required').max(100),
  official_email: z
    .string()
    .trim()
    .email('Please enter a valid official email address')
    .max(255),
  personal_email: z
    .string()
    .trim()
    .email('Please enter a valid email address')
    .optional()
    .or(z.literal('')),
  mobile_number: z
    .string()
    .trim()
    .regex(mobileRegex, 'Enter a valid 10-digit Indian mobile number (+91 or 10 digits)'),
  company_id: z.string().uuid('Please select a company'),
  department_id: z.string().uuid('Please select a department'),
  designation_id: z.string().uuid('Please select a designation'),
  manager_user_id: z.string().uuid().optional().or(z.literal('')),
  date_of_joining: z.string().min(1, 'Date of joining is required'),
  employment_type: z.enum([
    'FULL_TIME',
    'PART_TIME',
    'CONTRACT',
    'INTERN',
    'CONSULTANT',
  ]),
  account_status: z.enum(['PENDING', 'ACTIVE', 'INACTIVE', 'SUSPENDED']),
});

type EmployeeFormData = z.infer<typeof employeeFormSchema>;

export const EmployeeFormPage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const isEditMode = Boolean(userId);
  const navigate = useNavigate();

  const [isLoadingEmployee, setIsLoadingEmployee] = useState<boolean>(isEditMode);
  const [employeeCode, setEmployeeCode] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  // Lookup datasets
  const [companies, setCompanies] = useState<CompanyLookup[]>([]);
  const [departments, setDepartments] = useState<DepartmentLookup[]>([]);
  const [designations, setDesignations] = useState<DesignationLookup[]>([]);
  const [managers, setManagers] = useState<ManagerLookup[]>([]);

  // Track initial load for edit mode to avoid clearing values prematurely
  const isInitialLoad = useRef(true);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
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
      account_status: 'PENDING',
    },
  });

  const selectedCompanyId = watch('company_id');

  // Load Companies lookup
  useEffect(() => {
    getLookupCompaniesApi()
      .then(setCompanies)
      .catch((err) => console.error('Failed to load companies lookup:', err));
  }, []);

  // Cascading dependent lookups on company selection
  const loadDependentLookups = useCallback(
    async (companyId: string) => {
      if (!companyId) {
        setDepartments([]);
        setDesignations([]);
        setManagers([]);
        return;
      }
      try {
        const [depts, desigs, mgrs] = await Promise.all([
          getLookupDepartmentsApi(companyId),
          getLookupDesignationsApi(companyId),
          getLookupManagersApi(companyId, isEditMode ? userId : undefined),
        ]);
        setDepartments(depts);
        setDesignations(desigs);
        setManagers(mgrs);
      } catch (err) {
        console.error('Failed to load dependent lookups:', err);
      }
    },
    [isEditMode, userId]
  );

  // When company ID changes in form
  useEffect(() => {
    if (selectedCompanyId) {
      loadDependentLookups(selectedCompanyId);

      // Only reset children if not during initial edit populate
      if (!isInitialLoad.current) {
        setValue('department_id', '');
        setValue('designation_id', '');
        setValue('manager_user_id', '');
      }
    } else {
      setDepartments([]);
      setDesignations([]);
      setManagers([]);
    }
  }, [selectedCompanyId, loadDependentLookups, setValue]);

  // Pre-populate when in Edit mode
  useEffect(() => {
    if (isEditMode && userId) {
      setIsLoadingEmployee(true);
      getEmployeeByIdApi(userId)
        .then(async (emp) => {
          setEmployeeCode(emp.employee_code);
          await loadDependentLookups(emp.company_id);
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
          isInitialLoad.current = false;
        })
        .catch((err) => {
          setApiError(extractErrorMessage(err));
        })
        .finally(() => {
          setIsLoadingEmployee(false);
        });
    } else {
      isInitialLoad.current = false;
    }
  }, [isEditMode, userId, reset, loadDependentLookups]);

  const onSubmit = async (formData: EmployeeFormData) => {
    setApiError(null);
    try {
      const payload = {
        ...formData,
        middle_name: formData.middle_name?.trim() || null,
        personal_email: formData.personal_email?.trim() || null,
        manager_user_id: formData.manager_user_id?.trim() || null,
      };

      if (isEditMode && userId) {
        const updated = await updateEmployeeApi(userId, payload);
        navigate(`/employees/${updated.user_id}`);
      } else {
        const created = await createEmployeeApi(payload);
        navigate(`/employees/${created.user_id}`);
      }
    } catch (err) {
      setApiError(extractErrorMessage(err));
    }
  };

  if (isLoadingEmployee) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-3">
        <RefreshCw className="w-8 h-8 text-brand-600 animate-spin" />
        <p className="text-sm font-medium text-slate-600">
          Loading employee details...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fade-in pb-12">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => navigate(isEditMode ? `/employees/${userId}` : '/employees')}
            className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100 transition-colors"
            title="Back"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              {isEditMode ? 'Edit Employee Profile' : 'Add New Employee'}
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              {isEditMode
                ? `Updating profile details for ${employeeCode}`
                : 'Create an employee with automatic employee-code generation'}
            </p>
          </div>
        </div>

        {isEditMode && employeeCode && (
          <div className="px-3 py-1.5 rounded-lg bg-brand-50 border border-brand-200 font-mono text-xs font-bold text-brand-700">
            Code: {employeeCode} (Read-Only)
          </div>
        )}
      </div>

      {/* Error Alert */}
      {apiError && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3 animate-fade-in shadow-xs">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Failed to save employee profile</p>
            <p className="text-xs text-rose-700 mt-0.5">{apiError}</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>
        {/* Section 1: Organizational Hierarchy & Placement */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 sm:p-6 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100 text-sm font-bold text-slate-800 uppercase tracking-wider">
            <Building2 className="w-4 h-4 text-brand-600" />
            <span>1. Organization & Hierarchy Placement</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Company Selection */}
            <div>
              <label
                htmlFor="company_id"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Company <span className="text-rose-500">*</span>
              </label>
              <select
                id="company_id"
                {...register('company_id')}
                className={`w-full p-2.5 text-sm bg-slate-50 border rounded-lg focus:outline-none focus:ring-2 focus:bg-white transition-all ${
                  errors.company_id
                    ? 'border-rose-400 focus:ring-rose-200'
                    : 'border-slate-300 focus:ring-brand-500'
                }`}
              >
                <option value="">Select Company...</option>
                {companies.map((c) => (
                  <option key={c.company_id} value={c.company_id}>
                    {c.company_name} ({c.company_code} - {c.employee_code_prefix})
                  </option>
                ))}
              </select>
              {errors.company_id && (
                <p className="text-xs text-rose-600 font-medium mt-1">
                  {errors.company_id.message}
                </p>
              )}
            </div>

            {/* Department Selection */}
            <div>
              <label
                htmlFor="department_id"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Department <span className="text-rose-500">*</span>
              </label>
              <select
                id="department_id"
                disabled={!selectedCompanyId || departments.length === 0}
                {...register('department_id')}
                className={`w-full p-2.5 text-sm bg-slate-50 border rounded-lg focus:outline-none focus:ring-2 focus:bg-white transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                  errors.department_id
                    ? 'border-rose-400 focus:ring-rose-200'
                    : 'border-slate-300 focus:ring-brand-500'
                }`}
              >
                <option value="">
                  {!selectedCompanyId
                    ? 'Select Company first...'
                    : departments.length === 0
                    ? 'No departments found'
                    : 'Select Department...'}
                </option>
                {departments.map((d) => (
                  <option key={d.department_id} value={d.department_id}>
                    {d.department_name} ({d.department_code})
                  </option>
                ))}
              </select>
              {errors.department_id && (
                <p className="text-xs text-rose-600 font-medium mt-1">
                  {errors.department_id.message}
                </p>
              )}
            </div>

            {/* Designation Selection */}
            <div>
              <label
                htmlFor="designation_id"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Designation <span className="text-rose-500">*</span>
              </label>
              <select
                id="designation_id"
                disabled={!selectedCompanyId || designations.length === 0}
                {...register('designation_id')}
                className={`w-full p-2.5 text-sm bg-slate-50 border rounded-lg focus:outline-none focus:ring-2 focus:bg-white transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                  errors.designation_id
                    ? 'border-rose-400 focus:ring-rose-200'
                    : 'border-slate-300 focus:ring-brand-500'
                }`}
              >
                <option value="">
                  {!selectedCompanyId
                    ? 'Select Company first...'
                    : designations.length === 0
                    ? 'No designations found'
                    : 'Select Designation...'}
                </option>
                {designations.map((d) => (
                  <option key={d.designation_id} value={d.designation_id}>
                    {d.designation_name} (Rank: {d.level_rank}
                    {d.is_managerial ? ' - Managerial' : ''})
                  </option>
                ))}
              </select>
              {errors.designation_id && (
                <p className="text-xs text-rose-600 font-medium mt-1">
                  {errors.designation_id.message}
                </p>
              )}
            </div>

            {/* Reporting Manager */}
            <div>
              <label
                htmlFor="manager_user_id"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Reporting Manager <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <select
                id="manager_user_id"
                disabled={!selectedCompanyId}
                {...register('manager_user_id')}
                className="w-full p-2.5 text-sm bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">None (Top Level / Direct Director Report)</option>
                {managers.map((m) => (
                  <option key={m.user_id} value={m.user_id}>
                    {m.first_name} {m.last_name} ({m.employee_code}
                    {m.designation_name ? ` - ${m.designation_name}` : ''})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Section 2: Personal Identity & Name */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 sm:p-6 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100 text-sm font-bold text-slate-800 uppercase tracking-wider">
            <User className="w-4 h-4 text-brand-600" />
            <span>2. Personal Information</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* First Name */}
            <div>
              <label
                htmlFor="first_name"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                First Name <span className="text-rose-500">*</span>
              </label>
              <input
                id="first_name"
                type="text"
                placeholder="e.g. Rahul"
                {...register('first_name')}
                className={`w-full p-2.5 text-sm bg-slate-50 border rounded-lg focus:outline-none focus:ring-2 focus:bg-white transition-all ${
                  errors.first_name
                    ? 'border-rose-400 focus:ring-rose-200'
                    : 'border-slate-300 focus:ring-brand-500'
                }`}
              />
              {errors.first_name && (
                <p className="text-xs text-rose-600 font-medium mt-1">
                  {errors.first_name.message}
                </p>
              )}
            </div>

            {/* Middle Name */}
            <div>
              <label
                htmlFor="middle_name"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Middle Name <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <input
                id="middle_name"
                type="text"
                placeholder="e.g. Kumar"
                {...register('middle_name')}
                className="w-full p-2.5 text-sm bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-all"
              />
            </div>

            {/* Last Name */}
            <div>
              <label
                htmlFor="last_name"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Last Name <span className="text-rose-500">*</span>
              </label>
              <input
                id="last_name"
                type="text"
                placeholder="e.g. Sharma"
                {...register('last_name')}
                className={`w-full p-2.5 text-sm bg-slate-50 border rounded-lg focus:outline-none focus:ring-2 focus:bg-white transition-all ${
                  errors.last_name
                    ? 'border-rose-400 focus:ring-rose-200'
                    : 'border-slate-300 focus:ring-brand-500'
                }`}
              />
              {errors.last_name && (
                <p className="text-xs text-rose-600 font-medium mt-1">
                  {errors.last_name.message}
                </p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            {/* Official Email */}
            <div>
              <label
                htmlFor="official_email"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Official Email <span className="text-rose-500">*</span>
              </label>
              <input
                id="official_email"
                type="email"
                placeholder="rahul.s@gocompliances.in"
                {...register('official_email')}
                className={`w-full p-2.5 text-sm bg-slate-50 border rounded-lg focus:outline-none focus:ring-2 focus:bg-white transition-all font-mono ${
                  errors.official_email
                    ? 'border-rose-400 focus:ring-rose-200'
                    : 'border-slate-300 focus:ring-brand-500'
                }`}
              />
              {errors.official_email && (
                <p className="text-xs text-rose-600 font-medium mt-1">
                  {errors.official_email.message}
                </p>
              )}
            </div>

            {/* Personal Email */}
            <div>
              <label
                htmlFor="personal_email"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Personal Email <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <input
                id="personal_email"
                type="email"
                placeholder="rahul.personal@gmail.com"
                {...register('personal_email')}
                className={`w-full p-2.5 text-sm bg-slate-50 border rounded-lg focus:outline-none focus:ring-2 focus:bg-white transition-all font-mono ${
                  errors.personal_email
                    ? 'border-rose-400 focus:ring-rose-200'
                    : 'border-slate-300 focus:ring-brand-500'
                }`}
              />
              {errors.personal_email && (
                <p className="text-xs text-rose-600 font-medium mt-1">
                  {errors.personal_email.message}
                </p>
              )}
            </div>

            {/* Mobile Number */}
            <div>
              <label
                htmlFor="mobile_number"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Mobile Number <span className="text-rose-500">*</span>
              </label>
              <input
                id="mobile_number"
                type="text"
                placeholder="+919876543210 or 9876543210"
                {...register('mobile_number')}
                className={`w-full p-2.5 text-sm bg-slate-50 border rounded-lg focus:outline-none focus:ring-2 focus:bg-white transition-all font-mono ${
                  errors.mobile_number
                    ? 'border-rose-400 focus:ring-rose-200'
                    : 'border-slate-300 focus:ring-brand-500'
                }`}
              />
              {errors.mobile_number && (
                <p className="text-xs text-rose-600 font-medium mt-1">
                  {errors.mobile_number.message}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Section 3: Employment Terms & Status */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 sm:p-6 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100 text-sm font-bold text-slate-800 uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4 text-brand-600" />
            <span>3. Employment Terms & Status</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Date of Joining */}
            <div>
              <label
                htmlFor="date_of_joining"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Date of Joining <span className="text-rose-500">*</span>
              </label>
              <input
                id="date_of_joining"
                type="date"
                {...register('date_of_joining')}
                className={`w-full p-2.5 text-sm bg-slate-50 border rounded-lg focus:outline-none focus:ring-2 focus:bg-white transition-all ${
                  errors.date_of_joining
                    ? 'border-rose-400 focus:ring-rose-200'
                    : 'border-slate-300 focus:ring-brand-500'
                }`}
              />
              {errors.date_of_joining && (
                <p className="text-xs text-rose-600 font-medium mt-1">
                  {errors.date_of_joining.message}
                </p>
              )}
            </div>

            {/* Employment Type */}
            <div>
              <label
                htmlFor="employment_type"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Employment Type <span className="text-rose-500">*</span>
              </label>
              <select
                id="employment_type"
                {...register('employment_type')}
                className="w-full p-2.5 text-sm bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-all"
              >
                <option value="FULL_TIME">FULL TIME</option>
                <option value="PART_TIME">PART TIME</option>
                <option value="CONTRACT">CONTRACT</option>
                <option value="INTERN">INTERN</option>
                <option value="CONSULTANT">CONSULTANT</option>
              </select>
            </div>

            {/* Operational Status */}
            <div>
              <label
                htmlFor="account_status"
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1"
              >
                Account Status <span className="text-rose-500">*</span>
              </label>
              <select
                id="account_status"
                {...register('account_status')}
                className="w-full p-2.5 text-sm bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-all"
              >
                <option value="PENDING">PENDING (Awaiting activation)</option>
                <option value="ACTIVE">ACTIVE (Full access)</option>
                <option value="INACTIVE">INACTIVE (Deactivated)</option>
                <option value="SUSPENDED">SUSPENDED (Temporarily locked)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Security & Credentials Notice */}
        <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-600 flex items-start gap-3">
          <Info className="w-5 h-5 text-brand-600 shrink-0 mt-0.5" />
          <p>
            <span className="font-bold text-slate-800">Security Architecture Notice:</span>{' '}
            Employee codes are atomically generated on the backend using company-specific prefixes (e.g. CG0001). Initial credentials and account activation setup are handled through secure backend processes. No passwords or financial details are collected in this basic profile form.
          </p>
        </div>

        {/* Form Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-200">
          <Link
            to={isEditMode ? `/employees/${userId}` : '/employees'}
            className="px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-100 rounded-lg border border-slate-300 transition-colors"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2.5 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-lg shadow-button-glow transition-all flex items-center gap-2 disabled:opacity-50 cursor-pointer"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Saving employee...</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>{isEditMode ? 'Update Employee' : 'Create Employee'}</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

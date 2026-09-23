import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, Link, useOutletContext } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  FilePlus2,
  User,
  Phone,
  IndianRupee,
  Receipt,
  Percent,
  FileSpreadsheet,
  RotateCcw,
  Save,
  ArrowLeft,
  Search,
  CheckCircle2,
  AlertTriangle,
  Info,
  Sparkles,
} from 'lucide-react';
import { getSalesFormOptionsApi, createSalesEntryApi } from '../api/sales';
import { extractErrorMessage } from '../api/client';
import type {
  SalesFormOptionsResponse,
  SalesClientOption,
  SalesEntryFormData,
} from '../types/sales';
import { Button } from '../components/ui/button';

interface OutletContextType {
  addToast?: (type: 'success' | 'error' | 'info', title: string, message: string) => void;
}

// Zod Validation Schema (Invoicing & Operational Notes removed for initial sales entry phase)
const salesEntrySchema = z
  .object({
    order_date: z.string().min(1, 'Order date is required'),
    client_name: z.string().trim().min(2, 'Client name must be at least 2 characters'),
    client_id: z.string().optional().nullable(),
    contact_no: z
      .string()
      .trim()
      .regex(/^(\+91[\s-]?)?[6-9]\d{9}$/, 'Please enter a valid 10-digit Indian phone number'),
    lead_source: z.string().min(1, 'Please select a lead source'),
    service_id: z.string().uuid('Please select a valid service/work'),
    salesperson_user_id: z.string().uuid('Please select the sales employee (Converted By)'),
    order_value: z
      .number({ invalid_type_error: 'Total amount must be a number' })
      .min(0, 'Total amount must be greater than or equal to 0'),
    amount_received: z
      .number({ invalid_type_error: 'Advance amount must be a number' })
      .min(0, 'Advance amount cannot be negative'),
    govt_fees: z
      .number({ invalid_type_error: 'Govt fees must be a number' })
      .min(0, 'Govt fees cannot be negative')
      .default(0),
    incidental_cost: z
      .number({ invalid_type_error: 'Incidental cost must be a number' })
      .min(0, 'Incidental cost cannot be negative')
      .default(0),
  })
  .refine((data) => data.amount_received <= data.order_value, {
    message: 'Advance amount cannot exceed total amount',
    path: ['amount_received'],
  });

type SalesEntryFormValues = z.infer<typeof salesEntrySchema>;

function formatInr(val: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val || 0);
}

export const SalesEntryPage: React.FC = () => {
  const navigate = useNavigate();
  const outletCtx = useOutletContext<OutletContextType>();

  const [formOptions, setFormOptions] = useState<SalesFormOptionsResponse | null>(null);
  const [isLoadingOptions, setIsLoadingOptions] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Client Autocomplete State
  const [isClientDropdownOpen, setIsClientDropdownOpen] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<SalesEntryFormValues>({
    resolver: zodResolver(salesEntrySchema),
    defaultValues: {
      order_date: new Date().toISOString().slice(0, 10),
      client_name: '',
      client_id: '',
      contact_no: '',
      lead_source: 'Website',
      service_id: '',
      salesperson_user_id: '',
      order_value: 0,
      amount_received: 0,
      govt_fees: 0,
      incidental_cost: 0,
    },
  });

  // Watch fields for live calculation cards
  const watchedOrderValue = watch('order_value') || 0;
  const watchedAdvance = watch('amount_received') || 0;
  const watchedGovtFees = watch('govt_fees') || 0;
  const watchedIncidental = watch('incidental_cost') || 0;
  const watchedClientName = watch('client_name') || '';

  // Real-time Calculations
  const calculatedPending = Math.max(0, watchedOrderValue - watchedAdvance);
  const calculatedProfits = watchedOrderValue - watchedGovtFees - watchedIncidental;

  const paymentStatusBadge = useMemo(() => {
    if (watchedOrderValue <= 0) return { label: 'PENDING', color: 'amber' };
    if (watchedAdvance >= watchedOrderValue) return { label: 'FULLY_PAID', color: 'emerald' };
    if (watchedAdvance > 0) return { label: 'PARTIALLY_PAID', color: 'blue' };
    return { label: 'PENDING', color: 'amber' };
  }, [watchedOrderValue, watchedAdvance]);

  // Load Form Options
  useEffect(() => {
    let isMounted = true;
    async function loadOptions() {
      setIsLoadingOptions(true);
      try {
        const data = await getSalesFormOptionsApi();
        if (isMounted) {
          setFormOptions(data);
          // Set default salesperson if available and not yet set
          if (data.default_salesperson_id) {
            setValue('salesperson_user_id', data.default_salesperson_id);
          }
        }
      } catch (err) {
        console.error('Failed to load sales form options:', err);
        const msg = extractErrorMessage(err);
        setSubmitError(`Could not load form metadata: ${msg}`);
      } finally {
        if (isMounted) setIsLoadingOptions(false);
      }
    }
    loadOptions();
    return () => {
      isMounted = false;
    };
  }, [setValue]);

  // Filter existing clients for autocomplete
  const matchingClients = useMemo(() => {
    if (!formOptions?.clients || !watchedClientName.trim()) return [];
    const q = watchedClientName.toLowerCase().trim();
    return formOptions.clients
      .filter(
        (c) =>
          c.client_name.toLowerCase().includes(q) ||
          (c.contact_phone && c.contact_phone.includes(q))
      )
      .slice(0, 6);
  }, [formOptions?.clients, watchedClientName]);

  // Handle selecting an existing client from autocomplete
  const handleSelectClient = (client: SalesClientOption) => {
    setValue('client_id', client.client_id, { shouldValidate: true });
    setValue('client_name', client.client_name, { shouldValidate: true });
    if (client.contact_phone) {
      setValue('contact_no', client.contact_phone, { shouldValidate: true });
    }
    setIsClientDropdownOpen(false);
  };

  // Handle service selection to auto-populate pricing defaults
  const handleServiceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const serviceId = e.target.value;
    setValue('service_id', serviceId, { shouldValidate: true });
    if (!formOptions?.services) return;
    const selectedService = formOptions.services.find((s) => s.service_id === serviceId);
    if (selectedService) {
      // If order value is 0 or unassigned, auto-fill base price
      if (!watchedOrderValue || watchedOrderValue === 0) {
        setValue('order_value', Number(selectedService.base_price) || 0, { shouldValidate: true });
      }
      if (selectedService.govt_fee > 0 && (!watchedGovtFees || watchedGovtFees === 0)) {
        setValue('govt_fees', Number(selectedService.govt_fee) || 0, { shouldValidate: true });
      }
    }
  };

  // Form Submit Handler
  const onSubmit = async (values: SalesEntryFormValues, autoConfirm: boolean) => {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const payload: SalesEntryFormData = {
        order_date: values.order_date,
        client_id: values.client_id || undefined,
        client_name: values.client_name,
        contact_no: values.contact_no,
        service_id: values.service_id,
        salesperson_user_id: values.salesperson_user_id,
        lead_source: values.lead_source,
        order_value: Number(values.order_value),
        amount_received: Number(values.amount_received),
        govt_fees: Number(values.govt_fees || 0),
        incidental_cost: Number(values.incidental_cost || 0),
        auto_confirm: autoConfirm,
      };

      const result = await createSalesEntryApi(payload);
      const actionText = autoConfirm
        ? 'confirmed and routed to Operations queue (Unassigned)'
        : 'saved as draft';
      outletCtx.addToast?.(
        'success',
        'Sales Entry Created',
        `Order ${result.order_number || ''} for ${result.client_name} was successfully ${actionText}.`
      );
      navigate('/sales/register');
    } catch (err) {
      console.error('Create sales entry error:', err);
      const msg = extractErrorMessage(err);
      setSubmitError(msg);
      outletCtx.addToast?.('error', 'Sales Entry Failed', msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    reset({
      order_date: new Date().toISOString().slice(0, 10),
      client_name: '',
      client_id: '',
      contact_no: '',
      lead_source: 'Website',
      service_id: '',
      salesperson_user_id: formOptions?.default_salesperson_id || '',
      order_value: 0,
      amount_received: 0,
      govt_fees: 0,
      incidental_cost: 0,
    });
    setSubmitError(null);
  };

  if (isLoadingOptions) {
    return (
      <div className="flex-1 p-6 md:p-8 flex flex-col items-center justify-center min-h-[500px]">
        <div className="w-12 h-12 rounded-2xl bg-blue-100 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 flex items-center justify-center animate-pulse mb-4">
          <FilePlus2 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        </div>
        <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
          Loading sales entry configuration & options...
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-6">
      {/* Top Breadcrumb & Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Link
              to="/sales/register"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Back to Sales Register
            </Link>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-3">
            <span className="p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-sky-500/20 dark:from-blue-500/30 dark:to-cyan-500/30 border border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-400">
              <FilePlus2 className="w-6 h-6" />
            </span>
            New Sales Entry
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Record client conversion details and financial breakdown. Work will be assigned by the Operations Head.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link to="/sales/register">
            <Button variant="outline" size="sm" leftIcon={<FileSpreadsheet className="w-4 h-4" />}>
              Sales Register
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            leftIcon={<RotateCcw className="w-4 h-4" />}
          >
            Reset Form
          </Button>
        </div>
      </div>

      {/* Error Banner */}
      {submitError && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/80 text-rose-800 dark:text-rose-300 text-sm flex items-start gap-3 animate-fadeIn">
          <AlertTriangle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold">Unable to submit sales entry</p>
            <p className="mt-0.5 text-xs text-rose-700 dark:text-rose-400">{submitError}</p>
          </div>
        </div>
      )}

      {/* Live Financial KPI Indicator Ribbon */}
      <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {/* Total Amount Card */}
        <div className="p-4 rounded-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Total Amount
            </span>
            <div className="p-1.5 rounded-lg bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400">
              <IndianRupee className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {formatInr(watchedOrderValue)}
          </div>
          <div className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
            Order contract value
          </div>
        </div>

        {/* Pending Balance Card */}
        <div className="p-4 rounded-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Pending Balance
            </span>
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                paymentStatusBadge.color === 'emerald'
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                  : paymentStatusBadge.color === 'blue'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                  : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
              }`}
            >
              {paymentStatusBadge.label.replace('_', ' ')}
            </span>
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {formatInr(calculatedPending)}
          </div>
          <div className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
            Advance: <strong className="text-emerald-600 dark:text-emerald-400">{formatInr(watchedAdvance)}</strong>
          </div>
        </div>

        {/* Govt & Incidental Fees */}
        <div className="p-4 rounded-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Govt & Incidentals
            </span>
            <div className="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
              <Receipt className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {formatInr(watchedGovtFees + watchedIncidental)}
          </div>
          <div className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
            Govt: {formatInr(watchedGovtFees)} | Incidental: {formatInr(watchedIncidental)}
          </div>
        </div>

        {/* Net Profit Projection */}
        <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500/10 via-sky-500/5 to-transparent dark:from-emerald-950/30 dark:via-slate-900 border border-emerald-200/80 dark:border-emerald-800/60 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-800 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5" />
              Calculated Profit
            </span>
            <div className="p-1.5 rounded-lg bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400">
              <Percent className="w-4 h-4" />
            </div>
          </div>
          <div className={`mt-2 text-2xl font-black ${calculatedProfits >= 0 ? 'text-emerald-700 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
            {formatInr(calculatedProfits)}
          </div>
          <div className="mt-1 text-[11px] text-emerald-800/80 dark:text-emerald-400/80 flex items-center gap-1 font-medium">
            <Info className="w-3 h-3" />
            Total - Govt - Incidental
          </div>
        </div>
      </div>

      {/* Main Entry Form */}
      <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
        {/* Section 1: Client & Engagement Details */}
        <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 rounded-3xl p-6 md:p-8 shadow-sm space-y-6">
          <div className="border-b border-slate-100 dark:border-slate-800/80 pb-4">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <User className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              1. Client & Engagement Details
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Specify conversion date, client identity, lead source, and the sales representative (Converted By).
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {/* Column 2: Date */}
            <div>
              <label htmlFor="order_date" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Date <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="order_date"
                  type="date"
                  {...register('order_date')}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                />
              </div>
              {errors.order_date && (
                <p className="mt-1 text-xs text-rose-500">{errors.order_date.message}</p>
              )}
            </div>

            {/* Column 3: Client Name (Autocomplete + Direct Entry) */}
            <div className="relative">
              <label htmlFor="client_name" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 flex items-center justify-between">
                <span>Client Name <span className="text-rose-500">*</span></span>
                <span className="text-[11px] font-normal text-slate-400">Type or select existing</span>
              </label>
              <div className="relative">
                <input
                  id="client_name"
                  type="text"
                  placeholder="e.g. Acme Legal Solutions Pvt Ltd"
                  {...register('client_name', {
                    onChange: () => setIsClientDropdownOpen(true),
                  })}
                  onFocus={() => setIsClientDropdownOpen(true)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition pr-8"
                />
                <Search className="w-4 h-4 text-slate-400 absolute right-3 top-3 pointer-events-none" />
              </div>

              {/* Autocomplete Dropdown List */}
              {isClientDropdownOpen && matchingClients.length > 0 && (
                <div className="absolute left-0 right-0 top-full mt-1.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-2xl shadow-xl z-30 max-h-52 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800">
                  <div className="p-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400 bg-slate-50 dark:bg-slate-800/40">
                    Existing Clients Matching Search:
                  </div>
                  {matchingClients.map((c) => (
                    <button
                      key={c.client_id}
                      type="button"
                      onClick={() => handleSelectClient(c)}
                      className="w-full text-left px-3.5 py-2.5 hover:bg-blue-50 dark:hover:bg-blue-950/40 flex items-center justify-between text-xs transition"
                    >
                      <div>
                        <div className="font-semibold text-slate-900 dark:text-white">
                          {c.client_name}
                        </div>
                        <div className="text-[11px] text-slate-500 dark:text-slate-400">
                          {c.contact_phone || 'No phone'} {c.contact_email ? `• ${c.contact_email}` : ''}
                        </div>
                      </div>
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                        Select
                      </span>
                    </button>
                  ))}
                </div>
              )}

              {errors.client_name && (
                <p className="mt-1 text-xs text-rose-500">{errors.client_name.message}</p>
              )}
            </div>

            {/* Column 4: Contact No */}
            <div>
              <label htmlFor="contact_no" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Contact No <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="contact_no"
                  type="text"
                  placeholder="e.g. 9876543210"
                  {...register('contact_no')}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                />
                <Phone className="w-4 h-4 text-slate-400 absolute right-3 top-3 pointer-events-none" />
              </div>
              {errors.contact_no && (
                <p className="mt-1 text-xs text-rose-500">{errors.contact_no.message}</p>
              )}
            </div>

            {/* Column 5: Source */}
            <div>
              <label htmlFor="lead_source" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Source <span className="text-rose-500">*</span>
              </label>
              <select
                id="lead_source"
                {...register('lead_source')}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              >
                {(formOptions?.lead_sources || [
                  'Website',
                  'Referral',
                  'Direct',
                  'Walk-in',
                  'Social Media',
                  'Email Campaign',
                  'Channel Partner',
                  'Cold Call',
                  'Other',
                ]).map((src) => (
                  <option key={src} value={src}>
                    {src}
                  </option>
                ))}
              </select>
              {errors.lead_source && (
                <p className="mt-1 text-xs text-rose-500">{errors.lead_source.message}</p>
              )}
            </div>

            {/* Column 6: Work (Service) */}
            <div>
              <label htmlFor="service_id" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Work / Service <span className="text-rose-500">*</span>
              </label>
              <select
                id="service_id"
                {...register('service_id', {
                  onChange: handleServiceChange,
                })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              >
                <option value="">-- Select Service / Work --</option>
                {(formOptions?.services || []).map((srv) => (
                  <option key={srv.service_id} value={srv.service_id}>
                    {srv.service_name} ({srv.service_code}) - Base: {formatInr(srv.base_price)}
                  </option>
                ))}
              </select>
              {errors.service_id && (
                <p className="mt-1 text-xs text-rose-500">{errors.service_id.message}</p>
              )}
            </div>

            {/* Column 7: Converted By (Sales Employee Responsible) */}
            <div>
              <label htmlFor="salesperson_user_id" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Converted By (Sales Employee) <span className="text-rose-500">*</span>
              </label>
              <select
                id="salesperson_user_id"
                {...register('salesperson_user_id')}
                disabled={!formOptions?.can_select_salesperson && Boolean(formOptions?.default_salesperson_id)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition disabled:opacity-75 disabled:cursor-not-allowed"
              >
                <option value="">-- Select Salesperson --</option>
                {(formOptions?.salespersons || []).map((sp) => (
                  <option key={sp.user_id} value={sp.user_id}>
                    {sp.full_name} ({sp.employee_code}) {sp.designation_name ? `• ${sp.designation_name}` : ''}
                  </option>
                ))}
              </select>
              {errors.salesperson_user_id && (
                <p className="mt-1 text-xs text-rose-500">{errors.salesperson_user_id.message}</p>
              )}
            </div>
          </div>
        </div>

        {/* Section 2: Financials & Cost Analysis */}
        <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 rounded-3xl p-6 md:p-8 shadow-sm space-y-6">
          <div className="border-b border-slate-100 dark:border-slate-800/80 pb-4">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <IndianRupee className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              2. Financials & Cost Analysis
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Specify fee amounts. Advance balances and net profit margins calculate automatically.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {/* Column 10: Total Amount */}
            <div>
              <label htmlFor="order_value" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Total Amount (₹) <span className="text-rose-500">*</span>
              </label>
              <input
                id="order_value"
                type="number"
                step="any"
                min="0"
                placeholder="0"
                {...register('order_value', { valueAsNumber: true })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-sm font-semibold text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              />
              {errors.order_value && (
                <p className="mt-1 text-xs text-rose-500">{errors.order_value.message}</p>
              )}
            </div>

            {/* Column 11: Advance Amount */}
            <div>
              <label htmlFor="amount_received" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Advance Amount (₹) <span className="text-rose-500">*</span>
              </label>
              <input
                id="amount_received"
                type="number"
                step="any"
                min="0"
                placeholder="0"
                {...register('amount_received', { valueAsNumber: true })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-sm font-semibold text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              />
              {errors.amount_received && (
                <p className="mt-1 text-xs text-rose-500">{errors.amount_received.message}</p>
              )}
            </div>

            {/* Column 17: Govt Fees */}
            <div>
              <label htmlFor="govt_fees" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Govt Fees (₹)
              </label>
              <input
                id="govt_fees"
                type="number"
                step="any"
                min="0"
                placeholder="0"
                {...register('govt_fees', { valueAsNumber: true })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              />
              {errors.govt_fees && (
                <p className="mt-1 text-xs text-rose-500">{errors.govt_fees.message}</p>
              )}
            </div>

            {/* Column 18: Incidental Cost */}
            <div>
              <label htmlFor="incidental_cost" className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Incidental Cost (₹)
              </label>
              <input
                id="incidental_cost"
                type="number"
                step="any"
                min="0"
                placeholder="0"
                {...register('incidental_cost', { valueAsNumber: true })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              />
              {errors.incidental_cost && (
                <p className="mt-1 text-xs text-rose-500">{errors.incidental_cost.message}</p>
              )}
            </div>
          </div>

          {/* Live Formula Note */}
          <div className="p-3.5 rounded-2xl bg-blue-50/70 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900/60 text-xs text-blue-800 dark:text-blue-300 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0" />
              <span>
                <strong>Formula Reference:</strong> Pending = Total Amount - Advance Amount | Profit = Total Amount - Govt Fees - Incidental Cost
              </span>
            </div>
            <div className="font-mono text-[11px] text-blue-700 dark:text-blue-400 bg-white/80 dark:bg-slate-900 px-2.5 py-1 rounded-lg border border-blue-200 dark:border-blue-800">
              Pending: {formatInr(calculatedPending)} | Profit: {formatInr(calculatedProfits)}
            </div>
          </div>
        </div>

        {/* Action Buttons Bar */}
        <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 rounded-3xl p-4 sm:p-6 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Link to="/sales/register">
              <Button variant="outline" size="md">
                Cancel
              </Button>
            </Link>
            <Button
              type="button"
              variant="ghost"
              size="md"
              onClick={handleReset}
              leftIcon={<RotateCcw className="w-4 h-4" />}
            >
              Reset
            </Button>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {/* Save as Draft Button */}
            <Button
              type="button"
              variant="outline"
              size="md"
              isLoading={isSubmitting}
              disabled={isSubmitting}
              onClick={handleSubmit((data) => onSubmit(data, false))}
              leftIcon={<Save className="w-4 h-4 text-slate-600 dark:text-slate-300" />}
              className="w-full sm:w-auto"
            >
              Save as Draft
            </Button>

            {/* Save & Confirm Order Button (Routes to Operations as Unassigned) */}
            <Button
              type="button"
              variant="primary"
              size="md"
              isLoading={isSubmitting}
              disabled={isSubmitting}
              onClick={handleSubmit((data) => onSubmit(data, true))}
              leftIcon={<CheckCircle2 className="w-4 h-4" />}
              className="w-full sm:w-auto"
            >
              Save & Confirm Order
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};

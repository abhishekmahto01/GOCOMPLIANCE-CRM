import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  UploadCloud,
  FileSpreadsheet,
  Download,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  FileCheck2,
  ArrowRight,
  Pencil,
  Check,
  X,
} from 'lucide-react';
import { Modal } from '../ui/modal';
import { Button } from '../ui/button';
import { Checkbox } from '../ui/checkbox';
import { getOperationsAssigneesApi, getSalesFormOptionsApi } from '../../api/sales';
import {
  downloadMasterTemplateXlsxApi,
  downloadMasterTemplateCsvApi,
  previewSalesImportApi,
  executeBulkImportApi,
  downloadErrorReportApi,
} from '../../api/sales_import';
import { extractErrorMessage } from '../../api/client';
import type { SalesEmployeeOption, SalesServiceOption } from '../../types/sales';
import type {
  SalesImportPreviewResponse,
  SalesImportExecuteResponse,
  SalesImportRowValidation,
} from '../../types/sales_import';

interface BulkSalesImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  addToast?: (type: 'success' | 'error' | 'info', title: string, message: string) => void;
}

function formatInr(val: number | string | null | undefined): string {
  const num = typeof val === 'number' ? val : parseFloat(String(val ?? 0));
  const safeNum = isNaN(num) ? 0 : num;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(safeNum);
}

function formatSlNo(val: string | number | null | undefined): string {
  if (val === null || val === undefined || val === '') return '';
  return String(val).trim().replace(/\.0+$/, '');
}

function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export const BulkSalesImportModal: React.FC<BulkSalesImportModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  addToast,
}) => {
  // State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [assignees, setAssignees] = useState<SalesEmployeeOption[]>([]);
  const [selectedAssigneeId, setSelectedAssigneeId] = useState<string>('');
  const [isLoadingAssignees, setIsLoadingAssignees] = useState<boolean>(false);

  // Available active services and sources for inline quick-fix / editing
  const [availableServices, setAvailableServices] = useState<SalesServiceOption[]>([]);
  const [allowedLeadSources, setAllowedLeadSources] = useState<string[]>([
    'DIRECT',
    'WEBSITE',
    'REFERRAL',
    'SOCIAL_MEDIA',
    'CAMPAIGN',
    'PARTNER',
    'COLD_CALL',
    'OTHER',
  ]);

  const [isPreviewing, setIsPreviewing] = useState<boolean>(false);
  const [previewData, setPreviewData] = useState<SalesImportPreviewResponse | null>(null);
  const [allowDuplicates, setAllowDuplicates] = useState<boolean>(false);
  const [applyGst, setApplyGst] = useState<boolean>(false);

  // Row Inline Edit State
  const [editingRowNumber, setEditingRowNumber] = useState<number | null>(null);
  const [rowEditState, setRowEditState] = useState<{
    location: string;
    client_name: string;
    contact: string;
    source: string;
    work: string;
    service_id: string;
    total_amount: string;
    advance_amount: string;
    incidental_cost: string;
  } | null>(null);

  const [isImporting, setIsImporting] = useState<boolean>(false);
  const [importResult, setImportResult] = useState<SalesImportExecuteResponse | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isDownloadingXlsx, setIsDownloadingXlsx] = useState<boolean>(false);
  const [isDownloadingCsv, setIsDownloadingCsv] = useState<boolean>(false);
  const [isDownloadingErrors, setIsDownloadingErrors] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load eligible Operations assignees
  const loadAssignees = useCallback(async () => {
    setIsLoadingAssignees(true);
    try {
      const data = await getOperationsAssigneesApi();
      setAssignees(data);
      if (data.length > 0 && !selectedAssigneeId) {
        setSelectedAssigneeId(data[0].user_id);
      }
    } catch (err: unknown) {
      console.error('Failed to load Operations assignees:', err);
      addToast?.('error', 'Assignees Error', 'Could not load eligible Operations team members.');
    } finally {
      setIsLoadingAssignees(false);
    }
  }, [addToast, selectedAssigneeId]);

  useEffect(() => {
    if (isOpen) {
      loadAssignees();
      getSalesFormOptionsApi()
        .then((opts) => {
          if (opts.services && opts.services.length > 0) {
            setAvailableServices(opts.services);
          }
          if (opts.lead_sources && opts.lead_sources.length > 0) {
            setAllowedLeadSources(opts.lead_sources);
          }
        })
        .catch((err) => {
          console.error('Failed to load services options for bulk import:', err);
        });
    } else {
      // Reset state on close
      setSelectedFile(null);
      setPreviewData(null);
      setAllowDuplicates(false);
      setImportResult(null);
      setEditingRowNumber(null);
      setRowEditState(null);
    }
  }, [isOpen, loadAssignees]);

  // Handle template downloads
  const handleDownloadXlsx = async () => {
    setIsDownloadingXlsx(true);
    try {
      const { blob, filename } = await downloadMasterTemplateXlsxApi();
      downloadBlob(blob, filename);
      addToast?.('success', 'Template Downloaded', 'Master Excel template (.xlsx) downloaded successfully.');
    } catch (err: unknown) {
      addToast?.('error', 'Download Failed', extractErrorMessage(err));
    } finally {
      setIsDownloadingXlsx(false);
    }
  };

  const handleDownloadCsv = async () => {
    setIsDownloadingCsv(true);
    try {
      const { blob, filename } = await downloadMasterTemplateCsvApi();
      downloadBlob(blob, filename);
      addToast?.('success', 'Template Downloaded', 'Master CSV template (.csv) downloaded successfully.');
    } catch (err: unknown) {
      addToast?.('error', 'Download Failed', extractErrorMessage(err));
    } finally {
      setIsDownloadingCsv(false);
    }
  };

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (
        !file.name.toLowerCase().endsWith('.xlsx') &&
        !file.name.toLowerCase().endsWith('.csv') &&
        !file.name.toLowerCase().endsWith('.numbers')
      ) {
        addToast?.('error', 'Invalid File Format', 'Please upload a valid .xlsx, .csv, or .numbers file.');
        return;
      }
      setSelectedFile(file);
      setPreviewData(null);
      setValidationError(null);
      setAllowDuplicates(false);
      setImportResult(null);
    }
  };

  // Handle preview & validation
  const handleValidateAndPreview = async () => {
    if (!selectedFile) {
      addToast?.('error', 'No File Selected', 'Please select an Excel or CSV file to validate.');
      return;
    }
    setIsPreviewing(true);
    setValidationError(null);
    try {
      const res = await previewSalesImportApi(selectedFile, applyGst);
      setPreviewData(res);
      if (res.can_import) {
        addToast?.('success', 'Validation Passed', `${res.valid_rows_count} records ready for bulk import.`);
      } else {
        addToast?.(
          'error',
          'Validation Failed',
          `${res.error_rows_count} row(s) contain blocking errors. Please inspect the preview or download the error report.`
        );
      }
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      setValidationError(msg);
      addToast?.('error', 'Validation Notice', msg);
    } finally {
      setIsPreviewing(false);
    }
  };

  // Toggle GST Calculation (0% vs 18%) and recalculate rows dynamically
  const handleToggleGst = (newApplyGst: boolean) => {
    setApplyGst(newApplyGst);
    if (previewData) {
      const updatedRows = previewData.rows.map((r) => {
        const rawBase = r.base_amount !== null && r.base_amount !== undefined ? r.base_amount : (r.total_amount || 0);
        const base = rawBase;
        const gstAmt = newApplyGst ? Math.round(base * 18) / 100 : 0;
        const finalTot = newApplyGst ? Math.round((base + gstAmt) * 100) / 100 : base;

        // Recheck advance and incidental against finalTot
        const remainingErrors = (r.errors || []).filter(
          (err) =>
            !err.toLowerCase().includes('advance amount cannot exceed') &&
            !err.toLowerCase().includes('incidental cost cannot exceed')
        );

        if (r.advance_amount && r.advance_amount > finalTot) {
          remainingErrors.push('Advance Amount cannot exceed Total Amount.');
        }
        if (r.incidental_cost && r.incidental_cost > finalTot) {
          remainingErrors.push('Incidental Cost cannot exceed Total Amount.');
        }

        return {
          ...r,
          base_amount: base,
          gst_amount: gstAmt,
          gst_rate: newApplyGst ? 18 : 0,
          gst_invoice_required: newApplyGst,
          total_amount: finalTot,
          errors: remainingErrors,
          is_valid: remainingErrors.length === 0,
        };
      });

      const validCount = updatedRows.filter((r) => r.is_valid).length;
      const errorCount = updatedRows.filter((r) => !r.is_valid).length;
      const validBaseTotal = updatedRows.filter((r) => r.is_valid).reduce((acc, r) => acc + (r.base_amount || 0), 0);
      const validGstTotal = updatedRows.filter((r) => r.is_valid).reduce((acc, r) => acc + (r.gst_amount || 0), 0);

      setPreviewData({
        ...previewData,
        apply_gst: newApplyGst,
        total_base_amount: validBaseTotal,
        total_gst_amount: validGstTotal,
        valid_rows_count: validCount,
        error_rows_count: errorCount,
        can_import: updatedRows.length > 0 && errorCount === 0,
        rows: updatedRows,
      });
    }
  };

  // Handle downloading error report
  const handleDownloadErrorReport = async () => {
    if (!previewData?.rows) return;
    setIsDownloadingErrors(true);
    try {
      const { blob, filename } = await downloadErrorReportApi(previewData.rows);
      downloadBlob(blob, filename);
      addToast?.('info', 'Report Downloaded', 'Validation error report downloaded successfully.');
    } catch (err: unknown) {
      addToast?.('error', 'Download Failed', extractErrorMessage(err));
    } finally {
      setIsDownloadingErrors(false);
    }
  };

  // Handle atomic bulk execution
  const handleConfirmImport = async () => {
    if (!previewData || !selectedAssigneeId) return;

    if (!previewData.can_import) {
      addToast?.('error', 'Validation Required', 'Please resolve all errors in the file before importing.');
      return;
    }

    if (previewData.duplicate_warnings_count > 0 && !allowDuplicates) {
      addToast?.(
        'error',
        'Duplicate Confirmation Required',
        'Please check "Allow duplicate records" if these entries are intentional multi-orders.'
      );
      return;
    }

    setIsImporting(true);
    try {
      const idempotencyKey = `bulk-import-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      const result = await executeBulkImportApi({
        rows: previewData.rows,
        assignee_user_id: selectedAssigneeId,
        idempotency_key: idempotencyKey,
        allow_duplicates: allowDuplicates,
        apply_gst: applyGst,
      });

      setImportResult(result);
      addToast?.('success', 'Import Successful', result.message);
      onSuccess();
    } catch (err: unknown) {
      addToast?.('error', 'Import Failed', extractErrorMessage(err));
    } finally {
      setIsImporting(false);
    }
  };

  // Quick-fix Work / Service directly from cell dropdown
  const handleQuickFixService = (rowNumber: number, selectedServiceId: string) => {
    if (!previewData || !selectedServiceId) return;
    const targetService = availableServices.find((s) => s.service_id === selectedServiceId);
    if (!targetService) return;

    const updatedRows = previewData.rows.map((r) => {
      if (r.row_number !== rowNumber) return r;

      const remainingErrors = (r.errors || []).filter(
        (err) =>
          !err.toLowerCase().includes('work') &&
          !err.toLowerCase().includes('service')
      );

      return {
        ...r,
        work: targetService.service_name,
        service_id: targetService.service_id,
        service_name: targetService.service_name,
        errors: remainingErrors,
        is_valid: remainingErrors.length === 0,
      };
    });

    const validCount = updatedRows.filter((r) => r.is_valid).length;
    const errorCount = updatedRows.filter((r) => !r.is_valid).length;

    setPreviewData({
      ...previewData,
      rows: updatedRows,
      valid_rows_count: validCount,
      error_rows_count: errorCount,
      can_import: updatedRows.length > 0 && errorCount === 0,
    });

    addToast?.(
      'success',
      'Service Corrected',
      `Row ${rowNumber}: Set service to "${targetService.service_name}".`
    );
  };

  // Start editing a specific row
  const handleStartEditRow = (row: SalesImportRowValidation) => {
    setEditingRowNumber(row.row_number);
    const displayedBase = row.base_amount !== null && row.base_amount !== undefined ? row.base_amount : (row.total_amount ?? '');
    setRowEditState({
      location: row.location || '',
      client_name: row.client_name || '',
      contact: row.contact || '',
      source: (row.source || 'WEBSITE').toUpperCase(),
      work: row.service_name || row.work || '',
      service_id: row.service_id || '',
      total_amount: String(displayedBase),
      advance_amount:
        row.advance_amount !== null && row.advance_amount !== undefined
          ? String(row.advance_amount)
          : '0',
      incidental_cost:
        row.incidental_cost !== null && row.incidental_cost !== undefined
          ? String(row.incidental_cost)
          : '0',
    });
  };

  const handleCancelEditRow = () => {
    setEditingRowNumber(null);
    setRowEditState(null);
  };

  const handleSaveEditRow = (rowNumber: number) => {
    if (!previewData || !rowEditState) return;

    const newErrors: string[] = [];

    // Client Name validation
    const trimmedName = rowEditState.client_name.trim();
    if (!trimmedName) {
      newErrors.push('Client Name is required.');
    } else if (trimmedName.length > 200) {
      newErrors.push('Client Name exceeds 200 characters.');
    }

    // Contact validation
    const trimmedContact = rowEditState.contact.trim();
    const cleanDigits = trimmedContact.replace(/[\s\-+()]/g, '');
    if (!trimmedContact) {
      newErrors.push('Contact number is required.');
    } else if (!/^\d+$/.test(cleanDigits) || cleanDigits.length < 7 || cleanDigits.length > 20) {
      newErrors.push(`Invalid Contact number '${trimmedContact}'. Must contain 7-20 digits.`);
    }

    // Source validation
    const trimmedSource = rowEditState.source.trim().toUpperCase();
    if (!trimmedSource) {
      newErrors.push('Source is required.');
    }

    // Work / Service validation
    let matchedService = availableServices.find(
      (s) => s.service_id === rowEditState.service_id
    );
    if (!matchedService && rowEditState.work) {
      const wLower = rowEditState.work.trim().toLowerCase();
      matchedService = availableServices.find(
        (s) =>
          s.service_name.trim().toLowerCase() === wLower ||
          (s.service_code && s.service_code.trim().toLowerCase() === wLower)
      );
    }

    if (!matchedService) {
      newErrors.push(
        `Work '${rowEditState.work || 'None'}' does not match any active service in the system.`
      );
    }

    // Amount validation
    const cleanAmtStr = rowEditState.total_amount.replace(/[₹,\s]/g, '');
    const parsedBase = parseFloat(cleanAmtStr);
    if (!cleanAmtStr || isNaN(parsedBase) || parsedBase < 0) {
      newErrors.push('Total Amount must be a valid positive number.');
    }

    const calculatedGst = applyGst && !isNaN(parsedBase) ? Math.round(parsedBase * 18) / 100 : 0;
    const finalTotal = applyGst && !isNaN(parsedBase) ? Math.round((parsedBase + calculatedGst) * 100) / 100 : parsedBase;

    // Advance Amount validation
    const cleanAdvStr = rowEditState.advance_amount.replace(/[₹,\s]/g, '');
    const parsedAdv = cleanAdvStr ? parseFloat(cleanAdvStr) : 0;
    if (isNaN(parsedAdv) || parsedAdv < 0) {
      newErrors.push('Advance Amount must be a valid non-negative number.');
    } else if (!isNaN(finalTotal) && parsedAdv > finalTotal) {
      newErrors.push('Advance Amount cannot exceed Total Amount.');
    }

    // Incidental Cost validation
    const cleanIncStr = rowEditState.incidental_cost.replace(/[₹,\s]/g, '');
    const parsedInc = cleanIncStr ? parseFloat(cleanIncStr) : 0;
    if (isNaN(parsedInc) || parsedInc < 0) {
      newErrors.push('Incidental Cost must be a valid positive number.');
    } else if (!isNaN(finalTotal) && parsedInc > finalTotal) {
      newErrors.push('Incidental Cost cannot exceed Total Amount.');
    }

    const updatedRows = previewData.rows.map((r) => {
      if (r.row_number !== rowNumber) return r;

      return {
        ...r,
        location: rowEditState.location.trim() || null,
        client_name: trimmedName || null,
        contact: trimmedContact || null,
        source: trimmedSource || null,
        work: matchedService ? matchedService.service_name : rowEditState.work,
        service_id: matchedService ? matchedService.service_id : null,
        service_name: matchedService ? matchedService.service_name : null,
        base_amount: isNaN(parsedBase) ? null : parsedBase,
        gst_amount: calculatedGst,
        gst_rate: applyGst ? 18 : 0,
        gst_invoice_required: applyGst,
        total_amount: isNaN(finalTotal) ? null : finalTotal,
        advance_amount: isNaN(parsedAdv) ? 0 : parsedAdv,
        incidental_cost: isNaN(parsedInc) ? 0 : parsedInc,
        errors: newErrors,
        is_valid: newErrors.length === 0,
      };
    });

    const validCount = updatedRows.filter((r) => r.is_valid).length;
    const errorCount = updatedRows.filter((r) => !r.is_valid).length;
    const validBaseTotal = updatedRows.filter((r) => r.is_valid).reduce((acc, r) => acc + (r.base_amount || 0), 0);
    const validGstTotal = updatedRows.filter((r) => r.is_valid).reduce((acc, r) => acc + (r.gst_amount || 0), 0);

    setPreviewData({
      ...previewData,
      rows: updatedRows,
      total_base_amount: validBaseTotal,
      total_gst_amount: validGstTotal,
      valid_rows_count: validCount,
      error_rows_count: errorCount,
      can_import: updatedRows.length > 0 && errorCount === 0,
    });

    setEditingRowNumber(null);
    setRowEditState(null);

    if (newErrors.length === 0) {
      addToast?.('success', 'Row Saved', `Row ${rowNumber} updated and validated successfully.`);
    } else {
      addToast?.('error', 'Validation Notice', `Row ${rowNumber} saved with issues: ${newErrors.join('; ')}`);
    }
  };

  const selectedAssignee = assignees.find((a) => a.user_id === selectedAssigneeId);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Bulk Sales Import (Excel / CSV)"
      description="Upload bulk customer orders and automatically assign Operations tasks in a single atomic transaction."
      maxWidth="max-w-5xl"
    >
      <div className="space-y-6 max-h-[80vh] overflow-y-auto px-1 pr-2">
        {/* SUCCESS VIEW */}
        {importResult ? (
          <div className="py-8 text-center space-y-4">
            <div className="w-16 h-16 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center mx-auto shadow-md">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <div>
              <h4 className="text-xl font-bold text-slate-900 dark:text-white">
                Bulk Import Completed Successfully!
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-300 mt-1 max-w-lg mx-auto">
                {importResult.message}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 max-w-md mx-auto pt-2">
              <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="text-xs text-slate-500 uppercase font-semibold">Sales Orders</span>
                <div className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {importResult.imported_count}
                </div>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="text-xs text-slate-500 uppercase font-semibold">Ops Assignments</span>
                <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
                  {importResult.assignments_count}
                </div>
              </div>
            </div>

            {importResult.order_numbers && importResult.order_numbers.length > 0 && (
              <div className="max-w-md mx-auto text-left bg-slate-50 dark:bg-slate-800/40 p-3 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="text-xs font-semibold text-slate-500 uppercase">Created Orders:</span>
                <div className="flex flex-wrap gap-1.5 mt-1.5 max-h-24 overflow-y-auto">
                  {importResult.order_numbers.map((no) => (
                    <span
                      key={no}
                      className="inline-block px-2 py-0.5 rounded text-xs font-mono font-medium bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600"
                    >
                      {no}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-4 flex justify-center gap-3">
              <Button variant="primary" onClick={onClose} size="md">
                Done & View Sales Register
              </Button>
            </div>
          </div>
        ) : (
          <>
            {/* STEP 1 & 2: TEMPLATE DOWNLOAD & UPLOAD CONTROLS */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              {/* Step 1: Download Templates */}
              <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/80 space-y-3">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-300 font-bold text-xs flex items-center justify-center">
                    1
                  </div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    Download Master Template
                  </h4>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Use the pre-formatted master template with standard column headers: Sl No, Location, Client Name, Contact, Source, Work, Total Amount, Advance Amount, Incidental Cost.
                </p>
                <div className="flex flex-wrap gap-2.5 pt-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleDownloadXlsx}
                    isLoading={isDownloadingXlsx}
                    leftIcon={<FileSpreadsheet className="w-4 h-4 text-emerald-600" />}
                  >
                    Template (.xlsx)
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleDownloadCsv}
                    isLoading={isDownloadingCsv}
                    leftIcon={<Download className="w-4 h-4 text-blue-600" />}
                  >
                    Template (.csv)
                  </Button>
                </div>
              </div>

              {/* Step 2: Assignee Selection */}
              <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/80 space-y-3">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-300 font-bold text-xs flex items-center justify-center">
                    2
                  </div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    Select Operations Assignee
                  </h4>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Every imported sales entry will be automatically handed over and assigned to this Operations team member.
                </p>
                <div>
                  <label htmlFor="ops-assignee-select" className="block text-[11px] font-semibold text-slate-500 uppercase mb-1">
                    Operations Assignee
                  </label>
                  <select
                    id="ops-assignee-select"
                    value={selectedAssigneeId}
                    onChange={(e) => setSelectedAssigneeId(e.target.value)}
                    disabled={isLoadingAssignees || isImporting}
                    className="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                  >
                    {assignees.map((emp) => (
                      <option key={emp.user_id} value={emp.user_id}>
                        {emp.full_name} ({emp.employee_code}) — {emp.designation_name || emp.department_name || 'Operations'}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* STEP 3: GST CALCULATION (18%) */}
            <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/80 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-300 font-bold text-xs flex items-center justify-center">
                    3
                  </div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    GST Calculation Option (18%)
                  </h4>
                </div>
                <span className={`text-[11px] px-2.5 py-0.5 rounded-full font-semibold border ${
                  applyGst
                    ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700'
                    : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border-slate-300 dark:border-slate-700'
                }`}>
                  {applyGst ? '18% GST Enabled' : 'No GST (0%)'}
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Choose whether imported entries should have 18% GST auto-calculated and added to the order value at save time.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <label
                  className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                    !applyGst
                      ? 'bg-blue-50/60 dark:bg-blue-950/40 border-blue-400 dark:border-blue-600 shadow-xs'
                      : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="gst_calculation_option_main"
                    checked={!applyGst}
                    onChange={() => handleToggleGst(false)}
                    className="mt-0.5 text-blue-600 focus:ring-blue-500 h-4 w-4 border-slate-300"
                  />
                  <div className="space-y-0.5">
                    <span className="text-xs font-semibold text-slate-900 dark:text-white block">
                      No GST (Flat Amount)
                    </span>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 block leading-normal">
                      Amount entered in file is the final Total Amount. No 18% GST added.
                    </span>
                  </div>
                </label>

                <label
                  className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                    applyGst
                      ? 'bg-emerald-50/70 dark:bg-emerald-950/40 border-emerald-400 dark:border-emerald-600 shadow-xs'
                      : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="gst_calculation_option_main"
                    checked={applyGst}
                    onChange={() => handleToggleGst(true)}
                    className="mt-0.5 text-emerald-600 focus:ring-emerald-500 h-4 w-4 border-slate-300"
                  />
                  <div className="space-y-0.5">
                    <span className="text-xs font-semibold text-emerald-900 dark:text-emerald-200 block">
                      Add 18% GST (Auto Calculation)
                    </span>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 block leading-normal">
                      Amount in file is Base Amount. 18% GST will be added at save time & routes to Accounts.
                    </span>
                  </div>
                </label>
              </div>
            </div>

            {/* STEP 4: FILE UPLOAD & VALIDATE BAR */}
            <div className="p-4 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/50 space-y-3">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-950/60 dark:text-blue-400">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <div>
                    <h5 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Upload Completed Sales File (.xlsx, .csv, or .numbers)
                    </h5>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Supports Excel, CSV, and Apple Numbers (.numbers) up to 500 rows. Max 10 MB.
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".xlsx,.csv,.numbers"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    {selectedFile ? 'Change File' : 'Browse File'}
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleValidateAndPreview}
                    isLoading={isPreviewing}
                    disabled={!selectedFile}
                    leftIcon={<FileCheck2 className="w-4 h-4" />}
                  >
                    Validate & Preview
                  </Button>
                </div>
              </div>

              {selectedFile && (
                <div className="flex items-center justify-between px-3 py-2 bg-slate-50 dark:bg-slate-800 rounded-lg text-xs border border-slate-200 dark:border-slate-700">
                  <div className="flex items-center gap-2">
                    <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{selectedFile.name}</span>
                    <span className="text-slate-400">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                  </div>
                  <span className="text-blue-600 dark:text-blue-400 font-medium">Ready to validate</span>
                </div>
              )}
            </div>

            {/* Validation Notice / Error Banner */}
            {validationError && (
              <div className="p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-700/80 rounded-2xl flex items-start gap-3 animate-fadeIn">
                <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                <div className="flex-1 text-xs">
                  <h5 className="font-bold text-amber-900 dark:text-amber-200">
                    File Validation Notice
                  </h5>
                  <p className="text-amber-800 dark:text-amber-300 mt-1 leading-relaxed">
                    {validationError}
                  </p>
                  <p className="text-amber-700 dark:text-amber-400 mt-2 font-medium">
                    👉 Tip: Open the downloaded template, fill in your customer orders in the blank rows (Row 2 onwards), save the file, and click "Validate & Preview" again.
                  </p>
                </div>
              </div>
            )}

            {/* PREVIEW & VALIDATION SUMMARY */}
            {previewData && (
              <div className="space-y-4">
                {/* KPI Ribbon */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase">Total Data Rows</span>
                    <div className="text-lg font-bold text-slate-900 dark:text-white mt-1">
                      {previewData.total_rows}
                    </div>
                  </div>
                  <div className="p-3 bg-emerald-50/60 dark:bg-emerald-950/30 rounded-xl border border-emerald-200 dark:border-emerald-800/60">
                    <span className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 uppercase">Valid Rows</span>
                    <div className="text-lg font-bold text-emerald-700 dark:text-emerald-400 mt-1">
                      {previewData.valid_rows_count}
                    </div>
                  </div>
                  <div className="p-3 bg-rose-50/60 dark:bg-rose-950/30 rounded-xl border border-rose-200 dark:border-rose-800/60">
                    <span className="text-[11px] font-semibold text-rose-700 dark:text-rose-400 uppercase">Error Rows</span>
                    <div className="text-lg font-bold text-rose-700 dark:text-rose-400 mt-1">
                      {previewData.error_rows_count}
                    </div>
                  </div>
                  <div className="p-3 bg-amber-50/60 dark:bg-amber-950/30 rounded-xl border border-amber-200 dark:border-amber-800/60">
                    <span className="text-[11px] font-semibold text-amber-700 dark:text-amber-400 uppercase">Duplicate Warnings</span>
                    <div className="text-lg font-bold text-amber-700 dark:text-amber-400 mt-1">
                      {previewData.duplicate_warnings_count}
                    </div>
                  </div>
                </div>

                {/* Blocking Errors or All Valid Alert */}
                {previewData.error_rows_count > 0 ? (
                  <div className="p-3.5 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 rounded-xl flex items-start justify-between gap-3">
                    <div className="flex items-start gap-2.5">
                      <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
                      <div>
                        <h5 className="text-xs font-bold text-rose-800 dark:text-rose-300">
                          Validation Errors Detected ({previewData.error_rows_count} row{previewData.error_rows_count > 1 ? 's' : ''})
                        </h5>
                        <p className="text-xs text-rose-700 dark:text-rose-400 mt-0.5">
                          Work/Service name mismatches can be fixed directly in the table using the service dropdown, or click the pencil icon to edit row details.
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleDownloadErrorReport}
                      isLoading={isDownloadingErrors}
                      leftIcon={<Download className="w-3.5 h-3.5 text-rose-600" />}
                      className="border-rose-300 text-rose-700 hover:bg-rose-100 shrink-0 text-xs"
                    >
                      Error Report (CSV)
                    </Button>
                  </div>
                ) : (
                  <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-xl flex items-center gap-2.5 animate-fadeIn">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                    <div>
                      <h5 className="text-xs font-bold text-emerald-800 dark:text-emerald-300">
                        All Rows Valid & Ready to Import
                      </h5>
                      <p className="text-xs text-emerald-700 dark:text-emerald-400">
                        All {previewData.valid_rows_count} customer orders pass validation and are ready to be imported.
                      </p>
                    </div>
                  </div>
                )}

                {/* Duplicate Warnings Banner */}
                {previewData.duplicate_warnings_count > 0 && (
                  <div className="p-3.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl space-y-2">
                    <div className="flex items-start gap-2.5">
                      <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                      <div>
                        <h5 className="text-xs font-bold text-amber-800 dark:text-amber-300">
                          Potential Duplicates Detected ({previewData.duplicate_warnings_count} row{previewData.duplicate_warnings_count > 1 ? 's' : ''})
                        </h5>
                        <p className="text-xs text-amber-700 dark:text-amber-400 mt-0.5">
                          Some entries match existing CRM orders or duplicate another row in this file. (Note: Same client at different locations is accepted).
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 pl-7">
                      <Checkbox
                        id="allow-dup-check"
                        checked={allowDuplicates}
                        onChange={(e) => setAllowDuplicates(e.target.checked)}
                      />
                      <label htmlFor="allow-dup-check" className="text-xs font-semibold text-amber-900 dark:text-amber-200 cursor-pointer">
                        Allow duplicate records (confirm if these are legitimate recurring orders)
                      </label>
                    </div>
                  </div>
                )}

                {/* Preview Table */}
                <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm">
                  <div className="px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                        Records Preview ({previewData.rows.length} rows)
                      </span>
                      <span className="text-xs text-slate-500">
                        Target Assignee: <strong className="text-slate-800 dark:text-slate-200">{selectedAssignee?.full_name || 'None'}</strong>
                      </span>
                    </div>

                    {/* Quick GST Toggle Switch in Preview Bar */}
                    <div className="flex items-center gap-2 bg-white dark:bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 shadow-2xs">
                      <span className="text-[11px] font-semibold text-slate-500 uppercase">GST:</span>
                      <label className="inline-flex items-center gap-1.5 cursor-pointer text-xs">
                        <input
                          type="radio"
                          name="preview_gst_toggle"
                          checked={!applyGst}
                          onChange={() => handleToggleGst(false)}
                          className="h-3.5 w-3.5 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-slate-600 dark:text-slate-400 text-[11px] font-medium">Without GST (0%)</span>
                      </label>
                      <label className="inline-flex items-center gap-1.5 cursor-pointer text-xs">
                        <input
                          type="radio"
                          name="preview_gst_toggle"
                          checked={applyGst}
                          onChange={() => handleToggleGst(true)}
                          className="h-3.5 w-3.5 text-emerald-600 focus:ring-emerald-500"
                        />
                        <span className="text-emerald-700 dark:text-emerald-300 font-semibold text-[11px]">Add 18% GST</span>
                      </label>
                    </div>
                  </div>

                  <div className="max-h-72 overflow-x-auto overflow-y-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 sticky top-0 z-10 uppercase font-semibold text-[11px] tracking-wider border-b border-slate-200 dark:border-slate-700 shadow-xs">
                        <tr>
                          <th className="px-3 py-2.5 bg-slate-100 dark:bg-slate-800 w-12">Row</th>
                          <th className="px-3 py-2.5 bg-slate-100 dark:bg-slate-800">Location</th>
                          <th className="px-3 py-2.5 bg-slate-100 dark:bg-slate-800">Client Name</th>
                          <th className="px-3 py-2.5 bg-slate-100 dark:bg-slate-800">Contact</th>
                          <th className="px-3 py-2.5 bg-slate-100 dark:bg-slate-800">Source</th>
                          <th className="px-3 py-2.5 bg-slate-100 dark:bg-slate-800 min-w-[180px]">Work</th>
                          {applyGst ? (
                            <>
                              <th className="px-3 py-2.5 text-right bg-slate-100 dark:bg-slate-800">Base Amount</th>
                              <th className="px-3 py-2.5 text-right bg-slate-100 dark:bg-slate-800 text-emerald-600 dark:text-emerald-400">GST (18%)</th>
                              <th className="px-3 py-2.5 text-right bg-slate-100 dark:bg-slate-800 font-bold">Total Amount</th>
                            </>
                          ) : (
                            <th className="px-3 py-2.5 text-right bg-slate-100 dark:bg-slate-800">Total Amount</th>
                          )}
                          <th className="px-3 py-2.5 text-right bg-slate-100 dark:bg-slate-800">Advance</th>
                          <th className="px-3 py-2.5 text-right bg-slate-100 dark:bg-slate-800">Incidental</th>
                          <th className="px-3 py-2.5 bg-slate-100 dark:bg-slate-800 min-w-[180px]">Status / Issues</th>
                          <th className="px-3 py-2.5 text-center bg-slate-100 dark:bg-slate-800 w-16">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                        {previewData.rows.map((r) => {
                          const isEditing = editingRowNumber === r.row_number;
                          const hasErrors = !r.is_valid;
                          const hasWarnings = r.warnings && r.warnings.length > 0;
                          const hasWorkError = (r.errors || []).some(
                            (e) => e.toLowerCase().includes('work') || e.toLowerCase().includes('service')
                          );

                          return (
                            <tr
                              key={r.row_number}
                              className={
                                isEditing
                                  ? 'bg-blue-50/60 dark:bg-blue-950/30'
                                  : hasErrors
                                  ? 'bg-rose-50/40 dark:bg-rose-950/20'
                                  : hasWarnings
                                  ? 'bg-amber-50/30 dark:bg-amber-950/20'
                                  : 'hover:bg-slate-50/50 dark:hover:bg-slate-800/40'
                              }
                            >
                              {/* Row Number */}
                              <td className="px-3 py-2 font-mono text-slate-500">
                                {formatSlNo(r.sl_no || r.row_number)}
                              </td>

                              {/* Location */}
                              <td className="px-3 py-2 text-slate-700 dark:text-slate-300">
                                {isEditing && rowEditState ? (
                                  <input
                                    type="text"
                                    value={rowEditState.location}
                                    onChange={(e) => setRowEditState({ ...rowEditState, location: e.target.value })}
                                    className="w-24 px-1.5 py-1 text-xs border rounded bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs"
                                    placeholder="Location"
                                  />
                                ) : (
                                  r.location || '—'
                                )}
                              </td>

                              {/* Client Name */}
                              <td className="px-3 py-2 font-medium text-slate-900 dark:text-white">
                                {isEditing && rowEditState ? (
                                  <input
                                    type="text"
                                    value={rowEditState.client_name}
                                    onChange={(e) => setRowEditState({ ...rowEditState, client_name: e.target.value })}
                                    className="w-28 px-1.5 py-1 text-xs border rounded bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium shadow-xs"
                                    placeholder="Client Name"
                                  />
                                ) : (
                                  r.client_name || '—'
                                )}
                              </td>

                              {/* Contact */}
                              <td className="px-3 py-2 font-mono text-slate-700 dark:text-slate-300">
                                {isEditing && rowEditState ? (
                                  <input
                                    type="text"
                                    value={rowEditState.contact}
                                    onChange={(e) => setRowEditState({ ...rowEditState, contact: e.target.value })}
                                    className="w-24 px-1.5 py-1 text-xs font-mono border rounded bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs"
                                    placeholder="Contact"
                                  />
                                ) : (
                                  r.contact || '—'
                                )}
                              </td>

                              {/* Source */}
                              <td className="px-3 py-2 text-slate-600 dark:text-slate-400">
                                {isEditing && rowEditState ? (
                                  <select
                                    value={rowEditState.source}
                                    onChange={(e) => setRowEditState({ ...rowEditState, source: e.target.value })}
                                    className="px-1.5 py-1 text-xs border rounded bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs"
                                  >
                                    {allowedLeadSources.map((src) => (
                                      <option key={src} value={src}>
                                        {src}
                                      </option>
                                    ))}
                                  </select>
                                ) : (
                                  r.source || '—'
                                )}
                              </td>

                              {/* Work / Service */}
                              <td className="px-3 py-2 text-slate-700 dark:text-slate-300 min-w-[180px]">
                                {isEditing && rowEditState ? (
                                  <select
                                    value={rowEditState.service_id}
                                    onChange={(e) => {
                                      const svc = availableServices.find((s) => s.service_id === e.target.value);
                                      setRowEditState({
                                        ...rowEditState,
                                        service_id: e.target.value,
                                        work: svc ? svc.service_name : rowEditState.work,
                                      });
                                    }}
                                    className="w-full max-w-[200px] px-1.5 py-1 text-xs border rounded bg-white dark:bg-slate-900 border-blue-400 dark:border-blue-600 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium shadow-xs"
                                  >
                                    <option value="">-- Select Service --</option>
                                    {availableServices.map((s) => (
                                      <option key={s.service_id} value={s.service_id}>
                                        {s.service_name} ({s.service_code})
                                      </option>
                                    ))}
                                  </select>
                                ) : hasWorkError ? (
                                  <div className="space-y-1 py-0.5">
                                    <div className="flex items-center gap-1.5">
                                      <span
                                        className="line-through text-rose-500 dark:text-rose-400 font-medium text-[11px] truncate max-w-[140px]"
                                        title={r.work || '(blank)'}
                                      >
                                        {r.work || '(blank)'}
                                      </span>
                                    </div>
                                    <select
                                      aria-label={`Fix Service for row ${formatSlNo(r.sl_no || r.row_number)}`}
                                      value=""
                                      onChange={(e) => handleQuickFixService(r.row_number, e.target.value)}
                                      className="w-full min-w-[160px] text-[11px] py-1 px-1.5 bg-rose-50/90 dark:bg-rose-950/60 border border-rose-300 dark:border-rose-700 rounded text-slate-800 dark:text-slate-100 font-semibold focus:outline-none focus:ring-2 focus:ring-rose-500 shadow-xs cursor-pointer"
                                    >
                                      <option value="" disabled>
                                        👉 Fix: Select Service...
                                      </option>
                                      {availableServices.map((s) => (
                                        <option key={s.service_id} value={s.service_id}>
                                          {s.service_name} ({s.service_code})
                                        </option>
                                      ))}
                                    </select>
                                  </div>
                                ) : (
                                  <span className="font-medium text-slate-800 dark:text-slate-200">
                                    {r.service_name || r.work || '—'}
                                  </span>
                                )}
                              </td>

                              {/* Amount Columns */}
                              {applyGst ? (
                                <>
                                  {/* Base Amount */}
                                  <td className="px-3 py-2 text-right font-medium text-slate-700 dark:text-slate-300">
                                    {isEditing && rowEditState ? (
                                      <input
                                        type="number"
                                        value={rowEditState.total_amount}
                                        onChange={(e) => setRowEditState({ ...rowEditState, total_amount: e.target.value })}
                                        className="w-20 px-1.5 py-1 text-xs text-right border rounded bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium shadow-xs"
                                        placeholder="Base"
                                      />
                                    ) : (
                                      formatInr(r.base_amount ?? r.total_amount)
                                    )}
                                  </td>

                                  {/* GST (18%) */}
                                  <td className="px-3 py-2 text-right font-medium text-emerald-600 dark:text-emerald-400">
                                    {isEditing && rowEditState ? (
                                      formatInr(Math.round((parseFloat(rowEditState.total_amount) || 0) * 18) / 100)
                                    ) : (
                                      formatInr(r.gst_amount ?? (r.total_amount ? Math.round(Number(r.total_amount) * 18) / 100 : 0))
                                    )}
                                  </td>

                                  {/* Final Total */}
                                  <td className="px-3 py-2 text-right font-bold text-slate-900 dark:text-white">
                                    {isEditing && rowEditState ? (
                                      formatInr(
                                        (parseFloat(rowEditState.total_amount) || 0) +
                                        Math.round((parseFloat(rowEditState.total_amount) || 0) * 18) / 100
                                      )
                                    ) : (
                                      formatInr(r.total_amount)
                                    )}
                                  </td>
                                </>
                              ) : (
                                /* Total Amount (Flat) */
                                <td className="px-3 py-2 text-right font-medium text-slate-900 dark:text-white">
                                  {isEditing && rowEditState ? (
                                    <input
                                      type="number"
                                      value={rowEditState.total_amount}
                                      onChange={(e) => setRowEditState({ ...rowEditState, total_amount: e.target.value })}
                                      className="w-20 px-1.5 py-1 text-xs text-right border rounded bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium shadow-xs"
                                      placeholder="0"
                                    />
                                  ) : (
                                    formatInr(r.total_amount)
                                  )}
                                </td>
                              )}

                              {/* Advance Amount */}
                              <td className="px-3 py-2 text-right text-slate-700 dark:text-slate-300 font-medium">
                                {isEditing && rowEditState ? (
                                  <input
                                    type="number"
                                    value={rowEditState.advance_amount}
                                    onChange={(e) => setRowEditState({ ...rowEditState, advance_amount: e.target.value })}
                                    className="w-20 px-1.5 py-1 text-xs text-right border rounded bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium shadow-xs"
                                    placeholder="0"
                                  />
                                ) : (
                                  formatInr(r.advance_amount)
                                )}
                              </td>

                              {/* Incidental */}
                              <td className="px-3 py-2 text-right text-slate-600 dark:text-slate-400">
                                {isEditing && rowEditState ? (
                                  <input
                                    type="number"
                                    value={rowEditState.incidental_cost}
                                    onChange={(e) => setRowEditState({ ...rowEditState, incidental_cost: e.target.value })}
                                    className="w-16 px-1.5 py-1 text-xs text-right border rounded bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-xs"
                                    placeholder="0"
                                  />
                                ) : (
                                  formatInr(r.incidental_cost)
                                )}
                              </td>

                              {/* Status / Issues */}
                              <td className="px-3 py-2 min-w-[180px]">
                                {hasErrors ? (
                                  <span className="inline-flex items-start gap-1 text-[11px] font-semibold text-rose-600 dark:text-rose-400">
                                    <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                                    <span>{r.errors.join('; ')}</span>
                                  </span>
                                ) : hasWarnings ? (
                                  <span className="inline-flex items-start gap-1 text-[11px] font-medium text-amber-600 dark:text-amber-400">
                                    <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                                    <span>{r.warnings.join('; ')}</span>
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
                                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                                    Valid
                                  </span>
                                )}
                              </td>

                              {/* Action Column */}
                              <td className="px-3 py-2 text-center w-16">
                                {isEditing ? (
                                  <div className="flex items-center gap-1 justify-center">
                                    <button
                                      type="button"
                                      onClick={() => handleSaveEditRow(r.row_number)}
                                      className="p-1 rounded bg-emerald-600 text-white hover:bg-emerald-700 shadow-xs transition-colors"
                                      title="Save row"
                                      aria-label={`Save row ${formatSlNo(r.sl_no || r.row_number)}`}
                                    >
                                      <Check className="w-3.5 h-3.5" />
                                    </button>
                                    <button
                                      type="button"
                                      onClick={handleCancelEditRow}
                                      className="p-1 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-300 transition-colors"
                                      title="Cancel"
                                      aria-label={`Cancel editing row ${formatSlNo(r.sl_no || r.row_number)}`}
                                    >
                                      <X className="w-3.5 h-3.5" />
                                    </button>
                                  </div>
                                ) : (
                                  <button
                                    type="button"
                                    onClick={() => handleStartEditRow(r)}
                                    className="p-1 text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded transition-colors"
                                    title="Edit row details"
                                    aria-label={`Edit row ${formatSlNo(r.sl_no || r.row_number)}`}
                                  >
                                    <Pencil className="w-3.5 h-3.5" />
                                  </button>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Import Confirmation Bar */}
                <div className="p-4 bg-slate-50 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div>
                    <h5 className="text-xs font-bold text-slate-900 dark:text-white">
                      Confirm Import and Operations Assignment
                    </h5>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Importing {previewData.valid_rows_count} entries to <strong>{selectedAssignee?.full_name}</strong>. Transactions are atomic.
                    </p>
                  </div>
                  <div className="flex items-center gap-2.5">
                    <Button variant="outline" size="sm" onClick={onClose} disabled={isImporting}>
                      Cancel
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={handleConfirmImport}
                      isLoading={isImporting}
                      disabled={
                        !previewData.can_import ||
                        (previewData.duplicate_warnings_count > 0 && !allowDuplicates) ||
                        !selectedAssigneeId
                      }
                      leftIcon={<ArrowRight className="w-4 h-4" />}
                    >
                      Import All Entries ({previewData.valid_rows_count})
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Modal>
  );
};

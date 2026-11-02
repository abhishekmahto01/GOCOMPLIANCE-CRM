/**
 * Utility functions for formatting amounts and metrics in GoCompliance CRM.
 */

export interface GovtFeesObject {
  govt_fees?: number | string | null;
  govt_fee?: number | string | null;
  government_fees?: number | string | null;
  formatted_govt_fees?: string | null;
}

export function formatGovtFees(
  feesOrTask?: number | string | null | GovtFeesObject,
  formatted?: string | null
): string {
  let fees: number | string | null | undefined;
  let formattedStr: string | null | undefined = formatted;

  if (feesOrTask && typeof feesOrTask === 'object') {
    fees = feesOrTask.govt_fees ?? feesOrTask.govt_fee ?? feesOrTask.government_fees;
    formattedStr = formattedStr || feesOrTask.formatted_govt_fees;
  } else {
    fees = feesOrTask as number | string | null | undefined;
  }

  if (fees === null || fees === undefined || fees === '') {
    return formattedStr && formattedStr !== '₹0' ? formattedStr : '-';
  }
  const num = typeof fees === 'string' ? parseFloat(fees) : Number(fees);
  if (isNaN(num)) {
    return formattedStr && formattedStr !== '₹0' ? formattedStr : '-';
  }
  if (num === 0) {
    return '₹0';
  }
  if (formattedStr) {
    return formattedStr;
  }
  return `₹${num.toLocaleString('en-IN')}`;
}

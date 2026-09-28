export type LicenseStatus = 'ACTIVE' | 'INACTIVE';
export type LicenseCategory = 'LICENCE' | 'REGISTRATION' | 'INCORPORATION' | 'COMPLIANCE' | 'OTHER';

export interface License {
  service_id: string;
  service_code: string;
  service_name: string;
  category: string;
  description: string | null;
  base_price: number;
  govt_fee: number;
  standard_turnaround_days: number;
  status: LicenseStatus;
  created_at: string;
  updated_at: string;
}

export interface LicenseCreatePayload {
  service_name: string;
  service_code: string;
  category: string;
  description?: string | null;
  base_price?: number;
  govt_fee?: number;
  standard_turnaround_days?: number;
  status?: LicenseStatus;
}

export interface LicenseUpdatePayload {
  service_name?: string;
  category?: string;
  description?: string | null;
  base_price?: number;
  govt_fee?: number;
  standard_turnaround_days?: number;
  status?: LicenseStatus;
}

export type CompanyStatus = 'ACTIVE' | 'INACTIVE';

export interface Company {
  company_id: string;
  company_code: string;
  company_name: string;
  legal_name: string | null;
  employee_code_prefix: string;
  next_employee_number: number;
  status: CompanyStatus;
  created_at: string;
  updated_at: string;
}

export interface CompanyCreatePayload {
  company_code: string;
  company_name: string;
  legal_name?: string | null;
  employee_code_prefix: string;
  next_employee_number?: number;
  status?: CompanyStatus;
}

export interface CompanyUpdatePayload {
  company_name?: string;
  legal_name?: string | null;
  status?: CompanyStatus;
}

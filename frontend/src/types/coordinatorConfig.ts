/**
 * TypeScript interfaces for Operations Coordinator Configuration per company.
 */

export interface OperationsCoordinatorConfigItem {
  config_id: string;
  company_id: string;
  company_name: string;
  company_code: string;
  coordinator_user_id?: string | null;
  coordinator_name?: string | null;
  coordinator_employee_code?: string | null;
  coordinator_email?: string | null;
  coordinator_department_name?: string | null;
  updated_by_user_id?: string | null;
  updated_by_name?: string | null;
  updated_at: string;
}

export interface EligibleCoordinatorOption {
  user_id: string;
  employee_code: string;
  full_name: string;
  email?: string | null;
  company_id: string;
  company_name: string;
  company_code: string;
  department_name?: string | null;
  designation_name?: string | null;
}

export interface CoordinatorConfigUpdatePayload {
  company_id: string;
  coordinator_user_id?: string | null;
}

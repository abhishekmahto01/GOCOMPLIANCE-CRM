export interface CompanyLookup {
  company_id: string;
  company_code: string;
  company_name: string;
  employee_code_prefix: string;
}

export interface DepartmentLookup {
  department_id: string;
  company_id: string;
  department_code: string;
  department_name: string;
}

export interface DesignationLookup {
  designation_id: string;
  company_id: string;
  designation_code: string;
  designation_name: string;
  level_rank: number;
  is_managerial: boolean;
}

export interface ManagerLookup {
  user_id: string;
  employee_code: string;
  first_name: string;
  middle_name?: string | null;
  last_name: string;
  official_email: string;
  department_name?: string | null;
  designation_name?: string | null;
}

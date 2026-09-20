export type EmploymentType =
  | 'FULL_TIME'
  | 'PART_TIME'
  | 'CONTRACT'
  | 'INTERN'
  | 'CONSULTANT';

export type AccountStatus = 'PENDING' | 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';

export interface Employee {
  user_id: string;
  employee_code: string;
  first_name: string;
  middle_name?: string | null;
  last_name: string;
  official_email: string;
  personal_email?: string | null;
  mobile_number: string;
  company_id: string;
  department_id: string;
  designation_id: string;
  manager_user_id?: string | null;
  date_of_joining: string;
  employment_type: EmploymentType;
  account_status: AccountStatus;
  company_name?: string | null;
  company_code?: string | null;
  department_name?: string | null;
  department_code?: string | null;
  designation_name?: string | null;
  designation_code?: string | null;
  manager_name?: string | null;
  manager_employee_code?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreatePayload {
  company_id: string;
  department_id: string;
  designation_id: string;
  manager_user_id?: string | null;
  first_name: string;
  middle_name?: string | null;
  last_name: string;
  official_email: string;
  personal_email?: string | null;
  mobile_number: string;
  date_of_joining: string;
  employment_type: EmploymentType;
  account_status?: AccountStatus;
}

export interface EmployeeUpdatePayload {
  company_id?: string;
  department_id?: string;
  designation_id?: string;
  manager_user_id?: string | null;
  first_name?: string;
  middle_name?: string | null;
  last_name?: string;
  official_email?: string;
  personal_email?: string | null;
  mobile_number?: string;
  date_of_joining?: string;
  employment_type?: EmploymentType;
  account_status?: AccountStatus;
}

export interface EmployeeStatusUpdatePayload {
  account_status: AccountStatus;
}

export interface PaginatedEmployees {
  items: Employee[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface EmployeeFilterParams {
  page?: number;
  page_size?: number;
  search?: string;
  company_id?: string;
  department_id?: string;
  designation_id?: string;
  manager_user_id?: string;
  account_status?: string;
}

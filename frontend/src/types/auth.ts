export interface LoginCredentials {
  identifier: string; // Official Email or Employee Code
  password: string;
  rememberMe?: boolean;
}

export interface AuthTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  must_change_password: boolean;
}

export interface DepartmentInfo {
  id: string;
  code: string;
  name: string;
}

export interface CompanyInfo {
  id: string;
  code: string;
  name: string;
}

export interface DesignationInfo {
  id: string;
  code: string;
  name: string;
}

export interface CurrentUser {
  user_id: string;
  employee_code: string;
  first_name: string;
  middle_name?: string | null;
  last_name: string;
  official_email: string;
  personal_email?: string | null;
  mobile_number?: string | null;
  company_id?: string | null;
  department_id?: string | null;
  designation_id?: string | null;
  manager_user_id?: string | null;
  account_status: 'PENDING' | 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';
  must_change_password: boolean;
  is_hod?: boolean;
  is_reporting_manager?: boolean;
  primary_location?: string | null;
  company_name?: string | null;
  company_code?: string | null;
  department_name?: string | null;
  department_code?: string | null;
  designation_name?: string | null;
  designation_code?: string | null;
  department?: DepartmentInfo | null;
  company?: CompanyInfo | null;
  designation?: DesignationInfo | null;
}

export interface FeatureItem {
  id: string;
  title: string;
  subtitle: string;
  iconName: 'Shield' | 'BarChart3' | 'Users' | 'FileCheck2' | string;
}

export interface ChangeInitialPasswordPayload {
  current_password?: string;
  new_password: string;
  confirm_password?: string;
}


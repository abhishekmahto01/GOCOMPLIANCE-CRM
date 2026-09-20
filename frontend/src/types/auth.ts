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

export interface CurrentUser {
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
  account_status: 'PENDING' | 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';
  must_change_password: boolean;
  last_login_at?: string | null;
  company_name?: string | null;
  company_code?: string | null;
  department_name?: string | null;
  department_code?: string | null;
  designation_name?: string | null;
  designation_code?: string | null;
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


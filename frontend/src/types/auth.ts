export interface LoginCredentials {
  identifier: string; // Email or Employee ID (e.g., GC0001, EP0001, BM0001)
  password: string;
  rememberMe: boolean;
}

export type IdentifierType = 'email' | 'employee_id' | 'unknown';

export interface UserRole {
  id: string;
  name: 'super_admin' | 'compliance_officer' | 'auditor' | 'company_admin' | 'employee';
  permissions: string[];
}

export interface AuthUser {
  id: string;
  employeeId?: string;
  email: string;
  firstName: string;
  lastName: string;
  companyCode?: 'GC' | 'EP' | 'BM' | string;
  role: UserRole;
  avatarUrl?: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: 'Bearer';
}

export interface AuthResponse {
  user: AuthUser;
  tokens: AuthTokens;
}

export type SocialProvider = 'google' | 'microsoft' | 'sso';

export interface FeatureItem {
  id: string;
  title: string;
  subtitle: string;
  iconName: 'Shield' | 'BarChart3' | 'Users' | 'FileCheck2' | string;
}

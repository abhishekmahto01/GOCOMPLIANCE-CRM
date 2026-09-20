import { apiClient, ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from './client';
import type { AuthTokenResponse, CurrentUser, LoginCredentials } from '../types/auth';
import type { AccessibleModule } from '../types/permission';

export async function loginApi(credentials: LoginCredentials): Promise<AuthTokenResponse> {
  const response = await apiClient.post<AuthTokenResponse>('/auth/login', {
    identifier: credentials.identifier.trim(),
    password: credentials.password,
  });
  const data = response.data;
  if (data.access_token) {
    localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
  }
  return data;
}

export async function logoutApi(): Promise<void> {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  try {
    if (refreshToken) {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken });
    }
  } finally {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
}

export async function getCurrentUserApi(): Promise<CurrentUser> {
  const response = await apiClient.get<CurrentUser>('/auth/me');
  return response.data;
}

export async function getAccessibleModulesApi(): Promise<AccessibleModule[]> {
  const response = await apiClient.get<AccessibleModule[]>('/auth/me/modules');
  return response.data;
}

export async function refreshAccessTokenApi(): Promise<AuthTokenResponse> {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }
  const response = await apiClient.post<AuthTokenResponse>('/auth/refresh', {
    refresh_token: refreshToken,
  });
  const data = response.data;
  if (data.access_token) {
    localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
  }
  return data;
}

export async function changeInitialPasswordApi(payload: {
  current_password?: string;
  new_password: string;
  confirm_password?: string;
}): Promise<{ message: string }> {
  const response = await apiClient.post<{ message: string }>(
    '/auth/change-initial-password',
    payload
  );
  return response.data;
}

export async function changePasswordApi(payload: {
  current_password: string;
  new_password: string;
}): Promise<{ message: string }> {
  const response = await apiClient.post<{ message: string }>(
    '/auth/change-password',
    payload
  );
  return response.data;
}


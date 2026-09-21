import axios, { AxiosError } from 'axios';

export const ACCESS_TOKEN_KEY = 'gocompliance_crm_access_token';
export const REFRESH_TOKEN_KEY = 'gocompliance_crm_refresh_token';

/**
 * Resolves the base API URL:
 * - When envBaseUrl / VITE_API_BASE_URL is a non-empty string, normalizes it and appends '/api'.
 * - When VITE_API_BASE_URL is explicitly empty string '' (demo/relative mode) or unset/undefined, returns '/api' for same-origin proxying.
 */
export function getApiBaseUrl(envBaseUrl?: string): string {
  const rawUrl = arguments.length > 0 ? envBaseUrl : import.meta.env.VITE_API_BASE_URL;
  if (typeof rawUrl === 'string') {
    const trimmed = rawUrl.trim();
    if (trimmed === '' || trimmed === '/') {
      return '/api';
    }
    return `${trimmed.replace(/\/+$/, '')}/api`;
  }
  return '/api';
}

export const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request Interceptor: Attach JWT Access Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: 401 Session Handling & 403 Feedback
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear session
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);

      // Redirect to login if not already there
      if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export function extractErrorMessage(error: unknown): string {
  if (error && typeof error === 'object') {
    const errObj = error as Record<string, unknown>;
    const res = errObj.response as { data?: { detail?: unknown } } | undefined;
    const detail = res?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d: { msg?: string }) => d.msg || JSON.stringify(d)).join(', ');
    }
    if (typeof errObj.message === 'string' && errObj.message) {
      return errObj.message;
    }
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred. Please try again.';
}

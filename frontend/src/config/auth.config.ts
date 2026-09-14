/**
 * Temporary Static Authentication Configuration
 * 
 * NOTE: This configuration is for development and testing purposes only.
 * When backend API authentication is ready, replace this module with API service calls.
 */

export const STATIC_AUTH_CONFIG = {
  // Static development credentials
  credentials: {
    userId: 'admin',
    password: 'admin123',
  },

  // Storage keys used for persisting session state in localStorage
  storageKeys: {
    isAuthenticated: 'isAuthenticated',
    userRole: 'userRole',
    username: 'username',
    authTimestamp: 'authTimestamp',
  },

  // Default redirect paths
  routes: {
    login: '/login',
    dashboard: '/dashboard',
  },
} as const;

export type StaticCredentials = typeof STATIC_AUTH_CONFIG.credentials;

import { STATIC_AUTH_CONFIG } from '../config/auth.config';

export interface AuthSession {
  isAuthenticated: boolean;
  username: string;
  userRole: string;
  authTimestamp?: string;
}

/**
 * Retrieve the current authentication session from localStorage
 */
export const getStoredAuthSession = (): AuthSession => {
  try {
    const isAuth = localStorage.getItem(STATIC_AUTH_CONFIG.storageKeys.isAuthenticated);
    const username = localStorage.getItem(STATIC_AUTH_CONFIG.storageKeys.username);
    const userRole = localStorage.getItem(STATIC_AUTH_CONFIG.storageKeys.userRole);
    const authTimestamp = localStorage.getItem(STATIC_AUTH_CONFIG.storageKeys.authTimestamp);

    return {
      isAuthenticated: isAuth === 'true',
      username: username || '',
      userRole: userRole || '',
      authTimestamp: authTimestamp || undefined,
    };
  } catch (err) {
    console.error('Error reading auth session from storage:', err);
    return {
      isAuthenticated: false,
      username: '',
      userRole: '',
    };
  }
};

/**
 * Persist authentication session to localStorage
 */
export const setStoredAuthSession = (username: string, userRole: string = 'admin'): void => {
  try {
    localStorage.setItem(STATIC_AUTH_CONFIG.storageKeys.isAuthenticated, 'true');
    localStorage.setItem(STATIC_AUTH_CONFIG.storageKeys.username, username);
    localStorage.setItem(STATIC_AUTH_CONFIG.storageKeys.userRole, userRole);
    localStorage.setItem(STATIC_AUTH_CONFIG.storageKeys.authTimestamp, new Date().toISOString());
  } catch (err) {
    console.error('Error writing auth session to storage:', err);
  }
};

/**
 * Clear authentication session from localStorage
 */
export const clearStoredAuthSession = (): void => {
  try {
    localStorage.removeItem(STATIC_AUTH_CONFIG.storageKeys.isAuthenticated);
    localStorage.removeItem(STATIC_AUTH_CONFIG.storageKeys.username);
    localStorage.removeItem(STATIC_AUTH_CONFIG.storageKeys.userRole);
    localStorage.removeItem(STATIC_AUTH_CONFIG.storageKeys.authTimestamp);
  } catch (err) {
    console.error('Error clearing auth session from storage:', err);
  }
};

/**
 * Validate credentials against static dev configuration
 */
export const validateStaticCredentials = (
  userIdInput: string,
  passwordInput: string
): { success: boolean; error?: string } => {
  const trimmedId = userIdInput.trim();
  const trimmedPassword = passwordInput.trim();

  // Basic empty validation
  if (!trimmedId) {
    return { success: false, error: 'User ID cannot be empty.' };
  }

  if (!trimmedPassword) {
    return { success: false, error: 'Password cannot be empty.' };
  }

  // Check static credentials
  if (
    trimmedId === STATIC_AUTH_CONFIG.credentials.userId &&
    trimmedPassword === STATIC_AUTH_CONFIG.credentials.password
  ) {
    return { success: true };
  }

  return { success: false, error: 'Invalid User ID or Password' };
};

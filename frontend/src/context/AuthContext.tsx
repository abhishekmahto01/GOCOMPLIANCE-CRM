import React, { createContext, useContext, useState, useEffect, useTransition } from 'react';
import {
  getStoredAuthSession,
  setStoredAuthSession,
  clearStoredAuthSession,
  validateStaticCredentials,
} from '../utils/auth';
import type { AuthSession } from '../utils/auth';

interface AuthContextType {
  session: AuthSession;
  isAuthenticated: boolean;
  login: (userId: string, password: string) => { success: boolean; error?: string };
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<AuthSession>(() => getStoredAuthSession());
  const [, startTransition] = useTransition();

  // Listen for storage changes across tabs/windows
  useEffect(() => {
    const handleStorageChange = () => {
      startTransition(() => {
        setSession(getStoredAuthSession());
      });
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = (userId: string, password: string): { success: boolean; error?: string } => {
    const result = validateStaticCredentials(userId, password);

    if (result.success) {
      setStoredAuthSession(userId.trim(), 'admin');
      setSession({
        isAuthenticated: true,
        username: userId.trim(),
        userRole: 'admin',
        authTimestamp: new Date().toISOString(),
      });
      return { success: true };
    }

    return { success: false, error: result.error || 'Invalid User ID or Password' };
  };

  const logout = (): void => {
    clearStoredAuthSession();
    setSession({
      isAuthenticated: false,
      username: '',
      userRole: '',
    });
  };

  return (
    <AuthContext.Provider
      value={{
        session,
        isAuthenticated: session.isAuthenticated,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

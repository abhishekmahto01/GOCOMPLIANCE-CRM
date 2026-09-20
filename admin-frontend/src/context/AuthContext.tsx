import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { CurrentUser, LoginCredentials } from '../types/auth';
import { AccessibleModule, ActionType, DataScope } from '../types/permission';
import {
  getCurrentUserApi,
  getAccessibleModulesApi,
  loginApi,
  logoutApi,
} from '../api/auth';
import { ACCESS_TOKEN_KEY } from '../api/client';

interface AuthContextType {
  user: CurrentUser | null;
  modules: AccessibleModule[];
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshUserProfile: () => Promise<void>;
  hasPermission: (moduleCode: string, action: ActionType) => boolean;
  getEffectiveScope: (moduleCode: string) => DataScope | null;
  canAccessModule: (moduleCode: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [modules, setModules] = useState<AccessibleModule[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const loadUserData = useCallback(async () => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) {
      setUser(null);
      setModules([]);
      setIsLoading(false);
      return;
    }

    try {
      const [userData, userModules] = await Promise.all([
        getCurrentUserApi(),
        getAccessibleModulesApi(),
      ]);
      setUser(userData);
      setModules(userModules);
    } catch (err) {
      console.error('Failed to load user profile/modules:', err);
      setUser(null);
      setModules([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUserData();
  }, [loadUserData]);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    try {
      await loginApi(credentials);
      await loadUserData();
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await logoutApi();
    } catch (err) {
      console.error('Error during logout:', err);
    } finally {
      setUser(null);
      setModules([]);
      setIsLoading(false);
    }
  };

  const hasPermission = useCallback(
    (moduleCode: string, action: ActionType): boolean => {
      const targetCode = moduleCode.trim().toUpperCase();
      const mod = modules.find((m) => m.module_code.toUpperCase() === targetCode);
      if (!mod || !mod.can_view) return false;

      switch (action) {
        case 'view':
          return mod.can_view;
        case 'create':
          return mod.can_create;
        case 'edit':
          return mod.can_edit;
        case 'delete':
          return mod.can_delete;
        case 'approve':
          return mod.can_approve;
        default:
          return false;
      }
    },
    [modules]
  );

  const getEffectiveScope = useCallback(
    (moduleCode: string): DataScope | null => {
      const targetCode = moduleCode.trim().toUpperCase();
      const mod = modules.find((m) => m.module_code.toUpperCase() === targetCode);
      if (!mod || !mod.can_view) return null;
      return mod.data_scope;
    },
    [modules]
  );

  const canAccessModule = useCallback(
    (moduleCode: string): boolean => {
      return hasPermission(moduleCode, 'view');
    },
    [hasPermission]
  );

  const value: AuthContextType = {
    user,
    modules,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshUserProfile: loadUserData,
    hasPermission,
    getEffectiveScope,
    canAccessModule,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { CurrentUser, LoginCredentials } from '../types/auth';
import type { AccessibleModule, ActionType, DataScope } from '../types/permission';
import {
  getCurrentUserApi,
  getAccessibleModulesApi,
  loginApi,
  logoutApi,
} from '../api/auth';
import { ACCESS_TOKEN_KEY } from '../api/client';

export interface AuthSession {
  isAuthenticated: boolean;
  username: string;
  userRole: string;
  employeeCode?: string;
  email?: string;
  department?: string;
  designation?: string;
  company?: string;
  authTimestamp?: string;
}

interface AuthContextType {
  user: CurrentUser | null;
  modules: AccessibleModule[];
  session: AuthSession;
  isAuthenticated: boolean;
  mustChangePassword: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<{ must_change_password: boolean }>;
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
      const userData = await getCurrentUserApi();
      setUser(userData);

      if (!userData.must_change_password) {
        try {
          const userModules = await getAccessibleModulesApi();
          setModules(userModules);
        } catch (mErr) {
          console.error('Failed to load modules:', mErr);
          setModules([]);
        }
      } else {
        setModules([]);
      }
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
      const authRes = await loginApi(credentials);
      await loadUserData();
      return { must_change_password: !!authRes.must_change_password };
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

  function findModuleRecursively(list: AccessibleModule[], code: string): AccessibleModule | null {
    for (const m of list) {
      if (m.module_code.toUpperCase() === code) return m;
      if (m.child_modules && m.child_modules.length > 0) {
        const found = findModuleRecursively(m.child_modules, code);
        if (found) return found;
      }
    }
    return null;
  }

  const hasPermission = useCallback(
    (moduleCode: string, action: ActionType): boolean => {
      const targetCode = moduleCode.trim().toUpperCase();
      const mod = findModuleRecursively(modules, targetCode);
      if (!mod || !mod.can_view) return false;

      switch (action) {
        case 'view':
        case 'read':
          return mod.can_view;
        case 'create':
        case 'write':
          return mod.can_create;
        case 'edit':
        case 'update':
          return mod.can_edit;
        case 'delete':
          return mod.can_delete;
        case 'approve':
          return mod.can_approve;
        case 'assign':
          return Boolean(mod.can_assign);
        case 'reassign':
          return Boolean(mod.can_reassign);
        case 'export':
          return Boolean(mod.can_export);
        default:
          return false;
      }
    },
    [modules]
  );

  const getEffectiveScope = useCallback(
    (moduleCode: string): DataScope | null => {
      const targetCode = moduleCode.trim().toUpperCase();
      const mod = findModuleRecursively(modules, targetCode);
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

  const session: AuthSession = {
    isAuthenticated: !!user,
    username: user
      ? `${user.first_name} ${user.last_name}`.trim() || user.employee_code
      : '',
    userRole: user?.designation_name || user?.account_status || '',
    employeeCode: user?.employee_code || '',
    email: user?.official_email || '',
    department: user?.department_name || '',
    designation: user?.designation_name || '',
    company: user?.company_name || '',
  };

  const value: AuthContextType = {
    user,
    modules,
    session,
    isAuthenticated: !!user,
    mustChangePassword: user?.must_change_password ?? false,
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

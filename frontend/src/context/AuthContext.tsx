import React, { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';
import type { CurrentUser, LoginCredentials } from '../types/auth';
import type { AccessibleModule, ActionType, DataScope } from '../types/permission';
import {
  getCurrentUserApi,
  getAccessibleModulesApi,
  loginApi,
  logoutApi,
} from '../api/auth';
import { getAccessToken } from '../api/client';

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

export interface AuthContextType {
  user: CurrentUser | null;
  modules: AccessibleModule[];
  session: AuthSession;
  isAuthenticated: boolean;
  mustChangePassword: boolean;
  isLoading: boolean;
  permissionError: string | null;
  login: (credentials: LoginCredentials) => Promise<{ must_change_password: boolean }>;
  logout: () => Promise<void>;
  refreshUserProfile: () => Promise<void>;
  hasPermission: (
    moduleOrPageCode: string,
    actionOrPageCode?: ActionType | string,
    action?: ActionType
  ) => boolean;
  getEffectiveScope: (moduleCode: string) => DataScope | null;
  canAccessModule: (moduleCode: string) => boolean;
  hasModuleAccess: (moduleCode: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function normalizeModuleCode(code: string): string {
  const c = code.trim().toUpperCase();
  if (c === 'OPERATION' || c === 'OPERATIONS') return 'OPERATIONS';
  if (c === 'SALES' || c === 'SALE') return 'SALES';
  if (c === 'ADMIN' || c === 'ADMINISTRATION') return 'ADMIN';
  return c;
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [modules, setModules] = useState<AccessibleModule[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [permissionError, setPermissionError] = useState<string | null>(null);

  const loadUserData = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setUser(null);
      setModules([]);
      setPermissionError(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setPermissionError(null);
    try {
      const userData = await getCurrentUserApi();
      setUser(userData);

      if (!userData.must_change_password) {
        try {
          const userModules = await getAccessibleModulesApi();
          setModules(userModules);
          setPermissionError(null);
        } catch (mErr: unknown) {
          console.error('Failed to load modules:', mErr);
          setModules([]);
          const errMessage =
            (mErr as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail ||
            (mErr as Error)?.message ||
            'Failed to load user permissions';
          setPermissionError(errMessage);
        }
      } else {
        setModules([]);
        setPermissionError(null);
      }
    } catch (err: unknown) {
      console.error('Failed to load user profile/modules:', err);
      setUser(null);
      setModules([]);
      const errMessage =
        (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail ||
        (err as Error)?.message ||
        'Failed to authenticate user';
      setPermissionError(errMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUserData();
  }, [loadUserData]);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setUser(null);
    setModules([]);
    setPermissionError(null);
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
      setPermissionError(null);
      setIsLoading(false);
    }
  };

  function findModuleRecursively(list: AccessibleModule[], code: string): AccessibleModule | null {
    const target = code.trim().toUpperCase();
    for (const m of list) {
      if (m.module_code.toUpperCase() === target) return m;
      if (m.child_modules && m.child_modules.length > 0) {
        const found = findModuleRecursively(m.child_modules, target);
        if (found) return found;
      }
    }
    return null;
  }

  // Backend-confirmed Super Admin check
  const isSuperAdmin = useMemo(() => {
    if (
      user?.employee_code === 'CG0001' ||
      user?.designation?.name?.toLowerCase().includes('super admin') ||
      user?.designation_name?.toLowerCase().includes('super admin')
    ) {
      return true;
    }
    return modules.some(
      (m) =>
        m.module_code === 'ADMIN_ACCESS' &&
        m.data_scope === 'ALL' &&
        m.can_view &&
        m.can_edit
    );
  }, [modules, user]);

  const hasModuleAccess = useCallback(
    (moduleCode: string): boolean => {
      if (!moduleCode) return false;
      if (isSuperAdmin) return true;

      const norm = normalizeModuleCode(moduleCode);

      // Check direct module access
      const directMod = findModuleRecursively(modules, norm);
      if (directMod && directMod.can_view) return true;

      // Special aliases: OPERATIONS vs OPERATION
      if (norm === 'OPERATIONS') {
        const altMod = findModuleRecursively(modules, 'OPERATION');
        if (altMod && altMod.can_view) return true;
      }

      // Check if user has view permission on any child page belonging to this module
      const hasChildPermission = modules.some((m) => {
        if (!m.can_view) return false;
        const codeUpper = m.module_code.toUpperCase();
        if (norm === 'SALES' && codeUpper.startsWith('SALES_')) return true;
        if (
          norm === 'OPERATIONS' &&
          (codeUpper.startsWith('OPERATION_') || codeUpper.startsWith('OPERATIONS_'))
        ) {
          return true;
        }
        if (norm === 'ADMIN' && codeUpper.startsWith('ADMIN_')) return true;
        return false;
      });

      return hasChildPermission;
    },
    [modules, isSuperAdmin]
  );

  const hasPermission = useCallback(
    (
      moduleOrPageCode: string,
      actionOrPageCode?: ActionType | string,
      action?: ActionType
    ): boolean => {
      if (!moduleOrPageCode) return false;

      let targetCode: string;
      let targetAction: ActionType = 'view';

      const validActions: ActionType[] = [
        'view',
        'read',
        'create',
        'write',
        'edit',
        'update',
        'delete',
        'approve',
        'assign',
        'reassign',
        'export',
      ];

      if (typeof actionOrPageCode === 'string' && action !== undefined) {
        // Called as hasPermission(moduleCode, pageCode, action)
        const pageNorm = actionOrPageCode.trim().toUpperCase();
        const modNorm = normalizeModuleCode(moduleOrPageCode);
        targetCode = pageNorm.startsWith(`${modNorm}_`) ? pageNorm : `${modNorm}_${pageNorm}`;
        targetAction = action;
      } else if (
        typeof actionOrPageCode === 'string' &&
        validActions.includes(actionOrPageCode.toLowerCase() as ActionType)
      ) {
        // Called as hasPermission(code, action)
        targetCode = moduleOrPageCode.trim().toUpperCase();
        targetAction = actionOrPageCode.toLowerCase() as ActionType;
      } else if (typeof actionOrPageCode === 'string') {
        // Called as hasPermission(moduleCode, pageCode) with default 'view'
        const pageNorm = actionOrPageCode.trim().toUpperCase();
        const modNorm = normalizeModuleCode(moduleOrPageCode);
        targetCode = pageNorm.startsWith(`${modNorm}_`) ? pageNorm : `${modNorm}_${pageNorm}`;
        targetAction = 'view';
      } else {
        // Called as hasPermission(code) with default 'view'
        targetCode = moduleOrPageCode.trim().toUpperCase();
        targetAction = 'view';
      }

      if (isSuperAdmin) {
        return true;
      }

      const mod = findModuleRecursively(modules, targetCode);
      if (!mod || !mod.can_view) return false;

      let hasDirect = false;
      switch (targetAction) {
        case 'view':
        case 'read':
          hasDirect = mod.can_view;
          break;
        case 'create':
        case 'write':
          hasDirect = mod.can_create;
          break;
        case 'edit':
        case 'update':
          hasDirect = mod.can_edit;
          break;
        case 'delete':
          hasDirect = mod.can_delete;
          break;
        case 'approve':
          hasDirect = mod.can_approve;
          break;
        case 'assign':
          hasDirect = Boolean(mod.can_assign);
          break;
        case 'reassign':
          hasDirect = Boolean(mod.can_reassign);
          break;
        case 'export':
          hasDirect = Boolean(mod.can_export);
          break;
        default:
          hasDirect = false;
      }
      if (hasDirect) return true;

      // If checking parent module (e.g. SALES, OPERATIONS, ADMIN), check child module pages
      return modules.some((m) => {
        if (!m.can_view) return false;
        const codeUpper = m.module_code.toUpperCase();
        const matchesParent =
          (targetCode === 'SALES' && codeUpper.startsWith('SALES_')) ||
          (targetCode === 'OPERATIONS' && (codeUpper.startsWith('OPERATION_') || codeUpper.startsWith('OPERATIONS_'))) ||
          (targetCode === 'ADMIN' && codeUpper.startsWith('ADMIN_'));
        if (!matchesParent) return false;

        switch (targetAction) {
          case 'view':
          case 'read':
            return m.can_view;
          case 'create':
          case 'write':
            return m.can_create;
          case 'edit':
          case 'update':
            return m.can_edit;
          case 'delete':
            return m.can_delete;
          case 'approve':
            return m.can_approve;
          case 'assign':
            return Boolean(m.can_assign);
          case 'reassign':
            return Boolean(m.can_reassign);
          case 'export':
            return Boolean(m.can_export);
          default:
            return false;
        }
      });
    },
    [modules, isSuperAdmin]
  );

  const getEffectiveScope = useCallback(
    (moduleCode: string): DataScope | null => {
      if (isSuperAdmin) return 'ALL';
      const targetCode = moduleCode.trim().toUpperCase();
      const mod = findModuleRecursively(modules, targetCode);
      if (!mod || !mod.can_view) return null;
      return mod.data_scope;
    },
    [modules, isSuperAdmin]
  );

  const canAccessModule = useCallback(
    (moduleCode: string): boolean => {
      return hasModuleAccess(moduleCode);
    },
    [hasModuleAccess]
  );

  const session: AuthSession = {
    isAuthenticated: !!user,
    username: user
      ? `${user.first_name} ${user.last_name}`.trim() || user.employee_code
      : '',
    userRole: user?.designation?.name || user?.designation_name || user?.account_status || '',
    employeeCode: user?.employee_code || '',
    email: user?.official_email || '',
    department: user?.department?.name || user?.department_name || '',
    designation: user?.designation?.name || user?.designation_name || '',
    company: user?.company?.name || user?.company_name || '',
  };

  const value: AuthContextType = {
    user,
    modules,
    session,
    isAuthenticated: !!user,
    mustChangePassword: user?.must_change_password ?? false,
    isLoading,
    permissionError,
    login,
    logout,
    refreshUserProfile: loadUserData,
    hasPermission,
    getEffectiveScope,
    canAccessModule,
    hasModuleAccess,
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

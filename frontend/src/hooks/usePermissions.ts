import { useMemo, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import type { ActionType, DataScope } from '../types/permission';

export function usePermissions() {
  const { user, modules, hasPermission, getEffectiveScope, canAccessModule } = useAuth();

  // Standard permission check by module/page code and action
  const can = useCallback(
    (moduleOrPageCode: string, action: ActionType = 'view'): boolean => {
      return hasPermission(moduleOrPageCode, action);
    },
    [hasPermission]
  );

  // Permission check by canonical slug (e.g. "sales.dashboard.read", "operation.tasks.assign")
  const canSlug = useCallback(
    (slug: string): boolean => {
      if (!slug) return false;
      const parts = slug.toLowerCase().split('.');
      if (parts.length < 3) return false;

      const [moduleGroup, pageSubgroup, actionKey] = parts;

      // Construct likely page codes
      const candidateCodes = [
        `${moduleGroup.toUpperCase()}_${pageSubgroup.toUpperCase()}`,
        slug.toUpperCase().replace(/\./g, '_'),
      ];

      for (const code of candidateCodes) {
        if (hasPermission(code, actionKey as ActionType)) {
          return true;
        }
      }

      // Check root module if page code wasn't directly found
      return hasPermission(moduleGroup.toUpperCase(), actionKey as ActionType);
    },
    [hasPermission]
  );

  // Check if user can view/access a module or page
  const hasAccess = useCallback(
    (moduleOrPageCode: string): boolean => {
      return canAccessModule(moduleOrPageCode);
    },
    [canAccessModule]
  );

  // Get data scope
  const getScope = useCallback(
    (moduleOrPageCode: string): DataScope | null => {
      return getEffectiveScope(moduleOrPageCode);
    },
    [getEffectiveScope]
  );

  const isHod = useMemo(() => Boolean(user?.is_hod), [user]);
  const isReportingManager = useMemo(() => Boolean(user?.is_reporting_manager), [user]);

  return {
    user,
    modules,
    can,
    canSlug,
    hasAccess,
    getScope,
    isHod,
    isReportingManager,
  };
}

export default usePermissions;

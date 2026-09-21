import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import type { ActionType } from '../../types/permission';

interface ProtectedRouteProps {
  children: React.ReactElement;
  requiredModule?: string;
  requiredAction?: ActionType;
}

/**
 * Route guard that requires the user to be authenticated.
 * If not authenticated, redirects to /login while preserving location state.
 * If user lacks required module permission, redirects to /unauthorized.
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredModule,
  requiredAction = 'view',
}) => {
  const { isAuthenticated, mustChangePassword, isLoading, hasPermission, hasModuleAccess } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
            Verifying authentication...
          </span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Force mandatory password change on restricted first-login session
  if (mustChangePassword) {
    return <Navigate to="/change-password-required" replace />;
  }

  if (requiredModule) {
    const hasAccess =
      hasPermission(requiredModule, requiredAction) ||
      (requiredAction === 'view' && hasModuleAccess(requiredModule));
    if (!hasAccess) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return children;
};

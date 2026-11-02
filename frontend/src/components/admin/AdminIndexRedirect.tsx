import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { resolveActiveModule } from '../../utils/routeResolver';

export const AdminIndexRedirect: React.FC = () => {
  const { hasPermission, isLoading } = useAuth();
  const location = useLocation();
  const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
  const { basePath } = resolveActiveModule(hostname, location.pathname);
  const prefix = basePath === '/' ? '' : basePath;

  if (isLoading) {
    return (
      <div className="min-h-[300px] w-full flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // 1. Employee List if permitted
  if (hasPermission('ADMIN_EMPLOYEES', 'view') || hasPermission('ADMIN_EMPLOYEES', 'read')) {
    return <Navigate to={`${prefix}/employees`} replace />;
  }

  // 2. Add Employee if creation is permitted
  if (hasPermission('ADMIN_EMPLOYEES', 'create') || hasPermission('ADMIN_EMPLOYEES', 'write')) {
    return <Navigate to={`${prefix}/employees/new`} replace />;
  }

  // 3. User Control / Access Control if permitted
  if (hasPermission('ADMIN_ACCESS', 'view') || hasPermission('ADMIN_ACCESS', 'read')) {
    return <Navigate to={`${prefix}/access`} replace />;
  }

  // 4. Company Master if permitted
  if (hasPermission('ADMIN_COMPANIES', 'view') || hasPermission('ADMIN_COMPANIES', 'read')) {
    return <Navigate to={`${prefix}/companies`} replace />;
  }

  // 5. Department Master if permitted
  if (hasPermission('ADMIN_DEPARTMENTS', 'view') || hasPermission('ADMIN_DEPARTMENTS', 'read')) {
    return <Navigate to={`${prefix}/departments`} replace />;
  }

  // 6. Designation Master if permitted
  if (hasPermission('ADMIN_DESIGNATIONS', 'view') || hasPermission('ADMIN_DESIGNATIONS', 'read')) {
    return <Navigate to={`${prefix}/designations`} replace />;
  }

  // 7. License Master if permitted
  if (hasPermission('ADMIN_LICENSES', 'view') || hasPermission('ADMIN_LICENSES', 'read')) {
    return <Navigate to={`${prefix}/licenses`} replace />;
  }

  // 8. Fallback to 403 Unauthorized
  return <Navigate to="/unauthorized" replace />;
};

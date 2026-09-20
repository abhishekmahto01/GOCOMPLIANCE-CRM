import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const AdminIndexRedirect: React.FC = () => {
  const { hasPermission, canAccessModule, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-[300px] w-full flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // 1. Employee List if permitted
  if (hasPermission('ADMIN_EMPLOYEES', 'view')) {
    return <Navigate to="/admin/employees" replace />;
  }

  // 2. Add Employee if creation is permitted
  if (hasPermission('ADMIN_EMPLOYEES', 'create')) {
    return <Navigate to="/admin/employees/new" replace />;
  }

  // 3. User Control / Access Control if Admin module permitted
  if (canAccessModule('ADMIN') || hasPermission('ADMIN_ACCESS', 'view')) {
    return <Navigate to="/admin/access" replace />;
  }

  // 4. Fallback to 403 Unauthorized
  return <Navigate to="/unauthorized" replace />;
};

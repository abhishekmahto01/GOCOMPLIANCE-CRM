import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const SalesIndexRedirect: React.FC = () => {
  const { hasPermission, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-[300px] w-full flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // 1. Sales Dashboard if permitted
  if (hasPermission('SALES_DASHBOARD', 'view') || hasPermission('SALES_DASHBOARD', 'read')) {
    return <Navigate to="/sales/dashboard" replace />;
  }

  // 2. Create Confirmed Order if permitted
  if (
    hasPermission('SALES_CONFIRMED_ORDER', 'view') ||
    hasPermission('SALES_CONFIRMED_ORDER', 'read') ||
    hasPermission('SALES_CONFIRMED_ORDER', 'create') ||
    hasPermission('SALES_CONFIRMED_ORDER', 'write')
  ) {
    return <Navigate to="/sales/entry" replace />;
  }

  // 3. My Sales Orders if permitted
  if (hasPermission('SALES_MY_ORDERS', 'view') || hasPermission('SALES_MY_ORDERS', 'read')) {
    return <Navigate to="/sales/my-orders" replace />;
  }

  // 4. All Sales Orders if permitted
  if (hasPermission('SALES_ALL_ORDERS', 'view') || hasPermission('SALES_ALL_ORDERS', 'read')) {
    return <Navigate to="/sales/orders" replace />;
  }

  // 5. Client Master if permitted
  if (hasPermission('SALES_CLIENT_MASTER', 'view') || hasPermission('SALES_CLIENT_MASTER', 'read')) {
    return <Navigate to="/sales/clients" replace />;
  }

  // 6. Sales Reports if permitted
  if (hasPermission('SALES_REPORTS', 'view') || hasPermission('SALES_REPORTS', 'read')) {
    return <Navigate to="/sales/reports" replace />;
  }

  // 7. General Sales module access fallback
  if (hasPermission('SALES', 'view') || hasPermission('SALES', 'read')) {
    return <Navigate to="/sales/dashboard" replace />;
  }

  // 8. Fallback to 403 Unauthorized
  return <Navigate to="/unauthorized" replace />;
};

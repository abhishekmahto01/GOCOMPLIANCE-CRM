import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const AccountsIndexRedirect: React.FC = () => {
  const { hasPermission, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-[300px] w-full flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // 1. Accounts Dashboard if permitted
  if (hasPermission('ACCOUNTS_DASHBOARD', 'view') || hasPermission('ACCOUNTS_DASHBOARD', 'read')) {
    return <Navigate to="/accounts/dashboard" replace />;
  }

  // 2. Accounts Entries if permitted
  if (hasPermission('ACCOUNTS_ENTRIES', 'view') || hasPermission('ACCOUNTS_ENTRIES', 'read')) {
    return <Navigate to="/accounts/entries" replace />;
  }

  // 3. General Accounts module fallback
  if (hasPermission('ACCOUNTS', 'view') || hasPermission('ACCOUNTS', 'read')) {
    return <Navigate to="/accounts/dashboard" replace />;
  }

  // 4. Fallback to 403 Unauthorized
  return <Navigate to="/unauthorized" replace />;
};

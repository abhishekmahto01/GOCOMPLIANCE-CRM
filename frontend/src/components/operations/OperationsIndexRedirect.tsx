import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const OperationsIndexRedirect: React.FC = () => {
  const { hasPermission, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-[300px] w-full flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // 1. Operation Dashboard if permitted
  if (hasPermission('OPERATION_DASHBOARD', 'view') || hasPermission('OPERATION_DASHBOARD', 'read')) {
    return <Navigate to="/operations/dashboard" replace />;
  }

  // 2. My Assigned Tasks if permitted
  if (hasPermission('OPERATION_MY_TASKS', 'view') || hasPermission('OPERATION_MY_TASKS', 'read')) {
    return <Navigate to="/operations/my-tasks" replace />;
  }

  // 3. Unassigned Orders if permitted
  if (hasPermission('OPERATION_UNASSIGNED_ORDERS', 'view') || hasPermission('OPERATION_UNASSIGNED_ORDERS', 'read')) {
    return <Navigate to="/operations/unassigned-orders" replace />;
  }

  // 4. Task Assignment if permitted
  if (hasPermission('OPERATION_TASK_ASSIGNMENT', 'view') || hasPermission('OPERATION_TASK_ASSIGNMENT', 'read')) {
    return <Navigate to="/operations/task-assignment" replace />;
  }

  // 5. All Operation Tasks if permitted
  if (hasPermission('OPERATION_ALL_TASKS', 'view') || hasPermission('OPERATION_ALL_TASKS', 'read')) {
    return <Navigate to="/operations/all-tasks" replace />;
  }

  // 6. Required Documents if permitted
  if (hasPermission('OPERATION_DOCUMENTS', 'view') || hasPermission('OPERATION_DOCUMENTS', 'read')) {
    return <Navigate to="/operations/documents" replace />;
  }

  // 7. Application Status if permitted
  if (hasPermission('OPERATION_APPLICATION_STATUS', 'view') || hasPermission('OPERATION_APPLICATION_STATUS', 'read')) {
    return <Navigate to="/operations/application-status" replace />;
  }

  // 8. Operation Reports if permitted
  if (hasPermission('OPERATION_REPORTS', 'view') || hasPermission('OPERATION_REPORTS', 'read')) {
    return <Navigate to="/operations/reports" replace />;
  }

  // 9. General Operations module access fallback
  if (hasPermission('OPERATIONS', 'view') || hasPermission('OPERATIONS', 'read')) {
    return <Navigate to="/operations/dashboard" replace />;
  }

  // 10. Fallback to 403 Unauthorized
  return <Navigate to="/unauthorized" replace />;
};

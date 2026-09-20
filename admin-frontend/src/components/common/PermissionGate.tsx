import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { ActionType } from '../../types/permission';

interface PermissionGateProps {
  moduleCode: string;
  action: ActionType;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const PermissionGate: React.FC<PermissionGateProps> = ({
  moduleCode,
  action,
  children,
  fallback = null,
}) => {
  const { hasPermission } = useAuth();

  if (hasPermission(moduleCode, action)) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
};

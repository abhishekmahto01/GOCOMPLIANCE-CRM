import React from 'react';
import { useAuth } from '../../context/AuthContext';
import type { ActionType } from '../../types/permission';

interface PermissionGateProps {
  module: string;
  action: ActionType;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const PermissionGate: React.FC<PermissionGateProps> = ({
  module,
  action,
  children,
  fallback = null,
}) => {
  const { hasPermission } = useAuth();

  if (!hasPermission(module, action)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};

import React from 'react';
import { useAuth } from '../../context/AuthContext';
import type { ActionType } from '../../types/permission';

interface PermissionGateProps {
  module?: string;
  page?: string;
  slug?: string;
  action?: ActionType;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const PermissionGate: React.FC<PermissionGateProps> = ({
  module,
  page,
  slug,
  action = 'view',
  children,
  fallback = null,
}) => {
  const { hasPermission } = useAuth();

  let targetCode = module || page || '';
  if (slug) {
    const parts = slug.split('.');
    if (parts.length >= 3) {
      targetCode = `${parts[0].toUpperCase()}_${parts[1].toUpperCase()}`;
    }
  }

  if (!targetCode || !hasPermission(targetCode, action)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};

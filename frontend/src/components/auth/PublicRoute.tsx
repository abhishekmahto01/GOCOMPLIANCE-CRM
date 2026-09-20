import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

interface PublicRouteProps {
  children: React.ReactElement;
}

/**
 * Route wrapper for public-only pages like /login.
 * If the user is already authenticated, redirects them to /dashboard.
 */
export const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, mustChangePassword } = useAuth();

  if (isAuthenticated) {
    if (mustChangePassword) {
      return <Navigate to="/change-password-required" replace />;
    }
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

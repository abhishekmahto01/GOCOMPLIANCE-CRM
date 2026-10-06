import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

interface PublicRouteProps {
  children: React.ReactElement;
}

/**
 * Route wrapper for public-only pages like /login.
 * If the user is already authenticated, redirects them to /dashboard while preserving query params.
 */
export const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, mustChangePassword } = useAuth();
  const location = useLocation();

  if (isAuthenticated) {
    if (mustChangePassword) {
      return <Navigate to={`/change-password-required${location.search}`} replace />;
    }
    return <Navigate to={`/dashboard${location.search}`} replace />;
  }

  return children;
};

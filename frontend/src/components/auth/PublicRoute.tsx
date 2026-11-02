import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { resolveActiveModule } from '../../utils/routeResolver';

interface PublicRouteProps {
  children: React.ReactElement;
}

/**
 * Route wrapper for public-only pages like /login.
 * If the user is already authenticated, redirects them to their module dashboard
 * (/admin for Admin module, /dashboard for Workflow module) while preserving query params.
 */
export const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, mustChangePassword } = useAuth();
  const location = useLocation();

  if (isAuthenticated) {
    if (mustChangePassword) {
      return <Navigate to={`/change-password-required${location.search}`} replace />;
    }
    const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
    const { module } = resolveActiveModule(hostname, location.pathname);
    const destination = module === 'ADMIN' ? '/admin' : '/dashboard';
    return <Navigate to={`${destination}${location.search}`} replace />;
  }

  return children;
};

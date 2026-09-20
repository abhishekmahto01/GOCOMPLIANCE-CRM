import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { AdminLandingPage } from './pages/AdminLandingPage';
import { EmployeeListPage } from './pages/EmployeeListPage';
import { EmployeeFormPage } from './pages/EmployeeFormPage';
import { EmployeeDetailPage } from './pages/EmployeeDetailPage';
import { AdminPlaceholderPage } from './pages/AdminPlaceholderPage';
import { UnauthorizedPage } from './pages/UnauthorizedPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { PublicRoute } from './components/auth/PublicRoute';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Login Route */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />

          {/* Protected Main CRM Dashboard */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          {/* Protected Admin Module Landing Page */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                <AdminLandingPage />
              </ProtectedRoute>
            }
          />

          {/* Protected Employee Management Routes */}
          <Route
            path="/admin/employees"
            element={
              <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="view">
                <EmployeeListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/employees/new"
            element={
              <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="create">
                <EmployeeFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/employees/:userId"
            element={
              <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="view">
                <EmployeeDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/employees/:userId/edit"
            element={
              <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="edit">
                <EmployeeFormPage />
              </ProtectedRoute>
            }
          />

          {/* Protected Admin Placeholder Routes */}
          <Route
            path="/admin/access"
            element={
              <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                <AdminPlaceholderPage featureKey="access" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/account-activation"
            element={
              <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                <AdminPlaceholderPage featureKey="activation" />
              </ProtectedRoute>
            }
          />

          {/* 403 Forbidden Route */}
          <Route path="/unauthorized" element={<UnauthorizedPage />} />

          {/* Root Path */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* Catch-all Fallback */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;

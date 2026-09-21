import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { EmployeeListPage } from './pages/EmployeeListPage';
import { EmployeeFormPage } from './pages/EmployeeFormPage';
import { EmployeeDetailPage } from './pages/EmployeeDetailPage';
import { UserPermissionsPage } from './pages/UserPermissionsPage';
import { ChangePasswordRequiredPage } from './pages/ChangePasswordRequiredPage';
import { LoginCredentialsPage } from './pages/LoginCredentialsPage';
import { UnauthorizedPage } from './pages/UnauthorizedPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { PublicRoute } from './components/auth/PublicRoute';
import { AdminLayout } from './components/admin/AdminLayout';
import { AdminIndexRedirect } from './components/admin/AdminIndexRedirect';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
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

          {/* Mandatory First-Login Password Change Route */}
          <Route
            path="/change-password-required"
            element={<ChangePasswordRequiredPage />}
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

          {/* Protected Administration Module (Nested Layout with Collapsible Sidebar) */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            {/* Index Route redirects to first authorized child */}
            <Route index element={<AdminIndexRedirect />} />

            {/* Employee Management Routes */}
            <Route
              path="employees"
              element={
                <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="view">
                  <EmployeeListPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="employees/new"
              element={
                <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="create">
                  <EmployeeFormPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="employees/:userId"
              element={
                <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="view">
                  <EmployeeDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="employees/:userId/edit"
              element={
                <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="edit">
                  <EmployeeFormPage />
                </ProtectedRoute>
              }
            />

            {/* User Permissions Routes */}
            <Route
              path="access"
              element={
                <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                  <UserPermissionsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="permissions"
              element={
                <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
                  <UserPermissionsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="account-activation"
              element={
                <ProtectedRoute requiredModule="ADMIN_EMPLOYEES" requiredAction="view">
                  <LoginCredentialsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="login-credentials"
              element={<Navigate to="/admin/account-activation" replace />}
            />
          </Route>

          {/* 403 Forbidden Route */}
          <Route path="/unauthorized" element={<UnauthorizedPage />} />

          {/* Root Path */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* Catch-all Fallback */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </ThemeProvider>
  );
};

export default App;

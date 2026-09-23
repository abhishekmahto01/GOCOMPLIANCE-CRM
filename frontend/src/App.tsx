import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
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
import { SalesLayout } from './components/sales/SalesLayout';
import { SalesDashboardPage } from './pages/SalesDashboardPage';
import { SalesEntryPage } from './pages/SalesEntryPage';
import { SalesRegisterPage } from './pages/SalesRegisterPage';

const OperationsWorkspacePlaceholder: React.FC = () => (
  <div className="min-h-screen w-full flex flex-col items-center justify-center bg-slate-50 dark:bg-slate-950 p-6 text-center font-sans">
    <div className="max-w-md w-full bg-white dark:bg-slate-900 rounded-3xl p-8 shadow-xl border border-slate-200/80 dark:border-slate-800 space-y-4">
      <div className="w-14 h-14 rounded-2xl bg-orange-100 dark:bg-orange-950/50 text-orange-600 dark:text-orange-400 mx-auto flex items-center justify-center font-bold text-xl">
        Ops
      </div>
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Operations Workspace</h1>
      <p className="text-sm text-slate-500 dark:text-slate-400">
        You are authorized to access the Operations module. Workspace features will load in the next stage.
      </p>
      <div className="pt-2">
        <Link to="/dashboard" className="text-sm font-semibold text-blue-600 dark:text-blue-400 hover:underline">
          Return to Dashboard
        </Link>
      </div>
    </div>
  </div>
);

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

          {/* Protected Sales Module Routes */}
          <Route
            path="/sales"
            element={
              <ProtectedRoute requiredModule="SALES" requiredAction="view">
                <SalesLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/sales/dashboard" replace />} />
            <Route
              path="dashboard"
              element={
                <ProtectedRoute requiredModule="SALES" requiredAction="view">
                  <SalesDashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="entry"
              element={
                <ProtectedRoute requiredModule="SALES" requiredAction="create">
                  <SalesEntryPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="new"
              element={
                <ProtectedRoute requiredModule="SALES" requiredAction="create">
                  <SalesEntryPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="register"
              element={
                <ProtectedRoute requiredModule="SALES" requiredAction="view">
                  <SalesRegisterPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="orders"
              element={
                <ProtectedRoute requiredModule="SALES" requiredAction="view">
                  <SalesRegisterPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="my-orders"
              element={
                <ProtectedRoute requiredModule="SALES" requiredAction="view">
                  <SalesRegisterPage />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Protected Operations Module Routes */}
          <Route
            path="/operations"
            element={
              <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
                <OperationsWorkspacePlaceholder />
              </ProtectedRoute>
            }
          />
          <Route
            path="/operations/*"
            element={
              <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
                <OperationsWorkspacePlaceholder />
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

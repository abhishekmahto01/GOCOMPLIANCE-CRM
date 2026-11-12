import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { RemarkNotificationProvider } from './context/RemarkNotificationContext';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { EmployeeListPage } from './pages/EmployeeListPage';
import { EmployeeFormPage } from './pages/EmployeeFormPage';
import { EmployeeDetailPage } from './pages/EmployeeDetailPage';
import { UserPermissionsPage } from './pages/UserPermissionsPage';
import { CompanyMasterPage } from './pages/CompanyMasterPage';
import { DepartmentMasterPage } from './pages/DepartmentMasterPage';
import { DesignationMasterPage } from './pages/DesignationMasterPage';
import { LicenseMasterPage } from './pages/LicenseMasterPage';
import { SourceMasterPage } from './pages/SourceMasterPage';
import { ChangePasswordRequiredPage } from './pages/ChangePasswordRequiredPage';
import { LoginCredentialsPage } from './pages/LoginCredentialsPage';
import { UnauthorizedPage } from './pages/UnauthorizedPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { PublicRoute } from './components/auth/PublicRoute';
import { AdminLayout } from './components/admin/AdminLayout';
import { AdminIndexRedirect } from './components/admin/AdminIndexRedirect';
import { SalesLayout } from './components/sales/SalesLayout';
import { SalesIndexRedirect } from './components/sales/SalesIndexRedirect';
import { SalesDashboardPage } from './pages/SalesDashboardPage';
import { SalesEntryPage } from './pages/SalesEntryPage';
import { SalesRegisterPage } from './pages/SalesRegisterPage';

import { OperationsLayout } from './components/operations/OperationsLayout';
import { OperationsIndexRedirect } from './components/operations/OperationsIndexRedirect';
import { OperationsDashboardPage } from './pages/operations/OperationsDashboardPage';
import { MyTasksPage } from './pages/operations/MyTasksPage';
import { UnassignedOrdersPage } from './pages/operations/UnassignedOrdersPage';
import { TaskAssignmentPage } from './pages/operations/TaskAssignmentPage';
import { InternalTasksPage } from './pages/operations/InternalTasksPage';

import { AccountsLayout } from './components/accounts/AccountsLayout';
import { AccountsIndexRedirect } from './components/accounts/AccountsIndexRedirect';
import { AccountsDashboardPage } from './pages/accounts/AccountsDashboardPage';
import { AccountsEntriesPage } from './pages/accounts/AccountsEntriesPage';
import { ImpersonationBanner } from './components/common/ImpersonationBanner';
import { ImpersonationUrlHandler } from './components/auth/ImpersonationUrlHandler';
import { resolveActiveModule } from './utils/routeResolver';

/**
 * Deterministically redirects root '/' based on session:
 * - Unauthenticated -> /login
 * - Authenticated -> /dashboard (main dashboard with all module cards)
 */
const RootRedirect: React.FC = () => {
  const { isAuthenticated, isLoading, mustChangePassword } = useAuth();
  const location = useLocation();
  const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
  const { module } = resolveActiveModule(hostname, location.pathname);

  if (isLoading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
            Loading session...
          </span>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    if (mustChangePassword) {
      return <Navigate to={`/change-password-required${location.search}`} replace />;
    }
    const destination = module === 'ADMIN' ? '/admin' : '/dashboard';
    return <Navigate to={`${destination}${location.search}`} replace />;
  }

  return <Navigate to={`/login${location.search}`} replace />;
};

/**
 * Child routes shared across Admin layout mount points.
 */
const renderAdminChildRoutes = () => (
  <>
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
      element={<Navigate to="account-activation" replace />}
    />

    {/* Common Master / Company Master Routes */}
    <Route
      path="companies"
      element={
        <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
          <CompanyMasterPage />
        </ProtectedRoute>
      }
    />
    <Route
      path="company-master"
      element={<Navigate to="companies" replace />}
    />

    {/* Common Master / Department Master Routes */}
    <Route
      path="departments"
      element={
        <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
          <DepartmentMasterPage />
        </ProtectedRoute>
      }
    />
    <Route
      path="department-master"
      element={<Navigate to="departments" replace />}
    />

    {/* Common Master / Designation Master Routes */}
    <Route
      path="designations"
      element={
        <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
          <DesignationMasterPage />
        </ProtectedRoute>
      }
    />
    <Route
      path="designation-master"
      element={<Navigate to="designations" replace />}
    />

    {/* Common Master / License Master Routes */}
    <Route
      path="licenses"
      element={
        <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
          <LicenseMasterPage />
        </ProtectedRoute>
      }
    />
    <Route
      path="license-master"
      element={<Navigate to="licenses" replace />}
    />
    <Route
      path="services"
      element={<Navigate to="licenses" replace />}
    />

    {/* Common Master / Source Master Routes */}
    <Route
      path="sources"
      element={
        <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
          <SourceMasterPage />
        </ProtectedRoute>
      }
    />
    <Route
      path="source-master"
      element={<Navigate to="sources" replace />}
    />
  </>
);

export const AppRoutes: React.FC = () => {
  // Single-domain, path-based routing (same on localhost and production).
  // Main dashboard lives at /dashboard and the Admin panel at /admin.
  return (
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
        <Route index element={<SalesIndexRedirect />} />
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
            <ProtectedRoute requiredModule="SALES" requiredAction="view">
              <SalesEntryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="new"
          element={
            <ProtectedRoute requiredModule="SALES" requiredAction="view">
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
            <OperationsLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<OperationsIndexRedirect />} />
        <Route
          path="dashboard"
          element={
            <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
              <OperationsDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="my-tasks"
          element={
            <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
              <MyTasksPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="unassigned-orders"
          element={
            <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
              <UnassignedOrdersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="unassigned"
          element={
            <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
              <UnassignedOrdersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="task-assignment"
          element={
            <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
              <TaskAssignmentPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="work-assign"
          element={
            <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
              <TaskAssignmentPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="work-assignment"
          element={
            <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
              <TaskAssignmentPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="tasks"
          element={
            <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
              <TaskAssignmentPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="all-tasks"
          element={
            <ProtectedRoute requiredModule="OPERATIONS" requiredAction="view">
              <TaskAssignmentPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="internal-tasks"
          element={
            <ProtectedRoute requiredModule="OPERATION_INTERNAL_TASKS" requiredAction="view">
              <InternalTasksPage />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* Protected Accounts Module Routes */}
      <Route
        path="/accounts"
        element={
          <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
            <AccountsLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AccountsIndexRedirect />} />
        <Route
          path="dashboard"
          element={
            <ProtectedRoute requiredModule="ACCOUNTS_DASHBOARD" requiredAction="view">
              <AccountsDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="entries"
          element={
            <ProtectedRoute requiredModule="ACCOUNTS_ENTRIES" requiredAction="view">
              <AccountsEntriesPage />
            </ProtectedRoute>
          }
        />
        {/* Redirect legacy accounts routes to /accounts/entries */}
        <Route path="payments" element={<Navigate to="/accounts/entries" replace />} />
        <Route path="payment-register" element={<Navigate to="/accounts/entries" replace />} />
        <Route path="outstanding" element={<Navigate to="/accounts/entries" replace />} />
        <Route path="follow-ups" element={<Navigate to="/accounts/entries" replace />} />
        <Route path="invoices" element={<Navigate to="/accounts/entries" replace />} />
        <Route path="receipts" element={<Navigate to="/accounts/entries" replace />} />
        <Route path="expenses" element={<Navigate to="/accounts/entries" replace />} />
        <Route path="reimbursements" element={<Navigate to="/accounts/entries" replace />} />
        <Route path="reports" element={<Navigate to="/accounts/entries" replace />} />
      </Route>

      {/* Administration Module: mounted under /admin on the same origin (localhost and production) */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute requiredModule="ADMIN" requiredAction="view">
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        {renderAdminChildRoutes()}
      </Route>

      {/* 403 Forbidden Route */}
      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      {/* Root Path */}
      <Route path="/" element={<RootRedirect />} />

      {/* Catch-all Fallback */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <RemarkNotificationProvider>
          <BrowserRouter>
            <ImpersonationUrlHandler />
            <ImpersonationBanner />
            <AppRoutes />
          </BrowserRouter>
        </RemarkNotificationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;

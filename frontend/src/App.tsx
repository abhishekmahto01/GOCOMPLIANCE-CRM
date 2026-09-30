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
import { CompanyMasterPage } from './pages/CompanyMasterPage';
import { DepartmentMasterPage } from './pages/DepartmentMasterPage';
import { DesignationMasterPage } from './pages/DesignationMasterPage';
import { LicenseMasterPage } from './pages/LicenseMasterPage';
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

import { OperationsLayout } from './components/operations/OperationsLayout';
import { OperationsDashboardPage } from './pages/operations/OperationsDashboardPage';
import { MyTasksPage } from './pages/operations/MyTasksPage';
import { UnassignedOrdersPage } from './pages/operations/UnassignedOrdersPage';
import { TaskAssignmentPage } from './pages/operations/TaskAssignmentPage';

import { AccountsLayout } from './components/accounts/AccountsLayout';
import { AccountsDashboardPage } from './pages/accounts/AccountsDashboardPage';
import { PaymentRegisterPage } from './pages/accounts/PaymentRegisterPage';
import { OutstandingFollowupsPage } from './pages/accounts/OutstandingFollowupsPage';
import { InvoicesReceiptsPage } from './pages/accounts/InvoicesReceiptsPage';
import { ExpensesReimbursementsPage } from './pages/accounts/ExpensesReimbursementsPage';
import { FinancialReportsPage } from './pages/accounts/FinancialReportsPage';


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
            <Route index element={<Navigate to="/operations/dashboard" replace />} />
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
            <Route index element={<AccountsDashboardPage />} />
            <Route
              path="dashboard"
              element={
                <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                  <AccountsDashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="payments"
              element={
                <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                  <PaymentRegisterPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="payment-register"
              element={
                <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                  <PaymentRegisterPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="outstanding"
              element={
                <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                  <OutstandingFollowupsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="follow-ups"
              element={
                <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                  <OutstandingFollowupsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="invoices"
              element={
                <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                  <InvoicesReceiptsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="receipts"
              element={
                <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                  <InvoicesReceiptsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="expenses"
              element={
                <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                  <ExpensesReimbursementsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="reimbursements"
              element={
                <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                  <ExpensesReimbursementsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="reports"
              element={
                <ProtectedRoute requiredModule="ACCOUNTS" requiredAction="view">
                  <FinancialReportsPage />
                </ProtectedRoute>
              }
            />
          </Route>


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
              element={<Navigate to="/admin/companies" replace />}
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
              element={<Navigate to="/admin/departments" replace />}
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
              element={<Navigate to="/admin/designations" replace />}
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
              element={<Navigate to="/admin/licenses" replace />}
            />
            <Route
              path="services"
              element={<Navigate to="/admin/licenses" replace />}
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

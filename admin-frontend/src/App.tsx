import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AdminLayout } from './components/layout/AdminLayout';
import { ProtectedRoute } from './components/common/ProtectedRoute';

import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { EmployeeListPage } from './pages/EmployeeListPage';
import { EmployeeDetailPage } from './pages/EmployeeDetailPage';
import { EmployeeFormPage } from './pages/EmployeeFormPage';
import { UnauthorizedPage } from './pages/UnauthorizedPage';
import { NotFoundPage } from './pages/NotFoundPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Auth Route */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Admin Routes */}
          <Route element={<ProtectedRoute><AdminLayout /></ProtectedRoute>}>
            <Route path="/" element={<DashboardPage />} />

            {/* Employee Management Module */}
            <Route
              path="/employees"
              element={
                <ProtectedRoute moduleCode="ADMIN_EMPLOYEES" requiredAction="view">
                  <EmployeeListPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/employees/new"
              element={
                <ProtectedRoute moduleCode="ADMIN_EMPLOYEES" requiredAction="create">
                  <EmployeeFormPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/employees/:userId"
              element={
                <ProtectedRoute moduleCode="ADMIN_EMPLOYEES" requiredAction="view">
                  <EmployeeDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/employees/:userId/edit"
              element={
                <ProtectedRoute moduleCode="ADMIN_EMPLOYEES" requiredAction="edit">
                  <EmployeeFormPage />
                </ProtectedRoute>
              }
            />

            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;

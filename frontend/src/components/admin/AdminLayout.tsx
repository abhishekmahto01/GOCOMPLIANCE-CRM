import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { AdminHeader, type BreadcrumbItem } from '../dashboard/AdminHeader';
import { AdminSidebar } from './AdminSidebar';
import { ChangePasswordModal } from '../dashboard/ChangePasswordModal';
import { ToastContainer, type ToastMessage } from '../ui/toast';

export const AdminLayout: React.FC = () => {
  const { logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  // Mobile Drawer State
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Close mobile drawer on route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  // Password Modal State
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);

  // Layout-level Toasts
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const addToast = (type: 'success' | 'error' | 'info', title: string, message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };
  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Logout Handler
  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  // Compute Breadcrumbs from pathname
  const getBreadcrumbs = (pathname: string): BreadcrumbItem[] => {
    if (pathname === '/admin/employees') {
      return [{ label: 'Administration', href: '/admin' }, { label: 'Employee Directory' }];
    }
    if (pathname === '/admin/employees/new') {
      return [
        { label: 'Administration', href: '/admin' },
        { label: 'Employee Directory', href: '/admin/employees' },
        { label: 'Add Employee' },
      ];
    }
    if (pathname.endsWith('/edit')) {
      return [
        { label: 'Administration', href: '/admin' },
        { label: 'Employee Directory', href: '/admin/employees' },
        { label: 'Edit Employee' },
      ];
    }
    if (pathname.startsWith('/admin/employees/')) {
      return [
        { label: 'Administration', href: '/admin' },
        { label: 'Employee Directory', href: '/admin/employees' },
        { label: 'Employee Profile' },
      ];
    }
    if (pathname === '/admin/access' || pathname === '/admin/permissions') {
      return [{ label: 'Administration', href: '/admin' }, { label: 'User Permissions' }];
    }
    if (pathname === '/admin/account-activation') {
      return [{ label: 'Administration', href: '/admin' }, { label: 'Account Activation' }];
    }
    return [{ label: 'Administration' }];
  };

  return (
    <div
      className={`min-h-screen w-full flex flex-col font-sans transition-colors duration-300 relative overflow-x-hidden ${
        theme === 'dark' ? 'dark bg-slate-950 text-slate-100' : 'bg-[#f8faff] text-slate-800'
      }`}
    >
      {/* Abstract Soft Ambient Background Gradients */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/3 w-[800px] h-[500px] rounded-full bg-gradient-to-b from-blue-300/20 via-sky-200/10 to-transparent dark:from-blue-900/15 dark:via-indigo-950/10 blur-3xl" />
        <div className="absolute top-1/3 -left-32 w-[550px] h-[550px] rounded-full bg-cyan-200/15 dark:bg-cyan-900/10 blur-3xl" />
        <div className="absolute top-1/2 -right-32 w-[550px] h-[550px] rounded-full bg-blue-300/15 dark:bg-indigo-900/10 blur-3xl" />
      </div>

      {/* Top Fixed Admin Header */}
      <div className="sticky top-0 z-30 shrink-0">
        <AdminHeader
          breadcrumbs={getBreadcrumbs(location.pathname)}
          theme={theme}
          onToggleTheme={toggleTheme}
          onOpenPasswordModal={() => setIsPasswordModalOpen(true)}
          onLogout={handleLogout}
          onOpenMobileMenu={() => setIsMobileMenuOpen(true)}
        />
      </div>

      {/* Main Layout Body: Persistent Left Sidebar + Scrollable Content Area */}
      <div className="relative z-10 flex-1 flex w-full">
        {/* Persistent Collapsible Left Navigation Sidebar */}
        <AdminSidebar
          isOpen={isMobileMenuOpen}
          onClose={() => setIsMobileMenuOpen(false)}
        />

        {/* Selected Page Content Area */}
        <main className="flex-1 min-w-0 h-[calc(100vh-61px)] overflow-y-auto">
          <Outlet />
        </main>
      </div>

      {/* Change Password Modal */}
      <ChangePasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        onSuccessToast={(title, msg) => addToast('success', title, msg)}
      />

      {/* Global Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

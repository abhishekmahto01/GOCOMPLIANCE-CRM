import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { AdminHeader, type BreadcrumbItem } from '../dashboard/AdminHeader';
import { OperationsSidebar } from './OperationsSidebar';
import { ChangePasswordModal } from '../dashboard/ChangePasswordModal';
import { ToastContainer, type ToastMessage } from '../ui/toast';

export const OperationsLayout: React.FC = () => {
  const { logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  // Mobile Drawer State
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  // Desktop Sidebar Collapse State
  const [isDesktopSidebarCollapsed, setIsDesktopSidebarCollapsed] = useState(false);

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
    if (pathname.startsWith('/operations/my-tasks')) {
      return [{ label: 'Operations', href: '/operations/dashboard' }, { label: 'My Assigned Tasks' }];
    }
    if (pathname.startsWith('/operations/unassigned')) {
      return [{ label: 'Operations', href: '/operations/dashboard' }, { label: 'Unassigned Orders' }];
    }
    if (pathname.startsWith('/operations/task-assignment') || pathname.startsWith('/operations/tasks') || pathname.startsWith('/operations/all-tasks')) {
      return [{ label: 'Operations', href: '/operations/dashboard' }, { label: 'All Operations Tasks' }];
    }
    if (pathname.startsWith('/operations/dashboard')) {
      return [{ label: 'Operations', href: '/operations/dashboard' }, { label: 'Operation Dashboard' }];
    }
    return [{ label: 'Operations' }];
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

      {/* Main Container: Sidebar on Left, Header & Content on Right */}
      <div className="flex-1 flex w-full relative z-10">
        {/* Operations Navigation Sidebar */}
        <OperationsSidebar
          isOpen={isMobileMenuOpen}
          onClose={() => setIsMobileMenuOpen(false)}
          isCollapsed={isDesktopSidebarCollapsed}
          onToggleCollapse={() => setIsDesktopSidebarCollapsed(!isDesktopSidebarCollapsed)}
        />

        {/* Right Pane: Top Header + Content Area */}
        <div className="flex-1 flex flex-col min-w-0 transition-all duration-300">
          {/* Top Fixed Header */}
          <div className="sticky top-0 z-30 shrink-0">
            <AdminHeader
              showLogo={false}
              breadcrumbs={getBreadcrumbs(location.pathname)}
              theme={theme}
              onToggleTheme={toggleTheme}
              onOpenPasswordModal={() => setIsPasswordModalOpen(true)}
              onLogout={handleLogout}
              onOpenMobileMenu={() => setIsMobileMenuOpen(true)}
              onToggleSidebar={() => setIsDesktopSidebarCollapsed(!isDesktopSidebarCollapsed)}
              isSidebarCollapsed={isDesktopSidebarCollapsed}
            />
          </div>

          {/* Main Content Render */}
          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
            <Outlet context={{ addToast }} />
          </main>
        </div>
      </div>

      {/* Change Password Modal */}
      <ChangePasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        onSuccessToast={(title, msg) => {
          addToast('success', title, msg);
        }}
      />

      {/* Toast Notification Container */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { AdminHeader, type BreadcrumbItem } from '../dashboard/AdminHeader';
import { AccountsSidebar } from './AccountsSidebar';
import { ChangePasswordModal } from '../dashboard/ChangePasswordModal';
import { ToastContainer, type ToastMessage } from '../ui/toast';

export const AccountsLayout: React.FC = () => {
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
  const getBreadcrumbs = (): BreadcrumbItem[] => {
    const path = location.pathname;
    if (path.includes('/payments')) {
      return [{ label: 'Accounts', href: '/accounts/dashboard' }, { label: 'Payment Register' }];
    }
    if (path.includes('/outstanding')) {
      return [{ label: 'Accounts', href: '/accounts/dashboard' }, { label: 'Outstanding & Ageing' }];
    }
    if (path.includes('/invoices')) {
      return [{ label: 'Accounts', href: '/accounts/dashboard' }, { label: 'Invoices & Receipts' }];
    }
    if (path.includes('/expenses')) {
      return [{ label: 'Accounts', href: '/accounts/dashboard' }, { label: 'Expenses & Reimbursements' }];
    }
    if (path.includes('/reports')) {
      return [{ label: 'Accounts', href: '/accounts/dashboard' }, { label: 'Financial Reports' }];
    }
    return [{ label: 'Accounts', href: '/accounts/dashboard' }, { label: 'Dashboard' }];
  };


  return (
    <div className={`min-h-screen w-full flex flex-col font-sans transition-colors duration-300 ${theme === 'dark' ? 'dark bg-slate-950 text-slate-100' : 'bg-[#f4f7fe] text-slate-800'}`}>
      {/* Top Header */}
      <AdminHeader
        theme={theme}
        onToggleTheme={toggleTheme}
        onOpenPasswordModal={() => setIsPasswordModalOpen(true)}
        onLogout={handleLogout}
        onOpenMobileMenu={() => setIsMobileMenuOpen(true)}
        onToggleSidebar={() => setIsDesktopSidebarCollapsed(!isDesktopSidebarCollapsed)}
        isSidebarCollapsed={isDesktopSidebarCollapsed}
        breadcrumbs={getBreadcrumbs()}
      />

      {/* Main Container */}
      <div className="flex-1 flex overflow-hidden">
        {/* Desktop Sidebar */}
        <div className="hidden lg:block shrink-0">
          <AccountsSidebar isCollapsed={isDesktopSidebarCollapsed} />
        </div>

        {/* Mobile Drawer Overlay */}
        {isMobileMenuOpen && (
          <div className="fixed inset-0 z-50 lg:hidden flex">
            <div
              className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <div className="relative z-10">
              <AccountsSidebar
                isMobile
                onCloseMobile={() => setIsMobileMenuOpen(false)}
              />
            </div>
          </div>
        )}

        {/* Page Content Outlet */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>

      {/* Change Password Modal */}
      <ChangePasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        onSuccessToast={(title, msg) => addToast('success', title, msg)}
      />

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

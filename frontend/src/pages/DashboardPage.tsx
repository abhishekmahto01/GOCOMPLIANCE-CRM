import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, RefreshCw, Lock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { ModuleCard, type ModuleData } from '../components/dashboard/ModuleCard';
import { ChangePasswordModal } from '../components/dashboard/ChangePasswordModal';
import { ToastContainer, type ToastMessage } from '../components/ui/toast';

const MODULES_DATA: ModuleData[] = [
  {
    id: 'admin',
    title: 'Admin',
    description: 'Manage users, permissions and system settings',
    accentColor: 'blue',
  },
  {
    id: 'sales',
    title: 'Sales',
    description: 'Handle leads, clients and sales management',
    accentColor: 'emerald',
  },
  {
    id: 'operations',
    title: 'Operations',
    description: 'Manage applications and license processing',
    accentColor: 'orange',
  },
];

export const DashboardPage: React.FC = () => {
  const { session, user, logout, hasModuleAccess, isLoading, permissionError, refreshUserProfile } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  // Toast notification state
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

  // Password Modal state
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);

  // Department field from authenticated employee profile
  const userDepartment =
    session.department ||
    user?.department?.name ||
    user?.department_name ||
    'Department Not Assigned';

  // Logout handler
  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  // Module Card selection handler
  const handleModuleClick = (selectedModule: ModuleData) => {
    if (selectedModule.id === 'admin') {
      if (hasModuleAccess('ADMIN')) {
        navigate('/admin');
      } else {
        addToast(
          'error',
          'Access Restricted',
          'You do not have permission to access the Administration module.'
        );
      }
      return;
    }

    if (selectedModule.id === 'sales') {
      if (hasModuleAccess('SALES')) {
        navigate('/sales');
      } else {
        addToast(
          'error',
          'Access Restricted',
          'You do not have permission to access the Sales module.'
        );
      }
      return;
    }

    if (selectedModule.id === 'operations') {
      if (hasModuleAccess('OPERATIONS')) {
        navigate('/operations');
      } else {
        addToast(
          'error',
          'Access Restricted',
          'You do not have permission to access the Operations module.'
        );
      }
      return;
    }
  };

  // Filter modules strictly based on user's effective permissions
  const visibleModules = MODULES_DATA.filter((mod) => {
    if (mod.id === 'admin') return hasModuleAccess('ADMIN');
    if (mod.id === 'sales') return hasModuleAccess('SALES');
    if (mod.id === 'operations') return hasModuleAccess('OPERATIONS');
    return false;
  });

  return (
    <div className={`min-h-screen w-full flex flex-col font-sans transition-colors duration-300 relative overflow-x-hidden ${theme === 'dark' ? 'dark bg-slate-950 text-slate-100' : 'bg-[#f8faff] text-slate-800'}`}>
      
      {/* Abstract Soft Ambient Background Gradients */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/3 w-[800px] h-[500px] rounded-full bg-gradient-to-b from-blue-300/20 via-sky-200/10 to-transparent dark:from-blue-900/15 dark:via-indigo-950/10 blur-3xl" />
        <div className="absolute top-1/3 -left-32 w-[550px] h-[550px] rounded-full bg-cyan-200/15 dark:bg-cyan-900/10 blur-3xl" />
        <div className="absolute top-1/2 -right-32 w-[550px] h-[550px] rounded-full bg-blue-300/15 dark:bg-indigo-900/10 blur-3xl" />
      </div>

      {/* Top Professional Header */}
      <div className="relative z-20 shrink-0">
        <DashboardHeader
          session={session}
          department={userDepartment}
          theme={theme}
          onToggleTheme={toggleTheme}
          onOpenPasswordModal={() => setIsPasswordModalOpen(true)}
          onLogout={handleLogout}
        />
      </div>

      {/* Main Module Selection Body */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 lg:py-16">
        {/* Loading State Skeleton - Never flash unauthorized cards */}
        {isLoading && (
          <div data-testid="modules-loading" className="w-full max-w-6xl flex flex-col items-center justify-center py-16">
            <div className="flex flex-col items-center gap-4">
              <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Loading authorized modules...
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-7 lg:gap-8 w-full mt-10 opacity-40">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-56 bg-slate-200 dark:bg-slate-800/60 rounded-2xl animate-pulse" />
              ))}
            </div>
          </div>
        )}

        {/* Permission API Error State with Retry Button */}
        {!isLoading && permissionError && (
          <div data-testid="permission-error-state" className="max-w-md w-full bg-white dark:bg-slate-900 rounded-3xl p-8 shadow-xl border border-rose-200 dark:border-rose-900/50 text-center space-y-5 my-8">
            <div className="w-14 h-14 rounded-2xl bg-rose-100 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 mx-auto flex items-center justify-center">
              <AlertCircle className="w-7 h-7" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                Unable to Load Permissions
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                {permissionError}
              </p>
            </div>
            <button
              type="button"
              onClick={() => refreshUserProfile()}
              className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-xl shadow transition duration-150 cursor-pointer"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* No Access State */}
        {!isLoading && !permissionError && visibleModules.length === 0 && (
          <div data-testid="no-modules-assigned" className="max-w-md w-full bg-white dark:bg-slate-900 rounded-3xl p-8 sm:p-10 shadow-xl border border-slate-200/80 dark:border-slate-800 text-center space-y-5 my-8">
            <div className="w-16 h-16 rounded-2xl bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 mx-auto flex items-center justify-center">
              <Lock className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                No Modules Assigned
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                Please contact your administrator to request access.
              </p>
            </div>
          </div>
        )}

        {/* Module Cards Grid (Render only authorized modules) */}
        {!isLoading && !permissionError && visibleModules.length > 0 && (
          <div
            data-testid="modules-grid"
            className={`grid grid-cols-1 ${
              visibleModules.length === 1
                ? 'max-w-md w-full'
                : visibleModules.length === 2
                ? 'md:grid-cols-2 max-w-3xl w-full'
                : 'md:grid-cols-2 lg:grid-cols-3 max-w-6xl w-full'
            } gap-6 sm:gap-7 lg:gap-8`}
          >
            {visibleModules.map((module) => (
              <ModuleCard
                key={module.id}
                module={module}
                onClick={handleModuleClick}
              />
            ))}
          </div>
        )}

        {/* Footer Accent Text */}
        <div className="mt-14 sm:mt-16 lg:mt-20 flex items-center justify-center gap-4 text-xs sm:text-sm text-slate-400 dark:text-slate-500 font-medium select-none">
          <div className="w-12 sm:w-16 h-px bg-slate-200 dark:bg-slate-800" />
          <span>Compliance</span>
          <span className="text-slate-300 dark:text-slate-700">•</span>
          <span>Growth</span>
          <span className="text-slate-300 dark:text-slate-700">•</span>
          <span>Together</span>
          <div className="w-12 sm:w-16 h-px bg-slate-200 dark:bg-slate-800" />
        </div>
      </main>

      {/* Change Password Modal */}
      <ChangePasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        onSuccessToast={(title, msg) => addToast('success', title, msg)}
      />

      {/* Interactive Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
  const { session, user, logout, canAccessModule } = useAuth();
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

  // Department field
  const userDepartment = session.department || user?.department_name || 'Administration';

  // Logout handler
  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  // Module Card selection handler
  const handleModuleClick = (selectedModule: ModuleData) => {
    if (selectedModule.id === 'admin') {
      if (canAccessModule('ADMIN')) {
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

    // Sales & Operations feedback
    addToast(
      'info',
      `${selectedModule.title} Module`,
      `Module selected: ${selectedModule.title}. Workspace integration will load in the next stage.`
    );
  };

  // Filter modules based on user permissions if desired, or keep all 3 visible with permission guard
  // As per instruction: "The Admin card must appear only when the authenticated user has access to the ADMIN module or be hidden/disabled according to product conventions"
  const visibleModules = MODULES_DATA.filter((mod) => {
    if (mod.id === 'admin') {
      return canAccessModule('ADMIN');
    }
    return true;
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
        {/* Module Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-7 lg:gap-8 w-full max-w-6xl">
          {visibleModules.map((module) => (
            <ModuleCard
              key={module.id}
              module={module}
              onClick={handleModuleClick}
            />
          ))}
        </div>

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

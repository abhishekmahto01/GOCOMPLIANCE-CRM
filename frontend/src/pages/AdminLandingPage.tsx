import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AdminHeader } from '../components/dashboard/AdminHeader';
import { ChangePasswordModal } from '../components/dashboard/ChangePasswordModal';
import { ToastContainer, type ToastMessage } from '../components/ui/toast';
import {
  Users,
  ShieldCheck,
  UserCheck,
  ArrowRight,
  Sparkles,
  Lock,
} from 'lucide-react';

export const AdminLandingPage: React.FC = () => {
  const { logout, hasPermission } = useAuth();
  const navigate = useNavigate();

  // Dark / Light Mode state
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    try {
      const savedTheme = localStorage.getItem('gocompliances-theme');
      return savedTheme === 'dark' ? 'dark' : 'light';
    } catch {
      return 'light';
    }
  });

  useEffect(() => {
    try {
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        localStorage.setItem('gocompliances-theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch (err) {
      console.error('Error persisting theme:', err);
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

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

  // Permissions
  const canViewEmployees = hasPermission('ADMIN_EMPLOYEES', 'view');

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <div
      className={`min-h-screen w-full flex flex-col font-sans transition-colors duration-300 relative overflow-x-hidden ${
        theme === 'dark' ? 'dark bg-slate-950 text-slate-100' : 'bg-[#f8faff] text-slate-800'
      }`}
    >
      {/* Background Ambience */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/3 w-[800px] h-[500px] rounded-full bg-gradient-to-b from-blue-300/20 via-sky-200/10 to-transparent dark:from-blue-900/15 dark:via-indigo-950/10 blur-3xl" />
        <div className="absolute top-1/3 -left-32 w-[550px] h-[550px] rounded-full bg-cyan-200/15 dark:bg-cyan-900/10 blur-3xl" />
        <div className="absolute top-1/2 -right-32 w-[550px] h-[550px] rounded-full bg-blue-300/15 dark:bg-indigo-900/10 blur-3xl" />
      </div>

      {/* Header */}
      <div className="relative z-20 shrink-0">
        <AdminHeader
          breadcrumbs={[{ label: 'Administration' }]}
          theme={theme}
          onToggleTheme={toggleTheme}
          onOpenPasswordModal={() => setIsPasswordModalOpen(true)}
          onLogout={handleLogout}
        />
      </div>

      {/* Main Content */}
      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* Page Heading */}
        <div className="mb-10 text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-950/50 border border-blue-200/80 dark:border-blue-800 text-blue-700 dark:text-blue-300 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>CRM Core Administration</span>
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-[#0a2569] dark:text-white tracking-tight">
            Administration Module
          </h1>
          <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 mt-2 max-w-2xl">
            Manage organization employees, reporting hierarchies, and enterprise access governance.
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
          {/* Card 1: Employee Management (Active) */}
          <div
            className={`flex flex-col justify-between p-6 sm:p-7 rounded-3xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800 shadow-xl transition-all duration-300 ${
              canViewEmployees
                ? 'hover:border-blue-300 dark:hover:border-blue-700 hover:shadow-2xl hover:-translate-y-1'
                : 'opacity-70'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center">
                  <Users className="w-6 h-6" />
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                  Ready
                </span>
              </div>

              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                Employee Management
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
                Create and manage employee profiles, company affiliations, department assignments, and direct reporting lines.
              </p>
            </div>

            <div>
              {canViewEmployees ? (
                <Link
                  to="/admin/employees"
                  className="w-full inline-flex items-center justify-between px-4 py-3 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition shadow-sm hover:shadow-md"
                >
                  <span>Open Directory</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              ) : (
                <div className="w-full px-4 py-2.5 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 text-xs font-medium text-center">
                  Requires ADMIN_EMPLOYEES permission
                </div>
              )}
            </div>
          </div>

          {/* Card 2: User Access Management (Upcoming) */}
          <div className="flex flex-col justify-between p-6 sm:p-7 rounded-3xl bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-slate-200/60 dark:border-slate-800/60 shadow-lg relative overflow-hidden group">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-indigo-100/80 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                  Coming Next Stage
                </span>
              </div>

              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                Access Control & Scopes
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
                Configure module action permissions (View, Create, Edit, Delete, Approve) and data scopes (SELF, TEAM, DEPARTMENT, COMPANY, ALL).
              </p>
            </div>

            <Link
              to="/admin/access"
              className="w-full inline-flex items-center justify-between px-4 py-3 rounded-2xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold text-sm transition"
            >
              <div className="flex items-center gap-2">
                <Lock className="w-3.5 h-3.5 text-slate-400" />
                <span>View Details</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </Link>
          </div>

          {/* Card 3: Account Activation (Upcoming) */}
          <div className="flex flex-col justify-between p-6 sm:p-7 rounded-3xl bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-slate-200/60 dark:border-slate-800/60 shadow-lg relative overflow-hidden group">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-teal-100/80 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 flex items-center justify-center">
                  <UserCheck className="w-6 h-6" />
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                  Coming Next Stage
                </span>
              </div>

              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                Account Activation
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
                Generate initial secure credentials, dispatch one-time activation links, and manage credential lifecycle for newly created employees.
              </p>
            </div>

            <Link
              to="/admin/account-activation"
              className="w-full inline-flex items-center justify-between px-4 py-3 rounded-2xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold text-sm transition"
            >
              <div className="flex items-center gap-2">
                <Lock className="w-3.5 h-3.5 text-slate-400" />
                <span>View Details</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </Link>
          </div>
        </div>
      </main>

      {/* Password Modal */}
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

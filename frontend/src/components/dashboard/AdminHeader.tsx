import React from 'react';
import { Link } from 'react-router-dom';
import { BrandLogo } from '../auth/BrandLogo';
import { ThemeToggle } from './ThemeToggle';
import { LiveClock } from './LiveClock';
import { LogOut, ChevronRight, Home, KeyRound } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface AdminHeaderProps {
  breadcrumbs?: BreadcrumbItem[];
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  onOpenPasswordModal?: () => void;
  onLogout: () => void;
}

export const AdminHeader: React.FC<AdminHeaderProps> = ({
  breadcrumbs = [],
  theme,
  onToggleTheme,
  onOpenPasswordModal,
  onLogout,
}) => {
  const { session, user } = useAuth();
  const username = session.username || user?.employee_code || 'Admin';
  const initial = username.charAt(0).toUpperCase() || 'A';
  const isDark = theme === 'dark';

  return (
    <header className="w-full bg-white/80 dark:bg-slate-900/85 backdrop-blur-xl border-b border-slate-200/80 dark:border-slate-800 px-4 sm:px-8 py-3 transition-colors duration-300">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Left: Brand Identity & Breadcrumbs */}
        <div className="flex flex-wrap items-center gap-4 self-start md:self-center">
          <Link to="/dashboard" className="shrink-0">
            <BrandLogo showTagline={false} theme={isDark ? 'light' : 'dark'} size="sm" />
          </Link>

          {breadcrumbs.length > 0 && (
            <nav className="flex items-center gap-1.5 text-xs sm:text-sm text-slate-500 dark:text-slate-400 font-medium">
              <Link
                to="/dashboard"
                className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1 transition"
                title="Main Dashboard"
              >
                <Home className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Dashboard</span>
              </Link>
              {breadcrumbs.map((crumb, idx) => {
                const isLast = idx === breadcrumbs.length - 1;
                return (
                  <React.Fragment key={crumb.label}>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    {crumb.href && !isLast ? (
                      <Link
                        to={crumb.href}
                        className="hover:text-blue-600 dark:hover:text-blue-400 transition"
                      >
                        {crumb.label}
                      </Link>
                    ) : (
                      <span className="font-semibold text-slate-800 dark:text-slate-200">
                        {crumb.label}
                      </span>
                    )}
                  </React.Fragment>
                );
              })}
            </nav>
          )}
        </div>

        {/* Right: Controls & User Profile */}
        <div className="flex flex-wrap items-center justify-end gap-2.5 sm:gap-3 w-full md:w-auto">
          {/* Theme Toggle */}
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />

          {/* Live Digital Clock */}
          <div className="hidden sm:block px-3 py-1.5 rounded-full bg-slate-100/80 dark:bg-slate-800/80 border border-slate-200/60 dark:border-slate-700/60 text-xs sm:text-sm font-semibold text-slate-700 dark:text-slate-200 shadow-2xs">
            <LiveClock />
          </div>

          {/* User Profile Capsule */}
          <div className="flex items-center gap-2 px-2.5 py-1 sm:px-3 sm:py-1 rounded-full bg-white dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 shadow-2xs">
            <div className="w-7 h-7 rounded-full bg-blue-600 dark:bg-blue-500 text-white flex items-center justify-center font-bold text-xs shadow-2xs shrink-0">
              {initial}
            </div>
            <div className="flex flex-col text-left pr-1 leading-tight">
              <span className="text-xs font-bold text-slate-900 dark:text-white capitalize">
                {username}
              </span>
              <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
                {session.department || user?.department_name || 'Administration'}
              </span>
            </div>
          </div>

          {/* Password Button if handler provided */}
          {onOpenPasswordModal && (
            <button
              type="button"
              onClick={onOpenPasswordModal}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold
                bg-white/80 dark:bg-slate-800 text-slate-700 dark:text-slate-200
                border border-slate-200 dark:border-slate-700
                hover:bg-slate-50 dark:hover:bg-slate-750
                shadow-2xs transition select-none"
              title="Change Account Password"
            >
              <KeyRound className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
              <span className="hidden sm:inline">Password</span>
            </button>
          )}

          {/* Logout Button */}
          <button
            type="button"
            onClick={onLogout}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold
              bg-red-600 hover:bg-red-700 text-white
              shadow-xs hover:shadow-sm hover:shadow-red-500/20
              transform active:scale-95 transition select-none"
            title="Sign out of CRM"
          >
            <LogOut className="w-3.5 h-3.5 stroke-[2.5]" />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

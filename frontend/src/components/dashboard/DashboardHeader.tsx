import React from 'react';
import { BrandLogo } from '../auth/BrandLogo';
import { ThemeToggle } from './ThemeToggle';
import { LiveClock } from './LiveClock';
import { LogOut, KeyRound } from 'lucide-react';
import type { AuthSession } from '../../utils/auth';

export interface DashboardHeaderProps {
  session: AuthSession;
  department?: string;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  onOpenPasswordModal: () => void;
  onLogout: () => void;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  session,
  department = 'Department Not Assigned',
  theme,
  onToggleTheme,
  onOpenPasswordModal,
  onLogout,
}) => {
  const username = session.username || 'Employee';
  const initial = username.charAt(0).toUpperCase() || 'E';
  const isDark = theme === 'dark';
  const displayDepartment = department || session.department || 'Department Not Assigned';

  return (
    <header className="w-full bg-white/80 dark:bg-slate-900/85 backdrop-blur-xl border-b border-slate-200/80 dark:border-slate-800 px-4 sm:px-8 py-3.5 sm:py-4 transition-colors duration-300">
      <div className="max-w-[1440px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Left: Brand Identity */}
        <div className="flex items-center self-start md:self-center">
          <BrandLogo
            showTagline={true}
            theme={isDark ? 'light' : 'dark'}
            size="sm"
          />
        </div>

        {/* Right: Controls & User Profile (Order: Dark Mode | Live Time | User Profile | Password | Logout) */}
        <div className="flex flex-wrap items-center justify-end gap-2.5 sm:gap-3.5 w-full md:w-auto">
          {/* 1. Theme Toggle */}
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />

          {/* 2. Live Digital Clock */}
          <div className="px-3 py-1.5 rounded-full bg-slate-100/80 dark:bg-slate-800/80 border border-slate-200/60 dark:border-slate-700/60 text-xs sm:text-sm font-semibold text-slate-700 dark:text-slate-200 shadow-xs">
            <LiveClock />
          </div>

          {/* 3. User Profile Capsule */}
          <div className="flex items-center gap-2 px-2.5 py-1 sm:px-3 sm:py-1.5 rounded-full bg-white dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 shadow-xs">
            {/* Avatar Circle */}
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-blue-600 dark:bg-blue-500 text-white flex items-center justify-center font-bold text-xs sm:text-sm shadow-xs shrink-0">
              {initial}
            </div>

            {/* User Info */}
            <div className="flex flex-col text-left pr-1 sm:pr-2 leading-tight">
              <span data-testid="header-user-name" className="text-xs sm:text-[13px] font-bold text-slate-900 dark:text-white capitalize">
                {username}
              </span>
              <span data-testid="header-user-department" className="text-[10px] sm:text-[11px] font-medium text-slate-500 dark:text-slate-400">
                {displayDepartment}
              </span>
            </div>
          </div>

          {/* 4. Password Button */}
          <button
            type="button"
            onClick={onOpenPasswordModal}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold
              bg-white/80 dark:bg-slate-800 text-slate-700 dark:text-slate-200
              border border-slate-200 dark:border-slate-700
              hover:bg-slate-50 dark:hover:bg-slate-750 hover:border-slate-300 dark:hover:border-slate-600
              shadow-xs transition-all duration-200 select-none"
            title="Change Account Password"
          >
            <KeyRound className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
            <span>Password</span>
          </button>

          {/* 5. Logout Button (Red Action Button) */}
          <button
            type="button"
            onClick={onLogout}
            className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-bold
              bg-red-600 hover:bg-red-700 text-white
              shadow-sm hover:shadow-md hover:shadow-red-500/20
              transform active:scale-95 transition-all duration-200 select-none"
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

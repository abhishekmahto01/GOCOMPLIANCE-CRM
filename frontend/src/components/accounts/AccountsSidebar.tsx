import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Receipt,
  ArrowLeft,
  X,
  Sparkles,
} from 'lucide-react';

interface AccountsSidebarProps {
  isMobile?: boolean;
  onCloseMobile?: () => void;
  isCollapsed?: boolean;
}

interface NavItem {
  label: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
}

const NAV_ITEMS: NavItem[] = [
  {
    label: 'Accounts Overview',
    path: '/accounts',
    icon: LayoutDashboard,
  },
];

export const AccountsSidebar: React.FC<AccountsSidebarProps> = ({
  isMobile = false,
  onCloseMobile,
  isCollapsed = false,
}) => {
  return (
    <aside
      className={`h-full flex flex-col bg-white dark:bg-slate-900 border-r border-slate-200/80 dark:border-slate-800 transition-all duration-300 select-none ${
        isMobile ? 'w-72 p-4' : isCollapsed ? 'w-20 p-3' : 'w-64 p-4'
      }`}
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between pb-4 mb-2 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-700 to-blue-800 text-white flex items-center justify-center shadow-md shrink-0">
            <Receipt className="w-5 h-5" />
          </div>
          {(!isCollapsed || isMobile) && (
            <div className="overflow-hidden">
              <h2 className="text-sm font-extrabold text-[#0a2569] dark:text-white tracking-tight truncate">
                Accounts
              </h2>
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded-full border border-indigo-200/60 dark:border-indigo-800">
                <Sparkles className="w-2.5 h-2.5" /> Workspace
              </span>
            </div>
          )}
        </div>

        {isMobile && onCloseMobile && (
          <button
            onClick={onCloseMobile}
            className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-lg"
            aria-label="Close Sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1 py-2 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/accounts'}
              onClick={isMobile ? onCloseMobile : undefined}
              title={isCollapsed && !isMobile ? item.label : undefined}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-xs sm:text-sm transition-all duration-200 group relative ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-md font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
                } ${isCollapsed && !isMobile ? 'justify-center px-2' : ''}`
              }
            >
              <Icon className="w-4 h-4 shrink-0 transition-transform group-hover:scale-110" />
              {(!isCollapsed || isMobile) && (
                <span className="truncate">{item.label}</span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Back to Main Dashboard Navigation */}
      <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
        <NavLink
          to="/dashboard"
          title={isCollapsed && !isMobile ? 'Back to Main Dashboard' : undefined}
          className={`flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-[#0a2569] dark:hover:text-white transition-all ${
            isCollapsed && !isMobile ? 'justify-center px-2' : ''
          }`}
        >
          <ArrowLeft className="w-4 h-4 shrink-0" />
          {(!isCollapsed || isMobile) && <span>Back to Dashboard</span>}
        </NavLink>
      </div>
    </aside>
  );
};

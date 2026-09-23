import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Layers,
  ChevronDown,
  X,
  LayoutDashboard,
  CheckSquare,
  Clock,
  UserCheck,
  PanelLeftClose,
} from 'lucide-react';
import { BrandLogo } from '../auth/BrandLogo';
import { useTheme } from '../../context/ThemeContext';

export interface OperationsSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export const OperationsSidebar: React.FC<OperationsSidebarProps> = ({
  isOpen,
  onClose,
  isCollapsed = false,
  onToggleCollapse,
}) => {
  const location = useLocation();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [isOpsExpanded, setIsOpsExpanded] = useState(true);

  // Lock background scroll when mobile drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const isOpsDashboardActive =
    location.pathname === '/operations/dashboard' || location.pathname === '/operations';
  const isMyTasksActive = location.pathname.startsWith('/operations/my-tasks');
  const isUnassignedActive =
    location.pathname.startsWith('/operations/unassigned-orders') ||
    location.pathname.startsWith('/operations/unassigned');
  const isTaskAssignmentActive =
    location.pathname.startsWith('/operations/task-assignment') ||
    location.pathname.startsWith('/operations/tasks') ||
    location.pathname.startsWith('/operations/all-tasks');

  const isAnyOpsActive =
    isOpsDashboardActive || isMyTasksActive || isUnassignedActive || isTaskAssignmentActive;

  const renderSidebarContent = (isDrawer = false) => (
    <div className="flex flex-col h-full bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border-r border-slate-200/80 dark:border-slate-800 transition-colors duration-300 select-none">
      {/* Brand Header */}
      <div className="p-4 sm:p-5 flex items-center justify-between border-b border-slate-200/70 dark:border-slate-800/80">
        <Link to="/dashboard" className="flex items-center gap-2">
          <BrandLogo showTagline={false} theme={isDark ? 'light' : 'dark'} size="sm" />
        </Link>
        {isDrawer ? (
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            aria-label="Close Navigation"
          >
            <X className="w-5 h-5" />
          </button>
        ) : (
          onToggleCollapse && (
            <button
              type="button"
              onClick={onToggleCollapse}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition hidden lg:inline-flex"
              title="Collapse Sidebar"
              aria-label="Collapse Sidebar"
            >
              <PanelLeftClose className="w-4 h-4" />
            </button>
          )
        )}
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1.5 scrollbar-thin">
        {/* 1. Main Dashboard */}
        <Link
          to="/dashboard"
          className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50/50 dark:hover:bg-blue-950/30 transition-all"
        >
          <Home className="w-4 h-4 text-slate-400" />
          <span>Dashboard</span>
        </Link>

        {/* 2. Operations Group (Collapsible) */}
        <div className="space-y-1 pt-1">
          <button
            type="button"
            onClick={() => setIsOpsExpanded(!isOpsExpanded)}
            className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
              isAnyOpsActive
                ? 'bg-blue-50/80 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400'
                : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100/70 dark:hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center gap-3">
              <Layers className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span>Operations</span>
            </div>
            <ChevronDown
              className={`w-4 h-4 transition-transform duration-200 ${
                isOpsExpanded ? 'rotate-180 text-blue-600 dark:text-blue-400' : 'text-slate-400'
              }`}
            />
          </button>

          {isOpsExpanded && (
            <div className="pl-7 pr-1 py-1 space-y-1 border-l-2 border-blue-100 dark:border-blue-900/40 ml-4">
              {/* Operation Dashboard */}
              <Link
                to="/operations/dashboard"
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                  isOpsDashboardActive
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30'
                }`}
              >
                <LayoutDashboard className="w-3.5 h-3.5" />
                <span>Operation Dashboard</span>
              </Link>

              {/* My Assigned Tasks */}
              <Link
                to="/operations/my-tasks"
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                  isMyTasksActive
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30'
                }`}
              >
                <CheckSquare className="w-3.5 h-3.5" />
                <span>My Assigned Tasks</span>
              </Link>

              {/* Unassigned Orders */}
              <Link
                to="/operations/unassigned-orders"
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                  isUnassignedActive
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30'
                }`}
              >
                <Clock className="w-3.5 h-3.5" />
                <span>Unassigned Orders</span>
              </Link>

              {/* Task Assignment */}
              <Link
                to="/operations/task-assignment"
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                  isTaskAssignmentActive
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30'
                }`}
              >
                <UserCheck className="w-3.5 h-3.5" />
                <span>Task Assignment</span>
              </Link>
            </div>
          )}
        </div>
      </nav>
    </div>
  );

  return (
    <>
      {/* Desktop Sticky Sidebar */}
      {!isCollapsed && (
        <aside className="hidden lg:block w-64 shrink-0 sticky top-0 h-screen z-20 transition-all duration-300">
          {renderSidebarContent(false)}
        </aside>
      )}

      {/* Mobile Drawer Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
            onClick={onClose}
          />
          <div className="fixed inset-y-0 left-0 w-72 max-w-[85vw] shadow-2xl z-50 animate-in slide-in-from-left duration-200">
            {renderSidebarContent(true)}
          </div>
        </div>
      )}
    </>
  );
};

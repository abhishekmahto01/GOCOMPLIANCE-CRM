import React, { useState, useEffect, useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronDown, X, ShieldAlert } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import {
  TOP_NAV_ITEMS,
  ADMIN_NAV_GROUPS,
  type NavChildItem,
} from './adminNavConfig';

export interface AdminSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AdminSidebar: React.FC<AdminSidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { hasPermission } = useAuth();

  // Filter navigation groups based on authenticated permissions
  const visibleGroups = useMemo(() => {
    return ADMIN_NAV_GROUPS.map((group) => {
      const visibleChildren = group.children.filter((child) => {
        return hasPermission(child.requiredModule, child.requiredAction || 'view');
      });
      return {
        ...group,
        children: visibleChildren,
      };
    }).filter((group) => group.children.length > 0);
  }, [hasPermission]);

  // Track expanded/collapsed state for parent groups
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {};
    ADMIN_NAV_GROUPS.forEach((group) => {
      // Default to open if route belongs to this group or open by default
      const hasActiveChild = group.children.some(
        (c) =>
          location.pathname === c.route ||
          location.pathname.startsWith(`${c.route}/`)
      );
      initial[group.id] = hasActiveChild || group.id === 'employee_management';
    });
    return initial;
  });

  // Automatically expand the group containing the active route on route change
  useEffect(() => {
    ADMIN_NAV_GROUPS.forEach((group) => {
      const hasActiveChild = group.children.some(
        (c) =>
          location.pathname === c.route ||
          location.pathname.startsWith(`${c.route}/`)
      );
      if (hasActiveChild) {
        setOpenGroups((prev) => ({ ...prev, [group.id]: true }));
      }
    });
  }, [location.pathname]);

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

  const toggleGroup = (groupId: string) => {
    setOpenGroups((prev) => ({
      ...prev,
      [groupId]: !prev[groupId],
    }));
  };

  const isChildActive = (child: NavChildItem) => {
    if (location.pathname === child.route) return true;
    if (
      child.route !== '/admin' &&
      location.pathname.startsWith(`${child.route}/`)
    ) {
      // Avoid matching /admin/employees/new as /admin/employees when on new
      if (child.route === '/admin/employees' && location.pathname === '/admin/employees/new') {
        return false;
      }
      return true;
    }
    return false;
  };

  const renderSidebarContent = (isDrawer = false) => (
    <div className="flex flex-col h-full bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border-r border-slate-200/80 dark:border-slate-800 transition-colors duration-300 select-none">
      {/* Sidebar Header / Module Title */}
      <div className="p-4 sm:p-5 flex items-center justify-between border-b border-slate-200/70 dark:border-slate-800/80">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#0a2569] to-blue-600 dark:from-blue-600 dark:to-indigo-600 text-white flex items-center justify-center font-black text-sm shadow-sm">
            GC
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white leading-tight">
              Administration
            </h2>
            <span className="text-[10px] font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider">
              Control Panel
            </span>
          </div>
        </div>

        {/* Mobile close button (only present in drawer) */}
        {isDrawer && (
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            aria-label="Close Sidebar Menu"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Navigation Links Scroll Container */}
      <nav
        className="flex-1 overflow-y-auto px-3 py-4 space-y-4 text-xs font-medium"
        aria-label="Admin Sidebar Navigation"
      >
        {/* Top Direct Items (e.g. Dashboard) */}
        <div className="space-y-1">
          {TOP_NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.route;
            return (
              <Link
                key={item.id}
                to={item.route}
                onClick={onClose}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-xl transition font-semibold ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 dark:bg-blue-950/70 dark:text-blue-300 shadow-2xs'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100/80 dark:hover:bg-slate-800/70'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400'}`} />
                <span>{item.title}</span>
              </Link>
            );
          })}
        </div>

        <div className="h-px bg-slate-200/70 dark:bg-slate-800/70 mx-1" />

        {/* Expandable Group Sections */}
        {visibleGroups.length === 0 ? (
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 text-slate-400 text-center text-xs">
            <ShieldAlert className="w-6 h-6 mx-auto mb-1 opacity-60" />
            No accessible administration modules.
          </div>
        ) : (
          <div className="space-y-3">
            {visibleGroups.map((group) => {
              const isGroupExpanded = !!openGroups[group.id];
              const GroupIcon = group.icon;
              return (
                <div key={group.id} className="space-y-1">
                  {/* Parent Group Header / Toggle Button */}
                  <button
                    type="button"
                    onClick={() => toggleGroup(group.id)}
                    aria-expanded={isGroupExpanded}
                    aria-controls={`group-${group.id}-children`}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-slate-700 dark:text-slate-200 hover:bg-slate-100/70 dark:hover:bg-slate-800/60 transition group font-bold text-xs"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <GroupIcon className="w-4 h-4 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200 shrink-0 transition-colors" />
                      <span className="truncate">{group.title}</span>
                    </div>
                    <ChevronDown
                      className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 shrink-0 ${
                        isGroupExpanded ? 'rotate-180 text-blue-600 dark:text-blue-400' : ''
                      }`}
                    />
                  </button>

                  {/* Child Links Container */}
                  {isGroupExpanded && (
                    <div
                      id={`group-${group.id}-children`}
                      className="pl-6 pr-1 py-1 space-y-0.5 border-l border-slate-200/80 dark:border-slate-800/80 ml-4.5"
                    >
                      {group.children.map((child) => {
                        const ChildIcon = child.icon;
                        const active = isChildActive(child);
                        return (
                          <Link
                            key={child.id}
                            to={child.route}
                            onClick={onClose}
                            className={`flex items-center justify-between px-2.5 py-1.5 rounded-lg transition text-xs ${
                              active
                                ? 'bg-blue-50 text-blue-700 dark:bg-blue-950/70 dark:text-blue-300 font-bold shadow-2xs'
                                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100/60 dark:hover:bg-slate-800/40'
                            }`}
                          >
                            <div className="flex items-center gap-2 min-w-0">
                              <ChildIcon
                                className={`w-3.5 h-3.5 shrink-0 ${
                                  active
                                    ? 'text-blue-600 dark:text-blue-400'
                                    : 'text-slate-400'
                                }`}
                              />
                              <span className="truncate">{child.title}</span>
                            </div>

                            {child.badge && (
                              <span className="shrink-0 px-1.5 py-0.5 text-[9px] font-bold rounded-md bg-amber-100 text-amber-800 dark:bg-amber-950/70 dark:text-amber-300 border border-amber-200/60 dark:border-amber-800/60">
                                {child.badge}
                              </span>
                            )}
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </nav>

      {/* Footer Info Pill */}
      <div className="p-3 border-t border-slate-200/70 dark:border-slate-800/80 text-[11px] text-slate-400 dark:text-slate-500 text-center font-medium">
        GoCompliances CRM v1.0
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar (~260px) */}
      <aside
        data-testid="admin-sidebar"
        className="hidden lg:block w-64 xl:w-72 shrink-0 h-[calc(100vh-61px)] sticky top-[61px] overflow-hidden z-20"
      >
        {renderSidebarContent(false)}
      </aside>

      {/* Mobile/Tablet Off-Canvas Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          {/* Backdrop Overlay */}
          <div
            className="fixed inset-0 bg-slate-950/60 backdrop-blur-xs transition-opacity duration-300"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Drawer Panel */}
          <div className="fixed inset-y-0 left-0 w-72 max-w-[85vw] shadow-2xl z-50 animate-in slide-in-from-left duration-300">
            {renderSidebarContent(true)}
          </div>
        </div>
      )}
    </>
  );
};

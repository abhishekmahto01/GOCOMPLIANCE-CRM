import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Building2,
  Network,
  Award,
  ShieldCheck,
  FileText,
  ChevronRight,
} from 'lucide-react';
import clsx from 'clsx';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onCloseMobile }) => {
  const { canAccessModule } = useAuth();
  const canViewEmployees = canAccessModule('ADMIN_EMPLOYEES');

  const mainNavItems = [
    {
      name: 'Dashboard',
      path: '/',
      icon: <LayoutDashboard className="w-5 h-5" />,
      allowed: true,
    },
    {
      name: 'Employees',
      path: '/employees',
      icon: <Users className="w-5 h-5" />,
      allowed: canViewEmployees,
    },
  ];

  const placeholderNavItems = [
    { name: 'Companies', icon: <Building2 className="w-5 h-5" />, tag: 'Upcoming' },
    { name: 'Departments', icon: <Network className="w-5 h-5" />, tag: 'Upcoming' },
    { name: 'Designations', icon: <Award className="w-5 h-5" />, tag: 'Upcoming' },
    { name: 'Access Control', icon: <ShieldCheck className="w-5 h-5" />, tag: 'Upcoming' },
    { name: 'Audit Logs', icon: <FileText className="w-5 h-5" />, tag: 'Upcoming' },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs lg:hidden"
        />
      )}

      <aside
        className={clsx(
          'fixed top-0 bottom-0 left-0 z-40 w-64 bg-slate-900 text-white flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800 bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-cyan-400 flex items-center justify-center font-extrabold text-white text-base shadow-brand-glow">
              GC
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white block leading-tight">
                GoCompliances
              </span>
              <span className="text-[10px] uppercase tracking-wider font-semibold text-brand-400 block">
                Admin Panel
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Sections */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
          <div>
            <span className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Core Management
            </span>
            <nav className="mt-2 space-y-1">
              {mainNavItems
                .filter((item) => item.allowed)
                .map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === '/'}
                    onClick={onCloseMobile}
                    className={({ isActive }) =>
                      clsx(
                        'flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all group',
                        isActive
                          ? 'bg-brand-600 text-white shadow-button-glow font-semibold'
                          : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                      )
                    }
                  >
                    <div className="flex items-center gap-3">
                      {item.icon}
                      <span>{item.name}</span>
                    </div>
                    <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </NavLink>
                ))}
            </nav>
          </div>

          <div>
            <span className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-500">
              System Masters (Stage 8+)
            </span>
            <div className="mt-2 space-y-1">
              {placeholderNavItems.map((item) => (
                <div
                  key={item.name}
                  className="flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium text-slate-500 cursor-not-allowed opacity-60 hover:bg-slate-800/30"
                >
                  <div className="flex items-center gap-3">
                    {item.icon}
                    <span>{item.name}</span>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                    {item.tag}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Version Badge */}
        <div className="p-4 border-t border-slate-800/80 text-xs text-slate-400 flex items-center justify-between">
          <span>Admin Portal v0.1</span>
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500" title="API Connected" />
        </div>
      </aside>
    </>
  );
};

import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  CreditCard,
  Clock,
  FileText,
  Receipt,
  FileSpreadsheet,
  ArrowLeft,
  X,
  Sparkles,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface AccountsSidebarProps {
  isMobile?: boolean;
  onCloseMobile?: () => void;
  isCollapsed?: boolean;
}

interface NavItem {
  label: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  moduleCode?: string;
}

const NAV_ITEMS: NavItem[] = [
  {
    label: 'Dashboard',
    path: '/accounts/dashboard',
    icon: LayoutDashboard,
    moduleCode: 'ACCOUNTS_DASHBOARD',
  },
  {
    label: 'Payment Register',
    path: '/accounts/payments',
    icon: CreditCard,
    moduleCode: 'ACCOUNTS_PAYMENT_REGISTER',
  },
  {
    label: 'Outstanding & Ageing',
    path: '/accounts/outstanding',
    icon: Clock,
    moduleCode: 'ACCOUNTS_OUTSTANDING',
  },
  {
    label: 'Invoices & Receipts',
    path: '/accounts/invoices',
    icon: FileText,
    moduleCode: 'ACCOUNTS_INVOICES',
  },
  {
    label: 'Expenses & Reimbursements',
    path: '/accounts/expenses',
    icon: Receipt,
    moduleCode: 'ACCOUNTS_EXPENSES',
  },
  {
    label: 'Financial Reports',
    path: '/accounts/reports',
    icon: FileSpreadsheet,
    moduleCode: 'ACCOUNTS_REPORTS',
  },
];

export const AccountsSidebar: React.FC<AccountsSidebarProps> = ({
  isMobile = false,
  onCloseMobile,
  isCollapsed = false,
}) => {
  const { isSuperAdmin, session, hasModuleAccess } = useAuth();
  const isDirector = session.userRole?.toUpperCase() === 'DIRECTOR';


  const authorizedItems = NAV_ITEMS.filter((item) => {
    if (isSuperAdmin || isDirector) return true;
    if (!item.moduleCode) return true;
    return hasModuleAccess(item.moduleCode) || hasModuleAccess('ACCOUNTS');
  });

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
                Accounts & Finance
              </h2>
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded-full border border-indigo-200/60 dark:border-indigo-800">
                <Sparkles className="w-2.5 h-2.5" /> Finance Portal
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
      <nav className="flex-1 space-y-1.5 py-2 overflow-y-auto">
        {authorizedItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={isMobile ? onCloseMobile : undefined}
              title={isCollapsed && !isMobile ? item.label : undefined}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium text-xs sm:text-sm transition-all duration-200 group relative ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-md font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
                } ${isCollapsed && !isMobile ? 'justify-center px-2' : ''}`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={`w-4 h-4 shrink-0 transition-transform group-hover:scale-110 ${isActive ? 'text-white' : 'text-slate-500 dark:text-slate-400'}`} />
                  {(!isCollapsed || isMobile) && (
                    <span className="truncate flex-1">{item.label}</span>
                  )}
                  {isActive && (!isCollapsed || isMobile) && (
                    <ChevronRight className="w-3.5 h-3.5 text-white/80 shrink-0" />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Trust & Safe Mode Badge */}
      {(!isCollapsed || isMobile) && (
        <div className="mb-2 p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-800 flex items-center gap-2.5">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <div className="text-[11px] text-slate-500 dark:text-slate-400 leading-tight">
            <span className="font-semibold text-slate-700 dark:text-slate-200 block">Audit-Safe Ledger</span>
            Double-entry & verified balances
          </div>
        </div>
      )}

      {/* Back to Main Dashboard Navigation */}
      <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
        <NavLink
          to="/dashboard"
          title={isCollapsed && !isMobile ? 'Main Dashboard' : undefined}
          className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-medium text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white transition-colors ${
            isCollapsed && !isMobile ? 'justify-center px-2' : ''
          }`}
        >
          <ArrowLeft className="w-4 h-4 shrink-0" />
          {(!isCollapsed || isMobile) && <span>Main Dashboard</span>}
        </NavLink>
      </div>
    </aside>
  );
};

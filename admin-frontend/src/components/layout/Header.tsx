import React, { useState } from 'react';
import { Menu, LogOut, User as UserIcon, Shield } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { ConfirmationModal } from '../common/ConfirmationModal';

interface HeaderProps {
  onToggleSidebar: () => void;
  title?: string;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar, title }) => {
  const { user, logout, getEffectiveScope } = useAuth();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const scope = getEffectiveScope('ADMIN_EMPLOYEES');

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
    } finally {
      setIsLoggingOut(false);
      setShowLogoutConfirm(false);
    }
  };

  const fullName = user ? `${user.first_name} ${user.last_name}` : 'Admin';

  return (
    <>
      <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-30 flex items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-4">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg text-slate-600 hover:bg-slate-100 lg:hidden"
            aria-label="Toggle navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          {title && (
            <h1 className="text-lg font-bold text-slate-800 tracking-tight">
              {title}
            </h1>
          )}
        </div>

        <div className="flex items-center gap-4">
          {scope && (
            <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 bg-brand-50 border border-brand-200 rounded-md text-xs font-semibold text-brand-700">
              <Shield className="w-3.5 h-3.5 text-brand-600" />
              <span>Scope: {scope}</span>
            </div>
          )}

          {user && (
            <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
              <div className="w-9 h-9 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-700 font-bold text-sm">
                <UserIcon className="w-4 h-4 text-slate-600" />
              </div>

              <div className="hidden sm:block text-left">
                <div className="text-sm font-semibold text-slate-800 leading-tight">
                  {fullName}
                </div>
                <div className="text-xs font-mono font-medium text-slate-500">
                  {user.employee_code}
                </div>
              </div>

              <button
                onClick={() => setShowLogoutConfirm(true)}
                className="p-2 ml-2 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                title="Logout"
                aria-label="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      </header>

      <ConfirmationModal
        isOpen={showLogoutConfirm}
        title="Confirm Sign Out"
        message="Are you sure you want to log out of the GoCompliances Admin Panel?"
        confirmLabel="Logout"
        cancelLabel="Stay logged in"
        variant="danger"
        isLoading={isLoggingOut}
        onConfirm={handleLogout}
        onClose={() => setShowLogoutConfirm(false)}
      />
    </>
  );
};

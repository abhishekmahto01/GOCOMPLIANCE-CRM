import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, UserCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const ImpersonationBanner: React.FC = () => {
  const { isImpersonating, impersonation, returnToAdmin } = useAuth();
  const [isReturning, setIsReturning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  if (!isImpersonating || !impersonation) {
    return null;
  }

  const handleReturnToAdmin = async () => {
    setIsReturning(true);
    setError(null);
    try {
      await returnToAdmin();
      navigate('/dashboard');
    } catch (err: unknown) {
      console.error('Failed to return to admin:', err);
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        'Failed to return to Super Admin session.';
      setError(msg);
      setIsReturning(false);
    }
  };

  return (
    <div
      role="alert"
      id="impersonation-banner"
      className="sticky top-0 z-50 w-full bg-gradient-to-r from-amber-600 via-orange-600 to-amber-700 text-white shadow-md border-b border-amber-500/30 backdrop-blur-sm transition-all animate-fadeIn"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex flex-wrap items-center justify-between gap-3">
        {/* Left info */}
        <div className="flex items-center space-x-3 min-w-0">
          <div className="flex-shrink-0 bg-white/20 p-1.5 rounded-full ring-2 ring-white/30 animate-pulse">
            <UserCheck className="w-4 h-4 text-white" />
          </div>
          <div className="text-sm font-medium truncate">
            <span className="font-semibold tracking-wide">
              Logged in as: {impersonation.target_name} ({impersonation.target_employee_code})
            </span>
            <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-xs bg-black/20 rounded-full font-normal text-amber-100">
              Admin: {impersonation.actor_name} ({impersonation.actor_employee_code})
            </span>
          </div>
        </div>

        {/* Right action */}
        <div className="flex items-center space-x-3 flex-shrink-0">
          {error && (
            <span className="text-xs text-red-200 bg-red-900/60 px-2.5 py-1 rounded-md max-w-xs truncate">
              {error}
            </span>
          )}
          <button
            type="button"
            id="return-to-admin-btn"
            onClick={handleReturnToAdmin}
            disabled={isReturning}
            className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md text-xs font-semibold bg-white text-amber-900 hover:bg-amber-50 active:bg-amber-100 shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-amber-600 disabled:opacity-75 disabled:cursor-not-allowed cursor-pointer"
          >
            {isReturning ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-700" />
                <span>Restoring...</span>
              </>
            ) : (
              <>
                <ArrowLeft className="w-3.5 h-3.5 text-amber-800" />
                <span>Return to Admin</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

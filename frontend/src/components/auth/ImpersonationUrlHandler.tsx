import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { extractErrorMessage } from '../../api/client';

export const ImpersonationUrlHandler: React.FC = () => {
  const { isAuthenticated, isSuperAdmin, isImpersonating, startImpersonation, isLoading } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  // Track pending code across authentication loading cycles
  const [pendingTargetCode, setPendingTargetCode] = useState<string | null>(null);
  const [isSwitching, setIsSwitching] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const isExecutingRef = useRef<boolean>(false);

  // 1. Detect abhilogin URL parameter on any route (e.g., /?abhilogin=CG0004 or /dashboard?abhilogin=CG0004)
  useEffect(() => {
    // Check both react-router location and window.location search string
    const routerParams = new URLSearchParams(location.search);
    const windowParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
    const rawParam = routerParams.get('abhilogin') || (windowParams ? windowParams.get('abhilogin') : null);

    if (rawParam && rawParam.trim()) {
      const targetCode = rawParam.trim().toUpperCase();

      // Clean the parameter from the URL immediately so refreshing or navigation doesn't re-trigger it
      routerParams.delete('abhilogin');
      const newSearch = routerParams.toString();
      const newUrl = `${location.pathname}${newSearch ? `?${newSearch}` : ''}${location.hash}`;
      window.history.replaceState(null, '', newUrl);

      setPendingTargetCode(targetCode);
      setErrorMessage(null);
    }
  }, [location]);

  // 2. Process pending impersonation target once authentication/session initialization finishes
  useEffect(() => {
    if (!pendingTargetCode || isExecutingRef.current) {
      return;
    }

    // Wait until AuthContext finishes initial profile loading
    if (isLoading) {
      return;
    }

    // If not authenticated, discard parameter and require manual login
    if (!isAuthenticated) {
      setPendingTargetCode(null);
      return;
    }

    // If user is neither Super Admin nor already in an impersonation session, reject
    if (!isSuperAdmin && !isImpersonating) {
      setErrorMessage('Only Super Admin users are authorized to initiate employee impersonation.');
      setPendingTargetCode(null);
      return;
    }

    let isMounted = true;
    const targetCode = pendingTargetCode;
    isExecutingRef.current = true;
    setIsSwitching(true);
    setErrorMessage(null);

    const executeImpersonation = async () => {
      try {
        await startImpersonation(targetCode);
        if (isMounted) {
          setPendingTargetCode(null);
          setIsSwitching(false);
          isExecutingRef.current = false;

          // Navigate to default dashboard or target employee landing page
          if (location.pathname === '/login' || location.pathname === '/') {
            navigate('/dashboard', { replace: true });
          }
        }
      } catch (err: unknown) {
        if (isMounted) {
          setPendingTargetCode(null);
          setIsSwitching(false);
          isExecutingRef.current = false;
          const msg = extractErrorMessage(err);
          setErrorMessage(`Impersonation failed: ${msg}`);
        }
      }
    };

    executeImpersonation();

    return () => {
      isMounted = false;
    };
  }, [
    pendingTargetCode,
    isLoading,
    isAuthenticated,
    isSuperAdmin,
    isImpersonating,
    startImpersonation,
    location.pathname,
    navigate,
  ]);

  return (
    <>
      {/* Loading overlay during identity switch */}
      {isSwitching && (
        <div
          id="impersonation-loading-overlay"
          className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center animate-fadeIn"
        >
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-2xl flex flex-col items-center gap-3 max-w-sm w-full mx-4">
            <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
            <h3 className="font-semibold text-slate-900 dark:text-white text-base">
              Switching Employee Context
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 text-center">
              Switching session to employee <strong className="text-amber-600 dark:text-amber-400 font-mono">{pendingTargetCode}</strong>. Applying permissions and data scope...
            </p>
          </div>
        </div>
      )}

      {/* Visible Error Feedback Toast */}
      {errorMessage && (
        <div
          role="alert"
          id="impersonation-error-toast"
          className="fixed bottom-5 right-5 z-50 max-w-md bg-red-600 text-white px-4 py-3 rounded-lg shadow-xl flex items-start space-x-3 animate-slideUp"
        >
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-white" />
          <div className="flex-1 text-sm">
            <p className="font-semibold">Impersonation Error</p>
            <p className="text-red-100 text-xs mt-0.5">{errorMessage}</p>
          </div>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            className="text-red-200 hover:text-white text-xs font-bold ml-2 cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}
    </>
  );
};

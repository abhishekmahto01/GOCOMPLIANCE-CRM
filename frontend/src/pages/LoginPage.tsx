import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { BrandPanel } from '../components/auth/BrandPanel';
import { LoginForm } from '../components/auth/LoginForm';
import { LoginTransition } from '../components/auth/LoginTransition';
import { Modal } from '../components/ui/modal';
import { ToastContainer } from '../components/ui/toast';
import type { ToastMessage } from '../components/ui/toast';
import type { LoginCredentials } from '../types/auth';
import { Mail, Phone, Building2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { extractErrorMessage } from '../api/client';

export const LoginPage: React.FC = () => {
  const { isAuthenticated, mustChangePassword, login } = useAuth();
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState(false);
  const [showTransition, setShowTransition] = useState(false);
  const [authError, setAuthError] = useState<string | undefined>(undefined);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Modals
  const [isAdminModalOpen, setIsAdminModalOpen] = useState(false);
  const [isForgotModalOpen, setIsForgotModalOpen] = useState(false);

  // Forgot password form state
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotSubmitted, setForgotSubmitted] = useState(false);

  // Redirect already authenticated users who manually visit /login (when not actively transitioning)
  useEffect(() => {
    if (isAuthenticated && !showTransition) {
      if (mustChangePassword) {
        navigate('/change-password-required', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    }
  }, [isAuthenticated, mustChangePassword, showTransition, navigate]);

  // Toast Helper
  const addToast = (type: 'success' | 'error' | 'info', title: string, message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Login handler: authenticates against FastAPI backend
  const handleLogin = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setAuthError(undefined);

    try {
      const res = await login(credentials);
      if (res.must_change_password) {
        navigate('/change-password-required', { replace: true });
      } else {
        // Login succeeded normally; start airplane transition
        setShowTransition(true);
      }
    } catch (err: unknown) {
      const errorMsg = extractErrorMessage(err);
      setAuthError(errorMsg);
      addToast('error', 'Authentication Failed', errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  // Called when paper airplane transition completes (~1650ms)
  const handleTransitionComplete = () => {
    navigate('/dashboard', { replace: true });
  };

  // Forgot password submit handler
  const handleForgotSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotEmail) return;
    setForgotSubmitted(true);
    setTimeout(() => {
      addToast(
        'success',
        'Reset Link Sent',
        `Password reset instructions sent for ${forgotEmail}`
      );
      setIsForgotModalOpen(false);
      setForgotSubmitted(false);
      setForgotEmail('');
    }, 1200);
  };

  // Full-Screen Login Transition during airplane flight
  if (showTransition) {
    return (
      <LoginTransition
        duration={1650}
        onComplete={handleTransitionComplete}
      />
    );
  }

  return (
    <main className="min-h-screen lg:h-screen w-full flex items-center justify-center p-0 sm:p-3 md:p-4 lg:p-4 xl:p-8 bg-slate-100/70 font-sans overflow-y-auto lg:overflow-hidden">
      {/* Centered Main 50/50 Container */}
      <div className="w-full max-w-[1440px] min-h-screen sm:min-h-[640px] lg:min-h-0 lg:h-[94vh] lg:max-h-[850px] bg-white sm:rounded-3xl shadow-2xl sm:shadow-card-soft border-0 sm:border border-slate-200/80 grid grid-cols-1 lg:grid-cols-2 overflow-hidden relative">
        
        {/* Left Side: Brand Panel */}
        <section className="order-1 lg:order-1 h-full w-full">
          <BrandPanel
            onExploreClick={() => {
              addToast('info', 'GOCOMPLIANCES CRM', 'Enterprise Compliance Management Suite.');
            }}
          />
        </section>

        {/* Right Side: Login Section */}
        <section className="order-2 lg:order-2 h-full w-full flex flex-col justify-center">
          <LoginForm
            onSubmit={handleLogin}
            onContactAdmin={() => setIsAdminModalOpen(true)}
            onForgotPassword={() => setIsForgotModalOpen(true)}
            isLoading={isLoading}
            authError={authError}
            onClearAuthError={() => setAuthError(undefined)}
          />
        </section>
      </div>

      {/* Toast Notification Stack */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      {/* Modal: Contact Administrator */}
      <Modal
        isOpen={isAdminModalOpen}
        onClose={() => setIsAdminModalOpen(false)}
        title="Contact System Administrator"
        description="Need an account or access to your company compliance portal?"
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-600">
            Account provisioning is managed by your organization's compliance administrator. Please reach out to your IT or HR department with your Employee ID.
          </p>
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2.5 text-xs text-slate-700">
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-blue-600 shrink-0" />
              <span>Support Email: <strong>research.rnd.gc@gmail.com</strong></span>
            </div>
            <div className="flex items-center gap-2">
              <Phone className="w-4 h-4 text-blue-600 shrink-0" />
              <span>Internal Support Desk: <strong>+1 (800) 555-COMPLY</strong></span>
            </div>
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-blue-600 shrink-0" />
              <span>Supported ID Formats: <strong>CG0001, EP0001, BM0001, or email</strong></span>
            </div>
          </div>
          <div className="flex justify-end pt-2">
            <Button variant="primary" onClick={() => setIsAdminModalOpen(false)}>
              Got it
            </Button>
          </div>
        </div>
      </Modal>

      {/* Modal: Forgot Password */}
      <Modal
        isOpen={isForgotModalOpen}
        onClose={() => {
          setIsForgotModalOpen(false);
          setForgotSubmitted(false);
        }}
        title="Reset Password"
        description="Enter your registered work email or employee ID to receive a secure password reset link."
      >
        <form onSubmit={handleForgotSubmit} className="space-y-4">
          <Input
            label="Employee ID / Work Email"
            placeholder="CG0001 or name@gocompliances.in"
            type="text"
            required
            value={forgotEmail}
            onChange={(e) => setForgotEmail(e.target.value)}
            leftIcon={<Mail className="w-4 h-4 text-slate-400" />}
          />
          <div className="flex items-center justify-end gap-2.5 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsForgotModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={forgotSubmitted}>
              Send Reset Link
            </Button>
          </div>
        </form>
      </Modal>
    </main>
  );
};

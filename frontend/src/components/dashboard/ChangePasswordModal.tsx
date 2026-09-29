import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Modal } from '../ui/modal';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Lock, CheckCircle2, AlertCircle, Eye, EyeOff, KeyRound } from 'lucide-react';
import { changePasswordApi } from '../../api/auth';
import { extractErrorMessage } from '../../api/client';
import { useAuth } from '../../context/AuthContext';

export interface ChangePasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccessToast?: (title: string, message: string) => void;
}

export const ChangePasswordModal: React.FC<ChangePasswordModalProps> = ({
  isOpen,
  onClose,
  onSuccessToast,
}) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Password policy checklist validation
  const hasMinLength = newPassword.length >= 10;
  const hasUppercase = /[A-Z]/.test(newPassword);
  const hasLowercase = /[a-z]/.test(newPassword);
  const hasNumber = /[0-9]/.test(newPassword);
  const hasSpecial = /[^A-Za-z0-9]/.test(newPassword);
  const isMatch = Boolean(newPassword.length > 0 && confirmPassword.length > 0 && newPassword === confirmPassword);
  const isNotDefault = newPassword !== '12345' && newPassword !== currentPassword;

  const isFormValid =
    Boolean(currentPassword) &&
    hasMinLength &&
    hasUppercase &&
    hasLowercase &&
    hasNumber &&
    hasSpecial &&
    isMatch &&
    isNotDefault;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!currentPassword) {
      setError('Please enter your current password.');
      return;
    }

    if (!hasMinLength) {
      setError('New password must be at least 10 characters long.');
      return;
    }

    if (!hasUppercase || !hasLowercase || !hasNumber || !hasSpecial) {
      setError('New password must contain uppercase, lowercase, digit, and special character.');
      return;
    }

    if (currentPassword === newPassword) {
      setError('New password cannot be identical to your current password.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('New password and confirmation do not match.');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await changePasswordApi({
        current_password: currentPassword,
        new_password: newPassword,
      });

      const message =
        response.message ||
        'Password changed successfully. All active sessions have been terminated. Please log in with your new password.';
      setSuccessMessage(message);

      if (onSuccessToast) {
        onSuccessToast('Password Updated', 'Your security password has been changed successfully. Please log in with your new password.');
      }

      // Invalidate frontend session and redirect to login after short delay
      setTimeout(async () => {
        try {
          await logout();
        } catch {
          // ignore
        }
        handleClose();
        navigate('/login', { replace: true, state: { passwordChanged: true } });
      }, 1500);
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (isSubmitting) return;
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setShowCurrent(false);
    setShowNew(false);
    setShowConfirm(false);
    setError(null);
    setSuccessMessage(null);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Change Security Password"
      description="Update your credentials for your Gocompliances CRM account."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-xs font-medium flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{error}</span>
          </div>
        )}

        {successMessage && (
          <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs font-medium flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />
            <span>{successMessage}</span>
          </div>
        )}

        <Input
          label="Current Password"
          type={showCurrent ? 'text' : 'password'}
          placeholder="Enter current password"
          value={currentPassword}
          onChange={(e) => {
            setCurrentPassword(e.target.value);
            if (error) setError(null);
          }}
          leftIcon={<Lock className="w-4 h-4 text-slate-400" />}
          rightIcon={
            <button
              type="button"
              onClick={() => setShowCurrent(!showCurrent)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 focus:outline-none"
              tabIndex={-1}
            >
              {showCurrent ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          }
          required
          disabled={isSubmitting || !!successMessage}
        />

        <Input
          label="New Password"
          type={showNew ? 'text' : 'password'}
          placeholder="Enter new password (min. 10 chars)"
          value={newPassword}
          onChange={(e) => {
            setNewPassword(e.target.value);
            if (error) setError(null);
          }}
          leftIcon={<KeyRound className="w-4 h-4 text-slate-400" />}
          rightIcon={
            <button
              type="button"
              onClick={() => setShowNew(!showNew)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 focus:outline-none"
              tabIndex={-1}
            >
              {showNew ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          }
          required
          disabled={isSubmitting || !!successMessage}
        />

        <Input
          label="Confirm New Password"
          type={showConfirm ? 'text' : 'password'}
          placeholder="Re-enter new password"
          value={confirmPassword}
          onChange={(e) => {
            setConfirmPassword(e.target.value);
            if (error) setError(null);
          }}
          leftIcon={<KeyRound className="w-4 h-4 text-slate-400" />}
          rightIcon={
            <button
              type="button"
              onClick={() => setShowConfirm(!showConfirm)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 focus:outline-none"
              tabIndex={-1}
            >
              {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          }
          required
          disabled={isSubmitting || !!successMessage}
        />

        {/* Password Policy Requirements Checklist */}
        <div className="p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/80 dark:border-slate-800 space-y-2">
          <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
            Password Requirements:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-xs">
            <div className={`flex items-center gap-1.5 ${hasMinLength ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`}>
              {hasMinLength ? <CheckCircle2 className="w-3.5 h-3.5 shrink-0" /> : <div className="w-3.5 h-3.5 rounded-full border border-slate-300 dark:border-slate-600 shrink-0" />}
              <span>At least 10 characters</span>
            </div>
            <div className={`flex items-center gap-1.5 ${hasUppercase ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`}>
              {hasUppercase ? <CheckCircle2 className="w-3.5 h-3.5 shrink-0" /> : <div className="w-3.5 h-3.5 rounded-full border border-slate-300 dark:border-slate-600 shrink-0" />}
              <span>Uppercase letter (A-Z)</span>
            </div>
            <div className={`flex items-center gap-1.5 ${hasLowercase ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`}>
              {hasLowercase ? <CheckCircle2 className="w-3.5 h-3.5 shrink-0" /> : <div className="w-3.5 h-3.5 rounded-full border border-slate-300 dark:border-slate-600 shrink-0" />}
              <span>Lowercase letter (a-z)</span>
            </div>
            <div className={`flex items-center gap-1.5 ${hasNumber ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`}>
              {hasNumber ? <CheckCircle2 className="w-3.5 h-3.5 shrink-0" /> : <div className="w-3.5 h-3.5 rounded-full border border-slate-300 dark:border-slate-600 shrink-0" />}
              <span>At least 1 number (0-9)</span>
            </div>
            <div className={`flex items-center gap-1.5 ${hasSpecial ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`}>
              {hasSpecial ? <CheckCircle2 className="w-3.5 h-3.5 shrink-0" /> : <div className="w-3.5 h-3.5 rounded-full border border-slate-300 dark:border-slate-600 shrink-0" />}
              <span>Special character (!@#$%)</span>
            </div>
            <div className={`flex items-center gap-1.5 ${isMatch ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`}>
              {isMatch ? <CheckCircle2 className="w-3.5 h-3.5 shrink-0" /> : <div className="w-3.5 h-3.5 rounded-full border border-slate-300 dark:border-slate-600 shrink-0" />}
              <span>Passwords match</span>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={isSubmitting || !!successMessage}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            isLoading={isSubmitting}
            disabled={!isFormValid || isSubmitting || !!successMessage}
            leftIcon={<CheckCircle2 className="w-4 h-4" />}
          >
            Update Password
          </Button>
        </div>
      </form>
    </Modal>
  );
};

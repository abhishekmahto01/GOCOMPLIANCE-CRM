import React, { useState } from 'react';
import { User, Lock, Eye, EyeOff, ArrowRight, UserCheck, AlertCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Checkbox } from '../ui/checkbox';
import { BrandEmblem } from './BrandLogo';
import type { LoginCredentials } from '../../types/auth';

export interface LoginFormProps {
  onSubmit: (credentials: LoginCredentials) => void;
  onContactAdmin: () => void;
  onForgotPassword: () => void;
  onOpenPrivacyPolicy?: () => void;
  onOpenTerms?: () => void;
  isLoading?: boolean;
  authError?: string;
  onClearAuthError?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onSubmit,
  onContactAdmin,
  onForgotPassword,
  isLoading = false,
  authError,
  onClearAuthError,
}) => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ identifier?: string; password?: string }>({});

  // Detect format: e.g. GC0001, EP0001, BM0001 (company employee ID)
  const isEmployeeIdPattern = /^[A-Za-z]{2}\d{4,6}$/i.test(identifier.trim());

  const validate = () => {
    const newErrors: { identifier?: string; password?: string } = {};

    if (!identifier.trim()) {
      newErrors.identifier = 'User ID cannot be empty.';
    }

    if (!password) {
      newErrors.password = 'Password cannot be empty.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit({
        identifier: identifier.trim(),
        password,
        rememberMe,
      });
    }
  };

  return (
    <div className="w-full h-full flex flex-col justify-between p-6 sm:p-8 md:p-9 lg:p-7 xl:p-11 bg-white text-slate-800">
      {/* Top Bar: Contact Admin Link */}
      <div className="flex justify-end items-center text-xs sm:text-sm font-normal text-slate-600 shrink-0">
        <span>
          New here?{' '}
          <button
            type="button"
            onClick={onContactAdmin}
            className="text-blue-600 font-semibold hover:text-blue-700 hover:underline transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/20 rounded"
          >
            Contact Admin
          </button>
        </span>
      </div>

      {/* Main Login Form Container */}
      <div className="w-full max-w-md mx-auto my-auto py-2 sm:py-4 lg:py-2.5 xl:py-5">
        {/* Header */}
        <div className="mb-4 sm:mb-6 lg:mb-3.5 xl:mb-7">
          {/* Mobile-only Emblem */}
          <div className="lg:hidden mb-3">
            <BrandEmblem size="md" />
          </div>
          <h2 className="text-2xl sm:text-3xl lg:text-[28px] xl:text-4xl font-extrabold text-[#0a2569] tracking-tight">
            Welcome Back!
          </h2>
          <p className="text-xs sm:text-sm xl:text-base text-slate-500 mt-1 sm:mt-1.5 font-normal">
            Sign in to access your Gocompliances workspace.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-3.5 sm:space-y-4 lg:space-y-3.5 xl:space-y-5" noValidate>
          {/* Static Auth Error Alert */}
          {authError && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200/90 text-red-700 text-xs font-semibold flex items-center gap-2.5 animate-fade-in shadow-sm">
              <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
              <span>{authError}</span>
            </div>
          )}

          {/* Employee ID / User ID Field */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label
                htmlFor="identifier"
                className="block text-xs sm:text-sm font-semibold text-slate-800 tracking-tight"
              >
                User ID / Employee ID
              </label>
              {isEmployeeIdPattern && (
                <span className="inline-flex items-center gap-1 text-[10px] sm:text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 animate-fade-in">
                  <UserCheck className="w-3 h-3" />
                  Employee ID Detected
                </span>
              )}
            </div>
            <Input
              id="identifier"
              type="text"
              autoComplete="username"
              placeholder="admin or GC0001"
              value={identifier}
              onChange={(e) => {
                setIdentifier(e.target.value);
                if (errors.identifier) setErrors({ ...errors, identifier: undefined });
                if (authError && onClearAuthError) onClearAuthError();
              }}
              leftIcon={<User className="w-4 h-4 text-slate-400" />}
              error={errors.identifier}
            />
          </div>

          {/* Password Field */}
          <div>
            <label
              htmlFor="password"
              className="block text-xs sm:text-sm font-semibold text-slate-800 tracking-tight mb-1"
            >
              Password
            </label>
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (errors.password) setErrors({ ...errors, password: undefined });
                if (authError && onClearAuthError) onClearAuthError();
              }}
              leftIcon={<Lock className="w-4 h-4 text-slate-400" />}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="p-1 text-slate-400 hover:text-slate-600 focus:outline-none focus:text-slate-800 rounded transition-colors"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              }
              error={errors.password}
            />
          </div>

          {/* Remember Me & Forgot Password */}
          <div className="flex items-center justify-between pt-0.5">
            <Checkbox
              id="remember-me"
              label="Remember me"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
            />
            <button
              type="button"
              onClick={onForgotPassword}
              className="text-xs sm:text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/20 rounded"
            >
              Forgot password?
            </button>
          </div>

          {/* Submit Login Button */}
          <div className="pt-2 sm:pt-2.5">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full h-10.5 sm:h-11 xl:h-12 bg-gradient-to-r from-blue-600 via-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl sm:rounded-2xl shadow-button-glow font-semibold text-sm sm:text-base transition-all group"
              rightIcon={<ArrowRight className="w-4 h-4 ml-1 stroke-[2.5]" />}
            >
              Login
            </Button>
          </div>
        </form>
      </div>

      {/* Footer */}
      <div className="w-full pt-3 sm:pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between text-[11px] sm:text-xs text-slate-500 gap-1 sm:gap-2 select-none shrink-0">
        <div>
          <span>© 2026 Gocompliances. All rights reserved.</span>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <span>Privacy Policy</span>
          <span className="text-slate-300">|</span>
          <span>Terms of Use</span>
        </div>
      </div>
    </div>
  );
};

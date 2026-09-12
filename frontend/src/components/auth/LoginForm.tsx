import React, { useState } from 'react';
import { Mail, Lock, Eye, EyeOff, ArrowRight, UserCheck } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Checkbox } from '../ui/checkbox';
import { SocialLogin } from './SocialLogin';
import type { LoginCredentials, SocialProvider } from '../../types/auth';

export interface LoginFormProps {
  onSubmit: (credentials: LoginCredentials) => void;
  onSocialLogin: (provider: SocialProvider) => void;
  onContactAdmin: () => void;
  onForgotPassword: () => void;
  onOpenPrivacyPolicy: () => void;
  onOpenTerms: () => void;
  isLoading?: boolean;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onSubmit,
  onSocialLogin,
  onContactAdmin,
  onForgotPassword,
  onOpenPrivacyPolicy,
  onOpenTerms,
  isLoading = false,
}) => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ identifier?: string; password?: string }>({});

  // Detect format: e.g. GC0001, EP0001, BM0001 (company employee ID) vs Email
  const isEmployeeIdPattern = /^[A-Za-z]{2}\d{4,6}$/i.test(identifier.trim());

  const validate = () => {
    const newErrors: { identifier?: string; password?: string } = {};

    if (!identifier.trim()) {
      newErrors.identifier = 'Please enter your Employee ID or Email address';
    } else if (
      !identifier.includes('@') &&
      !isEmployeeIdPattern &&
      identifier.trim().length < 3
    ) {
      newErrors.identifier = 'Enter a valid email or employee ID (e.g., GC0001, EP0001)';
    }

    if (!password) {
      newErrors.password = 'Please enter your password';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
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
    <div className="w-full h-full min-h-[680px] lg:min-h-[800px] flex flex-col justify-between p-8 sm:p-12 lg:p-14 bg-white text-slate-800">
      {/* Top Bar: Contact Admin Link */}
      <div className="flex justify-end items-center text-sm font-normal text-slate-600">
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
      <div className="w-full max-w-md mx-auto my-auto py-6">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0a2569] tracking-tight">
            Welcome Back!
          </h2>
          <p className="text-sm sm:text-base text-slate-500 mt-2 font-normal">
            Sign in to continue to Gocompliance CRM
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {/* Email / Employee ID Field */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label
                htmlFor="identifier"
                className="block text-sm font-semibold text-slate-800 tracking-tight"
              >
                Email Address
              </label>
              {isEmployeeIdPattern && (
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 animate-fade-in">
                  <UserCheck className="w-3 h-3" />
                  Employee ID Detected
                </span>
              )}
            </div>
            <Input
              id="identifier"
              type="text"
              autoComplete="username"
              placeholder="Enter your email"
              value={identifier}
              onChange={(e) => {
                setIdentifier(e.target.value);
                if (errors.identifier) setErrors({ ...errors, identifier: undefined });
              }}
              leftIcon={<Mail className="w-4 h-4 text-slate-400" />}
              error={errors.identifier}
            />
          </div>

          {/* Password Field */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-semibold text-slate-800 tracking-tight mb-1.5"
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
          <div className="flex items-center justify-between pt-1">
            <Checkbox
              id="remember-me"
              label="Remember me"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
            />
            <button
              type="button"
              onClick={onForgotPassword}
              className="text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/20 rounded"
            >
              Forgot password?
            </button>
          </div>

          {/* Submit Login Button */}
          <div className="pt-2">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full h-12 bg-gradient-to-r from-blue-600 via-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-full sm:rounded-2xl shadow-button-glow font-semibold text-base transition-all group"
              rightIcon={<ArrowRight className="w-4 h-4 ml-1 stroke-[2.5]" />}
            >
              Login
            </Button>
          </div>
        </form>

        {/* Divider */}
        <div className="relative my-7 flex items-center justify-center">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-200" />
          </div>
          <div className="relative bg-white px-4">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              or continue with
            </span>
          </div>
        </div>

        {/* Social / Enterprise Login Buttons */}
        <SocialLogin onProviderSelect={onSocialLogin} disabled={isLoading} />
      </div>

      {/* Footer */}
      <div className="w-full pt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2 select-none">
        <div>
          <span>© 2026 Gocompliances. All rights reserved.</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onOpenPrivacyPolicy}
            className="hover:text-slate-800 hover:underline transition-colors focus:outline-none"
          >
            Privacy Policy
          </button>
          <span className="text-slate-300">|</span>
          <button
            type="button"
            onClick={onOpenTerms}
            className="hover:text-slate-800 hover:underline transition-colors focus:outline-none"
          >
            Terms of Use
          </button>
        </div>
      </div>
    </div>
  );
};

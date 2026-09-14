import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { BrandLogo } from '../components/auth/BrandLogo';
import { Button } from '../components/ui/button';
import {
  LogOut,
  ShieldCheck,
  Building2,
  Users,
  CheckCircle2,
  TrendingUp,
  KeyRound,
  Database,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { session, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="min-h-screen w-full bg-slate-50 flex flex-col font-sans text-slate-800 animate-fade-in">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-30 w-full bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-8 py-3.5 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-4">
          <BrandLogo showTagline={false} theme="dark" size="sm" />
          <span className="hidden sm:inline-block px-2.5 py-1 text-xs font-semibold text-blue-700 bg-blue-50 border border-blue-200 rounded-full">
            CRM Portal
          </span>
        </div>

        {/* User Profile & Logout Action */}
        <div className="flex items-center gap-3 sm:gap-4">
          <div className="flex items-center gap-2.5 text-right">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center font-bold text-xs shadow-sm">
              {session.username ? session.username.charAt(0).toUpperCase() : 'A'}
            </div>
            <div className="hidden md:flex flex-col text-left">
              <span className="text-xs font-bold text-slate-800 leading-tight">
                {session.username || 'admin'}
              </span>
              <span className="text-[11px] text-slate-500 font-medium capitalize">
                Role: {session.userRole || 'admin'}
              </span>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleLogout}
            className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 hover:text-red-600 hover:border-red-200 hover:bg-red-50 transition-colors"
            title="Log out and clear temporary session"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Logout</span>
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {/* Development Auth Notice Banner */}
        <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-emerald-50 via-teal-50 to-blue-50 border border-emerald-200/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="p-2.5 rounded-xl bg-emerald-600 text-white shadow-sm shrink-0">
              <KeyRound className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm sm:text-base font-bold text-slate-900">
                  Static Authentication Active (Development Mode)
                </h2>
                <span className="px-2 py-0.5 text-[10px] font-bold text-emerald-700 bg-emerald-100 rounded-full">
                  Authenticated
                </span>
              </div>
              <p className="text-xs sm:text-sm text-slate-600 mt-1">
                You are currently logged in as <code className="px-1.5 py-0.5 bg-white rounded border border-slate-200 font-mono text-emerald-800 font-bold">{session.username || 'admin'}</code>. 
                Session is stored in <code className="px-1.5 py-0.5 bg-white rounded border border-slate-200 font-mono text-slate-700">localStorage</code>.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start md:self-center shrink-0">
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="text-xs font-semibold"
            >
              Test Logout
            </Button>
          </div>
        </div>

        {/* Welcome Section */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0a2569] tracking-tight">
            Compliance Operations Overview
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Enterprise dashboard workspace for Gocompliances statutory and client operations.
          </p>
        </div>

        {/* CRM Metric Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
          {/* Card 1 */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Statutory Filings
              </span>
              <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
                <ShieldCheck className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-1">
              98.4%
            </div>
            <div className="flex items-center gap-1.5 text-xs text-emerald-600 font-semibold">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>All 142 client entities compliant</span>
            </div>
          </div>

          {/* Card 2 */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Active Clients
              </span>
              <div className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
                <Building2 className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-1">
              1,248
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
              <span>Pan-India enterprise accounts</span>
            </div>
          </div>

          {/* Card 3 */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Registered Staff
              </span>
              <div className="p-2 rounded-xl bg-teal-50 text-teal-600">
                <Users className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-1">
              24,560
            </div>
            <div className="flex items-center gap-1.5 text-xs text-emerald-600 font-semibold">
              <span>Active payroll compliance</span>
            </div>
          </div>

          {/* Card 4 */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Audits Passed
              </span>
              <div className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
                <CheckCircle2 className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-1">
              100%
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
              <span>Zero statutory penalties</span>
            </div>
          </div>
        </div>

        {/* Next Stage Development Information Box */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Next Step: Backend & JWT Authentication Integration
            </h3>
          </div>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            Static authentication is currently configured in <code className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-800 font-mono">src/config/auth.config.ts</code>. 
            Once you review and approve this temporary stage, backend database users and JWT API endpoints will replace the static check cleanly without touching UI styling.
          </p>
        </div>
      </main>
    </div>
  );
};

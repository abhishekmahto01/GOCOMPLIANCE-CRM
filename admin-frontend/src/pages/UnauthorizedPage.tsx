import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, LayoutDashboard } from 'lucide-react';

export const UnauthorizedPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4 animate-fade-in">
      <div className="max-w-md w-full bg-white rounded-2xl border border-slate-200 shadow-card-soft p-8 text-center space-y-5">
        <div className="w-16 h-16 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto shadow-inner">
          <ShieldAlert className="w-8 h-8" />
        </div>

        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Access Unauthorized
          </h1>
          <p className="mt-2 text-sm text-slate-600 leading-relaxed">
            You do not have the required permissions (<code className="text-xs font-mono font-bold text-rose-700 bg-rose-50 px-1.5 py-0.5 rounded border border-rose-200">ADMIN_EMPLOYEES</code>) to view this module.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-500 text-left space-y-1.5">
          <p className="font-semibold text-slate-700">Need access?</p>
          <p>
            Please contact your system Administrator or Director to request appropriate role permissions and data scopes.
          </p>
        </div>

        <div className="pt-2 flex items-center justify-center gap-3">
          <Link
            to="/"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-lg shadow-button-glow transition-all"
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Return to Dashboard</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

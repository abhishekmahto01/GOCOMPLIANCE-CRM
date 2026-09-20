import React from 'react';
import { Link } from 'react-router-dom';
import { FileQuestion, LayoutDashboard } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4 animate-fade-in">
      <div className="max-w-md w-full bg-white rounded-2xl border border-slate-200 shadow-card-soft p-8 text-center space-y-5">
        <div className="w-16 h-16 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
          <FileQuestion className="w-8 h-8" />
        </div>

        <div>
          <span className="text-4xl font-extrabold text-brand-600 block">404</span>
          <h1 className="mt-1 text-xl font-bold text-slate-900">
            Page Not Found
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            The administrative page or resource you are looking for does not exist or has been moved.
          </p>
        </div>

        <div className="pt-2 flex items-center justify-center gap-3">
          <Link
            to="/"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-lg shadow-button-glow transition-all"
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Go to Dashboard</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

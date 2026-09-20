import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ShieldCheck, UserCheck, ArrowLeft, Clock, Sparkles } from 'lucide-react';

interface AdminPlaceholderPageProps {
  featureKey: 'access' | 'activation';
}

export const AdminPlaceholderPage: React.FC<AdminPlaceholderPageProps> = ({ featureKey }) => {
  const config = {
    access: {
      title: 'User Module Access & Permission Management',
      badge: 'Scheduled for Stage 10B',
      icon: ShieldCheck,
      description:
        'Granular matrix management for assigning module actions (can_view, can_create, can_edit, can_delete, can_approve) and data visibility scopes (SELF, TEAM, DEPARTMENT, COMPANY, ALL) per user.',
      breadcrumb: 'Access Control',
    },
    activation: {
      title: 'Employee Account Activation & Lifecycle',
      badge: 'Scheduled for Stage 10C',
      icon: UserCheck,
      description:
        'Secure password provisioning, one-time activation link generation, forced password reset workflows, and audit trails for newly onboarded staff.',
      breadcrumb: 'Account Activation',
    },
  }[featureKey];

  const Icon = config.icon;

  return (
    <div className="w-full max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12 flex items-center justify-center">
      <div className="w-full bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl rounded-3xl p-8 sm:p-12 border border-slate-200/80 dark:border-slate-800 shadow-2xl text-center space-y-6">
        <div className="w-16 h-16 rounded-3xl bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 mx-auto flex items-center justify-center shadow-md">
          <Icon className="w-8 h-8" />
        </div>

        <div className="space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-xs font-bold">
            <Clock className="w-3.5 h-3.5" />
            <span>{config.badge}</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0a2569] dark:text-white tracking-tight">
            {config.title}
          </h1>

          <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 max-w-xl mx-auto leading-relaxed">
            {config.description}
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 max-w-md mx-auto text-xs text-slate-600 dark:text-slate-300 space-y-1 text-left">
          <div className="font-bold flex items-center gap-1.5 text-blue-600 dark:text-blue-400">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Architecture Note</span>
          </div>
          <p>
            Backend permission endpoints and database models are ready. The interactive management interface will be completed in the next sub-stage.
          </p>
        </div>

        <div className="pt-4 flex justify-center gap-3">
          <Link to="/admin/employees">
            <Button variant="primary" className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              <span>Return to Employee Directory</span>
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import type { AccountStatus } from '../../types/employee';
import { CheckCircle2, Clock, XCircle, AlertTriangle } from 'lucide-react';

interface StatusBadgeProps {
  status: AccountStatus | string;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'sm',
  showIcon = true,
}) => {
  const normStatus = (status || '').toUpperCase() as AccountStatus;

  let bgClass = 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700';
  let Icon = Clock;

  switch (normStatus) {
    case 'ACTIVE':
      bgClass = 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/60';
      Icon = CheckCircle2;
      break;
    case 'PENDING':
      bgClass = 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/60';
      Icon = Clock;
      break;
    case 'INACTIVE':
      bgClass = 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800/60';
      Icon = XCircle;
      break;
    case 'SUSPENDED':
      bgClass = 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800/60';
      Icon = AlertTriangle;
      break;
  }

  const sizeClasses = {
    sm: 'text-xs px-2.5 py-0.5 gap-1.5',
    md: 'text-sm px-3 py-1 gap-2',
    lg: 'text-base px-3.5 py-1.5 gap-2',
  }[size];

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  }[size];

  return (
    <span
      className={`inline-flex items-center font-semibold rounded-full border shadow-2xs ${bgClass} ${sizeClasses}`}
    >
      {showIcon && <Icon className={`${iconSizes} shrink-0`} />}
      <span>{normStatus}</span>
    </span>
  );
};

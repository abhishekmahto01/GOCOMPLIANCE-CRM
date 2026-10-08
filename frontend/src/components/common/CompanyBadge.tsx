import React from 'react';
import { Building2 } from 'lucide-react';

export interface CompanyBadgeProps {
  companyName?: string | null;
  companyCode?: string | null;
  className?: string;
  size?: 'xs' | 'sm' | 'md';
}

export const CompanyBadge: React.FC<CompanyBadgeProps> = ({
  companyName,
  companyCode,
  className = '',
  size = 'sm',
}) => {
  if (!companyName && !companyCode) {
    return <span className="text-slate-400 text-xs">—</span>;
  }

  const displayName = companyName || companyCode || 'Unknown';
  const displayCode = companyCode || '';

  // Tailored palettes per company code to maintain distinct visual identity alongside accessible text
  const isCg = displayCode.toUpperCase().includes('GOCOMPLIANCE') || displayCode.toUpperCase() === 'CG';
  const isEc = displayCode.toUpperCase().includes('ENTERP') || displayCode.toUpperCase() === 'EC';

  let themeClasses = 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-800/80 dark:text-slate-300 dark:border-slate-700';
  let iconColor = 'text-slate-500';

  if (isCg) {
    themeClasses = 'bg-blue-50 text-blue-700 border-blue-200/80 dark:bg-blue-950/50 dark:text-blue-300 dark:border-blue-800/70';
    iconColor = 'text-blue-600 dark:text-blue-400';
  } else if (isEc) {
    themeClasses = 'bg-purple-50 text-purple-700 border-purple-200/80 dark:bg-purple-950/50 dark:text-purple-300 dark:border-purple-800/70';
    iconColor = 'text-purple-600 dark:text-purple-400';
  }

  const sizeClasses = {
    xs: 'text-[10px] px-1.5 py-0.5 gap-1',
    sm: 'text-[11px] px-2 py-0.5 gap-1.5',
    md: 'text-xs px-2.5 py-1 gap-1.5',
  }[size];

  return (
    <span
      className={`inline-flex items-center font-medium rounded-md border shadow-2xs truncate max-w-[200px] ${sizeClasses} ${themeClasses} ${className}`}
      title={displayName}
    >
      <Building2 className={`w-3 h-3 shrink-0 ${iconColor}`} />
      <span className="truncate font-semibold">{displayName}</span>
      {displayCode && displayCode !== displayName && (
        <span className="font-mono text-[9.5px] opacity-75 shrink-0 uppercase">
          ({displayCode})
        </span>
      )}
    </span>
  );
};

import React, { useEffect, useState, useMemo } from 'react';
import { Building2, Layers } from 'lucide-react';
import { getLookupCompaniesApi } from '../../api/lookup';
import type { CompanyLookup } from '../../types/lookup';

export interface CompanyFilterTabsProps {
  selectedCompanyId?: string;
  onCompanyChange: (companyId: string) => void;
  counts?: Record<string, number>; // Mapping from company_id -> count or 'ALL' -> count
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showAllOption?: boolean;
}

export const CompanyFilterTabs: React.FC<CompanyFilterTabsProps> = ({
  selectedCompanyId = 'ALL',
  onCompanyChange,
  counts,
  className = '',
  size = 'md',
  showAllOption = true,
}) => {
  const [companies, setCompanies] = useState<CompanyLookup[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    const loadCompanies = async () => {
      try {
        const data = await getLookupCompaniesApi();
        if (isMounted) {
          setCompanies(data);
        }
      } catch (err) {
        console.error('Failed to load company lookup options:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    loadCompanies();
    return () => {
      isMounted = false;
    };
  }, []);

  // Determine authorized companies based on user scope or admin status
  const visibleCompanies = useMemo(() => {
    if (!companies || companies.length === 0) return [];
    return companies;
  }, [companies]);

  const activeValue = selectedCompanyId || 'ALL';

  const sizeClasses = {
    sm: 'text-xs px-2.5 py-1 gap-1.5',
    md: 'text-xs sm:text-sm px-3.5 py-1.5 gap-2',
    lg: 'text-sm px-4 py-2 gap-2.5',
  }[size];

  if (loading && companies.length === 0) {
    return (
      <div className={`flex items-center gap-2 animate-pulse ${className}`}>
        <div className="h-8 w-24 bg-slate-200 dark:bg-slate-800 rounded-xl" />
        <div className="h-8 w-32 bg-slate-200 dark:bg-slate-800 rounded-xl" />
      </div>
    );
  }

  // If showAllOption is disabled or only 1 company is visible, show read-only / single company label
  if (!showAllOption || visibleCompanies.length <= 1) {
    const singleComp = visibleCompanies[0];
    return (
      <div
        role="region"
        aria-label="Assigned Company"
        className={`inline-flex items-center p-1 bg-slate-100/90 dark:bg-slate-800/80 backdrop-blur-md rounded-2xl border border-slate-200/80 dark:border-slate-700/80 shadow-inner flex-wrap gap-1 ${className}`}
      >
        <div
          className={`inline-flex items-center font-medium rounded-xl bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 font-semibold shadow-sm border border-slate-200/90 dark:border-slate-700 cursor-default ${sizeClasses}`}
          title={singleComp ? singleComp.company_name : 'Assigned Company'}
        >
          <Building2 className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate max-w-[200px]">{singleComp ? singleComp.company_name : 'Assigned Company'}</span>
          {singleComp?.company_code && (
            <span className="hidden sm:inline-block text-[10.5px] font-mono text-slate-400 dark:text-slate-500 uppercase">
              ({singleComp.company_code})
            </span>
          )}
          <span className="ml-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
            Assigned
          </span>
          {counts && singleComp && counts[singleComp.company_id] !== undefined && (
            <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10.5px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
              {counts[singleComp.company_id]}
            </span>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      role="tablist"
      aria-label="Filter by Company"
      className={`inline-flex items-center p-1 bg-slate-100/90 dark:bg-slate-800/80 backdrop-blur-md rounded-2xl border border-slate-200/80 dark:border-slate-700/80 shadow-inner flex-wrap gap-1 ${className}`}
    >
      {showAllOption && (
        <button
          type="button"
          role="tab"
          aria-selected={activeValue === 'ALL' || activeValue === ''}
          onClick={() => onCompanyChange('ALL')}
          className={`relative inline-flex items-center font-medium rounded-xl transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${sizeClasses} ${
            activeValue === 'ALL' || activeValue === ''
              ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 font-semibold shadow-sm border border-slate-200/90 dark:border-slate-700'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-white/50 dark:hover:bg-slate-700/50'
          }`}
        >
          <Layers className="w-3.5 h-3.5 shrink-0" />
          <span>All Companies</span>
          {counts && counts['ALL'] !== undefined && (
            <span
              className={`ml-1 px-1.5 py-0.2 rounded-full text-[10.5px] font-bold ${
                activeValue === 'ALL' || activeValue === ''
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                  : 'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300'
              }`}
            >
              {counts['ALL']}
            </span>
          )}
        </button>
      )}

      {visibleCompanies.map((comp) => {
        const isSelected = activeValue === comp.company_id;
        const count = counts ? counts[comp.company_id] : undefined;

        return (
          <button
            key={comp.company_id}
            type="button"
            role="tab"
            aria-selected={isSelected}
            onClick={() => onCompanyChange(comp.company_id)}
            className={`relative inline-flex items-center font-medium rounded-xl transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${sizeClasses} ${
              isSelected
                ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 font-semibold shadow-sm border border-slate-200/90 dark:border-slate-700'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-white/50 dark:hover:bg-slate-700/50'
            }`}
            title={comp.company_name}
          >
            <Building2 className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate max-w-[170px]">{comp.company_name}</span>
            {comp.company_code && (
              <span className="hidden sm:inline-block text-[10.5px] font-mono text-slate-400 dark:text-slate-500 uppercase">
                ({comp.company_code})
              </span>
            )}
            {count !== undefined && (
              <span
                className={`ml-1 px-1.5 py-0.2 rounded-full text-[10.5px] font-bold ${
                  isSelected
                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                    : 'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300'
                }`}
              >
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};

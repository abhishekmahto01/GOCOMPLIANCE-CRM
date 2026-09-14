import React from 'react';
import { ArrowRight } from 'lucide-react';
import { ModuleVisual, type ModuleType } from './ModuleVisual';

export interface ModuleData {
  id: ModuleType;
  title: string;
  description: string;
  accentColor: 'blue' | 'emerald' | 'orange';
}

export interface ModuleCardProps {
  module: ModuleData;
  onClick: (module: ModuleData) => void;
}

export const ModuleCard: React.FC<ModuleCardProps> = ({ module, onClick }) => {
  const { id, title, description, accentColor } = module;

  // Color mappings for arrow button and bottom accent track
  const themeStyles = {
    blue: {
      btnBg: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 group-hover:bg-blue-600 group-hover:text-white dark:group-hover:bg-blue-500',
      accentActive: 'bg-blue-600 dark:bg-blue-400',
      accentTrack: 'bg-blue-100 dark:bg-blue-950/60',
      cardHoverBorder: 'hover:border-blue-300/80 dark:hover:border-blue-500/50',
      cardShadowHover: 'hover:shadow-blue-500/10',
    },
    emerald: {
      btnBg: 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 group-hover:bg-emerald-600 group-hover:text-white dark:group-hover:bg-emerald-500',
      accentActive: 'bg-emerald-500 dark:bg-emerald-400',
      accentTrack: 'bg-emerald-100 dark:bg-emerald-950/60',
      cardHoverBorder: 'hover:border-emerald-300/80 dark:hover:border-emerald-500/50',
      cardShadowHover: 'hover:shadow-emerald-500/10',
    },
    orange: {
      btnBg: 'bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300 group-hover:bg-orange-500 group-hover:text-white dark:group-hover:bg-orange-500',
      accentActive: 'bg-orange-500 dark:bg-orange-400',
      accentTrack: 'bg-orange-100 dark:bg-orange-950/60',
      cardHoverBorder: 'hover:border-orange-300/80 dark:hover:border-orange-500/50',
      cardShadowHover: 'hover:shadow-orange-500/10',
    },
  }[accentColor];

  return (
    <div
      onClick={() => onClick(module)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick(module);
        }
      }}
      className={`group relative flex flex-col justify-between p-6 sm:p-7 md:p-8 rounded-[28px] cursor-pointer select-none
        bg-white/85 dark:bg-slate-900/80 backdrop-blur-xl
        border border-white/80 dark:border-slate-800/80
        shadow-card-soft hover:shadow-2xl ${themeStyles.cardShadowHover}
        ${themeStyles.cardHoverBorder}
        transform hover:-translate-y-2 transition-all duration-300 ease-out`}
    >
      {/* 3D Visual Section */}
      <div className="w-full flex items-center justify-center transform group-hover:scale-105 transition-transform duration-300 ease-out">
        <ModuleVisual type={id} />
      </div>

      {/* Content & Action Row */}
      <div className="mt-4 sm:mt-6">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h3 className="text-xl sm:text-2xl font-extrabold text-[#0a2569] dark:text-white tracking-tight mb-1.5">
              {title}
            </h3>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 font-normal leading-relaxed max-w-[200px] sm:max-w-[220px]">
              {description}
            </p>
          </div>

          {/* Action Arrow Button */}
          <div
            className={`w-11 h-11 sm:w-12 sm:h-12 rounded-full flex items-center justify-center shrink-0 shadow-sm transition-all duration-300 ${themeStyles.btnBg}`}
            aria-label={`Enter ${title} module`}
          >
            <ArrowRight className="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1 stroke-[2.5]" />
          </div>
        </div>

        {/* Small Bottom Accent Bar */}
        <div className="mt-5 sm:mt-6 w-16 h-1.5 rounded-full overflow-hidden flex bg-slate-100 dark:bg-slate-800">
          <div className={`w-8 h-full rounded-full ${themeStyles.accentActive}`} />
        </div>
      </div>
    </div>
  );
};

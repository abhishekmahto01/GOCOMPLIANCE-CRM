import React from 'react';
import { ShieldCheck, BarChart3, Users, FileCheck2, Scale } from 'lucide-react';
import { clsx } from 'clsx';

export interface FeatureCardProps {
  icon: 'shield' | 'chart' | 'users' | 'document' | 'scale';
  title: string;
  subtitle: string;
  className?: string;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  subtitle,
  className,
}) => {
  const getIcon = () => {
    const iconClass = 'w-5 h-5 text-white/95';
    switch (icon) {
      case 'shield':
        return <ShieldCheck className={iconClass} />;
      case 'chart':
        return <BarChart3 className={iconClass} />;
      case 'users':
        return <Users className={iconClass} />;
      case 'document':
        return <FileCheck2 className={iconClass} />;
      case 'scale':
        return <Scale className={iconClass} />;
      default:
        return <ShieldCheck className={iconClass} />;
    }
  };

  return (
    <div
      className={clsx(
        'group flex flex-col items-center justify-between text-center p-3 sm:p-3.5 rounded-2xl transition-all duration-300',
        'bg-white/10 hover:bg-white/15 backdrop-blur-md border border-white/20 hover:border-white/35 shadow-lg shadow-blue-950/20',
        'cursor-default select-none hover:-translate-y-1',
        className
      )}
    >
      <div className="w-9 h-9 rounded-xl bg-white/15 border border-white/25 flex items-center justify-center mb-2.5 shadow-inner transition-transform duration-300 group-hover:scale-110">
        {getIcon()}
      </div>
      <div className="flex flex-col items-center">
        <span className="text-[12px] font-semibold text-white leading-tight">
          {title}
        </span>
        <span className="text-[12px] font-medium text-white/90 leading-tight">
          {subtitle}
        </span>
      </div>
    </div>
  );
};

import React from 'react';
import { clsx } from 'clsx';

export interface BrandLogoProps {
  className?: string;
  showTagline?: boolean;
  theme?: 'light' | 'dark';
  size?: 'sm' | 'md' | 'lg';
}

export const BrandLogo: React.FC<BrandLogoProps> = ({
  className,
  showTagline = true,
  theme = 'light',
  size = 'md',
}) => {
  const isLight = theme === 'light';

  return (
    <div className={clsx('flex items-center gap-3.5 select-none', className)}>
      {/* Brand Geometric Triangle Icon */}
      <div className="relative shrink-0 flex items-center justify-center">
        <svg
          className={clsx(
            size === 'sm' && 'w-8 h-8',
            size === 'md' && 'w-10 h-10',
            size === 'lg' && 'w-12 h-12'
          )}
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Left Angle Wing */}
          <path
            d="M28 10L6 54H16L32 22L28 10Z"
            fill={isLight ? '#FFFFFF' : '#0066FF'}
            fillOpacity="0.95"
          />
          {/* Right Angle Wing with Chevron */}
          <path
            d="M36 10L32 22L48 54H58L36 10Z"
            fill={isLight ? '#FFFFFF' : '#00D2FF'}
          />
          {/* Center Core Stripe */}
          <path
            d="M32 27L22 47H30L32 43L34 47H42L32 27Z"
            fill={isLight ? '#E0F2FE' : '#1D4ED8'}
            opacity="0.9"
          />
        </svg>
      </div>

      {/* Brand Text */}
      <div className="flex flex-col">
        <span
          className={clsx(
            'font-extrabold tracking-wider leading-none uppercase',
            isLight ? 'text-white' : 'text-slate-900',
            size === 'sm' && 'text-lg',
            size === 'md' && 'text-xl',
            size === 'lg' && 'text-2xl'
          )}
          style={{ letterSpacing: '0.08em' }}
        >
          GOCOMPLIANCES
        </span>
        {showTagline && (
          <span
            className={clsx(
              'text-xs tracking-tight font-normal mt-1',
              isLight ? 'text-blue-100/90' : 'text-slate-500'
            )}
          >
            Compliance Today. A Safer Tomorrow.
          </span>
        )}
      </div>
    </div>
  );
};

import React from 'react';
import { clsx } from 'clsx';

export interface BrandLogoProps {
  className?: string;
  showText?: boolean;
  showTagline?: boolean;
  theme?: 'light' | 'dark';
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export const BrandEmblem: React.FC<{ size?: 'sm' | 'md' | 'lg' | 'xl'; className?: string }> = ({
  size = 'md',
  className,
}) => {
  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-12 h-12',
    lg: 'w-14 h-14',
    xl: 'w-20 h-20',
  };

  return (
    <div className={clsx('relative shrink-0 flex items-center justify-center select-none', sizeClasses[size], className)}>
      <svg
        viewBox="0 0 200 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full drop-shadow-md transition-transform hover:scale-105 duration-200"
      >
        <defs>
          {/* Circular Path for the curved circular text */}
          <path
            id="badgeCircleTextPath"
            d="M 100, 100 m 0, -73 a 73,73 0 1,1 0,146 a 73,73 0 1,1 0,-146"
          />
          <filter id="emblemShadow" x="-10%" y="-10%" width="125%" height="125%" filterUnits="userSpaceOnUse">
            <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#0f172a" flood-opacity="0.15" />
          </filter>
        </defs>

        {/* Outer Periwinkle Ring */}
        <circle cx="100" cy="100" r="92" fill="#BCC5FE" filter="url(#emblemShadow)" />

        {/* Curved Circular Text */}
        <text
          fill="#282274"
          fontSize="11.8"
          fontWeight="800"
          fontFamily="'Plus Jakarta Sans', system-ui, sans-serif"
          letterSpacing="0.14em"
        >
          <textPath href="#badgeCircleTextPath" startOffset="50%" textAnchor="middle">
            GOCOMPLIANCES - SIMPLIFY YOUR BUSINESS COMPLIANCE -
          </textPath>
        </text>

        {/* Middle Indigo Ring with Top-Left Pointer Notch */}
        <g>
          {/* Base Middle Circle */}
          <circle cx="100" cy="100" r="54" fill="#382FA8" />
          {/* Speech bubble / compass pointer notch at ~11 o'clock position */}
          <path
            d="M 68 62 L 66 48 L 82 54 Z"
            fill="#382FA8"
          />
        </g>

        {/* Inner Pure White Disk */}
        <circle cx="100" cy="100" r="36" fill="#FFFFFF" />

        {/* Central Bold "GO" Monogram */}
        <text
          x="100"
          y="112"
          textAnchor="middle"
          fontSize="33"
          fontWeight="900"
          fill="#382FA8"
          fontFamily="'Plus Jakarta Sans', 'Inter', system-ui, sans-serif"
          letterSpacing="-0.04em"
        >
          GO
        </text>
      </svg>
    </div>
  );
};

export const BrandLogo: React.FC<BrandLogoProps> = ({
  className,
  showText = true,
  showTagline = true,
  theme = 'light',
  size = 'md',
}) => {
  const isLight = theme === 'light';

  return (
    <div className={clsx('flex items-center gap-3.5 select-none', className)}>
      {/* Official Circular Emblem */}
      <BrandEmblem size={size} />

      {/* Brand Text */}
      {showText && (
        <div className="flex flex-col">
          <span
            className={clsx(
              'font-extrabold tracking-wider leading-none uppercase',
              isLight ? 'text-white' : 'text-slate-900',
              size === 'sm' && 'text-lg',
              size === 'md' && 'text-xl',
              size === 'lg' && 'text-2xl',
              size === 'xl' && 'text-3xl'
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
      )}
    </div>
  );
};

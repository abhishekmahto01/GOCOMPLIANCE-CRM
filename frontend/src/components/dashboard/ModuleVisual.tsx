import React from 'react';

export type ModuleType = 'admin' | 'sales' | 'operations';

export interface ModuleVisualProps {
  type: ModuleType;
  className?: string;
}

export const ModuleVisual: React.FC<ModuleVisualProps> = ({ type, className = '' }) => {
  if (type === 'admin') {
    return (
      <div className={`relative w-full h-44 sm:h-48 md:h-52 flex items-center justify-center select-none ${className}`}>
        <svg
          viewBox="0 0 320 220"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full overflow-visible"
        >
          <defs>
            {/* Ambient Background Glow */}
            <filter id="adminGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="16" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>

            <filter id="adminShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="12" stdDeviation="14" floodColor="#1e40af" floodOpacity="0.25" />
            </filter>

            {/* Pedestal Gradients */}
            <linearGradient id="adminPedestalTop" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="50%" stopColor="#E0EDFF" />
              <stop offset="100%" stopColor="#BFDBFE" />
            </linearGradient>

            <linearGradient id="adminPedestalSide" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#BFDBFE" />
              <stop offset="100%" stopColor="#93C5FD" />
            </linearGradient>

            {/* Shield Outer Gradient */}
            <linearGradient id="adminShieldGrad" x1="20%" y1="0%" x2="80%" y2="100%">
              <stop offset="0%" stopColor="#3B82F6" />
              <stop offset="50%" stopColor="#1D4ED8" />
              <stop offset="100%" stopColor="#1E3A8A" />
            </linearGradient>

            {/* Shield Inner Face */}
            <linearGradient id="adminShieldInner" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#60A5FA" />
              <stop offset="60%" stopColor="#2563EB" />
              <stop offset="100%" stopColor="#1D4ED8" />
            </linearGradient>
          </defs>

          {/* 1. Ambient Radial Aura */}
          <ellipse cx="160" cy="140" rx="90" ry="30" fill="#93C5FD" opacity="0.4" filter="url(#adminGlow)" />

          {/* 2. Orbital Glow Rings */}
          <ellipse cx="160" cy="120" rx="120" ry="42" stroke="#60A5FA" strokeWidth="1.2" strokeDasharray="6 8" opacity="0.5" />
          <circle cx="270" cy="110" r="3" fill="#3B82F6" opacity="0.8" />
          <circle cx="50" cy="130" r="2.5" fill="#60A5FA" opacity="0.8" />

          {/* 3. 3D Cylindrical Pedestal */}
          <g filter="url(#adminShadow)">
            {/* Lower Shadow Base */}
            <ellipse cx="160" cy="165" rx="80" ry="24" fill="#000000" opacity="0.08" />

            {/* Cylinder Body */}
            <path
              d="M 80 148 L 80 162 C 80 175, 240 175, 240 162 L 240 148 Z"
              fill="url(#adminPedestalSide)"
            />

            {/* Top Ellipse Platform */}
            <ellipse cx="160" cy="148" rx="80" ry="22" fill="url(#adminPedestalTop)" stroke="#DBEAFE" strokeWidth="1.5" />
          </g>

          {/* 4. Central 3D Glowing Shield */}
          <g transform="translate(0, -10)" filter="url(#adminShadow)">
            {/* Outer Shield Bevel */}
            <path
              d="M 160 52 C 195 52, 218 64, 218 94 C 218 132, 180 156, 160 168 C 140 156, 102 132, 102 94 C 102 64, 125 52, 160 52 Z"
              fill="url(#adminShieldGrad)"
            />

            {/* Inner Shield Face with Inset Highlight */}
            <path
              d="M 160 58 C 190 58, 210 68, 210 94 C 210 128, 176 150, 160 160 C 144 150, 110 128, 110 94 C 110 68, 130 58, 160 58 Z"
              fill="url(#adminShieldInner)"
            />

            {/* Top Rim Specular Reflection */}
            <path
              d="M 125 72 C 145 62, 175 62, 195 72"
              stroke="#FFFFFF"
              strokeWidth="2.5"
              strokeLinecap="round"
              opacity="0.8"
            />

            {/* User Avatar Silhouette inside Shield */}
            {/* Head */}
            <circle cx="160" cy="94" r="14" fill="#FFFFFF" />
            {/* Body */}
            <path
              d="M 138 130 C 138 116, 148 112, 160 112 C 172 112, 182 116, 182 130 Z"
              fill="#FFFFFF"
            />
          </g>

          {/* 5. Left Floating Badge (Gear / Settings) */}
          <g transform="translate(48, 86)" filter="url(#adminShadow)">
            <rect x="0" y="0" width="36" height="36" rx="10" fill="#FFFFFF" fillOpacity="0.9" stroke="#BFDBFE" strokeWidth="1.5" />
            {/* Mini Gear */}
            <circle cx="18" cy="18" r="7" fill="#3B82F6" />
            <circle cx="18" cy="18" r="3.5" fill="#FFFFFF" />
            {/* Gear teeth notches */}
            <rect x="16.5" y="7.5" width="3" height="3" rx="0.8" fill="#3B82F6" />
            <rect x="16.5" y="25.5" width="3" height="3" rx="0.8" fill="#3B82F6" />
            <rect x="7.5" y="16.5" width="3" height="3" rx="0.8" fill="#3B82F6" />
            <rect x="25.5" y="16.5" width="3" height="3" rx="0.8" fill="#3B82F6" />
          </g>

          {/* 6. Right Floating Badge (Team Users) */}
          <g transform="translate(236, 88)" filter="url(#adminShadow)">
            <rect x="0" y="0" width="36" height="36" rx="10" fill="#FFFFFF" fillOpacity="0.9" stroke="#BFDBFE" strokeWidth="1.5" />
            {/* Team User silhouettes */}
            <circle cx="15" cy="15" r="4" fill="#2563EB" />
            <path d="M 8 26 C 8 21, 12 20, 15 20 C 18 20, 22 21, 22 26 Z" fill="#2563EB" />
            <circle cx="23" cy="14" r="3.2" fill="#60A5FA" />
            <path d="M 18 24 C 18 20, 21 19, 23 19 C 25 19, 28 20, 28 24 Z" fill="#60A5FA" />
          </g>
        </svg>
      </div>
    );
  }

  if (type === 'sales') {
    return (
      <div className={`relative w-full h-44 sm:h-48 md:h-52 flex items-center justify-center select-none ${className}`}>
        <svg
          viewBox="0 0 320 220"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full overflow-visible"
        >
          <defs>
            {/* Ambient Background Glow */}
            <filter id="salesGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="16" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>

            <filter id="salesShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="12" stdDeviation="14" floodColor="#059669" floodOpacity="0.22" />
            </filter>

            {/* Pedestal Gradients */}
            <linearGradient id="salesPedestalTop" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="50%" stopColor="#E6FFFA" />
              <stop offset="100%" stopColor="#A7F3D0" />
            </linearGradient>

            <linearGradient id="salesPedestalSide" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#A7F3D0" />
              <stop offset="100%" stopColor="#6EE7B7" />
            </linearGradient>

            {/* Bar Gradients */}
            <linearGradient id="bar1Grad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#34D399" />
              <stop offset="100%" stopColor="#059669" />
            </linearGradient>

            <linearGradient id="bar2Grad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#2DD4BF" />
              <stop offset="100%" stopColor="#0D9488" />
            </linearGradient>

            <linearGradient id="bar3Grad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="100%" stopColor="#0284C7" />
            </linearGradient>

            {/* Growth Arrow Gradient */}
            <linearGradient id="arrowGrad" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10B981" />
              <stop offset="50%" stopColor="#14B8A6" />
              <stop offset="100%" stopColor="#06B6D4" />
            </linearGradient>
          </defs>

          {/* 1. Ambient Radial Aura */}
          <ellipse cx="160" cy="140" rx="90" ry="30" fill="#6EE7B7" opacity="0.38" filter="url(#salesGlow)" />

          {/* 2. Orbital Glow Rings */}
          <ellipse cx="160" cy="120" rx="120" ry="42" stroke="#34D399" strokeWidth="1.2" strokeDasharray="6 8" opacity="0.5" />
          <circle cx="270" cy="130" r="3" fill="#10B981" opacity="0.8" />
          <circle cx="50" cy="110" r="2.5" fill="#2DD4BF" opacity="0.8" />

          {/* 3. 3D Cylindrical Pedestal */}
          <g filter="url(#salesShadow)">
            {/* Lower Shadow Base */}
            <ellipse cx="160" cy="165" rx="80" ry="24" fill="#000000" opacity="0.08" />

            {/* Cylinder Body */}
            <path
              d="M 80 148 L 80 162 C 80 175, 240 175, 240 162 L 240 148 Z"
              fill="url(#salesPedestalSide)"
            />

            {/* Top Ellipse Platform */}
            <ellipse cx="160" cy="148" rx="80" ry="22" fill="url(#salesPedestalTop)" stroke="#D1FAE5" strokeWidth="1.5" />
          </g>

          {/* 4. 3D Rising Bar Chart */}
          <g transform="translate(0, -6)" filter="url(#salesShadow)">
            {/* Bar 1 (Left - Small Green) */}
            <g transform="translate(108, 102)">
              {/* Front Face */}
              <rect x="0" y="6" width="22" height="34" rx="4" fill="url(#bar1Grad)" />
              {/* Top Face */}
              <path d="M 0 6 L 6 0 L 28 0 L 22 6 Z" fill="#6EE7B7" />
              {/* Side Face */}
              <path d="M 22 6 L 28 0 L 28 34 L 22 40 Z" fill="#047857" opacity="0.6" />
            </g>

            {/* Bar 2 (Center - Medium Teal) */}
            <g transform="translate(138, 78)">
              {/* Front Face */}
              <rect x="0" y="6" width="22" height="58" rx="4" fill="url(#bar2Grad)" />
              {/* Top Face */}
              <path d="M 0 6 L 6 0 L 28 0 L 22 6 Z" fill="#5EEAD4" />
              {/* Side Face */}
              <path d="M 22 6 L 28 0 L 28 58 L 22 64 Z" fill="#0F766E" opacity="0.6" />
            </g>

            {/* Bar 3 (Right - Tall Cyan/Blue) */}
            <g transform="translate(168, 54)">
              {/* Front Face */}
              <rect x="0" y="6" width="22" height="82" rx="4" fill="url(#bar3Grad)" />
              {/* Top Face */}
              <path d="M 0 6 L 6 0 L 28 0 L 22 6 Z" fill="#7DD3FC" />
              {/* Side Face */}
              <path d="M 22 6 L 28 0 L 28 82 L 22 88 Z" fill="#0369A1" opacity="0.6" />
            </g>

            {/* 3D Curved Soaring Growth Arrow */}
            <g transform="translate(102, 38)">
              {/* Curved Arrow Ribbon */}
              <path
                d="M 0 72 C 30 68, 62 48, 86 16"
                stroke="url(#arrowGrad)"
                strokeWidth="7"
                strokeLinecap="round"
              />
              {/* Arrow Head */}
              <polygon points="98,6 74,12 88,26" fill="#06B6D4" />
              <polygon points="98,6 88,26 82,24" fill="#0E7490" />
            </g>
          </g>

          {/* 5. Left Floating Badge (User Profile) */}
          <g transform="translate(48, 92)" filter="url(#salesShadow)">
            <rect x="0" y="0" width="36" height="36" rx="10" fill="#FFFFFF" fillOpacity="0.9" stroke="#A7F3D0" strokeWidth="1.5" />
            <circle cx="18" cy="15" r="4.5" fill="#10B981" />
            <path d="M 10 26 C 10 21, 14 20, 18 20 C 22 20, 26 21, 26 26 Z" fill="#10B981" />
          </g>

          {/* 6. Right Floating Badge (Analytics Graph) */}
          <g transform="translate(236, 92)" filter="url(#salesShadow)">
            <rect x="0" y="0" width="36" height="36" rx="10" fill="#FFFFFF" fillOpacity="0.9" stroke="#A7F3D0" strokeWidth="1.5" />
            <rect x="10" y="18" width="3.5" height="10" rx="1" fill="#34D399" />
            <rect x="16" y="13" width="3.5" height="15" rx="1" fill="#10B981" />
            <rect x="22" y="8" width="3.5" height="20" rx="1" fill="#059669" />
          </g>
        </svg>
      </div>
    );
  }

  // Operations Visual
  return (
    <div className={`relative w-full h-44 sm:h-48 md:h-52 flex items-center justify-center select-none ${className}`}>
      <svg
        viewBox="0 0 320 220"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full overflow-visible"
      >
        <defs>
          {/* Ambient Background Glow */}
          <filter id="opsGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="16" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>

          <filter id="opsShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="12" stdDeviation="14" floodColor="#ea580c" floodOpacity="0.22" />
          </filter>

          {/* Pedestal Gradients */}
          <linearGradient id="opsPedestalTop" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="50%" stopColor="#FFF7ED" />
            <stop offset="100%" stopColor="#FED7AA" />
          </linearGradient>

          <linearGradient id="opsPedestalSide" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FED7AA" />
            <stop offset="100%" stopColor="#FDBA74" />
          </linearGradient>

          {/* 3D Gear Gradients */}
          <linearGradient id="gearFaceGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FB923C" />
            <stop offset="50%" stopColor="#F97316" />
            <stop offset="100%" stopColor="#EA580C" />
          </linearGradient>

          <linearGradient id="gearSideGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#C2410C" />
            <stop offset="100%" stopColor="#9A3412" />
          </linearGradient>
        </defs>

        {/* 1. Ambient Radial Aura */}
        <ellipse cx="160" cy="140" rx="90" ry="30" fill="#FDBA74" opacity="0.4" filter="url(#opsGlow)" />

        {/* 2. Orbital Glow Rings */}
        <ellipse cx="160" cy="120" rx="120" ry="42" stroke="#FB923C" strokeWidth="1.2" strokeDasharray="6 8" opacity="0.5" />
        <circle cx="270" cy="120" r="3" fill="#F97316" opacity="0.8" />
        <circle cx="50" cy="120" r="2.5" fill="#FB923C" opacity="0.8" />

        {/* 3. 3D Cylindrical Pedestal */}
        <g filter="url(#opsShadow)">
          {/* Lower Shadow Base */}
          <ellipse cx="160" cy="165" rx="80" ry="24" fill="#000000" opacity="0.08" />

          {/* Cylinder Body */}
          <path
            d="M 80 148 L 80 162 C 80 175, 240 175, 240 162 L 240 148 Z"
            fill="url(#opsPedestalSide)"
          />

          {/* Top Ellipse Platform */}
          <ellipse cx="160" cy="148" rx="80" ry="22" fill="url(#opsPedestalTop)" stroke="#FFEDD5" strokeWidth="1.5" />
        </g>

        {/* 4. Central Large 3D Orange Mechanical Gear */}
        <g transform="translate(160, 98)" filter="url(#opsShadow)">
          {/* 3D Extrusion Side Wall */}
          <g transform="translate(0, 8)">
            <circle cx="0" cy="0" r="46" fill="url(#gearSideGrad)" />
          </g>

          {/* Main 3D Gear Body */}
          <g>
            {/* Gear Outline with 8 Teeth */}
            <path
              d="
                M -12 -46 L 12 -46 L 15 -38 C 21 -36, 26 -33, 31 -29 L 39 -32 L 50 -15 L 43 -9 C 45 -3, 46 3, 45 9 L 52 16 L 41 33 L 33 30 C 28 35, 23 38, 17 40 L 14 48 L -14 48 L -17 40 C -23 38, -28 35, -33 30 L -41 33 L -52 16 L -45 9 C -46 3, -45 -3, -43 -9 L -50 -15 L -39 -32 L -31 -29 C -26 -33, -21 -36, -15 -38 Z
              "
              fill="url(#gearFaceGrad)"
              stroke="#FDBA74"
              strokeWidth="1.5"
            />

            {/* Inner Center Hole */}
            <circle cx="0" cy="0" r="18" fill="url(#opsPedestalTop)" stroke="#F97316" strokeWidth="2" />
            <circle cx="0" cy="0" r="14" fill="#C2410C" opacity="0.25" />

            {/* Top Specular Rim Reflection */}
            <path
              d="M -26 -26 C -8 -40, 8 -40, 26 -26"
              stroke="#FFFFFF"
              strokeWidth="2.5"
              strokeLinecap="round"
              opacity="0.75"
            />
          </g>
        </g>

        {/* 5. Left Floating Badge (Document / Workflow) */}
        <g transform="translate(48, 92)" filter="url(#opsShadow)">
          <rect x="0" y="0" width="36" height="36" rx="10" fill="#FFFFFF" fillOpacity="0.9" stroke="#FED7AA" strokeWidth="1.5" />
          {/* Document Sheet */}
          <rect x="11" y="9" width="14" height="18" rx="2" fill="#F97316" />
          <line x1="14" y1="14" x2="22" y2="14" stroke="#FFFFFF" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="14" y1="18" x2="22" y2="18" stroke="#FFFFFF" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="14" y1="22" x2="19" y2="22" stroke="#FFFFFF" strokeWidth="1.5" strokeLinecap="round" />
        </g>

        {/* 6. Right Floating Badge (Verified Shield / Check) */}
        <g transform="translate(236, 92)" filter="url(#opsShadow)">
          <rect x="0" y="0" width="36" height="36" rx="10" fill="#FFFFFF" fillOpacity="0.9" stroke="#FED7AA" strokeWidth="1.5" />
          <rect x="9" y="9" width="18" height="18" rx="5" fill="#EA580C" />
          {/* Checkmark inside */}
          <path d="M 13 18 L 16.5 21.5 L 23 15" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </g>
      </svg>
    </div>
  );
};

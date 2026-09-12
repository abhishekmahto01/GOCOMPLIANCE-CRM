import React from 'react';

export const BuildingVisual: React.FC = () => {
  return (
    <div className="relative w-full mt-auto pt-6 flex items-end justify-between overflow-hidden">
      {/* Cursive Handwriting Text */}
      <div className="relative z-10 pb-4 pl-1 select-none pointer-events-none">
        <div className="font-handwriting text-2xl sm:text-3xl text-white/95 leading-tight font-normal tracking-wide drop-shadow-md">
          <p>Building</p>
          <p>Compliant Businesses</p>
          <div className="relative inline-block">
            <p>Together</p>
            {/* Elegant Hand-drawn swoosh underline */}
            <svg
              className="absolute -bottom-2.5 left-0 w-32 h-4 text-white/70 overflow-visible"
              viewBox="0 0 120 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M2 8C25 3 70 3 118 12M60 11C85 13 105 14 115 14"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Corporate Glass Building Architectural Graphic */}
      <div className="relative w-[52%] max-w-[280px] h-[190px] sm:h-[220px] shrink-0 pointer-events-none select-none">
        <svg
          className="w-full h-full object-contain filter drop-shadow-2xl opacity-90"
          viewBox="0 0 320 260"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* Building Glass Gradients */}
            <linearGradient id="facadeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#2a6ef5" stop-opacity="0.9" />
              <stop offset="50%" stop-color="#1142b5" stop-opacity="0.95" />
              <stop offset="100%" stop-color="#07236d" stop-opacity="0.98" />
            </linearGradient>

            <linearGradient id="glassReflection" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.3" />
              <stop offset="40%" stop-color="#93c5fd" stop-opacity="0.15" />
              <stop offset="70%" stop-color="#ffffff" stop-opacity="0.35" />
              <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.1" />
            </linearGradient>

            <linearGradient id="roofGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#0b2866" />
              <stop offset="50%" stop-color="#17449e" />
              <stop offset="100%" stop-color="#0e327a" />
            </linearGradient>
          </defs>

          {/* Perspective Main Tower Building */}
          {/* Main front glass facade */}
          <polygon
            points="60,95 240,40 320,80 320,260 60,260"
            fill="url(#facadeGrad)"
          />

          {/* Left Wing Facade */}
          <polygon
            points="0,150 60,95 60,260 0,260"
            fill="#092569"
            opacity="0.85"
          />

          {/* Parapet / Roof Header Beam */}
          <polygon
            points="60,95 240,40 320,80 320,98 240,58 60,113"
            fill="url(#roofGrad)"
          />

          {/* Illuminated Brand Signage on Building Roof Edge */}
          <g transform="translate(110, 68) rotate(-16.5)">
            <rect
              x="-4"
              y="-2"
              width="142"
              height="18"
              rx="3"
              fill="#061c4d"
              opacity="0.8"
            />
            {/* Small Glowing Logo Mark */}
            <path
              d="M3 13 L8 3 L13 13 H10 L8 8 L6 13 Z"
              fill="#00D2FF"
              filter="drop-shadow(0 0 3px #00D2FF)"
            />
            <text
              x="16"
              y="11.5"
              fill="#FFFFFF"
              fontSize="9.5"
              fontWeight="800"
              letterSpacing="0.08em"
              fontFamily="sans-serif"
              filter="drop-shadow(0 0 2px rgba(255,255,255,0.8))"
            >
              GOCOMPLIANCES
            </text>
          </g>

          {/* Architectural Window Grid Lines (Perspective) */}
          {/* Horizontal floor dividers */}
          <line x1="60" y1="135" x2="320" y2="102" stroke="#60a5fa" strokeWidth="1.5" strokeOpacity="0.4" />
          <line x1="60" y1="165" x2="320" y2="132" stroke="#60a5fa" strokeWidth="1.5" strokeOpacity="0.4" />
          <line x1="60" y1="195" x2="320" y2="162" stroke="#60a5fa" strokeWidth="1.5" strokeOpacity="0.4" />
          <line x1="60" y1="225" x2="320" y2="192" stroke="#60a5fa" strokeWidth="1.5" strokeOpacity="0.4" />

          {/* Left Wing floor dividers */}
          <line x1="0" y1="185" x2="60" y2="135" stroke="#3b82f6" strokeWidth="1.5" strokeOpacity="0.3" />
          <line x1="0" y1="215" x2="60" y2="165" stroke="#3b82f6" strokeWidth="1.5" strokeOpacity="0.3" />

          {/* Vertical mullion columns */}
          <line x1="105" y1="120" x2="105" y2="260" stroke="#3b82f6" strokeWidth="1.2" strokeOpacity="0.35" />
          <line x1="150" y1="106" x2="150" y2="260" stroke="#3b82f6" strokeWidth="1.2" strokeOpacity="0.35" />
          <line x1="195" y1="92" x2="195" y2="260" stroke="#3b82f6" strokeWidth="1.2" strokeOpacity="0.35" />
          <line x1="240" y1="78" x2="240" y2="260" stroke="#3b82f6" strokeWidth="1.2" strokeOpacity="0.35" />
          <line x1="280" y1="79" x2="280" y2="260" stroke="#3b82f6" strokeWidth="1.2" strokeOpacity="0.35" />

          {/* Left wing vertical columns */}
          <line x1="20" y1="170" x2="20" y2="260" stroke="#1d4ed8" strokeWidth="1.2" strokeOpacity="0.3" />
          <line x1="40" y1="152" x2="40" y2="260" stroke="#1d4ed8" strokeWidth="1.2" strokeOpacity="0.3" />

          {/* Realistic Diagonal Glass Light Reflection */}
          <polygon
            points="120,115 190,95 240,260 170,260"
            fill="url(#glassReflection)"
            opacity="0.55"
          />
          <polygon
            points="220,84 270,70 310,260 260,260"
            fill="url(#glassReflection)"
            opacity="0.4"
          />
        </svg>
      </div>
    </div>
  );
};

import React from 'react';
import { ArrowRight } from 'lucide-react';
import { BrandLogo } from './BrandLogo';
import { FeatureCard } from './FeatureCard';
import { BuildingVisual } from './BuildingVisual';

export interface BrandPanelProps {
  onExploreClick?: () => void;
}

export const BrandPanel: React.FC<BrandPanelProps> = ({ onExploreClick }) => {
  return (
    <div className="relative w-full h-full min-h-[680px] lg:min-h-[800px] flex flex-col justify-between p-8 sm:p-12 lg:p-14 overflow-hidden blue-gradient-panel text-white">
      {/* Dynamic Background Overlays & Decorative Elements */}
      {/* 1. Large Top-Left Radial Glow Circle */}
      <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-blue-400/20 blur-3xl pointer-events-none" />
      
      {/* 2. Top Hanging Capsule / Pill Gradient */}
      <div className="absolute top-0 right-36 sm:right-48 w-12 sm:w-16 h-36 sm:h-44 rounded-b-full bg-gradient-to-b from-white/30 via-white/10 to-transparent backdrop-blur-md pointer-events-none border-x border-b border-white/20 shadow-inner" />

      {/* 3. Floating Ring Circle */}
      <div className="absolute top-16 right-24 sm:right-32 w-7 h-7 sm:w-8 sm:h-8 rounded-full border-2 border-white/60 pointer-events-none animate-float-slow" />

      {/* 4. Translucent 4x4 Dot Matrix */}
      <div className="absolute top-20 right-10 sm:right-16 grid grid-cols-4 gap-2 pointer-events-none opacity-40">
        {Array.from({ length: 16 }).map((_, i) => (
          <div key={i} className="w-1.5 h-1.5 rounded-full bg-white" />
        ))}
      </div>

      {/* 5. Glowing Cyan Sphere (Bottom-Left) */}
      <div className="absolute bottom-28 left-8 sm:left-12 w-11 h-11 sm:w-12 sm:h-12 rounded-full bg-gradient-to-tr from-cyan-300 via-sky-400 to-blue-400 shadow-brand-glow pointer-events-none border border-white/40" />

      {/* 6. Soft Cyan Glow Behind Hero */}
      <div className="absolute top-1/3 left-1/4 w-80 h-80 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />

      {/* Top Header Section */}
      <div className="relative z-10">
        <BrandLogo showTagline={true} theme="light" size="md" />
      </div>

      {/* Middle Hero & Feature Section */}
      <div className="relative z-10 my-auto py-8 sm:py-10 max-w-xl">
        {/* Uppercase Small Heading */}
        <div className="inline-block mb-3">
          <span className="text-[11px] sm:text-xs font-semibold tracking-[0.22em] text-blue-200/90 uppercase select-none">
            25+ YEARS OF COMPLIANCE EXPERTISE
          </span>
        </div>

        {/* Main Title */}
        <h1 className="text-3xl sm:text-4xl lg:text-[42px] font-extrabold text-white tracking-tight leading-[1.15] mb-4">
          <span>Simplifying Compliance.</span>
          <br />
          <span>Empowering Businesses.</span>
        </h1>

        {/* Subtitle / Description */}
        <p className="text-sm sm:text-base text-blue-100/85 font-normal leading-relaxed max-w-md mb-6">
          A unified workspace for managing HR compliance, statutory operations, client services, applications and regulatory processes across India.
        </p>

        {/* Subtle Horizontal Divider Accent */}
        <div className="w-16 h-1 bg-white/40 rounded-full mb-8" />

        {/* 4 Glassmorphism Feature Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-3.5 max-w-lg">
          <FeatureCard
            icon="shield"
            title="Compliance"
            subtitle="Management"
          />
          <FeatureCard
            icon="scale"
            title="Statutory"
            subtitle="Operations"
          />
          <FeatureCard
            icon="users"
            title="Client"
            subtitle="Management"
          />
          <FeatureCard
            icon="chart"
            title="Real-time"
            subtitle="Insights"
          />
        </div>
      </div>

      {/* Bottom Visual Section */}
      <div className="relative z-10">
        <BuildingVisual />
      </div>

      {/* Floating Split Connector Circular Badge (Desktop Only) */}
      <div
        onClick={onExploreClick}
        className="hidden lg:flex absolute top-1/2 -right-7 -translate-y-1/2 z-30 group cursor-pointer items-center justify-center w-14 h-14 rounded-full bg-white p-1 shadow-connector transition-all duration-300 hover:scale-105 hover:shadow-2xl"
        title="GOCOMPLIANCE CRM Portal"
        role="button"
        tabIndex={0}
      >
        <div className="w-full h-full rounded-full bg-gradient-to-r from-cyan-400 via-teal-400 to-blue-500 flex items-center justify-center text-white shadow-inner transition-transform group-hover:rotate-12">
          <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-0.5 stroke-[2.5]" />
        </div>
      </div>
    </div>
  );
};

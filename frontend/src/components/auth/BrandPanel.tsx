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
    <div className="relative w-full h-full flex flex-col justify-between p-6 sm:p-8 md:p-9 lg:p-7 xl:p-11 overflow-hidden blue-gradient-panel text-white">
      {/* Dynamic Background Overlays & Decorative Elements */}
      {/* 1. Large Top-Left Radial Glow Circle */}
      <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-blue-400/20 blur-3xl pointer-events-none" />
      
      {/* 2. Top Hanging Capsule / Pill Gradient */}
      <div className="absolute top-0 right-36 sm:right-48 w-12 sm:w-16 h-36 sm:h-44 rounded-b-full bg-gradient-to-b from-white/30 via-white/10 to-transparent backdrop-blur-md pointer-events-none border-x border-b border-white/20 shadow-inner" />

      {/* 3. Floating Ring Circle */}
      <div className="absolute top-12 sm:top-16 right-24 sm:right-32 w-6 h-6 sm:w-8 sm:h-8 rounded-full border-2 border-white/60 pointer-events-none animate-float-slow" />

      {/* 4. Translucent 4x4 Dot Matrix */}
      <div className="absolute top-16 sm:top-20 right-8 sm:right-16 grid grid-cols-4 gap-1.5 sm:gap-2 pointer-events-none opacity-40">
        {Array.from({ length: 16 }).map((_, i) => (
          <div key={i} className="w-1.5 h-1.5 rounded-full bg-white" />
        ))}
      </div>

      {/* 5. Glowing Cyan Sphere (Bottom-Left) */}
      <div className="absolute bottom-20 sm:bottom-28 left-6 sm:left-12 w-9 h-9 sm:w-12 sm:h-12 rounded-full bg-gradient-to-tr from-cyan-300 via-sky-400 to-blue-400 shadow-brand-glow pointer-events-none border border-white/40" />

      {/* 6. Soft Cyan Glow Behind Hero */}
      <div className="absolute top-1/3 left-1/4 w-80 h-80 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />

      {/* Top Header Section */}
      <div className="relative z-10 shrink-0">
        <BrandLogo showTagline={true} theme="light" size="md" />
      </div>

      {/* Middle Hero & Feature Section */}
      <div className="relative z-10 my-auto py-2 sm:py-4 lg:py-2.5 xl:py-5 max-w-xl">
        {/* Uppercase Small Heading */}
        <div className="inline-block mb-1.5 sm:mb-2 lg:mb-1.5 xl:mb-2.5">
          <span className="text-[10px] sm:text-[11px] xl:text-xs font-semibold tracking-[0.2em] text-blue-200/90 uppercase select-none">
            25+ YEARS OF COMPLIANCE EXPERTISE
          </span>
        </div>

        {/* Main Title */}
        <h1 className="text-2xl sm:text-3xl lg:text-[28px] xl:text-[40px] font-extrabold text-white tracking-tight leading-[1.14] mb-2 sm:mb-3 lg:mb-2 xl:mb-4">
          <span>Simplifying Compliance.</span>
          <br />
          <span>Empowering Businesses.</span>
        </h1>

        {/* Subtitle / Description */}
        <p className="text-xs sm:text-sm xl:text-base text-blue-100/85 font-normal leading-relaxed max-w-md mb-3 sm:mb-4 lg:mb-3 xl:mb-5">
          A unified workspace for managing HR compliance, statutory operations, client services, applications and regulatory processes across India.
        </p>

        {/* Subtle Horizontal Divider Accent */}
        <div className="w-12 sm:w-16 h-1 bg-white/40 rounded-full mb-3.5 sm:mb-5 lg:mb-3 xl:mb-6" />

        {/* 4 Glassmorphism Feature Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-2.5 lg:gap-2 xl:gap-3 max-w-lg">
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
      <div className="relative z-10 shrink-0">
        <BuildingVisual />
      </div>

      {/* Floating Split Connector Circular Badge (Desktop Only) */}
      <div
        onClick={onExploreClick}
        className="hidden lg:flex absolute top-1/2 -right-6 lg:-right-6 xl:-right-7 -translate-y-1/2 z-30 group cursor-pointer items-center justify-center w-12 h-12 lg:w-12 lg:h-12 xl:w-14 xl:h-14 rounded-full bg-white p-1 shadow-connector transition-all duration-300 hover:scale-105 hover:shadow-2xl"
        title="GOCOMPLIANCE CRM Portal"
        role="button"
        tabIndex={0}
      >
        <div className="w-full h-full rounded-full bg-gradient-to-r from-cyan-400 via-teal-400 to-blue-500 flex items-center justify-center text-white shadow-inner transition-transform group-hover:rotate-12">
          <ArrowRight className="w-4 h-4 xl:w-5 xl:h-5 transition-transform group-hover:translate-x-0.5 stroke-[2.5]" />
        </div>
      </div>
    </div>
  );
};

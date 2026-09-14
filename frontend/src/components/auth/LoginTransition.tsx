import React, { useEffect, useState } from 'react';

export interface LoginTransitionProps {
  onComplete: () => void;
  duration?: number; // Total sequence duration in ms (default: 1650ms)
}

export const LoginTransition: React.FC<LoginTransitionProps> = ({
  onComplete,
  duration = 1650,
}) => {
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState<'enter' | 'flying' | 'exit'>('enter');

  useEffect(() => {
    const startTime = performance.now();
    let animFrameId: number;

    // Fast initial entrance
    const enterTimer = setTimeout(() => {
      setStage('flying');
    }, 100);

    // Synchronized progress update (0% -> 100% over duration)
    const updateProgress = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const raw = Math.min(elapsed / duration, 1);

      // Smooth custom easing
      const eased =
        raw < 0.5
          ? 2 * raw * raw
          : 1 - Math.pow(-2 * raw + 2, 2) / 2;

      setProgress(Math.round(eased * 100));

      if (raw < 1) {
        animFrameId = requestAnimationFrame(updateProgress);
      }
    };

    animFrameId = requestAnimationFrame(updateProgress);

    // Stage 2 (last 280ms): Seamless exit fade into dashboard
    const exitTimer = setTimeout(() => {
      setStage('exit');
    }, duration - 280);

    // Stage 3 (~1.65s): Transition completes
    const completeTimer = setTimeout(() => {
      onComplete();
    }, duration);

    return () => {
      clearTimeout(enterTimer);
      clearTimeout(exitTimer);
      clearTimeout(completeTimer);
      cancelAnimationFrame(animFrameId);
    };
  }, [duration, onComplete]);

  return (
    <div
      role="status"
      aria-label="Taking you to your dashboard..."
      className={`fixed inset-0 z-50 flex flex-col items-center justify-between overflow-hidden bg-gradient-to-br from-[#1b7cfc] via-[#0b5ce8] to-[#043fb8] text-white select-none ${
        stage === 'exit'
          ? 'opacity-0 transition-opacity duration-[280ms] ease-out'
          : 'opacity-100 transition-opacity duration-150 ease-in'
      }`}
    >
      {/* 1. Sunburst Flare & Radial Atmosphere in Top-Left */}
      <div className="absolute -top-16 -left-16 w-[500px] sm:w-[700px] h-[500px] sm:h-[700px] rounded-full bg-[radial-gradient(circle,_rgba(255,255,255,0.95)_0%,_rgba(255,255,255,0.5)_20%,_rgba(186,230,253,0.3)_45%,_transparent_70%)] pointer-events-none blur-xl login-sunbeam" />
      
      {/* Sunbeam Light Rays emanating from top-left */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden opacity-40">
        <svg className="w-full h-full" viewBox="0 0 1440 900" fill="none" preserveAspectRatio="none">
          <polygon points="0,0 280,900 120,900" fill="url(#sunRayGrad)" />
          <polygon points="0,0 650,900 480,900" fill="url(#sunRayGrad)" opacity="0.6" />
          <polygon points="0,0 1100,900 920,900" fill="url(#sunRayGrad)" opacity="0.4" />
          <defs>
            <linearGradient id="sunRayGrad" x1="0%" y1="0%" x2="50%" y2="100%">
              <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.45" />
              <stop offset="60%" stopColor="#FFFFFF" stopOpacity="0.1" />
              <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* 2. Main Flight Canvas (Paper Airplane + Loop-the-Loop Dotted Trail) */}
      <div className="relative w-full max-w-5xl flex-1 flex flex-col items-center justify-center px-4 pt-6 sm:pt-10">
        <div className="relative w-full max-w-[560px] sm:max-w-[720px] md:max-w-[840px] h-[280px] sm:h-[360px] md:h-[420px] flex items-center justify-center overflow-visible">
          
          {/* A. Loop-the-Loop Dotted Flight Trail SVG */}
          <svg
            className="absolute inset-0 w-full h-full overflow-visible pointer-events-none"
            viewBox="0 0 840 420"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient id="trailGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.1" />
                <stop offset="25%" stopColor="#FFFFFF" stopOpacity="0.75" />
                <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0.95" />
              </linearGradient>

              <linearGradient id="speedLineGrad" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.7" />
                <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
              </linearGradient>
            </defs>

            {/* Loop-the-Loop Corkscrew Trail Path matching reference photo */}
            <path
              d="M 10 330 C 90 320, 160 305, 225 270 C 255 250, 275 220, 260 190 C 242 155, 195 160, 190 200 C 185 238, 225 268, 260 255 C 320 235, 400 195, 490 148 C 530 128, 565 110, 595 98"
              stroke="url(#trailGradient)"
              strokeWidth="3.4"
              strokeDasharray="9 11"
              strokeLinecap="round"
              className="login-loop-trail"
            />

            {/* Speed / Wind Streaks at airplane tail */}
            <line x1="595" y1="98" x2="550" y2="120" stroke="url(#speedLineGrad)" strokeWidth="1.8" strokeLinecap="round" />
            <line x1="605" y1="112" x2="560" y2="134" stroke="url(#speedLineGrad)" strokeWidth="1.5" strokeLinecap="round" />
            <line x1="615" y1="85" x2="575" y2="105" stroke="url(#speedLineGrad)" strokeWidth="1.2" strokeLinecap="round" />
          </svg>

          {/* B. Gocompliances 3D Origami Dart Airplane */}
          <div className="login-airplane-flight will-change-transform pointer-events-none z-10 flex items-center justify-center">
            <svg
              className="w-[360px] sm:w-[460px] md:w-[540px] h-auto overflow-visible"
              viewBox="0 0 520 280"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                {/* Airplane Soft Shadow */}
                <filter id="planeShadowRef" x="-30%" y="-30%" width="160%" height="160%">
                  <feDropShadow
                    dx="0"
                    dy="18"
                    stdDeviation="20"
                    floodColor="#021038"
                    floodOpacity="0.45"
                  />
                </filter>

                {/* Main Top Wing (Crisp Pure White Paper Face) */}
                <linearGradient id="topWingGrad" x1="15%" y1="0%" x2="100%" y2="80%">
                  <stop offset="0%" stopColor="#FFFFFF" />
                  <stop offset="60%" stopColor="#FAFCFF" />
                  <stop offset="100%" stopColor="#E5EFFF" />
                </linearGradient>

                {/* Far Wing Fold (Subtle shadow across ridge) */}
                <linearGradient id="farWingFold" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#F4F8FF" />
                  <stop offset="60%" stopColor="#E2EDFF" />
                  <stop offset="100%" stopColor="#CADDFD" />
                </linearGradient>

                {/* Side Body / Logo Facet (Crisp white facing down-right) */}
                <linearGradient id="sideFacetGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FFFFFF" />
                  <stop offset="50%" stopColor="#F5F9FF" />
                  <stop offset="100%" stopColor="#DFEBFF" />
                </linearGradient>

                {/* Underside Keel Shadow (Deep Royal Blue / Navy) */}
                <linearGradient id="keelShadowGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#256bf5" />
                  <stop offset="50%" stopColor="#1248cf" />
                  <stop offset="100%" stopColor="#082980" />
                </linearGradient>
              </defs>

              <g style={{ filter: 'url(#planeShadowRef)' }}>
                {/* Airplane geometry matching reference photo */}
                <g transform="translate(60, 35) rotate(-12)">
                  
                  {/* Facet 1: Far Left Wing (Top flap) */}
                  <polygon
                    points="420,38 120,42 220,78"
                    fill="url(#farWingFold)"
                  />

                  {/* Facet 2: Center Keel Underside Fold */}
                  <polygon
                    points="420,38 220,78 240,142"
                    fill="url(#keelShadowGrad)"
                  />

                  {/* Facet 3: Main Top Wing Face */}
                  <polygon
                    points="420,38 0,85 220,78"
                    fill="url(#topWingGrad)"
                  />

                  {/* Facet 4: Lower Side Fuselage Facet (where logo is printed) */}
                  <polygon
                    points="420,38 220,78 240,142 340,95"
                    fill="url(#sideFacetGrad)"
                  />

                  {/* Facet 5: Trailing Back Wing Flap */}
                  <polygon
                    points="0,85 220,78 240,142 140,125"
                    fill="#D9E7FF"
                  />

                  {/* Facet 6: Center Spine Highlight Ridge */}
                  <line
                    x1="0"
                    y1="85"
                    x2="420"
                    y2="38"
                    stroke="#FFFFFF"
                    strokeWidth="2.2"
                    strokeOpacity="0.95"
                  />

                  {/* Gocompliances Branded Text on Paper Airplane Wing/Side */}
                  <g transform="translate(195, 82) rotate(-6)">
                    <text
                      x="0"
                      y="0"
                      fill="#0B2B82"
                      fontSize="22"
                      fontWeight="800"
                      letterSpacing="-0.02em"
                      fontFamily="'Plus Jakarta Sans', system-ui, sans-serif"
                      style={{ textShadow: '0 1px 2px rgba(255,255,255,0.5)' }}
                    >
                      Gocompliances
                    </text>
                  </g>
                </g>
              </g>
            </svg>
          </div>
        </div>

        {/* 3. Center UI: Status Text, Progress Bar & GOCOMPLIANCES Subtext */}
        <div className="mt-2 sm:mt-4 flex flex-col items-center text-center z-20 space-y-3.5">
          {/* Main Status Text */}
          <h2 className="text-lg sm:text-xl md:text-[22px] font-semibold text-white tracking-normal drop-shadow-[0_2px_10px_rgba(0,25,80,0.45)]">
            Taking you to your dashboard...
          </h2>

          {/* Capsule Glowing Progress Bar */}
          <div className="w-68 sm:w-80 md:w-96 h-2 sm:h-2.5 rounded-full bg-white/25 backdrop-blur-md p-0.5 border border-white/40 shadow-inner">
            <div
              className="h-full rounded-full bg-gradient-to-r from-cyan-300 via-white to-cyan-100 shadow-[0_0_14px_rgba(255,255,255,0.95),0_0_24px_rgba(56,189,248,0.7)] transition-all ease-out"
              style={{
                width: `${progress}%`,
                transitionDuration: '50ms',
              }}
            />
          </div>

          {/* Wide-Spaced Corporate Subtext matching reference image */}
          <span className="text-[10px] sm:text-xs text-white/95 font-bold tracking-[0.42em] uppercase select-none drop-shadow-[0_1px_5px_rgba(0,20,60,0.4)]">
            GOCOMPLIANCES
          </span>
        </div>
      </div>

      {/* 4. Volumetric Cumulus Cloudscape (Bottom & Lower Edges) */}
      <div className="relative w-full h-40 sm:h-52 md:h-64 pointer-events-none shrink-0 overflow-hidden">
        {/* Ambient Deep Blue Cloud Glow */}
        <div className="absolute -bottom-6 left-0 right-0 h-44 opacity-40 blur-lg">
          <svg className="w-full h-full" viewBox="0 0 1440 260" fill="none" preserveAspectRatio="none">
            <path
              d="M0 260L0 140C140 80 300 160 480 110C660 60 820 150 1020 90C1220 50 1340 120 1440 80L1440 260Z"
              fill="#2563EB"
            />
          </svg>
        </div>

        {/* Middle Cumulus Cloud Layer with Soft Drift */}
        <div className="absolute -bottom-4 left-[-3%] right-[-3%] h-44 opacity-70 login-cloud-drift">
          <svg
            className="w-full h-full filter drop-shadow-[0_-10px_20px_rgba(10,60,190,0.35)]"
            viewBox="0 0 1500 240"
            fill="none"
            preserveAspectRatio="none"
          >
            <path
              d="M0 240L0 110C80 70 180 120 300 80C420 40 540 100 680 60C820 20 940 80 1080 40C1220 10 1340 70 1440 40C1480 30 1500 60 1500 50L1500 240Z"
              fill="#93C5FD"
              fillOpacity="0.5"
            />
          </svg>
        </div>

        {/* Front Realistic Puffy Cumulus Cloud Puffs (Billowy Whites) */}
        <div className="absolute bottom-0 left-0 right-0 h-32 sm:h-44 md:h-52">
          <svg
            className="w-full h-full filter drop-shadow-[0_-12px_28px_rgba(255,255,255,0.25)]"
            viewBox="0 0 1440 220"
            fill="none"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="cloudWhitePuff" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.98" />
                <stop offset="40%" stopColor="#F0F6FF" stopOpacity="0.95" />
                <stop offset="75%" stopColor="#D5E6FF" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#AFCFFF" stopOpacity="0.85" />
              </linearGradient>
            </defs>
            
            {/* Multi-dome Cumulus Billows framing bottom left, center, and bottom right */}
            <path
              d="M 0 220 
                 L 0 110 
                 C 40 70, 90 60, 140 80 
                 C 180 40, 260 30, 320 65 
                 C 370 20, 470 15, 540 50 
                 C 600 25, 690 30, 750 60 
                 C 810 15, 920 10, 990 45 
                 C 1060 20, 1160 25, 1220 60 
                 C 1280 30, 1370 40, 1440 70 
                 L 1440 220 Z"
              fill="url(#cloudWhitePuff)"
            />
          </svg>
        </div>
      </div>
    </div>
  );
};

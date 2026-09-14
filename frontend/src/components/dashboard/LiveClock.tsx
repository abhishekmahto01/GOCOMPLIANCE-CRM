import React, { useState, useEffect } from 'react';

export const LiveClock: React.FC<{ className?: string }> = ({ className = '' }) => {
  const [timeStr, setTimeStr] = useState<string>(() => formatTime(new Date()));

  function formatTime(date: Date): string {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });
  }

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeStr(formatTime(new Date()));
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div
      className={`font-medium tracking-wide text-xs sm:text-sm select-none text-slate-700 dark:text-slate-300 ${className}`}
      aria-label="Current local time"
    >
      {timeStr}
    </div>
  );
};

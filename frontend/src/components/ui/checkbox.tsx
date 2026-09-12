import React from 'react';
import { Check } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, id, checked, onChange, disabled, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <label
        htmlFor={inputId}
        className={clsx(
          'inline-flex items-center gap-2.5 cursor-pointer select-none text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <div className="relative flex items-center justify-center">
          <input
            id={inputId}
            type="checkbox"
            ref={ref}
            checked={checked}
            onChange={onChange}
            disabled={disabled}
            className="peer sr-only"
            {...props}
          />
          <div
            className={twMerge(
              clsx(
                'w-4 h-4 rounded-[4px] border border-slate-300 bg-white transition-all duration-150 flex items-center justify-center peer-focus-visible:ring-2 peer-focus-visible:ring-blue-500/30 peer-checked:bg-blue-600 peer-checked:border-blue-600',
                className
              )
            )}
          >
            <Check
              className={clsx(
                'w-3 h-3 text-white transition-opacity duration-150 stroke-[3]',
                checked ? 'opacity-100' : 'opacity-0'
              )}
            />
          </div>
        </div>
        {label && <span>{label}</span>}
      </label>
    );
  }
);

Checkbox.displayName = 'Checkbox';

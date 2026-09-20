import React from 'react';
import { AlertTriangle, X } from 'lucide-react';
import clsx from 'clsx';

interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  message: string | React.ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'primary';
  isLoading?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'primary',
  isLoading = false,
  onConfirm,
  onClose,
}) => {
  if (!isOpen) return null;

  let confirmBtnClasses = 'bg-brand-600 hover:bg-brand-700 text-white';
  if (variant === 'danger') {
    confirmBtnClasses = 'bg-rose-600 hover:bg-rose-700 text-white';
  } else if (variant === 'warning') {
    confirmBtnClasses = 'bg-amber-600 hover:bg-amber-700 text-white';
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-200">
        <div className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div
                className={clsx(
                  'w-10 h-10 rounded-full flex items-center justify-center shrink-0',
                  variant === 'danger'
                    ? 'bg-rose-100 text-rose-600'
                    : variant === 'warning'
                    ? 'bg-amber-100 text-amber-600'
                    : 'bg-brand-100 text-brand-600'
                )}
              >
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 id="modal-title" className="text-lg font-bold text-slate-900">
                {title}
              </h3>
            </div>
            <button
              onClick={onClose}
              disabled={isLoading}
              className="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded-lg hover:bg-slate-100"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="mt-4 text-sm text-slate-600">{message}</div>

          <div className="mt-6 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 rounded-lg border border-slate-300 transition-colors disabled:opacity-50"
            >
              {cancelLabel}
            </button>
            <button
              type="button"
              onClick={onConfirm}
              disabled={isLoading}
              className={clsx(
                'px-4 py-2 text-sm font-semibold rounded-lg transition-colors shadow-sm disabled:opacity-50 flex items-center gap-2',
                confirmBtnClasses
              )}
            >
              {isLoading && (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              )}
              {confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

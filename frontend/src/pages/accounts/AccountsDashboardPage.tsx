import React from 'react';
import {
  Receipt,
  ArrowUpRight,
  CreditCard,
  Building2,
  Clock,
  Sparkles,
  Layers,
  ArrowRight,
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Link } from 'react-router-dom';

export const AccountsDashboardPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Top Banner Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-900 via-indigo-800 to-blue-900 text-white shadow-xl relative overflow-hidden">
        {/* Subtle Background Shapes */}
        <div className="absolute -right-10 -bottom-10 w-64 h-64 rounded-full bg-white/5 blur-2xl pointer-events-none" />
        <div className="absolute top-0 right-1/4 w-40 h-40 rounded-full bg-indigo-500/10 blur-xl pointer-events-none" />

        <div className="relative z-10 space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-bold text-indigo-200 border border-white/10">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>Accounts & Finance</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Financial Management & Ledgers
          </h1>
          <p className="text-xs sm:text-sm text-indigo-200 max-w-xl leading-relaxed">
            Manage client billing, tax invoices, transaction reconciliations, and financial statements.
          </p>
        </div>

        <div className="relative z-10 flex items-center gap-3">
          <Link to="/dashboard">
            <Button
              variant="outline"
              size="sm"
              className="bg-white/10 hover:bg-white/20 text-white border-white/20 backdrop-blur-md rounded-xl text-xs font-semibold"
            >
              Main Dashboard
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Total Invoiced
            </span>
            <div className="text-2xl font-black text-slate-900 dark:text-white mt-1">
              ₹0.00
            </div>
            <span className="text-[11px] text-slate-400 mt-0.5 block">
              All time client billings
            </span>
          </div>
          <div className="p-3 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <Receipt className="w-6 h-6" />
          </div>
        </div>

        {/* Metric 2 */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Collected Amount
            </span>
            <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
              ₹0.00
            </div>
            <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold mt-0.5 flex items-center gap-0.5">
              <ArrowUpRight className="w-3 h-3" /> Advance & receipts
            </span>
          </div>
          <div className="p-3 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
            <CreditCard className="w-6 h-6" />
          </div>
        </div>

        {/* Metric 3 */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Pending Balance
            </span>
            <div className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-1">
              ₹0.00
            </div>
            <span className="text-[11px] text-slate-400 mt-0.5 block">
              Outstanding receivables
            </span>
          </div>
          <div className="p-3 rounded-2xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400">
            <Clock className="w-6 h-6" />
          </div>
        </div>

        {/* Metric 4 */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-wider">
              Active Client Ledgers
            </span>
            <div className="text-2xl font-black text-blue-600 dark:text-blue-400 mt-1">
              0
            </div>
            <span className="text-[11px] text-slate-400 mt-0.5 block">
              Registered corporate entities
            </span>
          </div>
          <div className="p-3 rounded-2xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
            <Building2 className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Clean Workspace Canvas */}
      <div className="p-8 sm:p-12 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs text-center flex flex-col items-center justify-center space-y-4">
        <div className="w-16 h-16 rounded-3xl bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-100 dark:border-indigo-800 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shadow-inner">
          <Layers className="w-8 h-8" />
        </div>

        <div className="space-y-1 max-w-md">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">
            Accounts & Financial Workspace
          </h3>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
            This module is structured and ready for upcoming ledger tracking, GST invoicing, payment milestones, and financial statements.
          </p>
        </div>

        <div className="flex items-center gap-3 pt-2">
          <Link to="/sales/register">
            <Button
              variant="outline"
              size="sm"
              className="text-xs font-semibold rounded-xl flex items-center gap-1.5"
            >
              <span>View Sales Register</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
          <Link to="/dashboard">
            <Button
              variant="primary"
              size="sm"
              className="text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white"
            >
              Return to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

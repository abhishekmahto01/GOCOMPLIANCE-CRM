import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  UserPlus,
  Shield,
  Building,
  CheckCircle,
  ArrowRight,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getEmployeesApi } from '../api/employees';

export const DashboardPage: React.FC = () => {
  const { user, modules, hasPermission, getEffectiveScope } = useAuth();
  const [totalEmployees, setTotalEmployees] = useState<number | null>(null);
  const [activeEmployees, setActiveEmployees] = useState<number | null>(null);
  const [isLoadingStats, setIsLoadingStats] = useState<boolean>(true);

  const canViewEmployees = hasPermission('ADMIN_EMPLOYEES', 'view');
  const canCreateEmployees = hasPermission('ADMIN_EMPLOYEES', 'create');
  const employeeScope = getEffectiveScope('ADMIN_EMPLOYEES');

  useEffect(() => {
    let isMounted = true;
    if (canViewEmployees) {
      setIsLoadingStats(true);
      Promise.all([
        getEmployeesApi({ page: 1, page_size: 1 }),
        getEmployeesApi({ page: 1, page_size: 1, account_status: 'ACTIVE' }),
      ])
        .then(([allRes, activeRes]) => {
          if (isMounted) {
            setTotalEmployees(allRes.total);
            setActiveEmployees(activeRes.total);
          }
        })
        .catch((err) => {
          console.error('Failed to load stats on dashboard:', err);
        })
        .finally(() => {
          if (isMounted) setIsLoadingStats(false);
        });
    } else {
      setIsLoadingStats(false);
    }
    return () => {
      isMounted = false;
    };
  }, [canViewEmployees]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-brand-900 via-brand-800 to-brand-700 rounded-2xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-cyan-400/10 rounded-full blur-2xl pointer-events-none" />
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-xs font-semibold text-brand-200 mb-4 border border-white/15">
            <Building className="w-3.5 h-3.5" />
            <span>GoCompliances CRM Platform</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {user?.first_name} {user?.last_name}!
          </h1>
          <p className="mt-2 text-sm sm:text-base text-brand-100/90 leading-relaxed">
            Manage your organization's staff, departmental hierarchies, and status workflows from this dedicated administrative panel.
          </p>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Total Employees */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Total In Scope
            </p>
            <h3 className="text-2xl font-extrabold text-slate-900 mt-1">
              {isLoadingStats ? (
                <span className="inline-block w-8 h-6 bg-slate-100 rounded animate-pulse" />
              ) : (
                totalEmployees ?? 0
              )}
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Employees in your {employeeScope || 'assigned'} scope
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center shrink-0">
            <Users className="w-6 h-6" />
          </div>
        </div>

        {/* Active Accounts */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Active Status
            </p>
            <h3 className="text-2xl font-extrabold text-emerald-600 mt-1">
              {isLoadingStats ? (
                <span className="inline-block w-8 h-6 bg-slate-100 rounded animate-pulse" />
              ) : (
                activeEmployees ?? 0
              )}
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Operational active CRM users
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
            <CheckCircle className="w-6 h-6" />
          </div>
        </div>

        {/* Data Scope */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Assigned Scope
            </p>
            <h3 className="text-2xl font-extrabold text-indigo-600 mt-1">
              {employeeScope || 'N/A'}
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Backend visibility boundary
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
            <Shield className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Quick Actions & Navigation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Core Quick Links */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200/80 shadow-xs p-6">
          <h2 className="text-base font-bold text-slate-900 mb-4">
            Employee Actions
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {canViewEmployees && (
              <Link
                to="/employees"
                className="p-4 rounded-xl border border-slate-200 hover:border-brand-500 hover:shadow-md transition-all group bg-slate-50/50 flex flex-col justify-between"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-brand-100 text-brand-600 flex items-center justify-center">
                    <Users className="w-5 h-5" />
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-brand-600 group-hover:translate-x-1 transition-all" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 group-hover:text-brand-600 transition-colors">
                    View Employee Directory
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Search, filter, view details, and manage status workflows.
                  </p>
                </div>
              </Link>
            )}

            {canCreateEmployees && (
              <Link
                to="/employees/new"
                className="p-4 rounded-xl border border-slate-200 hover:border-brand-500 hover:shadow-md transition-all group bg-slate-50/50 flex flex-col justify-between"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center">
                    <UserPlus className="w-5 h-5" />
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-600 group-hover:translate-x-1 transition-all" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 group-hover:text-emerald-600 transition-colors">
                    Add New Employee
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Onboard a new employee with automatic employee code assignment.
                  </p>
                </div>
              </Link>
            )}
          </div>
        </div>

        {/* Modules & Permissions Summary */}
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs p-6">
          <h2 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Shield className="w-4 h-4 text-brand-600" />
            <span>Accessible Modules</span>
          </h2>
          <div className="space-y-3">
            {modules.map((mod) => (
              <div
                key={mod.module_id}
                className="p-3 rounded-lg border border-slate-100 bg-slate-50 flex items-center justify-between"
              >
                <div>
                  <div className="text-xs font-bold text-slate-800">
                    {mod.module_name}
                  </div>
                  <div className="text-[11px] font-mono text-slate-500">
                    {mod.module_code}
                  </div>
                </div>
                <div className="flex items-center gap-1 text-[10px] font-semibold text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                  {mod.data_scope}
                </div>
              </div>
            ))}
            {modules.length === 0 && (
              <p className="text-xs text-slate-500">
                No active module permissions granted to this user.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  LayoutDashboard,
  Layers,
  Clock,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  TrendingUp,
  RefreshCw,
  Eye,
  AlertCircle,
  Users,
} from 'lucide-react';
import type { OperationsDashboardResponse } from '../../types/operations';
import { getOperationsDashboardApi } from '../../api/operations';
import { TaskDetailModal } from '../../components/operations/TaskDetailModal';

export const OperationsDashboardPage: React.FC = () => {
  const context = useOutletContext<{
    addToast?: (type: 'success' | 'error' | 'info', title: string, message: string) => void;
  }>();

  const [dashboardData, setDashboardData] = useState<OperationsDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selected task modal state
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getOperationsDashboardApi();
      setDashboardData(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load Operations Dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const openTaskDetail = (appId: string) => {
    setSelectedAppId(appId);
    setIsDetailModalOpen(true);
  };

  const getPriorityBadge = (p: string) => {
    switch (p?.toUpperCase()) {
      case 'URGENT':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-300">URGENT</span>;
      case 'HIGH':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">HIGH</span>;
      case 'LOW':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">LOW</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">MEDIUM</span>;
    }
  };

  const getStatusBadge = (s: string) => {
    switch (s?.toUpperCase()) {
      case 'APPROVED':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">Approved</span>;
      case 'IN_PROGRESS':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300">In Progress</span>;
      case 'PENDING_DOCUMENTS':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">Pending Docs</span>;
      case 'READY_FOR_SUBMISSION':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-cyan-100 text-cyan-700 dark:bg-cyan-950/60 dark:text-cyan-300">Ready to Submit</span>;
      case 'SUBMITTED':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-100 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300">Submitted</span>;
      case 'AUTHORITY_QUERY':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300">Authority Query</span>;
      case 'CANCELLED':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300">Cancelled</span>;
      case 'UNASSIGNED':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">Unassigned</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">Assigned</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
              Operation Dashboard
            </h1>
            {dashboardData && (
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                Scope: {dashboardData.scope}
              </span>
            )}
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Real-time compliance application lifecycle, SLA tracking, and team workload analytics.
          </p>
        </div>

        <button
          type="button"
          onClick={loadDashboard}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 shadow-xs transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-blue-600' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading && !dashboardData && (
        <div className="py-20 flex flex-col items-center justify-center text-slate-400 space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
          <p className="text-sm">Loading live operations metrics...</p>
        </div>
      )}

      {!loading && dashboardData && (
        <>
          {/* Top KPI Summary Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
            {/* Card 1: Total Applications */}
            <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
                <span>Total Tasks</span>
                <Layers className="w-4 h-4 text-blue-600" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-black text-slate-900 dark:text-white">
                  {dashboardData.kpis.total_applications}
                </span>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  {dashboardData.kpis.unassigned_count} unassigned
                </p>
              </div>
            </div>

            {/* Card 2: In Progress */}
            <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-indigo-600 dark:text-indigo-400 text-xs font-semibold">
                <span>In Progress</span>
                <Clock className="w-4 h-4" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-black text-indigo-600 dark:text-indigo-400">
                  {dashboardData.kpis.in_progress_count}
                </span>
                <p className="text-[11px] text-slate-400 mt-0.5">Active fulfillment</p>
              </div>
            </div>

            {/* Card 3: Pending Docs */}
            <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-amber-600 dark:text-amber-400 text-xs font-semibold">
                <span>Pending Docs</span>
                <FileCheck className="w-4 h-4" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-black text-amber-600 dark:text-amber-400">
                  {dashboardData.kpis.pending_documents_count}
                </span>
                <p className="text-[11px] text-slate-400 mt-0.5">Awaiting client docs</p>
              </div>
            </div>

            {/* Card 4: Under Review / Submitted */}
            <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-purple-600 dark:text-purple-400 text-xs font-semibold">
                <span>Submitted</span>
                <TrendingUp className="w-4 h-4" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-black text-purple-600 dark:text-purple-400">
                  {dashboardData.kpis.ready_submitted_count}
                </span>
                <p className="text-[11px] text-slate-400 mt-0.5">Under authority review</p>
              </div>
            </div>

            {/* Card 5: Approved */}
            <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-emerald-600 dark:text-emerald-400 text-xs font-semibold">
                <span>Approved</span>
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                  {dashboardData.kpis.approved_count}
                </span>
                <p className="text-[11px] text-slate-400 mt-0.5">Successfully fulfilled</p>
              </div>
            </div>

            {/* Card 6: Overdue / SLA */}
            <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-red-600 dark:text-red-400 text-xs font-semibold">
                <span>Overdue SLA</span>
                <AlertTriangle className="w-4 h-4" />
              </div>
              <div className="mt-2">
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-black text-red-600 dark:text-red-400">
                    {dashboardData.kpis.overdue_count}
                  </span>
                  <span className="text-xs font-bold text-slate-500">
                    ({dashboardData.kpis.sla_adherence_percent}%)
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5">Adherence rating</p>
              </div>
            </div>
          </div>

          {/* Section: Status Breakdown Progress & Priority Queue */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Status Breakdown */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-4">
              <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <LayoutDashboard className="w-4 h-4 text-blue-600" />
                Application Status Distribution
              </h2>

              <div className="space-y-3">
                {dashboardData.status_breakdown.map((item) => (
                  <div key={item.status} className="space-y-1">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-slate-700 dark:text-slate-300">{item.label}</span>
                      <span className="text-slate-500">
                        {item.count} ({item.percentage}%)
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${item.percentage}%`,
                          backgroundColor: item.color,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Priority Queue / Overdue Applications */}
            <div className="lg:col-span-2 p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500" />
                  Priority & Critical Queue
                </h2>
                <span className="text-xs text-slate-400">
                  {dashboardData.priority_queue.length} urgent / high priority tasks
                </span>
              </div>

              {dashboardData.priority_queue.length === 0 ? (
                <div className="p-8 text-center bg-slate-50 dark:bg-slate-800/40 rounded-xl text-slate-400 text-xs">
                  No high priority or overdue tasks in queue.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 uppercase text-[10px]">
                        <th className="py-2.5 px-3">App #</th>
                        <th className="py-2.5 px-3">Client</th>
                        <th className="py-2.5 px-3">Service</th>
                        <th className="py-2.5 px-3">Assignee</th>
                        <th className="py-2.5 px-3">Due Date</th>
                        <th className="py-2.5 px-3">Status</th>
                        <th className="py-2.5 px-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
                      {dashboardData.priority_queue.map((task) => (
                        <tr key={task.application_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                          <td className="py-2.5 px-3 font-mono font-bold text-blue-600 dark:text-blue-400">
                            {task.application_number}
                          </td>
                          <td className="py-2.5 px-3 text-slate-800 dark:text-slate-200">{task.client_name}</td>
                          <td className="py-2.5 px-3 text-slate-600 dark:text-slate-400">{task.service_name}</td>
                          <td className="py-2.5 px-3 text-slate-700 dark:text-slate-300">
                            {task.assigned_to_name || <span className="text-amber-500">Unassigned</span>}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={task.is_overdue ? 'text-red-600 font-bold' : 'text-slate-500'}>
                              {task.formatted_due_date || '—'}
                              {task.is_overdue && ' ⚠️'}
                            </span>
                          </td>
                          <td className="py-2.5 px-3">{getStatusBadge(task.application_status)}</td>
                          <td className="py-2.5 px-3 text-right">
                            <button
                              type="button"
                              onClick={() => openTaskDetail(task.application_id)}
                              className="p-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 dark:bg-blue-950 dark:text-blue-300 transition"
                              title="Open Task Details"
                            >
                              <Eye className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* Section: Executive Workload Table */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-600" />
                Operations Executive Workload & Throughput
              </h2>
              <span className="text-xs text-slate-400">Permitted team members</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 uppercase text-[10px]">
                    <th className="py-3 px-4">Executive</th>
                    <th className="py-3 px-4">Designation</th>
                    <th className="py-3 px-4 text-center">Active Tasks</th>
                    <th className="py-3 px-4 text-center">In Progress</th>
                    <th className="py-3 px-4 text-center">Completed</th>
                    <th className="py-3 px-4 text-center">Overdue</th>
                    <th className="py-3 px-4 text-right">SLA Rating</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
                  {dashboardData.workload_by_executive.map((exec) => (
                    <tr key={exec.user_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                      <td className="py-3 px-4">
                        <div className="font-bold text-slate-900 dark:text-white">{exec.full_name}</div>
                        <div className="text-[11px] font-mono text-slate-400">{exec.employee_code}</div>
                      </td>
                      <td className="py-3 px-4 text-slate-500">{exec.designation_name || 'Operations Executive'}</td>
                      <td className="py-3 px-4 text-center font-bold text-blue-600 dark:text-blue-400">
                        {exec.active_tasks}
                      </td>
                      <td className="py-3 px-4 text-center font-medium text-slate-700 dark:text-slate-300">
                        {exec.in_progress_tasks}
                      </td>
                      <td className="py-3 px-4 text-center font-semibold text-emerald-600 dark:text-emerald-400">
                        {exec.completed_tasks}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={exec.overdue_tasks > 0 ? 'text-red-600 font-bold' : 'text-slate-400'}>
                          {exec.overdue_tasks}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right font-bold">
                        <span
                          className={`px-2.5 py-1 rounded-full text-[11px] ${
                            exec.sla_rating >= 90
                              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                              : exec.sla_rating >= 75
                              ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
                              : 'bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300'
                          }`}
                        >
                          {exec.sla_rating}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section: Recent Applications Table */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-4">
            <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-blue-600" />
              Recent Compliance Applications
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 uppercase text-[10px]">
                    <th className="py-3 px-3">Application #</th>
                    <th className="py-3 px-3">Order #</th>
                    <th className="py-3 px-3">Client</th>
                    <th className="py-3 px-3">Service</th>
                    <th className="py-3 px-3">Assigned To</th>
                    <th className="py-3 px-3">Converted By</th>
                    <th className="py-3 px-3">Priority</th>
                    <th className="py-3 px-3">Status</th>
                    <th className="py-3 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
                  {dashboardData.recent_applications.map((app) => (
                    <tr key={app.application_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                      <td className="py-3 px-3 font-mono font-bold text-blue-600 dark:text-blue-400">
                        {app.application_number}
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-500">{app.sales_order_number || '—'}</td>
                      <td className="py-3 px-3 font-semibold text-slate-900 dark:text-white">{app.client_name}</td>
                      <td className="py-3 px-3 text-slate-600 dark:text-slate-400">{app.service_name}</td>
                      <td className="py-3 px-3 text-slate-700 dark:text-slate-300">
                        {app.assigned_to_name ? (
                          <span className="font-semibold text-slate-900 dark:text-white">{app.assigned_to_name}</span>
                        ) : (
                          <span className="text-amber-500 font-medium">Unassigned</span>
                        )}
                      </td>
                      <td className="py-3 px-3 text-slate-500">{app.salesperson_name || '—'}</td>
                      <td className="py-3 px-3">{getPriorityBadge(app.priority)}</td>
                      <td className="py-3 px-3">{getStatusBadge(app.application_status)}</td>
                      <td className="py-3 px-3 text-right">
                        <button
                          type="button"
                          onClick={() => openTaskDetail(app.application_id)}
                          className="p-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 dark:bg-blue-950 dark:text-blue-300 transition"
                          title="Open Task Details"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Task Details Modal */}
      <TaskDetailModal
        applicationId={selectedAppId}
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedAppId(null);
        }}
        onRefresh={loadDashboard}
        onShowToast={context?.addToast}
      />
    </div>
  );
};

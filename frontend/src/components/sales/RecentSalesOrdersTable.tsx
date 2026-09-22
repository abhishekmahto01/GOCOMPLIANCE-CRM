import React from 'react';
import { FileText, Eye, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import type { RecentOrderItem } from '../../types/sales';

export interface RecentSalesOrdersTableProps {
  orders: RecentOrderItem[];
  onViewOrder?: (orderId: string) => void;
}

function formatInr(val: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val);
}

function renderPaymentBadge(status: string) {
  switch (status) {
    case 'FULLY_PAID':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800/60">
          <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
          Fully Paid
        </span>
      );
    case 'PARTIALLY_PAID':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-400 dark:border-blue-800/60">
          Partially Paid
        </span>
      );
    case 'PENDING':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-800/60">
          <Clock className="w-3 h-3 text-amber-600 dark:text-amber-400" />
          Pending
        </span>
      );
    case 'OVERDUE':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-800/60">
          <AlertCircle className="w-3 h-3 text-rose-600 dark:text-rose-400" />
          Overdue
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
          {status}
        </span>
      );
  }
}

function renderOperationBadge(status: string) {
  const s = status.toUpperCase();
  if (s === 'COMPLETED') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800/60">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        Completed
      </span>
    );
  }
  if (['IN_PROGRESS', 'ASSIGNED', 'DOCUMENT_VERIFICATION'].includes(s)) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-400 dark:border-blue-800/60">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
        In Progress
      </span>
    );
  }
  if (['UNASSIGNED', 'PENDING', 'NONE'].includes(s)) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-800/60">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
        Pending
      </span>
    );
  }
  if (s === 'REJECTED') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-800/60">
        Rejected
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
      {status}
    </span>
  );
}

export const RecentSalesOrdersTable: React.FC<RecentSalesOrdersTableProps> = ({
  orders,
  onViewOrder,
}) => {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-xs border border-slate-200/80 dark:border-slate-800 transition-colors">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">
            Recent Sales Orders
          </h2>
        </div>
      </div>

      {/* Table with horizontal scroll support */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs sm:text-sm">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              <th scope="col" className="py-3 px-3">ORDER ID</th>
              <th scope="col" className="py-3 px-3">DATE</th>
              <th scope="col" className="py-3 px-3">CLIENT</th>
              <th scope="col" className="py-3 px-3">SERVICE</th>
              <th scope="col" className="py-3 px-3">SALESPERSON</th>
              <th scope="col" className="py-3 px-3 text-right">ORDER VALUE</th>
              <th scope="col" className="py-3 px-3 text-right">RECEIVED</th>
              <th scope="col" className="py-3 px-3 text-right">BALANCE</th>
              <th scope="col" className="py-3 px-3 text-center">PAYMENT STATUS</th>
              <th scope="col" className="py-3 px-3 text-center">OPERATION STATUS</th>
              <th scope="col" className="py-3 px-3 text-center">ACTIONS</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
            {orders.length > 0 ? (
              orders.map((order) => (
                <tr
                  key={order.order_id}
                  className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors"
                >
                  <td className="py-3 px-3 font-semibold text-slate-900 dark:text-slate-100">
                    {order.order_number}
                  </td>
                  <td className="py-3 px-3 text-slate-600 dark:text-slate-300 whitespace-nowrap">
                    {order.formatted_date}
                  </td>
                  <td className="py-3 px-3 font-medium text-slate-800 dark:text-slate-200">
                    {order.client_name}
                  </td>
                  <td className="py-3 px-3 text-slate-600 dark:text-slate-300">
                    {order.service_name}
                  </td>
                  <td className="py-3 px-3 text-slate-700 dark:text-slate-300">
                    {order.salesperson_name}
                  </td>
                  <td className="py-3 px-3 text-right font-semibold text-slate-900 dark:text-white">
                    {formatInr(order.order_value)}
                  </td>
                  <td className="py-3 px-3 text-right font-medium text-emerald-600 dark:text-emerald-400">
                    {formatInr(order.amount_received)}
                  </td>
                  <td className="py-3 px-3 text-right font-medium text-slate-700 dark:text-slate-300">
                    {formatInr(order.balance_amount)}
                  </td>
                  <td className="py-3 px-3 text-center whitespace-nowrap">
                    {renderPaymentBadge(order.payment_status)}
                  </td>
                  <td className="py-3 px-3 text-center whitespace-nowrap">
                    {renderOperationBadge(order.operation_status)}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <button
                      type="button"
                      onClick={() => onViewOrder && onViewOrder(order.order_id)}
                      className="p-1 rounded-lg text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/50 transition"
                      title="View Order Details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={11} className="py-8 text-center text-slate-400 dark:text-slate-500 text-xs">
                  No sales orders found in this period
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

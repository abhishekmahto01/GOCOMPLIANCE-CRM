export interface ApplicationDoc {
  app_doc_id: string;
  application_id: string;
  document_code: string;
  document_name: string;
  is_mandatory: boolean;
  status: 'PENDING' | 'RECEIVED' | 'VERIFIED' | 'REJECTED' | 'NOT_APPLICABLE' | string;
  rejection_reason?: string | null;
  verified_by_user_id?: string | null;
  verified_by_name?: string | null;
  verified_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssignmentHistory {
  history_id: string;
  application_id: string;
  assigned_by_user_id: string;
  assigned_by_name?: string | null;
  previous_assignee_user_id?: string | null;
  previous_assignee_name?: string | null;
  new_assignee_user_id?: string | null;
  new_assignee_name?: string | null;
  reason?: string | null;
  assigned_at: string;
}

export interface ActivityLog {
  activity_id: string;
  application_id: string;
  actor_user_id: string;
  actor_name?: string | null;
  action_type: string;
  old_value?: string | null;
  new_value?: string | null;
  comment?: string | null;
  created_at: string;
}

export interface OperationRemark {
  remark_id: string;
  application_id: string;
  author_user_id: string;
  author_name: string;
  author_employee_code?: string | null;
  author_department?: string | null;
  author_designation?: string | null;
  remark_text: string;
  created_at: string;
  formatted_created_at?: string | null;
}

export interface OperationRemarkCreate {
  remark_text: string;
}

export interface OperationApplication {
  application_id: string;
  application_number: string;
  sales_order_id: string;
  sales_order_number?: string | null;
  company_id: string;
  client_id: string;
  client_name?: string | null;
  client_phone?: string | null;
  client_email?: string | null;
  service_id: string;
  service_name?: string | null;
  service_code?: string | null;
  salesperson_name?: string | null;
  salesperson_code?: string | null;
  assigned_to_user_id?: string | null;
  assigned_to_name?: string | null;
  assigned_to_code?: string | null;
  assigned_by_user_id?: string | null;
  assigned_by_name?: string | null;
  assigned_at?: string | null;
  formatted_assigned_at?: string | null;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT' | string;
  application_status:
    | 'UNASSIGNED'
    | 'ASSIGNED'
    | 'IN_PROGRESS'
    | 'PENDING_DOCUMENTS'
    | 'READY_FOR_SUBMISSION'
    | 'SUBMITTED'
    | 'AUTHORITY_QUERY'
    | 'APPROVED'
    | 'CANCELLED'
    | string;
  target_due_date?: string | null;
  formatted_due_date?: string | null;
  completion_date?: string | null;
  assignment_notes?: string | null;
  documents_completed: number;
  documents_total: number;
  is_overdue: boolean;
  is_due_soon: boolean;
  order_date?: string | null;
  formatted_order_date?: string | null;
  latest_remark?: OperationRemark | null;
  created_at: string;
  updated_at: string;
}

export interface OperationApplicationDetail extends OperationApplication {
  documents: ApplicationDoc[];
  assignment_history: AssignmentHistory[];
  activity_logs: ActivityLog[];
  remarks: OperationRemark[];
}

export interface OperationsKpiSummary {
  total_applications: number;
  assigned_count: number;
  in_progress_count: number;
  pending_documents_count: number;
  ready_submitted_count: number;
  authority_query_count: number;
  approved_count: number;
  overdue_count: number;
  unassigned_count: number;
  sla_adherence_percent: number;
}

export interface OperationsStatusBreakdownItem {
  status: string;
  label: string;
  count: number;
  percentage: number;
  color: string;
}

export interface ExecutiveWorkloadItem {
  user_id: string;
  employee_code: string;
  full_name: string;
  designation_name?: string | null;
  active_tasks: number;
  in_progress_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  sla_rating: number;
}

export interface OperationsTaskSummary {
  total_tasks: number;
  assigned: number;
  in_progress: number;
  pending_docs: number;
  under_review: number;
  completed: number;
  overdue: number;
}

export interface OperationsTaskListResponse {
  items: OperationApplication[];
  total_count: number;
  page: number;
  limit: number;
  total_pages: number;
  summary: OperationsTaskSummary;
}

export interface OperationsDashboardResponse {
  kpis: OperationsKpiSummary;
  status_breakdown: OperationsStatusBreakdownItem[];
  workload_by_executive: ExecutiveWorkloadItem[];
  recent_applications: OperationApplication[];
  priority_queue: OperationApplication[];
  scope: string;
  company_id: string;
  company_name: string;
}

export interface TaskAssignRequest {
  assignee_user_id: string;
  priority?: string;
  target_due_date?: string | null;
  notes?: string | null;
}

export interface TaskReassignRequest {
  new_assignee_user_id: string;
  reason: string;
  priority?: string;
  target_due_date?: string | null;
  notes?: string | null;
}

export interface ApplicationStatusUpdateRequest {
  new_status: string;
  comment?: string;
}

export interface ApplicationDocUpdate {
  status: string;
  rejection_reason?: string | null;
}

export interface AssigneeOption {
  user_id: string;
  employee_code: string;
  full_name: string;
  name?: string;
  department_name?: string | null;
  designation_name?: string | null;
}

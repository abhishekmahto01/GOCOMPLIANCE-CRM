/** Types for the R&D / Internal Tasks feature (tasks not linked to Sales orders). */

export type InternalTaskType = 'RESEARCH' | 'VENDOR' | 'OTHER';
export type InternalTaskStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
export type InternalTaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export interface InternalTaskUserRef {
  user_id: string;
  name: string;
  employee_code?: string | null;
  department_name?: string | null;
  company_name?: string | null;
}

export interface InternalTask {
  task_id: string;
  task_number: string;
  company_id: string;
  company_name?: string | null;
  title: string;
  description?: string | null;
  task_type: InternalTaskType;
  priority: InternalTaskPriority;
  status: InternalTaskStatus;
  assigned_to?: InternalTaskUserRef | null;
  created_by?: InternalTaskUserRef | null;
  due_date?: string | null;
  is_overdue: boolean;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
  can_update_status: boolean;
  can_edit: boolean;
  can_reassign: boolean;
}

export interface InternalTaskSummary {
  total: number;
  pending: number;
  in_progress: number;
  completed: number;
  cancelled: number;
}

export interface InternalTaskCapabilities {
  can_create: boolean;
  can_assign: boolean;
  is_manager: boolean;
  scope?: string | null;
}

export interface InternalTaskListResponse {
  items: InternalTask[];
  total: number;
  summary: InternalTaskSummary;
  capabilities: InternalTaskCapabilities;
}

export interface InternalTaskCreatePayload {
  title: string;
  description?: string | null;
  task_type: InternalTaskType;
  priority: InternalTaskPriority;
  assigned_to_user_id: string;
  due_date?: string | null;
}

export interface InternalTaskMessage {
  message_id: string;
  task_id: string;
  author_user_id?: string | null;
  author_name?: string | null;
  author_employee_code?: string | null;
  author_department_name?: string | null;
  message_type: 'COMMENT' | 'SYSTEM_EVENT';
  message_text: string;
  is_own: boolean;
  created_at: string;
}

export interface InternalTaskThread {
  task: InternalTask;
  messages: InternalTaskMessage[];
  can_post: boolean;
}

export interface InternalTaskListParams {
  status?: InternalTaskStatus | '';
  task_type?: InternalTaskType | '';
  search?: string;
  mine?: boolean;
}

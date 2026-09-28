/**
 * Department entity and API schema definitions.
 */

export type DepartmentStatus = 'ACTIVE' | 'INACTIVE';

export interface Department {
  department_id: string;
  company_id?: string | null;
  department_code: string;
  department_name: string;
  description?: string | null;
  status: DepartmentStatus;
  created_at: string;
  updated_at: string;
}

export interface DepartmentCreatePayload {
  company_id?: string | null;
  department_code: string;
  department_name: string;
  description?: string | null;
  status?: DepartmentStatus;
}

export interface DepartmentUpdatePayload {
  department_name?: string;
  description?: string | null;
  status?: DepartmentStatus;
}

export interface DepartmentFilterParams {
  company_id?: string;
  search?: string;
  status?: string;
}

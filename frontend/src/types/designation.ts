/**
 * Designation entity and API schema definitions.
 */

export type DesignationStatus = 'ACTIVE' | 'INACTIVE';

export interface Designation {
  designation_id: string;
  company_id?: string | null;
  designation_code: string;
  designation_name: string;
  level_rank: number;
  is_managerial: boolean;
  description?: string | null;
  status: DesignationStatus;
  created_at: string;
  updated_at: string;
}

export interface DesignationCreatePayload {
  company_id?: string | null;
  designation_code: string;
  designation_name: string;
  level_rank: number;
  is_managerial?: boolean;
  description?: string | null;
  status?: DesignationStatus;
}

export interface DesignationUpdatePayload {
  designation_name?: string;
  level_rank?: number;
  is_managerial?: boolean;
  description?: string | null;
  status?: DesignationStatus;
}

export interface DesignationFilterParams {
  company_id?: string;
  search?: string;
  status?: string;
}

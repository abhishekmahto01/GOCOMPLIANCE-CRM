export type SourceStatus = 'ACTIVE' | 'INACTIVE';

export interface SourceMaster {
  source_id: string;
  source_code: string;
  source_name: string;
  description?: string | null;
  status: SourceStatus;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface SourceCreatePayload {
  source_code: string;
  source_name: string;
  description?: string;
  status?: SourceStatus;
}

export interface SourceUpdatePayload {
  source_name?: string;
  description?: string;
  status?: SourceStatus;
}

export interface SourceFilterParams {
  search?: string;
  status?: string;
}


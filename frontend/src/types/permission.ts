export type ActionType =
  | 'view'
  | 'read'
  | 'create'
  | 'write'
  | 'edit'
  | 'update'
  | 'delete'
  | 'approve'
  | 'assign'
  | 'reassign'
  | 'export';

export type DataScope = 'SELF' | 'TEAM' | 'DEPARTMENT' | 'COMPANY' | 'ALL';

export interface AccessibleModule {
  module_id: string;
  module_code: string;
  module_name: string;
  parent_module_id?: string | null;
  route?: string | null;
  display_order: number;
  is_navigation: boolean;
  can_view: boolean;
  can_create: boolean;
  can_edit: boolean;
  can_delete: boolean;
  can_approve: boolean;
  can_assign?: boolean;
  can_reassign?: boolean;
  can_export?: boolean;
  data_scope: DataScope;
  child_modules?: AccessibleModule[];
}

export interface CatalogPageItem {
  page_code: string;
  page_name: string;
  route?: string | null;
  supported_actions: string[];
  action_slugs: Record<string, string>;
  display_order: number;
}

export interface CatalogModuleItem {
  module_code: string;
  module_name: string;
  pages: CatalogPageItem[];
}

export interface PermissionCatalogResponse {
  modules: CatalogModuleItem[];
}

export interface PageActionPermission {
  page_code: string;
  can_view: boolean;
  can_create: boolean;
  can_edit: boolean;
  can_delete: boolean;
  can_assign: boolean;
  can_reassign: boolean;
  can_export: boolean;
  can_approve: boolean;
  data_scope: DataScope;
  status: 'ACTIVE' | 'INACTIVE';
}

export interface UserSettingsUpdate {
  is_active?: boolean | null;
  is_hod?: boolean | null;
  is_reporting_manager?: boolean | null;
  manager_user_id?: string | null;
  primary_location?: string | null;
}

export interface UserPermissionsDetailResponse {
  user_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  official_email: string;
  company_id: string;
  company_name?: string | null;
  department_id: string;
  department_name?: string | null;
  designation_id: string;
  designation_name?: string | null;
  is_active: boolean;
  is_hod: boolean;
  is_reporting_manager: boolean;
  manager_user_id?: string | null;
  manager_name?: string | null;
  primary_location?: string | null;
  permissions: PageActionPermission[];
}

export interface UserPermissionsSaveRequest {
  permissions: PageActionPermission[];
  user_settings?: UserSettingsUpdate | null;
}

export interface CopyPermissionsRequest {
  source_user_id: string;
}

export interface CopyPermissionsResponse {
  message: string;
  copied_count: number;
  source_user_id: string;
  target_user_id: string;
}

export interface UserEffectivePermissionsResponse {
  user_id: string;
  employee_code: string;
  official_email: string;
  first_name: string;
  last_name: string;
  company_id: string;
  department_id: string;
  permissions: Record<string, boolean>;
  accessible_pages: AccessibleModule[];
}

export interface UserEffectivePermissions {
  user_id: string;
  employee_code: string;
  is_active: boolean;
  is_hod: boolean;
  is_reporting_manager: boolean;
  permission_slugs: string[];
  permissions: AccessibleModule[];
}

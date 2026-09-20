export type ActionType = 'view' | 'create' | 'edit' | 'delete' | 'approve';

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
  data_scope: DataScope;
  child_modules?: AccessibleModule[];
}

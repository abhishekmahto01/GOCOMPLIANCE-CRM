import type React from 'react';
import {
  LayoutDashboard,
  Users,
  UserPlus,
  ShieldCheck,
  UserCheck,
  Building2,
  Layers,
  FileBadge,
  Network,
  Award,
} from 'lucide-react';
import type { ActionType } from '../../types/permission';

export interface NavChildItem {
  id: string;
  title: string;
  route: string;
  icon: React.ComponentType<{ className?: string }>;
  requiredModule: string;
  requiredAction?: ActionType;
  badge?: string;
  isUpcoming?: boolean;
}

export interface NavParentGroup {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  children: NavChildItem[];
}

export interface DirectNavItem {
  id: string;
  title: string;
  route: string;
  icon: React.ComponentType<{ className?: string }>;
  requiredModule?: string;
  requiredAction?: ActionType;
}

export const TOP_NAV_ITEMS: DirectNavItem[] = [
  {
    id: 'dashboard',
    title: 'Dashboard',
    route: '/dashboard',
    icon: LayoutDashboard,
  },
];

export const ADMIN_NAV_GROUPS: NavParentGroup[] = [
  {
    id: 'employee_master',
    title: 'Employee Master',
    icon: Users,
    children: [
      {
        id: 'employee_list',
        title: 'Employee List',
        route: '/admin/employees',
        icon: Users,
        requiredModule: 'ADMIN_EMPLOYEES',
        requiredAction: 'view',
      },
      {
        id: 'add_employee',
        title: 'Add Employee',
        route: '/admin/employees/new',
        icon: UserPlus,
        requiredModule: 'ADMIN_EMPLOYEES',
        requiredAction: 'create',
      },
    ],
  },
  {
    id: 'user_control',
    title: 'User Control',
    icon: ShieldCheck,
    children: [
      {
        id: 'access_control',
        title: 'User Permissions',
        route: '/admin/access',
        icon: ShieldCheck,
        requiredModule: 'ADMIN',
        requiredAction: 'view',
      },
      {
        id: 'account_activation',
        title: 'Login Credentials',
        route: '/admin/account-activation',
        icon: UserCheck,
        requiredModule: 'ADMIN_EMPLOYEES',
        requiredAction: 'view',
      },
    ],
  },
  {
    id: 'common_master',
    title: 'Common Master',
    icon: Layers,
    children: [
      {
        id: 'company_master',
        title: 'Company Master',
        route: '/admin/companies',
        icon: Building2,
        requiredModule: 'ADMIN',
        requiredAction: 'view',
      },
      {
        id: 'department_master',
        title: 'Department Master',
        route: '/admin/departments',
        icon: Network,
        requiredModule: 'ADMIN',
        requiredAction: 'view',
      },
      {
        id: 'designation_master',
        title: 'Designation Master',
        route: '/admin/designations',
        icon: Award,
        requiredModule: 'ADMIN',
        requiredAction: 'view',
      },
      {
        id: 'license_master',
        title: 'License Master',
        route: '/admin/licenses',
        icon: FileBadge,
        requiredModule: 'ADMIN',
        requiredAction: 'view',
      },
    ],
  },
];

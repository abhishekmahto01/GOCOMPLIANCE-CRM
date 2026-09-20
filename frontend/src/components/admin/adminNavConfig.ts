import type React from 'react';
import {
  LayoutDashboard,
  Users,
  UserPlus,
  ShieldCheck,
  KeyRound,
  UserCheck,
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
    id: 'employee_management',
    title: 'Employee Management',
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
        title: 'Access Control & Scopes',
        route: '/admin/access',
        icon: KeyRound,
        badge: 'Coming Soon',
        isUpcoming: true,
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
];

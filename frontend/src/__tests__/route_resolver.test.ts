import { describe, it, expect } from 'vitest';
import {
  resolveActiveModule,
  isLocalEnvironment,
  getCrossModuleUrl,
} from '../utils/routeResolver';

describe('Centralized Route Resolver (resolveActiveModule) — single domain, path-based', () => {
  describe('Localhost', () => {
    it('/admin/* loads ADMIN with basePath /admin', () => {
      expect(resolveActiveModule('localhost', '/admin/tasks')).toEqual({ module: 'ADMIN', basePath: '/admin' });
      expect(resolveActiveModule('127.0.0.1', '/admin/employees')).toEqual({ module: 'ADMIN', basePath: '/admin' });
      expect(resolveActiveModule('localhost:5173', '/admin/companies')).toEqual({ module: 'ADMIN', basePath: '/admin' });
      expect(resolveActiveModule('macbook.local', '/admin')).toEqual({ module: 'ADMIN', basePath: '/admin' });
    });

    it('all other paths load WORKFLOW with basePath /', () => {
      expect(resolveActiveModule('localhost', '/dashboard')).toEqual({ module: 'WORKFLOW', basePath: '/' });
      expect(resolveActiveModule('127.0.0.1', '/sales/register')).toEqual({ module: 'WORKFLOW', basePath: '/' });
      expect(resolveActiveModule('macbook.local', '/operations/tasks')).toEqual({ module: 'WORKFLOW', basePath: '/' });
    });
  });

  describe('Production (same rules as localhost)', () => {
    it('/admin/* on the production domain loads ADMIN with basePath /admin', () => {
      expect(resolveActiveModule('workflow.gocompliances.com', '/admin')).toEqual({ module: 'ADMIN', basePath: '/admin' });
      expect(resolveActiveModule('workflow.gocompliances.com', '/admin/employees')).toEqual({ module: 'ADMIN', basePath: '/admin' });
    });

    it('CRM pages on the production domain load WORKFLOW with basePath /', () => {
      for (const p of ['/', '/dashboard', '/sales/orders', '/operations/dashboard', '/accounts/entries']) {
        expect(resolveActiveModule('workflow.gocompliances.com', p)).toEqual({ module: 'WORKFLOW', basePath: '/' });
      }
    });

    it('a host named admin.* no longer forces a separate Admin portal', () => {
      expect(resolveActiveModule('admin.gocompliances.com', '/dashboard')).toEqual({ module: 'WORKFLOW', basePath: '/' });
      expect(resolveActiveModule('admin.gocompliances.com', '/admin/employees')).toEqual({ module: 'ADMIN', basePath: '/admin' });
    });
  });

  describe('Cross-Module Transition Helper (getCrossModuleUrl)', () => {
    it('always returns same-origin relative routes', () => {
      for (const host of ['localhost', 'workflow.gocompliances.com', 'admin.gocompliances.com']) {
        expect(getCrossModuleUrl('ADMIN', host)).toBe('/admin');
        expect(getCrossModuleUrl('WORKFLOW', host)).toBe('/dashboard');
      }
      expect(getCrossModuleUrl('ADMIN')).toBe('/admin');
      expect(getCrossModuleUrl('WORKFLOW')).toBe('/dashboard');
    });
  });

  describe('isLocalEnvironment detection helper', () => {
    it('identifies local development hosts correctly', () => {
      expect(isLocalEnvironment('localhost')).toBe(true);
      expect(isLocalEnvironment('127.0.0.1')).toBe(true);
      expect(isLocalEnvironment('dev-machine.local')).toBe(true);
    });

    it('identifies production hosts as not local', () => {
      expect(isLocalEnvironment('workflow.gocompliances.com', 'production')).toBe(false);
      expect(isLocalEnvironment('admin.gocompliances.com', 'production')).toBe(false);
    });
  });
});

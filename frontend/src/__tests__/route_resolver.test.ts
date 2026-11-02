import { describe, it, expect } from 'vitest';
import {
  resolveActiveModule,
  isLocalEnvironment,
  getCrossModuleUrl,
} from '../utils/routeResolver';

describe('Centralized Route Resolver (resolveActiveModule)', () => {
  describe('Mandatory Specification Test Scenarios', () => {
    it('1. Localhost with /admin/tasks strictly loads ADMIN with basePath /admin', () => {
      const res = resolveActiveModule('localhost', '/admin/tasks');
      expect(res.module).toBe('ADMIN');
      expect(res.basePath).toBe('/admin');
    });

    it('2. Localhost with /dashboard strictly loads WORKFLOW with basePath /', () => {
      const res = resolveActiveModule('localhost', '/dashboard');
      expect(res.module).toBe('WORKFLOW');
      expect(res.basePath).toBe('/');
    });

    it('3. Production admin.gocompliances.com with / strictly loads ADMIN with basePath /', () => {
      const res = resolveActiveModule('admin.gocompliances.com', '/');
      expect(res.module).toBe('ADMIN');
      expect(res.basePath).toBe('/');
    });

    it('4. Production workflow.gocompliances.com with / strictly loads WORKFLOW with basePath /', () => {
      const res = resolveActiveModule('workflow.gocompliances.com', '/');
      expect(res.module).toBe('WORKFLOW');
      expect(res.basePath).toBe('/');
    });
  });

  describe('Localhost Edge Cases', () => {
    it('handles 127.0.0.1 for local admin and workflow routing', () => {
      expect(resolveActiveModule('127.0.0.1', '/admin/employees')).toEqual({
        module: 'ADMIN',
        basePath: '/admin',
      });
      expect(resolveActiveModule('127.0.0.1', '/sales/register')).toEqual({
        module: 'WORKFLOW',
        basePath: '/',
      });
    });

    it('handles .local domain (e.g. MacBook.local) for local routing', () => {
      expect(resolveActiveModule('macbook.local', '/admin')).toEqual({
        module: 'ADMIN',
        basePath: '/admin',
      });
      expect(resolveActiveModule('macbook.local', '/operations/tasks')).toEqual({
        module: 'WORKFLOW',
        basePath: '/',
      });
    });

    it('handles localhost with port (e.g. localhost:5173)', () => {
      expect(resolveActiveModule('localhost:5173', '/admin/companies')).toEqual({
        module: 'ADMIN',
        basePath: '/admin',
      });
      expect(resolveActiveModule('localhost:5173', '/dashboard')).toEqual({
        module: 'WORKFLOW',
        basePath: '/',
      });
    });
  });

  describe('Production Subdomain Routing Scenarios', () => {
    it('admin.gocompliances.com routes all nested admin pages to ADMIN with basePath /', () => {
      expect(resolveActiveModule('admin.gocompliances.com', '/employees')).toEqual({
        module: 'ADMIN',
        basePath: '/',
      });
      expect(resolveActiveModule('admin.gocompliances.com', '/companies')).toEqual({
        module: 'ADMIN',
        basePath: '/',
      });
      expect(resolveActiveModule('admin.gocompliances.com', '/admin/employees')).toEqual({
        module: 'ADMIN',
        basePath: '/',
      });
    });

    it('workflow.gocompliances.com routes all CRM pages to WORKFLOW with basePath /', () => {
      expect(resolveActiveModule('workflow.gocompliances.com', '/sales/orders')).toEqual({
        module: 'WORKFLOW',
        basePath: '/',
      });
      expect(resolveActiveModule('workflow.gocompliances.com', '/operations/dashboard')).toEqual({
        module: 'WORKFLOW',
        basePath: '/',
      });
      expect(resolveActiveModule('workflow.gocompliances.com', '/accounts/entries')).toEqual({
        module: 'WORKFLOW',
        basePath: '/',
      });
    });

    it('case-insensitivity of production subdomains', () => {
      expect(resolveActiveModule('ADMIN.gocompliances.com', '/')).toEqual({
        module: 'ADMIN',
        basePath: '/',
      });
      expect(resolveActiveModule('WORKFLOW.gocompliances.com', '/')).toEqual({
        module: 'WORKFLOW',
        basePath: '/',
      });
    });
  });

  describe('Cross-Module Transition Helper (getCrossModuleUrl)', () => {
    it('returns relative routes on localhost', () => {
      expect(getCrossModuleUrl('ADMIN', 'localhost')).toBe('/admin');
      expect(getCrossModuleUrl('WORKFLOW', 'localhost')).toBe('/dashboard');
    });

    it('returns absolute production URLs on production domains', () => {
      expect(getCrossModuleUrl('ADMIN', 'workflow.gocompliances.com')).toBe(
        'https://admin.gocompliances.com'
      );
      expect(getCrossModuleUrl('WORKFLOW', 'admin.gocompliances.com')).toBe(
        'https://workflow.gocompliances.com/dashboard'
      );
    });
  });

  describe('isLocalEnvironment detection helper', () => {
    it('identifies local development hosts correctly', () => {
      expect(isLocalEnvironment('localhost')).toBe(true);
      expect(isLocalEnvironment('127.0.0.1')).toBe(true);
      expect(isLocalEnvironment('dev-machine.local')).toBe(true);
    });

    it('identifies production subdomains as not local', () => {
      expect(isLocalEnvironment('admin.gocompliances.com')).toBe(false);
      expect(isLocalEnvironment('workflow.gocompliances.com')).toBe(false);
    });
  });
});


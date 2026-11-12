/**
 * Centralized, deterministic routing resolver for GoCompliance CRM.
 *
 * Strategy (identical on localhost and production — single domain, path-based):
 *   - /admin/*  -> Admin Panel (basePath: '/admin')
 *   - /*        -> Workflow / CRM Panel (basePath: '/')
 *
 * There is no separate admin subdomain: the Admin panel always lives under /admin on the
 * same origin, so the login session is shared between the main dashboard and Admin.
 */

export type AppModule = 'ADMIN' | 'WORKFLOW';

export interface RouteResolution {
  module: AppModule;
  basePath: string;
}

/**
 * Checks if the given hostname and/or environment corresponds to local development.
 *
 * Priority:
 * 1. Standard localhost / 127.0.0.1 / *.local hostnames are always treated as local.
 * 2. Fallback checks NODE_ENV or Vite mode for custom local hostnames.
 */
export function isLocalEnvironment(hostname: string, envNodeEnv?: string): boolean {
  const normalizedHost = (hostname || '').toLowerCase().trim();

  // Strip port if present (e.g. 'localhost:5173' -> 'localhost')
  const hostWithoutPort = normalizedHost.split(':')[0];

  if (
    hostWithoutPort === 'localhost' ||
    hostWithoutPort === '127.0.0.1' ||
    hostWithoutPort.endsWith('.local')
  ) {
    return true;
  }

  const nodeEnv =
    envNodeEnv ??
    (typeof process !== 'undefined' ? process.env?.NODE_ENV : undefined) ??
    (typeof import.meta !== 'undefined' && import.meta.env?.MODE ? import.meta.env.MODE : undefined);

  return nodeEnv === 'development';
}

/**
 * Resolves the active module and base path from the URL path (same on every host).
 *
 * @param _hostname Kept for call-site compatibility; routing no longer depends on the host.
 * @param pathname The window.location.pathname or test pathname
 */
export function resolveActiveModule(
  _hostname: string,
  pathname: string,
  _envNodeEnv?: string
): RouteResolution {
  if (pathname.startsWith('/admin')) {
    return { module: 'ADMIN', basePath: '/admin' };
  }
  return { module: 'WORKFLOW', basePath: '/' };
}

/**
 * Same-origin route used when moving between the main dashboard and the Admin panel
 * (e.g. clicking the Admin card, or the logo / Dashboard link inside Admin).
 */
export function getCrossModuleUrl(targetModule: AppModule, _currentHostname?: string): string {
  return targetModule === 'ADMIN' ? '/admin' : '/dashboard';
}

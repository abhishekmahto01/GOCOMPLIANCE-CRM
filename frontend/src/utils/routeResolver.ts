/**
 * Centralized, deterministic routing resolver for GoCompliance CRM.
 * 
 * Strategy:
 * - Localhost / Development: Distinguish between Admin and Workflow using explicit URL paths.
 *   - http://localhost:<PORT>/admin/* -> Strictly loads Admin Panel (basePath: '/admin')
 *   - http://localhost:<PORT>/*       -> Strictly loads Workflow / CRM Panel (basePath: '/')
 * - Production / Deployed: Distinguish between Admin and Workflow using subdomains.
 *   - admin.gocompliances.com         -> Strictly loads Admin Panel (basePath: '/')
 *   - workflow.gocompliances.com      -> Strictly loads Workflow / CRM Panel (basePath: '/')
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
 * 2. Explicit production/deployed subdomains (starting with 'admin.' or 'workflow.')
 *    are NEVER treated as local, even during test execution or development builds.
 * 3. Fallback checks NODE_ENV or Vite mode for custom local hostnames.
 */
export function isLocalEnvironment(hostname: string, envNodeEnv?: string): boolean {
  const normalizedHost = (hostname || '').toLowerCase().trim();

  // Strip port if present (e.g. 'localhost:5173' -> 'localhost')
  const hostWithoutPort = normalizedHost.split(':')[0];

  // 1. Explicit local hosts
  if (
    hostWithoutPort === 'localhost' ||
    hostWithoutPort === '127.0.0.1' ||
    hostWithoutPort.endsWith('.local')
  ) {
    return true;
  }

  // 2. Explicit production subdomains
  if (
    hostWithoutPort.startsWith('admin.') ||
    hostWithoutPort.startsWith('workflow.')
  ) {
    return false;
  }

  // 3. Environment mode check for local networks/IPs
  const nodeEnv =
    envNodeEnv ??
    (typeof process !== 'undefined' ? process.env?.NODE_ENV : undefined) ??
    (typeof import.meta !== 'undefined' && import.meta.env?.MODE ? import.meta.env.MODE : undefined);

  return nodeEnv === 'development';
}

/**
 * Deterministically resolves the active module and base path.
 * 
 * @param hostname The window.location.hostname or test hostname
 * @param pathname The window.location.pathname or test pathname
 * @param envNodeEnv Optional explicit NODE_ENV for testing
 */
export function resolveActiveModule(
  hostname: string,
  pathname: string,
  envNodeEnv?: string
): RouteResolution {
  const isLocal = isLocalEnvironment(hostname, envNodeEnv);

  if (isLocal) {
    if (pathname.startsWith('/admin')) {
      return { module: 'ADMIN', basePath: '/admin' };
    }
    return { module: 'WORKFLOW', basePath: '/' };
  }

  // Production / Deployed environment
  const normalizedHost = (hostname || '').toLowerCase().trim();
  const hostWithoutPort = normalizedHost.split(':')[0];

  if (hostWithoutPort.startsWith('admin.')) {
    return { module: 'ADMIN', basePath: '/' };
  }
  return { module: 'WORKFLOW', basePath: '/' };
}

/**
 * Helper to obtain the correct URL when transitioning across modules
 * (e.g., clicking Administration from Workflow Dashboard, or clicking Dashboard from Admin).
 */
export function getCrossModuleUrl(
  targetModule: AppModule,
  currentHostname: string = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
): string {
  const isLocal = isLocalEnvironment(currentHostname);

  if (isLocal) {
    return targetModule === 'ADMIN' ? '/admin' : '/dashboard';
  }

  if (targetModule === 'ADMIN') {
    return 'https://admin.gocompliances.com';
  }
  return 'https://workflow.gocompliances.com/dashboard';
}


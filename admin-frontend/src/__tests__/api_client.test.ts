import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  apiClient,
  extractErrorMessage,
  ACCESS_TOKEN_KEY,
  REFRESH_TOKEN_KEY,
} from '../api/client';

describe('API Client & Error Handling', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('attaches Bearer token in request headers when available in localStorage', async () => {
    localStorage.setItem(ACCESS_TOKEN_KEY, 'sample_bearer_token');

    // Test the request interceptor handler directly
    const anyClient = apiClient as unknown as {
      interceptors: {
        request: {
          handlers: Array<{
            fulfilled: (config: { headers: Record<string, string> }) => {
              headers: Record<string, string>;
            };
          }>;
        };
      };
    };
    const requestHandler = anyClient.interceptors.request.handlers[0].fulfilled;
    const config = { headers: {} };
    const modifiedConfig = requestHandler(config);

    expect(modifiedConfig.headers.Authorization).toBe('Bearer sample_bearer_token');
  });

  it('clears session on 401 response error', async () => {
    localStorage.setItem(ACCESS_TOKEN_KEY, 'sample_bearer_token');
    localStorage.setItem(REFRESH_TOKEN_KEY, 'sample_refresh_token');

    const anyClient = apiClient as unknown as {
      interceptors: {
        response: {
          handlers: Array<{
            rejected: (error: unknown) => Promise<unknown>;
          }>;
        };
      };
    };
    const errorHandler = anyClient.interceptors.response.handlers[0].rejected;

    const mock401Error = {
      response: {
        status: 401,
        data: { detail: 'Token expired' },
      },
    };

    try {
      await errorHandler(mock401Error);
    } catch (e) {
      expect(e).toBe(mock401Error);
    }

    expect(localStorage.getItem(ACCESS_TOKEN_KEY)).toBeNull();
    expect(localStorage.getItem(REFRESH_TOKEN_KEY)).toBeNull();
  });

  it('extracts detail string from backend error response', () => {
    const errorObj = {
      isAxiosError: true,
      response: {
        data: {
          detail: 'Access denied outside company scope.',
        },
      },
    };
    expect(extractErrorMessage(errorObj)).toBe('Access denied outside company scope.');
  });
});

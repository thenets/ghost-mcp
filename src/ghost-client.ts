/**
 * Ghost API Client
 *
 * Unified client for both Ghost Content API (read-only) and Admin API (read/write).
 * Handles authentication, request/response processing, and error handling.
 */

// TODO: Phase 1 - Implement this client
// - Content API authentication (query parameter)
// - Admin API JWT authentication
// - Request/response handling
// - Error mapping
// - Retry logic

export interface GhostClientConfig {
  ghostUrl: string;
  contentApiKey?: string;
  adminApiKey?: string;
  apiVersion: string;
}

export interface GhostApiResponse<T> {
  data: T;
  meta?: {
    pagination?: {
      page: number;
      limit: number;
      pages: number;
      total: number;
      next?: number;
      prev?: number;
    };
  };
}

export class GhostClient {
  constructor(config: GhostClientConfig) {
    // TODO: Phase 1 - Initialize client with configuration
  }

  // TODO: Phase 1 - Content API methods
  async contentGet<T>(endpoint: string, params?: Record<string, unknown>): Promise<GhostApiResponse<T>> {
    throw new Error('Not implemented - Phase 1');
  }

  // TODO: Phase 1 - Admin API methods
  async adminGet<T>(endpoint: string, params?: Record<string, unknown>): Promise<GhostApiResponse<T>> {
    throw new Error('Not implemented - Phase 1');
  }

  async adminPost<T>(endpoint: string, data: unknown): Promise<GhostApiResponse<T>> {
    throw new Error('Not implemented - Phase 1');
  }

  async adminPut<T>(endpoint: string, data: unknown): Promise<GhostApiResponse<T>> {
    throw new Error('Not implemented - Phase 1');
  }

  async adminDelete<T>(endpoint: string): Promise<GhostApiResponse<T>> {
    throw new Error('Not implemented - Phase 1');
  }
}
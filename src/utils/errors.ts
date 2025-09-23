/**
 * Error Handling Utilities
 *
 * Error classes, mapping functions, and logging utilities.
 * Implements error handling strategy from contracts/error-responses.md
 */

import { v4 as uuidv4 } from 'uuid';
import { GhostApiError, GhostApiErrorResponse } from '../types/ghost.js';
import { MCPError } from '../types/mcp.js';

// TODO: Phase 1 - Implement comprehensive error handling
// Based on contracts/error-responses.md

export enum ErrorCategory {
  NETWORK = 'NETWORK',
  AUTHENTICATION = 'AUTHENTICATION',
  GHOST_API = 'GHOST_API',
  MCP_PROTOCOL = 'MCP_PROTOCOL',
  FILE_UPLOAD = 'FILE_UPLOAD',
  VALIDATION = 'VALIDATION',
}

export class GhostMCPError extends Error {
  public readonly id: string;
  public readonly category: ErrorCategory;
  public readonly code?: string;
  public readonly context?: string;
  public readonly requestId?: string;

  constructor(
    message: string,
    category: ErrorCategory,
    code?: string,
    context?: string,
    requestId?: string
  ) {
    super(message);
    this.name = 'GhostMCPError';
    this.id = uuidv4();
    this.category = category;
    this.code = code;
    this.context = context;
    this.requestId = requestId;
  }
}

export class NetworkError extends GhostMCPError {
  constructor(message: string, context?: string, requestId?: string) {
    super(message, ErrorCategory.NETWORK, 'NETWORK_ERROR', context, requestId);
    this.name = 'NetworkError';
  }
}

export class AuthenticationError extends GhostMCPError {
  constructor(message: string, context?: string, requestId?: string) {
    super(message, ErrorCategory.AUTHENTICATION, 'AUTH_ERROR', context, requestId);
    this.name = 'AuthenticationError';
  }
}

export class GhostApiError extends GhostMCPError {
  constructor(message: string, code?: string, context?: string, requestId?: string) {
    super(message, ErrorCategory.GHOST_API, code, context, requestId);
    this.name = 'GhostApiError';
  }
}

export class ValidationError extends GhostMCPError {
  constructor(message: string, context?: string, requestId?: string) {
    super(message, ErrorCategory.VALIDATION, 'VALIDATION_ERROR', context, requestId);
    this.name = 'ValidationError';
  }
}

// Error mapping functions
export function mapGhostErrorToMCP(ghostError: GhostApiErrorResponse, requestId?: string): MCPError {
  // TODO: Phase 1 - Implement Ghost API error to MCP error mapping
  const firstError = ghostError.errors[0];
  return {
    code: -32603, // Internal error
    message: firstError?.message || 'Unknown Ghost API error',
    data: {
      type: firstError?.type,
      context: firstError?.context,
      requestId,
    },
  };
}

export function createMCPError(error: Error, requestId?: string): MCPError {
  // TODO: Phase 1 - Create MCP error from any error type
  if (error instanceof GhostMCPError) {
    return {
      code: -32603,
      message: error.message,
      data: {
        category: error.category,
        code: error.code,
        context: error.context,
        requestId: error.requestId || requestId,
      },
    };
  }

  return {
    code: -32603,
    message: error.message || 'Internal server error',
    data: { requestId },
  };
}

// Retry logic utilities
export interface RetryConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  exponentialBase: number;
}

export const defaultRetryConfig: RetryConfig = {
  maxRetries: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  exponentialBase: 2,
};

export async function withRetry<T>(
  operation: () => Promise<T>,
  config: Partial<RetryConfig> = {},
  requestId?: string
): Promise<T> {
  // TODO: Phase 1 - Implement retry logic with exponential backoff
  const finalConfig = { ...defaultRetryConfig, ...config };

  for (let attempt = 0; attempt <= finalConfig.maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (attempt === finalConfig.maxRetries) {
        throw error;
      }

      // Calculate delay with exponential backoff
      const delay = Math.min(
        finalConfig.baseDelay * Math.pow(finalConfig.exponentialBase, attempt),
        finalConfig.maxDelay
      );

      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw new Error('Retry logic failed unexpectedly');
}
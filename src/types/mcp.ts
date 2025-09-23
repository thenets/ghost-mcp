/**
 * MCP-Specific Types
 *
 * TypeScript interfaces for MCP tool definitions and responses.
 */

// TODO: Phase 1 - Define MCP-specific types

export interface MCPToolParameter {
  type: string;
  description?: string;
  required?: boolean;
  enum?: string[];
  properties?: Record<string, MCPToolParameter>;
}

export interface MCPToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: 'object';
    properties: Record<string, MCPToolParameter>;
    required?: string[];
  };
}

export interface MCPToolResponse {
  content: Array<{
    type: 'text' | 'image' | 'resource';
    text?: string;
    data?: string;
    url?: string;
    mimeType?: string;
  }>;
  isError?: boolean;
}

export interface MCPToolRequest {
  name: string;
  arguments: Record<string, unknown>;
}

// MCP Error types
export interface MCPError {
  code: number;
  message: string;
  data?: unknown;
}

// Configuration types
export interface MCPServerConfig {
  ghost: {
    url: string;
    contentApiKey?: string;
    adminApiKey?: string;
    version: string;
    mode: 'readonly' | 'readwrite' | 'auto';
  };
  logging: {
    level: 'debug' | 'info' | 'warn' | 'error';
    structured: boolean;
  };
}
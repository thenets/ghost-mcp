"""MCP-specific type definitions."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class MCPToolParameter(BaseModel):
    """MCP tool parameter definition."""
    type: str
    description: Optional[str] = None
    required: bool = False
    enum: Optional[List[str]] = None
    properties: Optional[Dict[str, "MCPToolParameter"]] = None


class MCPToolDefinition(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPContent(BaseModel):
    """MCP response content."""
    type: str
    text: Optional[str] = None
    data: Optional[str] = None
    url: Optional[str] = None
    mimeType: Optional[str] = None


class MCPToolResponse(BaseModel):
    """MCP tool response."""
    content: List[MCPContent]
    isError: bool = False


class MCPToolRequest(BaseModel):
    """MCP tool request."""
    name: str
    arguments: Dict[str, Any]


class MCPError(BaseModel):
    """MCP error response."""
    code: int
    message: str
    data: Optional[Any] = None
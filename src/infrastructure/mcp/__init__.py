"""MCP Server infrastructure for Knowledge-as-Code."""

from src.infrastructure.mcp.knowledge_server import create_server, ReleaseNotesMCPServer

__all__ = [
    "create_server",
    "ReleaseNotesMCPServer",
]

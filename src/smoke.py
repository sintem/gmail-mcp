# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""Smoke test tools for LIAM Gmail MCP (doitliam.com)."""

from mcp.types import TextContent, Tool

from dedalus_mcp.types import ToolAnnotations

from dedalus_mcp import tool


@tool(
    description="Smoke test tool that echoes input (LIAM Gmail MCP)",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def smoke_echo(message: str) -> list[TextContent]:
    """Echo a message back to verify server is working."""
    return [TextContent(type="text", text=f"Echo: {message}")]


@tool(
    description="Smoke test tool that returns server info (LIAM Gmail MCP)",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def smoke_info() -> list[TextContent]:
    """Return basic server information."""
    return [
        TextContent(
            type="text",
            text="LIAM Gmail MCP server v0.0.1 - Provided by LIAM (doitliam.com)",
        )
    ]


smoke_tools: list[Tool] = [smoke_echo, smoke_info]

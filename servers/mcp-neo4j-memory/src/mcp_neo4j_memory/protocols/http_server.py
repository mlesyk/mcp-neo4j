"""
HTTP protocol implementation for MCP Neo4j Memory server.
"""

import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ..core import Neo4jMemory, get_mcp_tools, execute_tool_http

# Set up logging
logger = logging.getLogger('mcp_neo4j_memory.protocols.http')


class HTTPServer:
    """HTTP server for MCP Neo4j Memory."""

    def __init__(self, memory: Neo4jMemory):
        self.memory = memory
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(
            title="MCP Neo4j Memory Server",
            description="HTTP API for Neo4j knowledge graph memory",
            version="1.1"
        )

        # Add CORS middleware - required for cross-origin HTTP requests
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow requests from any origin
            allow_credentials=True,
            allow_methods=["GET", "POST"],  # HTTP API only needs GET and POST
            allow_headers=["*"],
        )

        # Register routes
        self._register_routes(app)

        return app

    def _register_routes(self, app: FastAPI):
        """Register HTTP routes."""

        @app.get("/")
        async def root():
            """Root endpoint with server info."""
            return {
                "service": "MCP Neo4j Memory Server",
                "version": "1.1",
                "protocol": "http",
                "endpoints": {
                    "health": "/health",
                    "tools": "/tools",
                    "execute": "/execute"
                }
            }

        @app.get("/health")
        async def health_check():
          """Lightweight health check endpoint."""
          try:
            # Simple connection test - just verify driver connectivity
            # This uses a minimal query that doesn't load data
            self.memory.neo4j_driver.execute_query("RETURN 1")
            return {"status": "healthy", "neo4j": "connected"}
          except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=503, detail="Neo4j unavailable")

        @app.get("/tools")
        async def list_tools():
            """List available MCP tools."""
            tools = get_mcp_tools()
            return {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools
                ]
            }

        @app.post("/execute")
        async def execute_tool_endpoint(request: Request):
            """Execute a tool via HTTP POST."""
            try:
                data = await request.json()
                tool_name = data.get("tool")
                arguments = data.get("arguments", {})

                if not tool_name:
                    raise HTTPException(status_code=400, detail="Tool name is required")

                result = await execute_tool_http(self.memory, tool_name, arguments)
                return result

            except Exception as e:
                logger.error(f"Error executing tool: {e}")
                return {"success": False, "error": str(e)}


async def run_http_server(memory: Neo4jMemory, host: str = "0.0.0.0", port: int = 3001):
    """
    Run the HTTP server.

    Args:
        memory: Neo4jMemory instance
        host: Host to bind to
        port: Port to bind to
    """
    logger.info(f"Starting HTTP server on {host}:{port}")

    http_server = HTTPServer(memory)
    config = uvicorn.Config(http_server.app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

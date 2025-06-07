#!/usr/bin/env python3
"""
Multi-protocol MCP server supporting stdio, SSE, and HTTP endpoints.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from . import server as mcp_server
from .server import Neo4jMemory, Entity, Relation, ObservationAddition, ObservationDeletion
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiProtocolServer:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str, neo4j_database: str):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.neo4j_database = neo4j_database
        self.memory = None
        self.mcp_server = None
        
    async def initialize(self):
        """Initialize the Neo4j connection and MCP server."""
        from neo4j import GraphDatabase
        
        # Connect to Neo4j
        neo4j_driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password),
            database=self.neo4j_database
        )
        
        # Verify connection
        try:
            neo4j_driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.neo4j_uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
            
        self.memory = Neo4jMemory(neo4j_driver)
        self.mcp_server = Server("mcp-neo4j-memory")
        
        # Register MCP handlers (same as your original server.py)
        self._register_mcp_handlers()
        
    def _register_mcp_handlers(self):
        """Register MCP tool handlers."""
        
        @self.mcp_server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            # Same tools as in your original server.py
            return [
                types.Tool(
                    name="create_entities",
                    description="Create multiple new entities in the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entities": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "The name of the entity"},
                                        "type": {"type": "string", "description": "The type of the entity"},
                                        "observations": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "An array of observation contents associated with the entity"
                                        },
                                    },
                                    "required": ["name", "type", "observations"],
                                },
                            },
                        },
                        "required": ["entities"],
                    },
                ),
                types.Tool(
                    name="create_relations",
                    description="Create multiple new relations between entities in the knowledge graph. Relations should be in active voice",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "relations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "source": {"type": "string", "description": "The name of the entity where the relation starts"},
                                        "target": {"type": "string", "description": "The name of the entity where the relation ends"},
                                        "relationType": {"type": "string", "description": "The type of the relation"},
                                    },
                                    "required": ["source", "target", "relationType"],
                                },
                            },
                        },
                        "required": ["relations"],
                    },
                ),
                types.Tool(
                    name="add_observations",
                    description="Add new observations to existing entities in the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "observations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "entityName": {"type": "string", "description": "The name of the entity to add the observations to"},
                                        "contents": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "An array of observation contents to add"
                                        },
                                    },
                                    "required": ["entityName", "contents"],
                                },
                            },
                        },
                        "required": ["observations"],
                    },
                ),
                types.Tool(
                    name="delete_entities",
                    description="Delete multiple entities and their associated relations from the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entityNames": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "An array of entity names to delete"
                            },
                        },
                        "required": ["entityNames"],
                    },
                ),
                types.Tool(
                    name="delete_observations",
                    description="Delete specific observations from entities in the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deletions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "entityName": {"type": "string", "description": "The name of the entity containing the observations"},
                                        "observations": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "An array of observations to delete"
                                        },
                                    },
                                    "required": ["entityName", "observations"],
                                },
                            },
                        },
                        "required": ["deletions"],
                    },
                ),
                types.Tool(
                    name="delete_relations",
                    description="Delete multiple relations from the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "relations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "source": {"type": "string", "description": "The name of the entity where the relation starts"},
                                        "target": {"type": "string", "description": "The name of the entity where the relation ends"},
                                        "relationType": {"type": "string", "description": "The type of the relation"},
                                    },
                                    "required": ["source", "target", "relationType"],
                                },
                                "description": "An array of relations to delete"
                            },
                        },
                        "required": ["relations"],
                    },
                ),
                types.Tool(
                    name="read_graph",
                    description="Read the entire knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                types.Tool(
                    name="search_nodes",
                    description="Search for nodes in the knowledge graph based on a query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query to match against entity names, types, and observation content"},
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="find_nodes",
                    description="Find specific nodes in the knowledge graph by their names",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "names": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "An array of entity names to retrieve",
                            },
                        },
                        "required": ["names"],
                    },
                ),
            ]

        @self.mcp_server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any] | None
        ) -> List[types.TextContent | types.ImageContent]:
            try:
                if name == "read_graph":
                    result = await self.memory.read_graph()
                    return [types.TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))]

                if not arguments:
                    raise ValueError(f"No arguments provided for tool: {name}")

                if name == "create_entities":
                    entities = [Entity(**entity) for entity in arguments.get("entities", [])]
                    result = await self.memory.create_entities(entities)
                    return [types.TextContent(type="text", text=json.dumps([e.model_dump() for e in result], indent=2))]

                elif name == "create_relations":
                    relations = [Relation(**relation) for relation in arguments.get("relations", [])]
                    result = await self.memory.create_relations(relations)
                    return [types.TextContent(type="text", text=json.dumps([r.model_dump() for r in result], indent=2))]

                elif name == "add_observations":
                    observations = [ObservationAddition(**obs) for obs in arguments.get("observations", [])]
                    result = await self.memory.add_observations(observations)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "delete_entities":
                    await self.memory.delete_entities(arguments.get("entityNames", []))
                    return [types.TextContent(type="text", text="Entities deleted successfully")]

                elif name == "delete_observations":
                    deletions = [ObservationDeletion(**deletion) for deletion in arguments.get("deletions", [])]
                    await self.memory.delete_observations(deletions)
                    return [types.TextContent(type="text", text="Observations deleted successfully")]

                elif name == "delete_relations":
                    relations = [Relation(**relation) for relation in arguments.get("relations", [])]
                    await self.memory.delete_relations(relations)
                    return [types.TextContent(type="text", text="Relations deleted successfully")]

                elif name == "search_nodes":
                    result = await self.memory.search_nodes(arguments.get("query", ""))
                    return [types.TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))]

                elif name == "find_nodes":
                    result = await self.memory.find_nodes(arguments.get("names", []))
                    return [types.TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))]

                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Error handling tool call: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def run_stdio(self):
        """Run the server in stdio mode."""
        logger.info("Starting MCP Neo4j Memory server in stdio mode")
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.mcp_server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-neo4j-memory",
                    server_version="1.1",
                    capabilities=self.mcp_server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a tool and return the result as a dictionary."""
        try:
            if tool_name == "read_graph":
                result = await self.memory.read_graph()
                return {"success": True, "data": result.model_dump()}

            if not arguments:
                raise ValueError(f"No arguments provided for tool: {tool_name}")

            if tool_name == "create_entities":
                entities = [Entity(**entity) for entity in arguments.get("entities", [])]
                result = await self.memory.create_entities(entities)
                return {"success": True, "data": [e.model_dump() for e in result]}

            elif tool_name == "create_relations":
                relations = [Relation(**relation) for relation in arguments.get("relations", [])]
                result = await self.memory.create_relations(relations)
                return {"success": True, "data": [r.model_dump() for r in result]}

            elif tool_name == "add_observations":
                observations = [ObservationAddition(**obs) for obs in arguments.get("observations", [])]
                result = await self.memory.add_observations(observations)
                return {"success": True, "data": result}

            elif tool_name == "delete_entities":
                await self.memory.delete_entities(arguments.get("entityNames", []))
                return {"success": True, "message": "Entities deleted successfully"}

            elif tool_name == "delete_observations":
                deletions = [ObservationDeletion(**deletion) for deletion in arguments.get("deletions", [])]
                await self.memory.delete_observations(deletions)
                return {"success": True, "message": "Observations deleted successfully"}

            elif tool_name == "delete_relations":
                relations = [Relation(**relation) for relation in arguments.get("relations", [])]
                await self.memory.delete_relations(relations)
                return {"success": True, "message": "Relations deleted successfully"}

            elif tool_name == "search_nodes":
                result = await self.memory.search_nodes(arguments.get("query", ""))
                return {"success": True, "data": result.model_dump()}

            elif tool_name == "find_nodes":
                result = await self.memory.find_nodes(arguments.get("names", []))
                return {"success": True, "data": result.model_dump()}

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            return {"success": False, "error": str(e)}

# Global server instance
multi_server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage server lifecycle."""
    global multi_server
    
    # Get configuration from environment
    neo4j_uri = os.getenv("NEO4J_URL", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")
    
    try:
        logger.info("Starting MCP Neo4j Memory server...")
        multi_server = MultiProtocolServer(neo4j_uri, neo4j_user, neo4j_password, neo4j_database)
        await multi_server.initialize()
        logger.info("MCP Neo4j Memory server initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
    finally:
        logger.info("Shutting down MCP Neo4j Memory server...")

# FastAPI app for HTTP/SSE endpoints
app = FastAPI(
    title="MCP Neo4j Memory Server",
    description="Multi-protocol MCP server for Neo4j knowledge graph memory",
    version="0.1.4",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "service": "MCP Neo4j Memory Server",
        "version": "0.1.4",
        "protocols": ["stdio", "sse", "http"],
        "endpoints": {
            "health": "/health",
            "sse": "/sse", 
            "tools": "/tools",
            "execute": "/execute"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global multi_server
    try:
        if multi_server and multi_server.memory:
            # Test Neo4j connection
            await multi_server.memory.read_graph()
            return {"status": "healthy", "neo4j": "connected"}
        else:
            return {"status": "initializing"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

@app.get("/tools")
async def list_tools():
    """List available MCP tools."""
    global multi_server
    if not multi_server:
        raise HTTPException(status_code=503, detail="Server not initialized")
    
    tools = await multi_server.mcp_server._tool_handlers["list_tools"]()
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
async def execute_tool(request: Request):
    """Execute a tool via HTTP POST."""
    global multi_server
    if not multi_server:
        raise HTTPException(status_code=503, detail="Server not initialized")
    
    try:
        data = await request.json()
        tool_name = data.get("tool")
        arguments = data.get("arguments", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name is required")
        
        result = await multi_server.execute_tool(tool_name, arguments)
        return result
        
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        return {"success": False, "error": str(e)}

@app.get("/sse")
async def sse_endpoint(request: Request):
    """Server-Sent Events endpoint for LibreChat integration."""
    
    async def event_generator():
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connection', 'status': 'connected', 'server': 'mcp-neo4j-memory'})}\n\n"
            
            # Send available tools
            if multi_server:
                tools = await multi_server.mcp_server._tool_handlers["list_tools"]()
                tools_data = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools
                ]
                yield f"data: {json.dumps({'type': 'tools', 'tools': tools_data})}\n\n"
            
            # Keep connection alive with heartbeat
            while True:
                await asyncio.sleep(30)
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': asyncio.get_event_loop().time()})}\n\n"
                
        except asyncio.CancelledError:
            logger.info("SSE connection cancelled")
            yield f"data: {json.dumps({'type': 'disconnect', 'reason': 'cancelled'})}\n\n"
            return  # Exit the generator cleanly
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            return  # Exit the generator on error

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )

# Main function for running the server
async def main_multi_protocol(
    neo4j_uri: str, 
    neo4j_user: str, 
    neo4j_password: str, 
    neo4j_database: str, 
    mode: str = "http",
    host: str = "0.0.0.0",
    port: int = 3001
):
    """
    Main function to run the server in different modes.
    
    Args:
        mode: "stdio", "http", or "both"
    """
    
    global multi_server
    multi_server = MultiProtocolServer(neo4j_uri, neo4j_user, neo4j_password, neo4j_database)
    await multi_server.initialize()
    
    if mode == "stdio":
        await multi_server.run_stdio()
    elif mode == "http":
        logger.info(f"Starting HTTP/SSE server on {host}:{port}")
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    elif mode == "both":
        # This would require more complex setup to run both simultaneously
        # For now, we'll default to HTTP mode when "both" is requested
        logger.warning("Both mode not fully implemented, starting HTTP mode")
        logger.info(f"Starting HTTP/SSE server on {host}:{port}")
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    else:
        raise ValueError(f"Invalid mode: {mode}. Use 'stdio', 'http', or 'both'")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-protocol MCP Neo4j Memory Server')
    parser.add_argument('--db-url', 
                       default=os.getenv("NEO4J_URL", "bolt://localhost:7687"),
                       help='Neo4j connection URL')
    parser.add_argument('--username', 
                       default=os.getenv("NEO4J_USERNAME", "neo4j"),
                       help='Neo4j username')
    parser.add_argument('--password', 
                       default=os.getenv("NEO4J_PASSWORD", "password"),
                       help='Neo4j password')
    parser.add_argument("--database",
                        default=os.getenv("NEO4J_DATABASE", "neo4j"),
                        help="Neo4j database name")
    parser.add_argument("--mode",
                        choices=["stdio", "http", "both"],
                        default="http",
                        help="Server mode: stdio, http, or both")
    parser.add_argument("--host",
                        default="0.0.0.0",
                        help="Host to bind HTTP server")
    parser.add_argument("--port",
                        type=int,
                        default=3001,
                        help="Port for HTTP server")
    
    args = parser.parse_args()
    
    asyncio.run(main_multi_protocol(
        args.db_url, 
        args.username, 
        args.password, 
        args.database,
        args.mode,
        args.host,
        args.port
    ))

from . import server
from . import multi_server
import asyncio
import argparse
import os


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description='Neo4j Cypher MCP Server')
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
                        default=os.getenv("MCP_MODE", "stdio"),
                        help="Server mode: stdio (default), http, or both")
    parser.add_argument("--host",
                        default=os.getenv("MCP_SERVER_HOST", "0.0.0.0"),
                        help="Host to bind HTTP server")
    parser.add_argument("--port",
                        type=int,
                        default=int(os.getenv("MCP_SERVER_PORT", "3001")),
                        help="Port for HTTP server")
    
    args = parser.parse_args()
    
    if args.mode == "stdio":
        # Use original stdio-only server
        asyncio.run(server.main(args.db_url, args.username, args.password, args.database))
    else:
        # Use multi-protocol server
        asyncio.run(multi_server.main_multi_protocol(
            args.db_url, 
            args.username, 
            args.password, 
            args.database,
            args.mode,
            args.host,
            args.port
        ))


# Optionally expose other important items at package level
__all__ = ["main", "server", "multi_server"]

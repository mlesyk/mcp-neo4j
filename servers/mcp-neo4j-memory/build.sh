#!/bin/bash
set -e

echo "Building MCP Neo4j Memory Docker image..."

# Build the image
docker build -t mcp-neo4j-memory:latest .

# Tag for different versions
docker tag mcp-neo4j-memory:latest mcp-neo4j-memory:0.1.4

echo "Build complete!"
echo "Available images:"
docker images | grep mcp-neo4j-memory

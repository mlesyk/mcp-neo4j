#!/bin/bash
set -e

# Default environment variables
NEO4J_PASSWORD=${NEO4J_PASSWORD:-"your_password_here"}
MONGO_PASSWORD=${MONGO_PASSWORD:-"your_mongo_password"}

# Export for docker-compose
export NEO4J_PASSWORD
export MONGO_PASSWORD

echo "Starting MCP Neo4j Memory server with dependencies..."

# Check if we want development or production
if [ "$1" = "dev" ]; then
    echo "Starting development environment..."
    docker-compose up --build
elif [ "$1" = "prod" ]; then
    echo "Starting production environment with LibreChat..."
    docker-compose -f docker-compose.prod.yml up --build
else
    echo "Usage: $0 [dev|prod]"
    echo "  dev  - Start development environment (MCP + Neo4j only)"
    echo "  prod - Start production environment (MCP + Neo4j + LibreChat)"
    exit 1
fi

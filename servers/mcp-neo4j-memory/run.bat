@echo off
setlocal enabledelayedexpansion

REM Default environment variables
if "%NEO4J_PASSWORD%"=="" set NEO4J_PASSWORD=your_password_here
if "%MONGO_PASSWORD%"=="" set MONGO_PASSWORD=your_mongo_password

echo Starting MCP Neo4j Memory server with dependencies...

REM Check if we want development or production
if "%1"=="dev" (
    echo Starting development environment...
    docker-compose up --build
) else if "%1"=="prod" (
    echo Starting production environment with LibreChat...
    docker-compose -f docker-compose.prod.yml up --build
) else (
    echo Usage: %0 [dev^|prod]
    echo   dev  - Start development environment (MCP + Neo4j only^)
    echo   prod - Start production environment (MCP + Neo4j + LibreChat^)
    pause
    exit /b 1
)

# Docker Test Environment

This directory contains Docker configurations for running comprehensive tests in isolated containers, including full MCP protocol compliance testing.

## Test Infrastructure

### Core Services
- **`neo4j-test`** - Neo4j latest Docker image for testing
- **`test-runner`** - Main test execution container
- **`unit-tests`** - Unit tests only (no Neo4j dependency)
- **`integration-tests`** - Integration tests with Neo4j
- **`coverage-tests`** - Coverage analysis and reporting

### MCP Compliance Services (NEW)
- **`mcp-sse-server`** - Live SSE server for compliance testing
- **`mcp-http-server`** - Live HTTP server for cross-protocol testing
- **`mcp-compliance-suite`** - Comprehensive MCP protocol validation
- **`sse-compliance-tests`** - SSE protocol specific compliance tests
- **`live-sse-tests`** - Live server integration testing
- **`performance-tests`** - Performance and load testing
- **`test-results-viewer`** - Web interface for test results

### Dockerfiles
- **`Dockerfile_test`** - Test environment with all dependencies
- **`Dockerfile_stdio`** - Production stdio-only server image (default)
- **`Dockerfile_http`** - Production HTTP server image
- **`Dockerfile_sse`** - Production SSE server image

## Docker Compose Configurations

### Main Test Files
- **`docker-compose.test.yml`** - Standard integration testing
- **`docker-compose.mcp-compliance.yml`** - **NEW:** MCP protocol compliance testing
- **`docker-compose.test.override.yml`** - Development overrides

## Quick Start

### Basic Testing
```bash
# Run all tests (Linux/macOS)
./scripts/test.sh

# Run all tests (Windows)
scripts\test.bat
```

### MCP Compliance Testing (NEW)
```bash
# Run comprehensive MCP compliance tests
./scripts/test.sh mcp-compliance

# Run SSE compliance tests specifically
./scripts/test.sh sse-compliance

# Start live test environment with running servers
./scripts/test.sh live
```

## Test Commands

### Standard Tests
| Command | Description | Dependencies |
|---------|-------------|--------------|
| `unit` | Unit tests only | None |
| `integration` | Integration tests | Neo4j |
| `coverage` | Coverage reporting | Neo4j |
| `performance` | Performance tests | Neo4j |

### MCP Compliance Tests (NEW)
| Command | Description | Infrastructure |
|---------|-------------|----------------|
| `mcp-compliance` | **Full MCP protocol validation** | Neo4j + SSE + HTTP servers |
| `sse-compliance` | SSE transport compliance | Neo4j + SSE server |
| `mcp-live` | Live server integration | Neo4j + SSE server |
| `live` | **Interactive test environment** | Neo4j + SSE + HTTP + Web UI |

### Utility Commands
| Command | Description |
|---------|-------------|
| `build` | Build test images |
| `clean` | Clean up containers and results |
| `logs` | Show container logs |
| `help` | Show help and examples |

## MCP Compliance Features

### Protocol Validation
- ✅ **JSON-RPC 2.0 compliance** - Message format validation
- ✅ **SSE transport compliance** - Server-Sent Events specification
- ✅ **Session management** - UUID-based session tracking
- ✅ **Tool execution** - All 10 Neo4j memory tools validation
- ✅ **Error handling** - Proper error codes and messages
- ✅ **Cross-protocol consistency** - HTTP vs SSE data consistency

### Live Integration Testing
- ✅ **Running servers** - Test against actual SSE/HTTP servers
- ✅ **Real-world scenarios** - Connection, initialization, tool execution
- ✅ **Performance testing** - Load and stress testing
- ✅ **Health monitoring** - Service health verification

### Test Results Visualization
- ✅ **Web interface** - http://localhost:8080 for test results
- ✅ **Coverage reports** - Detailed HTML coverage analysis
- ✅ **Live monitoring** - Real-time test execution monitoring

## Usage Examples

### Quick Feedback Loop
```bash
# Fast unit tests during development
./scripts/test.sh unit

# Quick MCP compliance check
./scripts/test.sh sse-compliance
```

### Full Validation
```bash
# Complete test suite before commit
./scripts/test.sh all

# Comprehensive MCP compliance validation
./scripts/test.sh mcp-compliance
```

### Interactive Testing
```bash
# Start live test environment
./scripts/test.sh live

# Then access:
# - SSE Server: http://localhost:3001
# - Neo4j Browser: http://localhost:7474
# - Test Results: http://localhost:8080
```

### CI/CD Pipeline
```bash
# Unit tests (fast, no dependencies)
./scripts/test.sh unit

# Integration tests with Neo4j
./scripts/test.sh integration

# MCP compliance validation
./scripts/test.sh mcp-compliance

# Coverage reporting
./scripts/test.sh coverage
```

## File Structure

```
docker/
├── Dockerfile_test                    # Test container image
├── Dockerfile_stdio                   # stdio-only container image (default)
├── Dockerfile_http                    # HTTP/SSE container image
├── docker-compose.test.yml           # Main test orchestration
├── docker-compose.mcp-compliance.yml # NEW: MCP compliance testing
├── docker-compose.test.override.yml  # Development overrides
└── README.md                         # This file

scripts/                               # Test execution scripts
├── test.sh                           # Updated: Linux/macOS test runner
├── test.bat                          # Updated: Windows test runner
├── build-stdio.sh / build-stdio.bat  # Build stdio image (default)
├── build-http.sh / build-http.bat    # Build HTTP/SSE image
└── build-all.sh / build-all.bat      # Build all variants

test-results/                          # Test outputs (auto-created)
├── htmlcov/                          # Coverage HTML reports
├── coverage.xml                      # Coverage XML for CI
└── *.log                            # Test execution logs
```

## Development Workflow

### 1. **First Time Setup**
```bash
# Build test images
./scripts/test.sh build
```

### 2. **Regular Development**
```bash
# Quick feedback during development
./scripts/test.sh unit

# MCP compliance validation
./scripts/test.sh sse-compliance

# Full validation before commit
./scripts/test.sh coverage
```

### 3. **MCP Protocol Development**
```bash
# Start interactive test environment
./scripts/test.sh live

# Test MCP compliance iteratively
./scripts/test.sh mcp-compliance

# Debug with live servers and logs
./scripts/test.sh logs
```

### 4. **Development Shell**
```bash
# Interactive development environment
docker-compose -f docker/docker-compose.test.yml \
               -f docker/docker-compose.test.override.yml \
               run --rm test-dev

# Inside container:
# pytest tests/test_sse_mcp_compliance.py -v
# python tests/test_mcp_compliance.py
```

### 5. **Continuous Testing**
```bash
# Watch mode for continuous testing during development
docker-compose -f docker/docker-compose.test.yml \
               -f docker/docker-compose.test.override.yml \
               run --rm test-watch
```

## Environment Variables

### Standard Tests
```bash
NEO4J_URI=neo4j://neo4j-test:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=testpassword
NEO4J_DATABASE=neo4j
```

### MCP Compliance Tests (NEW)
```bash
# Server URLs for live testing
MCP_SSE_SERVER_URL=http://mcp-sse-server:3001
MCP_HTTP_SERVER_URL=http://mcp-http-server:3002

# Protocol configuration
MCP_MODE=sse
MCP_SERVER_PORT=3001
MCP_SERVER_HOST=0.0.0.0
```

## Test Results and Reporting

### Coverage Reports
After running coverage tests:

```bash
# View HTML coverage report
open test-results/htmlcov/index.html

# On Windows:
start test-results\htmlcov\index.html

# Or via web interface during live tests:
http://localhost:8080
```

### Live Test Environment
When running `./scripts/test.sh live`:

| Service | URL | Purpose |
|---------|-----|----------|
| **SSE Server** | http://localhost:3001 | MCP SSE endpoint testing |
| **Neo4j Browser** | http://localhost:7474 | Database inspection (neo4j/testpassword) |
| **Test Results** | http://localhost:8080 | Coverage and test reports |

### MCP Inspector Integration
Optional MCP Inspector for visual testing:

```bash
# Start MCP Inspector with compliance environment
docker-compose -f docker/docker-compose.mcp-compliance.yml up mcp-inspector

# Access at: http://localhost:3010
```

## Cleanup

```bash
# Clean up all test resources
./scripts/test.sh clean

# Remove specific test images (if needed)
docker rmi $(docker images mcp-neo4j-memory-* -q)

# Reset test results
rm -rf test-results/*
```

## CI/CD Integration

This Docker test setup is designed for CI/CD pipelines:

### GitHub Actions Example
```yaml
- name: Run Unit Tests
  run: ./scripts/test.sh unit
  
- name: Run Integration Tests
  run: ./scripts/test.sh integration
  
- name: Run MCP Compliance Tests
  run: ./scripts/test.sh mcp-compliance
  
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./test-results/coverage.xml
```

### GitLab CI Example
```yaml
test:unit:
  script:
    - ./scripts/test.sh unit
  
test:mcp-compliance:
  script:
    - ./scripts/test.sh mcp-compliance
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: test-results/coverage.xml
```

## Troubleshooting

### Neo4j Connection Issues
```bash
# Check Neo4j logs
./scripts/test.sh logs

# Verify Neo4j is healthy
docker-compose -f docker/docker-compose.test.yml ps

# Test Neo4j connection manually
docker-compose -f docker/docker-compose.test.yml exec neo4j-test cypher-shell -u neo4j -p testpassword "RETURN 1"
```

### MCP Server Issues
```bash
# Check SSE server health
curl http://localhost:3001/health

# View SSE server logs
docker-compose -f docker/docker-compose.mcp-compliance.yml logs mcp-sse-server

# Test SSE endpoint manually
curl -H "Accept: text/event-stream" http://localhost:3001/sse
```

### Permission Issues
```bash
# Fix ownership of test results (Linux/macOS)
sudo chown -R $USER:$USER test-results/

# Windows - run as Administrator if needed
```

### Container Build Issues
```bash
# Rebuild without cache
./scripts/test.sh build
docker-compose -f docker/docker-compose.test.yml build --no-cache

# Clean and rebuild
./scripts/test.sh clean
./scripts/test.sh build
```

### Memory Issues
```bash
# Increase Docker memory limit to 4GB+ for Neo4j
# Check Docker Desktop settings -> Resources -> Memory

# Monitor resource usage
docker stats
```

## Test Categories Explained

| Category | Speed | Dependencies | Purpose | New Features |
|----------|-------|--------------|---------|---------------|
| **Unit** | ⚡ Fast | None | Imports, models, basic functionality | ✅ MCP tool definitions |
| **Integration** | 🐌 Slow | Neo4j | Database operations, business logic | ✅ Cross-protocol consistency |
| **MCP Compliance** | 🔄 Medium | Neo4j + Servers | **NEW:** Protocol validation | ✅ JSON-RPC 2.0, SSE, Session mgmt |
| **Live Integration** | 🔄 Medium | All Services | **NEW:** Real-world testing | ✅ Live servers, performance |
| **Coverage** | 🐌 Slow | Neo4j + Servers | Complete analysis with reports | ✅ Enhanced reporting |

## Benefits

### Standard Benefits
✅ **Reproducible** - Same environment every time  
✅ **Isolated** - No conflicts with local setup  
✅ **Complete** - Includes all dependencies  
✅ **CI-Ready** - Works in automated pipelines  
✅ **Fast Feedback** - Unit tests run quickly  
✅ **Comprehensive** - Full integration testing  
✅ **Professional** - Coverage reporting included

### NEW: MCP Compliance Benefits
✅ **Protocol Validation** - Full MCP specification compliance  
✅ **Live Server Testing** - Real-world integration scenarios  
✅ **Interactive Environment** - Visual testing and debugging  
✅ **Performance Testing** - Load and stress testing capabilities  
✅ **Cross-Protocol Validation** - Consistency across SSE/HTTP  
✅ **Production Readiness** - Validates Claude Desktop compatibility  
✅ **Visual Test Results** - Web-based test result viewing  
✅ **MCP Inspector Ready** - Compatible with official MCP tools

## What's New in This Version

### 🎯 MCP Protocol Compliance Testing
- Comprehensive JSON-RPC 2.0 validation
- SSE transport specification compliance
- Session management verification
- Tool execution validation
- Error handling compliance

### 🚀 Live Integration Testing
- Running SSE and HTTP servers for real-world testing
- Interactive test environment with web UI
- Performance and load testing capabilities
- MCP Inspector integration

### 📊 Enhanced Test Infrastructure
- New Docker Compose configuration for MCP compliance
- Updated test scripts with MCP-specific commands
- Web-based test results viewer
- Improved logging and debugging capabilities

### 🔧 Developer Experience Improvements
- Color-coded test output
- Better error reporting and debugging
- Interactive live test environment
- Simplified command structure

Your MCP Neo4j Memory server is now **production-ready** with comprehensive testing that ensures compatibility with Claude Desktop, MCP Inspector, and any other MCP-compliant client! 🎉

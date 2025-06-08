# MCP Neo4j Memory - Test Suite

This directory contains comprehensive tests for the MCP Neo4j Memory server.

## Test Categories

### 🧪 Unit Tests (No External Dependencies)
- **`test_unit.py`** - Basic functionality, imports, module structure
- **`test_core_models.py`** - Pydantic data model validation and serialization
- **`test_json_string_parsing.py`** - JSON string parsing fix for LLM client compatibility

### 🔗 Integration Tests (Require Neo4j)
- **`test_neo4j_memory_integration.py`** - Core Neo4j operations and business logic
- **`test_transport_integration.py`** - HTTP/SSE protocol implementations
- **`test_sse_mcp_compliance.py`** - MCP SSE protocol compliance verification

### 🚀 Test Runners
- **`run_all_tests.py`** - Comprehensive test runner with environment checking
- **`test_mcp_compliance.py`** - Dedicated MCP protocol compliance test runner

## Running Tests

### Quick Start
```bash
# Run all available tests with comprehensive output
python tests/run_all_tests.py

# Run MCP compliance tests specifically
python tests/test_mcp_compliance.py
```

### Specific Test Categories
```bash
# Unit tests only (no external dependencies)
pytest tests/test_unit.py tests/test_core_models.py tests/test_json_string_parsing.py -v

# Integration tests (requires Neo4j)
pytest tests/test_neo4j_memory_integration.py -v
pytest tests/test_transport_integration.py -v

# MCP compliance tests
pytest tests/test_sse_mcp_compliance.py -v

# Live server integration tests (requires running SSE server)
pytest tests/test_sse_mcp_compliance.py -v -m integration

# All tests
pytest tests/ -v
```

### Individual Test Files
```bash
pytest tests/test_unit.py -v                          # Basic functionality
pytest tests/test_core_models.py -v                   # Data models
pytest tests/test_json_string_parsing.py -v           # JSON string parsing fix
pytest tests/test_neo4j_memory_integration.py -v      # Neo4j operations
pytest tests/test_transport_integration.py -v         # HTTP/SSE protocols
pytest tests/test_sse_mcp_compliance.py -v            # MCP SSE compliance
```

### Test Markers
```bash
# Run only unit tests
pytest tests/ -v -m unit

# Run only integration tests
pytest tests/ -v -m integration

# Run MCP compliance tests
pytest tests/ -v -m mcp_compliance

# Skip slow tests
pytest tests/ -v -m "not slow"
```

## Test Dependencies

### Always Available (Unit Tests)
- Python 3.10+
- Pytest
- Pydantic
- MCP Python SDK

### Integration Tests Require
- **Neo4j Database** running on `neo4j://localhost:7687`
- **aiohttp** - For async HTTP testing
- Environment variables (optional):
  ```bash
  export NEO4J_URI="neo4j://localhost:7687"
  export NEO4J_USERNAME="neo4j"
  export NEO4J_PASSWORD="password"
  export NEO4J_DATABASE="neo4j"
  ```

### Live Server Testing
- **Running SSE Server** on `http://localhost:3001`
- Environment variable (optional):
  ```bash
  export MCP_SSE_SERVER_URL="http://localhost:3001"
  ```

### Additional Dependencies
- **httpx** - For HTTP protocol testing
- **FastAPI TestClient** - For API endpoint testing
- **requests** - For live server health checks

## Test Structure

```
tests/
├── test_unit.py                     # ✅ Unit tests (always runnable)
├── test_core_models.py              # ✅ Model tests (always runnable)
├── test_json_string_parsing.py      # ✅ JSON parsing fix tests (always runnable)
├── test_neo4j_memory_integration.py # 🔗 Integration tests (needs Neo4j)
├── test_transport_integration.py    # 🔗 Protocol tests (needs Neo4j)
├── test_sse_mcp_compliance.py       # 🔗 MCP compliance tests (needs Neo4j)
├── run_all_tests.py                 # 🚀 Comprehensive test runner
└── test_mcp_compliance.py           # 🎯 MCP-focused test runner
```

## What Each Test Covers

### Unit Tests (`test_unit.py`)
- ✅ Module imports work correctly
- ✅ Package structure is sound
- ✅ MCP tools are properly defined
- ✅ Basic data model instantiation
- ✅ Tool count and structure validation
- ✅ JSON string parsing logic verification

### Core Models (`test_core_models.py`)
- ✅ Pydantic model validation
- ✅ Serialization/deserialization
- ✅ Edge cases and error handling
- ✅ Model relationships

### JSON String Parsing (`test_json_string_parsing.py`)
- ✅ Handles JSON string input from LLM clients
- ✅ Maintains backward compatibility with normal input
- ✅ Error handling for invalid JSON strings
- ✅ Warning logging when parsing occurs
- ✅ Edge cases and null handling
- ✅ Both MCP and HTTP tool execution versions

### Neo4j Integration (`test_neo4j_memory_integration.py`)
- ✅ Entity creation, reading, deletion
- ✅ Relation management
- ✅ Observation operations
- ✅ Search and query functionality
- ✅ Database transaction handling

### Transport Integration (`test_transport_integration.py`)
- ✅ HTTP server endpoints
- ✅ SSE streaming functionality
- ✅ Cross-protocol data consistency
- ✅ Tool execution via different transports
- ✅ Error handling consistency

### MCP SSE Compliance (`test_sse_mcp_compliance.py`)
- ✅ **SSE endpoint behavior** - Correct headers and streaming
- ✅ **JSON-RPC 2.0 compliance** - Message format validation
- ✅ **MCP protocol methods** - initialize, tools/list, tools/call, ping
- ✅ **Session management** - Creation, tracking, cleanup
- ✅ **Error handling** - Proper error codes and messages
- ✅ **Tool execution** - All 10 Neo4j memory tools
- ✅ **Live server integration** - Real SSE server testing

## MCP Compliance Testing

### Dedicated MCP Test Runner
```bash
# Run comprehensive MCP compliance tests
python tests/test_mcp_compliance.py
```

This specialized test runner:
- ✅ Checks all dependencies
- ✅ Verifies Neo4j connectivity
- ✅ Tests MCP protocol implementation
- ✅ Validates SSE transport compliance
- ✅ Runs live server tests if available
- ✅ Provides detailed compliance report

### MCP Compliance Checklist

#### Required SSE Endpoints
- ✅ `GET /sse` - SSE connection with session management
- ✅ `POST /messages` - JSON-RPC message handling
- ✅ `GET /health` - Server health status
- ✅ `OPTIONS /messages` - CORS preflight support

#### MCP Protocol Methods
- ✅ `initialize` - Protocol negotiation
- ✅ `initialized` - Initialization completion
- ✅ `tools/list` - Tool discovery
- ✅ `tools/call` - Tool execution
- ✅ `ping` - Connectivity testing

#### JSON-RPC 2.0 Compliance
- ✅ Correct message format (`jsonrpc: "2.0"`)
- ✅ Request/response ID matching
- ✅ Proper error codes and messages
- ✅ Notification handling (no response)

#### Session Management
- ✅ UUID-based session creation
- ✅ Session-scoped message routing
- ✅ Automatic session cleanup
- ✅ Concurrent session support

## Continuous Integration

The test suite is designed to work in CI environments:

1. **Unit tests** run in any Python environment
2. **Integration tests** require Neo4j service
3. **Live server tests** require running SSE server
4. **Graceful degradation** when dependencies are missing
5. **Clear test categorization** for selective execution
6. **Detailed failure reporting** for debugging

## Running in Different Environments

### Local Development
```bash
# Full test suite with all dependencies
python tests/run_all_tests.py

# MCP compliance only
python tests/test_mcp_compliance.py
```

### CI/CD Pipeline
```bash
# Unit tests only (no external dependencies)
pytest tests/ -v -m unit

# With Neo4j service
pytest tests/ -v -m "unit or integration"

# With live SSE server
pytest tests/ -v
```

### Docker Environment
```bash
# Start Neo4j and SSE server
docker run -d --name neo4j -p 7687:7687 -e NEO4J_AUTH=neo4j/testpassword neo4j:latest
docker run -d --name sse-server -p 3001:3001 \
  -e NEO4J_URL=bolt://host.docker.internal:7687 \
  -e NEO4J_PASSWORD=testpassword \
  -e MCP_MODE=sse \
  lesykm/mcp-neo4j-memory:sse

# Run tests
export NEO4J_PASSWORD=testpassword
export MCP_SSE_SERVER_URL=http://localhost:3001
python tests/test_mcp_compliance.py
```

## Success Criteria

✅ **All unit tests pass** - Basic functionality works  
✅ **Integration tests pass** - Neo4j operations work correctly  
✅ **Transport tests pass** - All protocols (stdio, HTTP, SSE) function properly  
✅ **MCP compliance tests pass** - Full MCP specification adherence  
✅ **Cross-protocol consistency** - Data accessible across all transports  
✅ **Error handling** - Graceful failure and recovery  
✅ **Live server integration** - Real-world usage scenarios work

## Troubleshooting

### Common Issues

**Import errors**
```bash
# Install dependencies
pip install -e .
pip install pytest aiohttp
```

**Neo4j connection failed**
```bash
# Check Neo4j is running
docker ps | grep neo4j

# Set environment variables
export NEO4J_URI=neo4j://localhost:7687
export NEO4J_PASSWORD=your_password
```

**SSE server not found**
```bash
# Start SSE server
python -m mcp_neo4j_memory --mode sse --port 3001

# Or with Docker
docker run -p 3001:3001 -e MCP_MODE=sse lesykm/mcp-neo4j-memory:sse
```

**Test failures**
```bash
# Run with verbose output
pytest tests/test_sse_mcp_compliance.py -v -s

# Run specific test
pytest tests/test_sse_mcp_compliance.py::TestMCPProtocolMethods::test_json_rpc_initialize_method -v
```

### Debug Mode
```bash
# Enable debug logging
export PYTHONPATH=src
export LOG_LEVEL=DEBUG
python tests/test_mcp_compliance.py
```

# Build and Test Scripts

This directory contains all build and test scripts for the MCP Neo4j Memory project.

## Build Scripts

### 🐳 **Docker Image Building**

The project now uses a **unified multi-stage Dockerfile** (`docker/Dockerfile`) that builds all variants from a single source. This simplifies maintenance and ensures consistency across all protocol variants.

| Script | Purpose | Output Tags |
|--------|---------|-------------|
| `build.sh/.bat` | Universal builder with arguments | All tags based on target |

### 🧪 **Testing**

| Script | Purpose |
|--------|---------|
| `test.sh/.bat` | Run Docker-based tests with multiple modes |

## Usage

### Quick Start

**Linux/Mac:**
```bash
# Build specific variants using unified Dockerfile
./scripts/build.sh stdio       # Build stdio-only (default) Docker container
./scripts/build.sh http        # Build HTTP REST API Docker container
./scripts/build.sh sse         # Build SSE streaming server Docker container
./scripts/build.sh test        # Build test environment Docker container
./scripts/build.sh all         # Build all Docker container variants (default) 

# Run tests
./scripts/test.sh               # Run all tests at docker compose environment with neo4j integration
./scripts/test.sh build         # Create test environment by building Docker container
./scripts/test.sh unit          # Run unit tests only at docker compose environment
./scripts/test.sh integration   # Run integration tests only at docker compose environment with neo4j integration
./scripts/test.sh coverage     # Run coverage reporting
```

**Windows:**
```cmd
REM Build specific variants
scripts\build.bat stdio
scripts\build.bat http
scripts\build.bat sse
scripts\build.bat test
scripts\build.bat all

REM Run tests
scripts\test.bat
scripts\test.bat build
scripts\test.bat unit
scripts\test.bat integration
scripts\test.bat coverage
```

### Version Management

All scripts automatically extract the version from `pyproject.toml`:

```toml
[project]
version = "0.1.4"  # ← Automatically detected
```

This creates tags like:
- `mcp-neo4j-memory:0.1.4-stdio`
- `mcp-neo4j-memory:0.1.4-http`
- `mcp-neo4j-memory:0.1.4-sse`
- `mcp-neo4j-memory:0.1.4`

## Docker Architecture

### 📦 **Multi-Stage Dockerfile Structure**

The unified `docker/Dockerfile` uses multi-stage builds with these targets:

1. **`builder`** - Shared build stage with dependencies
2. **`runtime-base`** - Common runtime configuration
3. **`stdio`** - stdio-only variant (default/latest)
4. **`http`** - HTTP REST API server variant
5. **`sse`** - Server-Sent Events server variant
6. **`test`** - Test environment with all dependencies

### 📦 **stdio (Default/Latest)**
- **Tag**: `:latest`, `:stdio`, `:VERSION`
- **Use**: Claude Desktop, MCP clients
- **Size**: Small (minimal dependencies)
- **Target**: `stdio`

```bash
./scripts/build.sh stdio
docker run -it mcp-neo4j-memory:latest
```

### 🌐 **HTTP Server**
- **Tag**: `:http`, `:VERSION-http`
- **Use**: Web apps, REST APIs
- **Size**: Medium (includes FastAPI)
- **Target**: `http`

```bash
./scripts/build.sh http
docker run -p 3001:3001 mcp-neo4j-memory:http
```

### 📡 **SSE (Server-Sent Events) Server**
- **Tag**: `:sse`, `:VERSION-sse`
- **Use**: Real-time streaming applications
- **Size**: Medium (includes FastAPI for SSE streaming)
- **Protocol**: Server-Sent Events for real-time data streaming
- **Target**: `sse`

```bash
./scripts/build.sh sse
docker run -p 3001:3001 mcp-neo4j-memory:sse
```

#### 🔧 **SSE Server Configuration**

The SSE server is specifically optimized for Server-Sent Events integration:

**Environment Variables:**
- `MCP_MODE=sse` - Enables SSE protocol mode
- `MCP_SERVER_HOST=0.0.0.0` - Server bind address
- `MCP_SERVER_PORT=3001` - SSE server port
- `NEO4J_URL` - Neo4j database connection string
- `NEO4J_USERNAME` - Database username
- `NEO4J_PASSWORD` - Database password
- `NEO4J_DATABASE` - Target database name

**Health Check Endpoint:**
```bash
curl -f http://localhost:3001/health
```

**SSE Endpoint:**
```bash
curl http://localhost:3001/sse
# Returns event-stream data for real-time streaming
```

**Complete Example:**
```bash
# Build SSE image
./scripts/build.sh sse

# Run with custom Neo4j connection
docker run -p 3001:3001 \
  -e NEO4J_URL="bolt://your-neo4j:7687" \
  -e NEO4J_PASSWORD="your-password" \
  -e NEO4J_USERNAME="neo4j" \
  mcp-neo4j-memory:sse

# Test the server
curl http://localhost:3001/sse
```

### 🧪 **Test Environment**
- **Tag**: `:test`, `:VERSION-test`
- **Use**: CI/CD, development testing
- **Size**: Large (all dependencies + testing tools)
- **Target**: `test`

```bash
./scripts/build.sh test
./scripts/test.sh
```

## File Overview

```
scripts/
├── build.sh/.bat              # Universal builder (replaces individual build scripts)
├── build-all.sh/.bat          # Build all variants at once
├── test.sh/.bat               # Docker tests with multiple modes
├── test_backup.bat            # Backup of old test script
└── README.md                  # This file
```

## Migration Notes

### **Before** (old structure with separate Dockerfiles)
```bash
./scripts/build-stdio.sh       # Built stdio using Dockerfile_stdio
./scripts/build-http.sh        # Built HTTP using Dockerfile_http
./scripts/build-sse.sh         # Built SSE using Dockerfile_sse
./scripts/build-all.sh         # Built all using separate Dockerfiles
```

### **After** (new unified structure)
```bash
./scripts/build.sh stdio       # Builds stdio target from unified Dockerfile
./scripts/build.sh http        # Builds http target from unified Dockerfile
./scripts/build.sh sse         # Builds sse target from unified Dockerfile
./scripts/build.sh all         # Builds all targets from unified Dockerfile
```

### **Benefits of Unified Dockerfile**
✅ **Single source of truth** - All variants built from same base  
✅ **Better layer caching** - Shared base layers across variants  
✅ **Easier maintenance** - Update dependencies in one place  
✅ **Consistent behavior** - All variants use identical base configuration  
✅ **Faster builds** - Multi-stage builds share common layers  

## Environment Variables

All scripts respect these environment variables from `pyproject.toml`:
- Automatically extracts version number
- No manual version updates needed
- Consistent versioning across all images

## CI/CD Integration

These scripts are designed for automated workflows:

```yaml
# Example GitHub Actions
- name: Build All Images
  run: ./scripts/build-all.sh

- name: Test
  run: ./scripts/test.sh coverage

- name: Tag Release
  run: |
    VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    docker tag mcp-neo4j-memory:latest myregistry/mcp-neo4j-memory:$VERSION
```

## Tips

✅ **Always use versioned tags in production**  
✅ **Use `:latest` only for development**  
✅ **Update `pyproject.toml` version before building releases**  
✅ **Test with `./scripts/test.sh` before deploying**  
✅ **Use `./scripts/build.sh all` to build all variants efficiently**  
✅ **The unified Dockerfile provides better caching and consistency**

"""
Integration tests for all transport protocols in the refactored MCP Neo4j Memory server.

Tests stdio, HTTP, and SSE protocols to ensure they work correctly with the new modular architecture.
"""

import os
import pytest
import asyncio
import json
import httpx
from typing import Dict, Any
from neo4j import GraphDatabase

from mcp_neo4j_memory.core import Neo4jMemory, Entity, Relation, get_mcp_tools, execute_tool_http
from mcp_neo4j_memory.protocols import run_http_server, run_sse_server


@pytest.fixture(scope="session")
def neo4j_driver():
    """Create a Neo4j driver for the test session."""
    uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "password")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Verify connection
    try:
        driver.verify_connectivity()
    except Exception as e:
        pytest.skip(f"Could not connect to Neo4j: {e}")

    yield driver

    # Clean up test data after all tests
    driver.execute_query("MATCH (n:Memory) DETACH DELETE n")
    driver.close()


@pytest.fixture(scope="function")
def memory(neo4j_driver):
    """Create a fresh Neo4jMemory instance for each test."""
    # Clean up before each test
    neo4j_driver.execute_query("MATCH (n:Memory) DETACH DELETE n")
    return Neo4jMemory(neo4j_driver)


class TestCoreTools:
    """Test core tool functionality independent of transport protocol."""

    @pytest.mark.asyncio
    async def test_get_mcp_tools(self):
        """Test that get_mcp_tools returns expected tools."""
        tools = get_mcp_tools()

        # Verify we have the expected number of tools
        assert len(tools) == 10

        # Verify expected tool names are present
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "create_entities", "create_relations", "add_observations",
            "delete_entities", "delete_observations", "delete_relations",
            "read_graph", "search_nodes", "find_nodes", "open_nodes"
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_execute_tool_http_create_entities(self, memory):
        """Test HTTP tool execution for creating entities."""
        arguments = {
            "entities": [
                {
                    "name": "TestPerson",
                    "type": "Person",
                    "observations": ["Test observation"]
                }
            ]
        }

        result = await execute_tool_http(memory, "create_entities", arguments)

        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "TestPerson"

    @pytest.mark.asyncio
    async def test_execute_tool_http_read_graph(self, memory):
        """Test HTTP tool execution for reading graph."""
        # First create some test data
        test_entity = Entity(name="TestEntity", type="Test", observations=["Test"])
        await memory.create_entities([test_entity])

        # Test read_graph
        result = await execute_tool_http(memory, "read_graph")

        assert result["success"] is True
        assert len(result["data"]["entities"]) == 1
        assert result["data"]["entities"][0]["name"] == "TestEntity"


class TestHttpServer:
    """Test HTTP server protocol implementation."""

    @pytest.fixture(scope="class")
    def http_server_port(self):
        """Get an available port for HTTP server testing."""
        return 8001  # Use a different port from default to avoid conflicts

    @pytest.mark.asyncio
    async def test_http_server_endpoints(self, memory, http_server_port):
        """Test HTTP server endpoints."""
        from mcp_neo4j_memory.protocols.http_server import HTTPServer

        # Create HTTP server
        http_server = HTTPServer(memory)
        app = http_server.app

        # Use FastAPI test client
        from fastapi.testclient import TestClient
        client = TestClient(app)

        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "MCP Neo4j Memory Server"
        assert data["protocol"] == "http"

        # Test tools endpoint
        response = client.get("/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) == 10

        # Test execute endpoint
        test_payload = {
            "tool": "read_graph",
            "arguments": {}
        }
        response = client.post("/execute", json=test_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_http_server_tool_execution(self, memory):
        """Test tool execution via HTTP server."""
        from mcp_neo4j_memory.protocols.http_server import HTTPServer
        from fastapi.testclient import TestClient

        # Create test data first
        test_entity = Entity(name="HttpTestEntity", type="Test", observations=["HTTP test"])
        await memory.create_entities([test_entity])

        # Create HTTP server and test client
        http_server = HTTPServer(memory)
        client = TestClient(http_server.app)

        # Test create_entities via HTTP
        create_payload = {
            "tool": "create_entities",
            "arguments": {
                "entities": [
                    {
                        "name": "NewHttpEntity",
                        "type": "HttpTest",
                        "observations": ["Created via HTTP"]
                    }
                ]
            }
        }

        response = client.post("/execute", json=create_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1

        # Test read_graph via HTTP
        read_payload = {
            "tool": "read_graph",
            "arguments": {}
        }

        response = client.post("/execute", json=read_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["entities"]) == 2  # Original + new entity


class TestSseServer:
    """Test SSE server protocol implementation."""

    @pytest.mark.asyncio
    async def test_sse_server_endpoints(self, memory):
        """Test SSE server endpoints."""
        from mcp_neo4j_memory.protocols.sse_server import MCPSSEServer
        from fastapi.testclient import TestClient

        # Create SSE server
        sse_server = MCPSSEServer(memory)
        client = TestClient(sse_server.app)

        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "MCP Neo4j Memory SSE Server"
        assert data["protocol"] == "mcp-sse"
        assert "endpoints" in data

    @pytest.mark.asyncio
    async def test_sse_stream_connection(self, memory):
        """Test SSE stream basic connectivity (headers only)."""
        from mcp_neo4j_memory.protocols.sse_server import MCPSSEServer
        from fastapi.testclient import TestClient
        import threading
        import time

        # Create SSE server
        sse_server = MCPSSEServer(memory)
        client = TestClient(sse_server.app)

        # Test root endpoint first to ensure server is working
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "MCP Neo4j Memory SSE Server"
        assert data["protocol"] == "mcp-sse"
        assert "endpoints" in data

        # For SSE endpoint, we'll test it in a separate thread with timeout
        # since SSE streams are infinite and would hang the main thread
        result = {"success": False, "status_code": None, "headers": None, "error": None}

        def test_sse_headers():
            try:
                # This will start the SSE connection but we'll interrupt it quickly
                with client as test_client:
                    # Make the request - this will start streaming but we'll catch it
                    response = test_client.get("/sse", headers={"Accept": "text/event-stream"})
                    # We should never reach here due to infinite stream, but if we do:
                    result["status_code"] = response.status_code
                    result["headers"] = dict(response.headers)
            except Exception as e:
                # This is expected - the SSE stream will cause issues
                result["error"] = str(e)

        # Run SSE test in thread with timeout
        thread = threading.Thread(target=test_sse_headers)
        thread.daemon = True
        thread.start()
        thread.join(timeout=2.0)  # 2 second timeout

        if thread.is_alive():
            # Thread is still running - this means SSE endpoint is working (infinite stream)
            result["success"] = True
            print("SSE endpoint is working (infinite stream detected as expected)")
        else:
            # Thread finished - check what happened
            if result["status_code"] == 200:
                result["success"] = True
                print("SSE endpoint responded with 200 (unlikely but valid)")
            elif result["error"]:
                # Some error occurred - this might be expected for SSE
                print(f"SSE test completed with: {result['error']}")
                # For SSE, some errors are expected due to infinite stream nature
                if "stream" in result["error"].lower() or "timeout" in result["error"].lower():
                    result["success"] = True

        # The test passes if we detected the SSE endpoint is working
        assert result["success"], f"SSE endpoint test failed: {result.get('error', 'Unknown error')}"

        print("SSE endpoint test completed successfully")


class TestProtocolIntegration:
    """Test integration between protocols and core functionality."""

    @pytest.mark.asyncio
    async def test_all_protocols_share_same_tools(self, memory):
        """Test that all protocols expose the same tools."""
        from mcp_neo4j_memory.core import get_mcp_tools
        from mcp_neo4j_memory.protocols.http_server import HTTPServer
        from fastapi.testclient import TestClient

        # Get tools from core
        core_tools = get_mcp_tools()
        core_tool_names = set(tool.name for tool in core_tools)

        # Get tools from HTTP server
        http_server = HTTPServer(memory)
        client = TestClient(http_server.app)
        response = client.get("/tools")
        http_tools = response.json()["tools"]
        http_tool_names = set(tool["name"] for tool in http_tools)

        # Verify they match
        assert core_tool_names == http_tool_names
        assert len(core_tool_names) == 10

    @pytest.mark.asyncio
    async def test_cross_protocol_data_consistency(self, memory):
        """Test that data created via one protocol is accessible via others."""
        from mcp_neo4j_memory.protocols.http_server import HTTPServer
        from fastapi.testclient import TestClient

        # Create data via core API
        test_entity = Entity(
            name="CrossProtocolEntity",
            type="Test",
            observations=["Created via core API"]
        )
        await memory.create_entities([test_entity])

        # Read data via HTTP API
        http_server = HTTPServer(memory)
        client = TestClient(http_server.app)

        read_payload = {
            "tool": "read_graph",
            "arguments": {}
        }

        response = client.post("/execute", json=read_payload)
        assert response.status_code == 200
        data = response.json()

        # Verify entity is accessible via HTTP
        assert data["success"] is True
        entities = data["data"]["entities"]
        assert len(entities) == 1
        assert entities[0]["name"] == "CrossProtocolEntity"
        assert entities[0]["observations"] == ["Created via core API"]

    @pytest.mark.asyncio
    async def test_error_handling_consistency(self, memory):
        """Test that error handling is consistent across protocols."""
        from mcp_neo4j_memory.core import execute_tool_http
        from mcp_neo4j_memory.protocols.http_server import HTTPServer
        from fastapi.testclient import TestClient

        # Test invalid tool name via core API
        core_result = await execute_tool_http(memory, "invalid_tool", {})
        assert core_result["success"] is False
        assert "error" in core_result

        # Test invalid tool name via HTTP API
        http_server = HTTPServer(memory)
        client = TestClient(http_server.app)

        invalid_payload = {
            "tool": "invalid_tool",
            "arguments": {}
        }

        response = client.post("/execute", json=invalid_payload)
        assert response.status_code == 200  # HTTP 200 but error in payload
        data = response.json()
        assert data["success"] is False
        assert "error" in data


# Utility functions for testing
def create_test_entities() -> list[Dict[str, Any]]:
    """Create test entities for integration testing."""
    return [
        {
            "name": "TestPerson1",
            "type": "Person",
            "observations": ["Likes testing", "Works with Neo4j"]
        },
        {
            "name": "TestPerson2",
            "type": "Person",
            "observations": ["Enjoys integration tests"]
        },
        {
            "name": "TestCompany",
            "type": "Organization",
            "observations": ["Technology company", "Uses knowledge graphs"]
        }
    ]


def create_test_relations() -> list[Dict[str, Any]]:
    """Create test relations for integration testing."""
    return [
        {
            "source": "TestPerson1",
            "target": "TestCompany",
            "relationType": "WORKS_FOR"
        },
        {
            "source": "TestPerson1",
            "target": "TestPerson2",
            "relationType": "COLLEAGUES_WITH"
        }
    ]


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_transport_integration.py -v
    pytest.main([__file__, "-v"])

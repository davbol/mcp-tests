#!/bin/bash

# Kill any existing processes on these ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null

echo "Starting Bio Vegetable Distributor APIs..."

# Start Product API on Port 8000
echo "Launching Product Management API on http://localhost:8000"
python products_api.py &

# Start Customer API on Port 8001
echo "Launching Customer Management API on http://localhost:8001"
python customers_api.py &

# Note: MCP Server is now managed by Antigravity/IDE via stdio (mcp_config.json)
# If you want to run it as a web service manually: python mcp_server.py --sse
# echo "Launching MCP Server on http://localhost:3001 (SSE support enabled)"
# python mcp_server.py --sse &

echo ""
echo "Backend APIs initialized."
echo "Product API: http://localhost:8000"
echo "Customer API: http://localhost:8001"

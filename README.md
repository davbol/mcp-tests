# mcp-tests

A reference implementation demonstrating the Model Context Protocol (MCP) as an AI-native integration layer for enterprise REST APIs.

## Architecture

This project contains a Swiss Bio Vegetable Distributor mock system with:

- **`products_api.py`** — Product Management REST API (Port 8000)
- **`customers_api.py`** — Customer Management REST API (Port 8001)
- **`mcp_server.py`** — MCP Server bridging both APIs with Tools, Resources, and Prompts

## Quick Start

```bash
pip install -r requirements.txt
./run.sh
```

## Documentation

- 📄 [**Why MCP over Direct REST for Agentic AI?**](mcp_advantages.md) — Architectural comparison of MCP vs. direct REST API integration for AI agents

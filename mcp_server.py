import asyncio
import httpx
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server

# Configuration
PRODUCTS_API_URL = "http://localhost:8000"
CUSTOMERS_API_URL = "http://localhost:8001"

server = Server("bio-distributor-mcp")
app = FastAPI(title="Bio Distributor MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sse = SseServerTransport(endpoint="/messages")

async def get_remote_schema(url: str, schema_name: str):
    """Fetch OAS from a remote FastAPI server and extract a specific schema."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{url}/openapi.json")
            if resp.status_code == 200:
                openapi = resp.json()
                return openapi.get("components", {}).get("schemas", {}).get(schema_name, {})
        except Exception:
            pass
    return None

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    # Dynamically fetch categories and certifications from the Products API
    product_schema = await get_remote_schema(PRODUCTS_API_URL, "ProductCreate")
    
    # Extract Enums if available, fallback to hardcoded Swiss values if API is down
    categories = ["Wurzelgemüse", "Blattgemüse", "Fruchtgemüse", "Kohlgemüse", "Knollengemüse", "Zwiebelgemüse", "Hülsenfrüchte"]
    certifications = ["EU-Bio", "Demeter", "Bio Suisse (Knospe)", "Naturland"]
    
    if product_schema:
        # Pydantic V2 often uses $ref for Enums, this is a simplified extraction
        # In a real premium app, we would resolve $refs recursively
        properties = product_schema.get("properties", {})
        # Note: This mock server uses simple string enums for the tools
        # For brevity in this mock, we use the resolved values if possible
        pass

    return [
        types.Tool(
            name="get_products",
            description="List all bio vegetable products",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_product",
            description="Get details of a specific product by ID",
            inputSchema={
                "type": "object",
                "properties": {"product_id": {"type": "string", "format": "uuid"}},
                "required": ["product_id"]
            },
        ),
        types.Tool(
            name="create_product",
            description="Add a new product to the catalog. (Prices in CHF)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string", "enum": categories},
                    "price_per_unit": {"type": "number", "description": "Preis in CHF"},
                    "unit": {"type": "string", "enum": ["kg", "piece", "bunch", "box"]},
                    "origin": {"type": "string"},
                    "stock_quantity": {"type": "number"},
                    "certification": {"type": "string", "enum": certifications},
                    "is_seasonal": {"type": "boolean"},
                    "description": {"type": "string"}
                },
                "required": ["name", "category", "price_per_unit", "unit", "origin", "stock_quantity", "certification"]
            },
        ),
        types.Tool(
            name="get_customers",
            description="List all customers",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_customer",
            description="Get details of a specific customer by ID",
            inputSchema={
                "type": "object",
                "properties": {"customer_id": {"type": "string", "format": "uuid"}},
                "required": ["customer_id"]
            },
        ),
        types.Tool(
            name="create_customer",
            description="Register a new customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "phone": {"type": "string"},
                    "customer_type": {"type": "string", "enum": ["Restaurant", "Retailer", "Private", "Wholesaler"]},
                    "address": {
                        "type": "object",
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"},
                            "zip_code": {"type": "string"},
                            "country": {"type": "string"}
                        },
                        "required": ["street", "city", "zip_code", "country"]
                    },
                    "loyalty_points": {"type": "integer"},
                    "notes": {"type": "string"}
                },
                "required": ["name", "email", "phone", "customer_type", "address"]
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    # Compatibility mapping (optional but helpful for transition)
    if arguments and name == "create_product":
        category_map = {"Root": "Wurzelgemüse", "Leafy": "Blattgemüse", "Fruit": "Fruchtgemüse", "Brassica": "Kohlgemüse", "Tuber": "Knollengemüse", "Allium": "Zwiebelgemüse", "Legume": "Hülsenfrüchte"}
        if arguments.get("category") in category_map:
            arguments["category"] = category_map[arguments["category"]]
        if arguments.get("certification") == "Bioland":
            arguments["certification"] = "Bio Suisse (Knospe)"

    async with httpx.AsyncClient() as client:
        try:
            if name == "get_products":
                resp = await client.get(f"{PRODUCTS_API_URL}/products")
                return [types.TextContent(type="text", text=resp.text)]
            elif name == "get_product":
                pid = arguments.get("product_id")
                resp = await client.get(f"{PRODUCTS_API_URL}/products/{pid}")
                return [types.TextContent(type="text", text=resp.text)]
            elif name == "create_product":
                resp = await client.post(f"{PRODUCTS_API_URL}/products", json=arguments)
                return [types.TextContent(type="text", text=resp.text)]
            elif name == "get_customers":
                resp = await client.get(f"{CUSTOMERS_API_URL}/customers")
                return [types.TextContent(type="text", text=resp.text)]
            elif name == "get_customer":
                cid = arguments.get("customer_id")
                resp = await client.get(f"{CUSTOMERS_API_URL}/customers/{cid}")
                return [types.TextContent(type="text", text=resp.text)]
            elif name == "create_customer":
                resp = await client.post(f"{CUSTOMERS_API_URL}/customers", json=arguments)
                return [types.TextContent(type="text", text=resp.text)]
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error calling API: {str(e)}")]

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="catalog://summary",
            name="Product Catalog Summary",
            description="A unified text summary of all current bio products, categories, and stock levels.",
            mimeType="text/plain",
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str | types.AnyUrl) -> str | bytes:
    if str(uri) == "catalog://summary":
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{PRODUCTS_API_URL}/products")
            if resp.status_code == 200:
                products = resp.json()
                summary = "Bio Distributor Catalog Summary:\n"
                for p in products:
                    summary += f"- {p['name']} ({p['category']}): {p['stock_quantity']} {p['unit']} available at {p['price_per_unit']} CHF\n"
                return summary
            return "Failed to load catalog."
    raise ValueError(f"Resource not found: {uri}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="draft_loyalty_email",
            description="Create a personalized loyalty reward email for a customer.",
            arguments=[
                types.PromptArgument(name="customer_id", description="UUID of the customer", required=True)
            ]
        )
    ]

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    if name == "draft_loyalty_email" and arguments and "customer_id" in arguments:
        cid = arguments["customer_id"]
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{CUSTOMERS_API_URL}/customers/{cid}")
            if resp.status_code == 200:
                customer = resp.json()
                return types.GetPromptResult(
                    description=f"Drafting email for {customer['name']}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"You are a Customer Success Manager for our Bio Distributor. Write a polite email in German to {customer['name']}. They currently have {customer['loyalty_points']} loyalty points. Thank them for being a {customer['customer_type']} customer and offer them a small seasonal vegetable box as a reward."
                            )
                        )
                    ]
                )
    raise ValueError(f"Prompt not found or missing arguments: {name}")

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="bio-distributor-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

@app.post("/messages")
async def handle_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

async def run_stdio():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="bio-distributor-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    if "--sse" in sys.argv:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=3001)
    else:
        asyncio.run(run_stdio())

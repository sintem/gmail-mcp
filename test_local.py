#!/usr/bin/env python3
"""Local test for LIAM Gmail MCP Server.

Usage:
    1. Start server in another terminal: python main.py
    2. Run this script: python test_local.py

Tests the MCP server running at http://127.0.0.1:8080
"""

import asyncio
import os
import json

import httpx
from dotenv import load_dotenv

load_dotenv()

MCP_URL = "http://127.0.0.1:8080"
LIAM_TOKEN = os.getenv("LIAM_ACCESS_TOKEN")

if not LIAM_TOKEN or LIAM_TOKEN == "your-liam-jwt-here":
    print("ERROR: Set LIAM_ACCESS_TOKEN in .env")
    print("Get it from LIAM web app: DevTools > Application > Local Storage > accessToken")
    exit(1)

print(f"MCP Server: {MCP_URL}")
print(f"LIAM Token: {LIAM_TOKEN[:30]}...")
print()


async def test_mcp():
    """Test MCP server endpoints."""
    headers = {
        "Authorization": f"Bearer {LIAM_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: List tools
        print("=== Testing: List Tools ===")
        try:
            resp = await client.post(
                f"{MCP_URL}/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {},
                },
            )
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    print(f"Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool.get('description', '')[:50]}...")
                else:
                    print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"Error: {resp.text}")
        except Exception as e:
            print(f"Error: {e}")

        print()

        # Test 2: Call gmail_get_profile
        print("=== Testing: gmail_get_profile ===")
        try:
            resp = await client.post(
                f"{MCP_URL}/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "gmail_get_profile",
                        "arguments": {},
                    },
                },
            )
            print(f"Status: {resp.status_code}")
            data = resp.json()
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
        except Exception as e:
            print(f"Error: {e}")

        print()

        # Test 3: Call gmail_list_labels
        print("=== Testing: gmail_list_labels ===")
        try:
            resp = await client.post(
                f"{MCP_URL}/mcp",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "gmail_list_labels",
                        "arguments": {},
                    },
                },
            )
            print(f"Status: {resp.status_code}")
            data = resp.json()
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp())

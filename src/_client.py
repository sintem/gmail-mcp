# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""Local MCP client demonstrating OAuth browser flow with LIAM.

Environment variables:
    DEDALUS_API_KEY: Your Dedalus API key (dsk-live-*)
    DEDALUS_API_URL: Dedalus Product API URL
"""

import asyncio
import os
import webbrowser
from collections.abc import Awaitable, Callable
from typing import TypeVar

from dotenv import load_dotenv

load_dotenv()

from dedalus_labs import AsyncDedalus, AuthenticationError, DedalusRunner


class MissingEnvError(ValueError):
    """Required environment variable not set."""


def get_env(key: str, default: str | None = None) -> str:
    """Get env var or raise if required."""
    val = os.getenv(key, default)
    if not val:
        raise MissingEnvError(f"Missing required env var: {key}")
    return val


# Configuration
DEDALUS_API_KEY = get_env("DEDALUS_API_KEY")
DEDALUS_API_URL = get_env("DEDALUS_API_URL", "https://api.dedaluslabs.ai")
DEDALUS_AS_URL = get_env("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")

# MCP server slug (after deployment to Dedalus)
MCP_SERVER = "sintem/gmail-mcp"

print("=== Environment ===")
print(f"  DEDALUS_API_URL: {DEDALUS_API_URL}")
print(f"  MCP_SERVER: {MCP_SERVER}")
print(f"  DEDALUS_API_KEY: {DEDALUS_API_KEY[:20]}...")


T = TypeVar("T")


async def with_oauth_retry(fn: Callable[[], Awaitable[T]]) -> T:
    """Run async function, handling OAuth browser flow if needed."""
    try:
        return await fn()
    except AuthenticationError as e:
        # Extract connect_url from error
        body = e.body if isinstance(e.body, dict) else {}
        url = body.get("connect_url") or body.get("detail", {}).get("connect_url")

        if not url:
            print(f"Auth error but no connect_url: {e}")
            raise

        print("\n" + "=" * 60)
        print("OAuth required. Opening browser...")
        print(f"\nConnect URL: {url}")
        print("\nThis will redirect to LIAM → Google OAuth")
        print("=" * 60)

        webbrowser.open(url)
        input("\nPress Enter after completing OAuth in browser...")

        return await fn()


async def run_interactive() -> None:
    """Interactive REPL for testing Gmail MCP."""
    client = AsyncDedalus(
        api_key=DEDALUS_API_KEY,
        base_url=DEDALUS_API_URL,
        as_base_url=DEDALUS_AS_URL,  # Dedalus AS is the authorization server
    )
    runner = DedalusRunner(client)

    print("\n" + "=" * 60)
    print("LIAM Gmail MCP Client")
    print("Type your requests, or 'quit' to exit")
    print("=" * 60 + "\n")

    while True:
        try:
            prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not prompt or prompt.lower() in ("quit", "exit", "q"):
            break

        print("Agent: ", end="", flush=True)

        try:
            result = await with_oauth_retry(
                lambda p=prompt: runner.run(
                    input=p,
                    model="anthropic/claude-sonnet-4-20250514",
                    mcp_servers=[MCP_SERVER],
                )
            )

            print(result.final_output if hasattr(result, 'final_output') else result.output)

            if hasattr(result, 'mcp_results') and result.mcp_results:
                print("\n  [MCP Tools Called]")
                for r in result.mcp_results:
                    print(f"    - {r.tool_name} ({r.duration_ms}ms)")

        except Exception as e:
            print(f"\nError: {e}")

        print()


async def run_single_query(query: str) -> None:
    """Run a single query (for testing)."""
    client = AsyncDedalus(
        api_key=DEDALUS_API_KEY,
        base_url=DEDALUS_API_URL,
        as_base_url=DEDALUS_AS_URL,
    )
    runner = DedalusRunner(client)

    result = await with_oauth_retry(
        lambda: runner.run(
            input=query,
            model="anthropic/claude-sonnet-4-20250514",
            mcp_servers=[MCP_SERVER],
        )
    )

    print("=== Result ===")
    print(result.final_output if hasattr(result, 'final_output') else result.output)


async def main() -> None:
    """Main entry point."""
    import sys

    if len(sys.argv) > 1:
        # Run single query from command line
        query = " ".join(sys.argv[1:])
        await run_single_query(query)
    else:
        # Interactive mode
        await run_interactive()


if __name__ == "__main__":
    asyncio.run(main())

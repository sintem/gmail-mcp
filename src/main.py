# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""Entrypoint for LIAM Gmail MCP Server (doitliam.com)."""

import asyncio

from dotenv import load_dotenv

load_dotenv()

from server import main

if __name__ == "__main__":
    asyncio.run(main())

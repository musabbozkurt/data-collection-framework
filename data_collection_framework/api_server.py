#!/usr/bin/env python3
"""Starts the REST + GraphQL server (uvicorn). The command logic is shared with server.py (TCP)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))

import uvicorn  # noqa: E402

from data_collection_framework.api.app import create_app  # noqa: E402

if __name__ == "__main__":
    uvicorn.run(create_app(), host=os.environ.get("API_HOST", "127.0.0.1"),
                port=int(os.environ.get("API_PORT", "8000")), log_level="info")

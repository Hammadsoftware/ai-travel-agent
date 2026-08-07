"""Compatibility shim for flight-related tools.

Some code imports `web_search` from `app.agents.tools.flight_tool`.
This module re-exports the Tavily-based `web_search` tool so those imports work.
"""

from app.agents.tools.tavily_tool import web_search, web_search_impl

__all__ = ["web_search", "web_search_impl"]

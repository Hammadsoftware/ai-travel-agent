from tavily import TavilyClient
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def web_search_impl(query: str) -> str:
    """Search the web for recent and factual information (callable helper).

    This implementation is usable directly in scripts/tests. The agent-facing
    StructuredTool is exposed as `web_search_tool` and kept for compatibility.
    """
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True,
            include_raw_content=False,
            include_images=False,
        )

        answer = response.get("answer", "")
        results = response.get("results", [])

        formatted = f"Answer:\n{answer}\n\nSources:\n"

        for i, result in enumerate(results, 1):
            formatted += (
                f"\n{i}. {result.get('title','')}\n"
                f"URL: {result.get('url','')}\n"
                f"{result.get('content','')}\n"
            )

        return formatted

    except Exception as e:
        return f"Search error: {str(e)}"


# Agent-facing StructuredTool (kept for imports that expect `web_search`)
web_search_tool = tool(web_search_impl)
# Backwards compatibility: export name `web_search` as the StructuredTool
web_search = web_search_tool
    
from fastapi import FastAPI
from pydantic import BaseModel

try:
    from app.agents.tools.tavily_tool import web_search
except ModuleNotFoundError:  # pragma: no cover
    from agents.tools.tavily_tool import web_search

app = FastAPI()


class SearchRequest(BaseModel):
    query: str


@app.post("/search")
async def search(request: SearchRequest):
    result = web_search.invoke({"query": request.query})

    return {
        "query": request.query,
        "result": result
    }
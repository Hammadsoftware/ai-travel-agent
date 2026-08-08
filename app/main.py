from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

# Tavily Tool
try:
    from app.agents.tools.tavily_tool import web_search
except ModuleNotFoundError:
    from agents.tools.tavily_tool import web_search

# Flight Tool
try:
    from app.agents.tools.flight_tool import search_flights
except ModuleNotFoundError:
    from agents.tools.flight_tool import search_flights

# LangGraph
try:
    from app.agents import graph
except ModuleNotFoundError:
    from agents import graph


app = FastAPI()


class SearchRequest(BaseModel):
    query: str


@app.post("/search")
async def search(request: SearchRequest):
    result = web_search.invoke({
        "query": request.query
    })

    return {
        "query": request.query,
        "result": result
    }


@app.post("/airlineData")
async def airline_data(request: SearchRequest):
    result = search_flights.invoke({
        "query": request.query
    })

    return {
        "query": request.query,
        "result": result
    }


@app.post("/travel")
async def travel(request: SearchRequest):

    state = {
        "user_query": request.query,
        "messages": [
            HumanMessage(content=request.query)
        ],
        "llm_calls": 0,
    }

    result = graph.invoke(state)

    return {
        "user_query": request.query,
        "flight_result": result.get("flight_result"),
        "hotel_result": result.get("hotel_result"),
        "itinerary": result.get("itinerary"),
        "final_response": result["messages"][-1].content,
        "llm_calls": result.get("llm_calls"),
    }
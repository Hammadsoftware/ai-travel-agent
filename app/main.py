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

try:
    from app.visualizations.charts import build_flight_charts, build_hotel_charts, build_trip_stats
except ModuleNotFoundError:
    from visualizations.charts import build_flight_charts, build_hotel_charts, build_trip_stats


app = FastAPI()

# Health route (from app.api.routes.health)
try:
    from app.api.routes.health import router as health_router
except ModuleNotFoundError:
    from api.routes.health import router as health_router

app.include_router(health_router)


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

    flight_items = result.get("flight_items", [])
    hotel_items = result.get("hotel_items", [])
    trip_stats = build_trip_stats(flight_items, hotel_items)
    visualizations = {
        "flights": [chart.model_dump() for chart in build_flight_charts(flight_items)],
        "hotels": [chart.model_dump() for chart in build_hotel_charts(hotel_items)],
    }

    return {
        "user_query": request.query,
        "flight_result": result.get("flight_result"),
        "hotel_result": result.get("hotel_result"),
        "itinerary": result.get("itinerary"),
        "final_response": result["messages"][-1].content,
        "llm_calls": result.get("llm_calls"),
        "trip_stats": trip_stats,
        "visualizations": visualizations,
    }
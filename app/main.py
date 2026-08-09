
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from app.routers.auth import router as auth_router

# LangGraph
from app.agents import graph

from fastapi.middleware.cors import CORSMiddleware


# Visualizations
try:
    from app.visualizations.charts import (
        build_flight_charts,
        build_hotel_charts,
        build_trip_stats,
    )
except ModuleNotFoundError:
    from visualizations.charts import (
        build_flight_charts,
        build_hotel_charts,
        build_trip_stats,
    )


# =====================================================
# FastAPI
# =====================================================

app = FastAPI(
    title="AI Travel Agent API",
    description="LangGraph AI Travel Agent Backend",
    version="1.0.0",
)


# =====================================================
# Authentication Router
# =====================================================

app.include_router(auth_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# Request Schema
# =====================================================

class AIRequest(BaseModel):
    query: str


# =====================================================
# AI TRAVEL API
# =====================================================

@app.post("/ai")
async def ai(request: AIRequest):

    try:

        # ---------------------------------------------
        # LangGraph State
        # ---------------------------------------------

        state = {
            "user_query": request.query,
            "messages": [
                HumanMessage(content=request.query)
            ],
            "llm_calls": 0,
        }

        # ---------------------------------------------
        # Run LangGraph
        # ---------------------------------------------

        result = graph.invoke(state)

        # ---------------------------------------------
        # Extract Data
        # ---------------------------------------------

        flight_items = result.get(
            "flight_items",
            []
        )

        hotel_items = result.get(
            "hotel_items",
            []
        )

        flight_result = result.get(
            "flight_result"
        )

        hotel_result = result.get(
            "hotel_result"
        )

        itinerary = result.get(
            "itinerary",
            []
        )

        llm_calls = result.get(
            "llm_calls",
            0
        )

        # ---------------------------------------------
        # Trip Statistics
        # ---------------------------------------------

        trip_stats = build_trip_stats(
            flight_items,
            hotel_items
        )

        # ---------------------------------------------
        # Visualizations
        # ---------------------------------------------

        visualizations = {
            "flights": [
                chart.model_dump()
                for chart in build_flight_charts(
                    flight_items
                )
            ],

            "hotels": [
                chart.model_dump()
                for chart in build_hotel_charts(
                    hotel_items
                )
            ],
        }

        # ---------------------------------------------
        # Final AI Response
        # ---------------------------------------------

        messages = result.get(
            "messages",
            []
        )

        final_response = ""

        if messages:
            final_response = messages[-1].content

        # ---------------------------------------------
        # Response
        # ---------------------------------------------

        return {
            "success": True,

            "query": request.query,

            "response": final_response,

            "data": {
                "flights": {
                    "result": flight_result,
                    "items": flight_items,
                },

                "hotels": {
                    "result": hotel_result,
                    "items": hotel_items,
                },

                "itinerary": itinerary,

                "trip_stats": trip_stats,

                "visualizations": visualizations,
            },

            "meta": {
                "llm_calls": llm_calls,
            },
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


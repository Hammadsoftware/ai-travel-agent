from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.agents import graph

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
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# Authentication
# =====================================================

app.include_router(auth_router)


# =====================================================
# Request Schema
# =====================================================

class AIRequest(BaseModel):
    query: str


# =====================================================
# Health Check
# =====================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Travel Agent API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# =====================================================
# AI TRAVEL API
# =====================================================

@app.post("/ai")
async def ai(request: AIRequest):

    try:

        # ---------------------------------------------
        # Validate query
        # ---------------------------------------------

        query = request.query.strip()

        if not query:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty",
            )

        print(f"AI REQUEST: {query}")

        # ---------------------------------------------
        # LangGraph State
        # ---------------------------------------------

        state = {
            "user_query": query,
            "messages": [
                HumanMessage(content=query)
            ],
            "llm_calls": 0,
        }

        # ---------------------------------------------
        # Run LangGraph
        # ---------------------------------------------

        print("Starting LangGraph...")

        result = graph.invoke(state)

        print("LangGraph completed")

        # ---------------------------------------------
        # Extract Data
        # ---------------------------------------------

        flight_items = result.get(
            "flight_items",
            []
        ) or []

        hotel_items = result.get(
            "hotel_items",
            []
        ) or []

        flight_result = result.get(
            "flight_result"
        )

        hotel_result = result.get(
            "hotel_result"
        )

        itinerary = result.get(
            "itinerary",
            []
        ) or []

        llm_calls = result.get(
            "llm_calls",
            0
        )

        # ---------------------------------------------
        # Trip Statistics
        # ---------------------------------------------

        trip_stats = build_trip_stats(
            flight_items,
            hotel_items,
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
        ) or []

        final_response = ""

        if messages:

            last_message = messages[-1]

            if hasattr(last_message, "content"):
                final_response = last_message.content

            else:
                final_response = str(last_message)

        # ---------------------------------------------
        # Response
        # ---------------------------------------------

        return {
            "success": True,

            "query": query,

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

    except HTTPException:
        raise

    except Exception as e:

        # VERY IMPORTANT for Render logs
        print("====================================")
        print("AI ENDPOINT ERROR")
        print("====================================")
        print(type(e).__name__)
        print(str(e))
        print("====================================")

        raise HTTPException(
            status_code=500,
            detail=f"AI agent error: {str(e)}",
        )
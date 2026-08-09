import os
from typing import Any

import certifi
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# ==========================
# LangGraph Imports
# ==========================

from langgraph.graph import MessagesState, StateGraph, START, END

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq

from app.agents.tools.tavily_tool import web_search
from app.agents.tools.flight_tool import fetch_flights_data
from app.visualizations.schemas import FlightItem, HotelItem

# ==========================
# LLM
# ==========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
)

# ==========================
# State
# ==========================

class TravelState(MessagesState):
    user_query: str
    flight_result: str
    hotel_result: str
    itinerary: str
    llm_calls: int
    flight_items: list[dict[str, Any]]
    hotel_items: list[dict[str, Any]]


class HotelExtractionResult(BaseModel):
    hotels: list[HotelItem] = Field(default_factory=list)


def _format_flight_items(flight_items: list[dict[str, Any]]) -> str:
    if not flight_items:
        return "No flight information found."

    lines: list[str] = []
    for item in flight_items:
        lines.append(
            f"Airline: {item.get('airline')}\n"
            f"Flight: {item.get('flight_number')}\n"
            f"Status: {item.get('status')}\n"
            f"Departure: {item.get('origin')} at {item.get('departure_time')}\n"
            f"Arrival: {item.get('destination')} at {item.get('arrival_time')}\n"
            f"Duration: {item.get('duration_minutes')} minutes\n"
            f"Estimated price: {item.get('estimated_price')}"
        )

    return "\n\n".join(lines)


def _format_hotel_items(hotel_items: list[dict[str, Any]]) -> str:
    if not hotel_items:
        return "No hotel information found."

    lines: list[str] = []
    for item in hotel_items:
        lines.append(
            f"Hotel: {item.get('name')}\n"
            f"Area: {item.get('area')}\n"
            f"Category: {item.get('category')}\n"
            f"Rating: {item.get('rating')}\n"
            f"Price per night: {item.get('price_per_night')}\n"
            f"Booking link: {item.get('booking_url')}"
        )

    return "\n\n".join(lines)

# ==========================
# Flight Agent
# ==========================

def flight_agent(state: TravelState):
    user_query = state["user_query"]

    # Extract ONLY origin to destination
    response = llm.invoke([
        SystemMessage(
            content="""
Extract ONLY the flight route from the user's travel request.

Return ONLY a simple string in this format:

ORIGIN to DESTINATION

Examples:

"Plan a trip from Lahore to Dubai and find hotels"
Lahore to Dubai

"trip a plane from Lahore to Canada give budget airlines and hotels"
Lahore to Canada

"I want to travel from Karachi to London"
Karachi to London

"Book a flight from Islamabad to Istanbul next week"
Islamabad to Istanbul

"Plan my trip from Faisalabad to Toronto and find hotels"
Faisalabad to Toronto

Rules:
- Return ONLY origin and destination.
- Use the format: ORIGIN to DESTINATION
- Ignore hotels.
- Ignore budget.
- Ignore dates.
- Ignore airlines.
- Ignore sightseeing.
- Do not return JSON.
- Do not use quotes.
- Do not add explanation.
"""
        ),
        HumanMessage(content=user_query)
    ])

    # Clean extracted query
    flight_query = response.content.strip()

    flight_data = fetch_flights_data(flight_query)
    flight_items = [FlightItem.model_validate(item).model_dump() for item in flight_data]
    flight_summary = _format_flight_items(flight_items)

    return {
        "flight_items": flight_items,
        "flight_result": flight_summary,
        "messages": [
            AIMessage(
                content=f"Flight search completed for {flight_query}"
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
   
# ==========================
# Hotel Agent
# ==========================
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


def hotel_agent(state: TravelState):
    user_query = state["user_query"]

    # Extract ONLY destination
    response = llm.invoke([
        SystemMessage(
            content="""
Extract ONLY the destination from the user's travel request.

Return ONLY the destination as a simple string.

Examples:

"trip a plane from Lahore to Dubai"
Dubai

"plan a trip from Lahore to Canada and find hotels"
Canada

"travel from Karachi to London and book a hotel"
London

"trip from Islamabad to Istanbul"
Istanbul

Rules:
- Extract the final destination.
- Ignore the origin.
- Ignore flights.
- Ignore hotels.
- Ignore budget.
- Ignore dates.
- Ignore airlines.
- Return ONLY the destination.
- No JSON.
- No quotes.
- No explanation.
"""
        ),
        HumanMessage(content=user_query)
    ])

    destination = response.content.strip()

    # Search specifically for hotels and prices
    hotel_search_text = web_search.invoke({
        "query": f"""
Find hotels in {destination}.

Return useful hotel information including:
- Hotel name
- Location/area
- Approximate price per night
- Hotel rating if available
- Budget-friendly options
- Mid-range options
- Luxury options
- Booking/source link if available

Do NOT return flight information.
Do NOT return airline information.
Do NOT return flight prices.

Focus ONLY on hotels in {destination}.
"""
    })

    hotel_extractor = llm.with_structured_output(HotelExtractionResult)
    hotel_response = hotel_extractor.invoke([
        SystemMessage(content="Extract structured hotel listings from the search results. Return only hotels that appear relevant to the destination."),
        HumanMessage(content=f"Destination: {destination}\n\nSearch results:\n{hotel_search_text}"),
    ])

    if isinstance(hotel_response, HotelExtractionResult):
        hotel_items = [item.model_dump() for item in hotel_response.hotels]
    else:
        hotel_items = [item.model_dump() if hasattr(item, "model_dump") else dict(item) for item in hotel_response.get("hotels", [])]

    hotel_summary = _format_hotel_items(hotel_items)

    return {
        "hotel_items": hotel_items,
        "hotel_result": hotel_summary,
        "messages": state["messages"] + [
            AIMessage(
                content=f"Hotel results fetched for {destination}."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
# ==========================
# Itinerary Agent
# ==========================

def itinerary_agent(state: TravelState):
    user_query = state["user_query"]
    flight_result = state.get("flight_result", "No flight information found.")
    hotel_result = state.get("hotel_result", "No hotel information found.")

    prompt = f"""
You are an expert travel planner.

Create a complete travel itinerary using the following information.

User Request:
{user_query}
   
Flight Information:
{flight_result}

Hotel Information:
{hotel_result}

Generate a well-formatted itinerary with:

1. Trip Summary
2. Recommended Flight
3. Recommended Hotel
4. Day-by-Day Plan
5. Estimated Budget 
6. Travel Tips

Return the response in Markdown.
"""

    response = llm.invoke([
        SystemMessage(content="You are an expert travel planner."),
        HumanMessage(content=prompt),
    ])

    return {
        "itinerary": response.content,
        "messages": state["messages"] + [
            AIMessage(content="Travel itinerary created successfully.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ==========================
# Final Result Agent
# ==========================

def final_result_agent(state: TravelState):
    prompt = f"""
You are an AI Travel Assistant.

Prepare a final response for the user using the information below.

User Request:
{state["user_query"]}

Flight Details:
{state.get("flight_result", "Not available")}

Hotel Details:
{state.get("hotel_result", "Not available")}

Travel Itinerary:
{state.get("itinerary", "Not available")}

Instructions:
- Write in a friendly and professional tone.
- Use Markdown formatting.
- Include:
  1. Flight Recommendation
  2. Hotel Recommendation
  3. Complete Itinerary
  4. Important Travel Tips
- End with: "Have a safe and enjoyable trip! ✈️"
"""

    response = llm.invoke([
        SystemMessage(content="You are an expert AI Travel Assistant."),
        HumanMessage(content=prompt)
    ])

    return {
        "messages": state["messages"] + [
            AIMessage(content=response.content)
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
    # Create Graph
builder = StateGraph(TravelState)

# ==========================
# Add Nodes
# ==========================

builder.add_node("flight_agent", flight_agent)
builder.add_node("hotel_agent", hotel_agent)
builder.add_node("itinerary_agent", itinerary_agent)
builder.add_node("final_result_agent", final_result_agent)

# ==========================
# Add Edges
# ==========================

builder.add_edge(START, "flight_agent")
builder.add_edge("flight_agent", "hotel_agent")
builder.add_edge("hotel_agent", "itinerary_agent")
builder.add_edge("itinerary_agent", "final_result_agent")
builder.add_edge("final_result_agent", END)

# ==========================
# Compile Graph
# ==========================

graph = builder.compile()
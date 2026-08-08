import os
import certifi
from dotenv import load_dotenv

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

try:
    from app.agents.tools.tavily_tool import web_search
    from app.agents.tools.flight_tool import search_flights
except ModuleNotFoundError:
    from agents.tools.tavily_tool import web_search
    from agents.tools.flight_tool import search_flights

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

    # Send only:
    # "Lahore to Canada"
    flight_data = search_flights.invoke({
        "query": flight_query
    })

    return {
        "flight_result": flight_data,
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
    hotel_results = web_search.invoke({
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

    return {
        "hotel_result": hotel_results,
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
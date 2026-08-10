✈️ AI Travel Agent

🌐 Live Demo

An intelligent AI-powered travel planning backend built with FastAPI and LangGraph.

AI Travel Agent is an agentic AI travel assistant that understands natural-language travel requests and orchestrates multiple AI agents to search for flights, find hotels, generate itineraries, calculate trip statistics, and return visualization-ready data through a clean REST API.

The backend is designed for modern AI applications using LangGraph, LangChain, FastAPI, PostgreSQL/Neon, Groq, and Tavily.

🚀 Features

🤖 Agentic AI Travel Planning

🧠 LangGraph workflow orchestration

✈️ Flight search

🏨 Hotel search

🗺️ Automatic itinerary generation

📊 Trip statistics

📈 Plotly-ready visualizations

🔐 User signup & signin

🗄️ Neon PostgreSQL database

🔎 Tavily web search

⚡ Groq-powered LLM

🚀 FastAPI REST API

🐍 Python backend

📦 Modular agent architecture

🔌 Frontend-ready JSON responses

🏗️ Application Architecture

                         ┌──────────────────────┐
                         │     Next.js / Web     │
                         │       Frontend       │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP / JSON
                                    ▼
                    ┌──────────────────────────────┐
                    │          FastAPI             │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │ Authentication API     │  │
                    │  │                        │  │
                    │  │ POST /auth/signup      │  │
                    │  │ POST /auth/signin      │  │
                    │  └────────────────────────┘  │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │ AI Travel API          │  │
                    │  │                        │  │
                    │  │ POST /ai               │  │
                    │  └───────────┬────────────┘  │
                    └──────────────┼───────────────┘
                                   │
                                   ▼
                     ┌─────────────────────────┐
                     │       LangGraph         │
                     │    Agentic Workflow     │
                     └────────────┬────────────┘
                                  │
                ┌─────────────────┼──────────────────┐
                │                 │                  │
                ▼                 ▼                  ▼
       ┌────────────────┐ ┌───────────────┐ ┌────────────────┐
       │  Flight Agent  │ │  Hotel Agent  │ │  AI / LLM      │
       │                │ │               │ │                │
       │ Flight Search  │ │ Hotel Search  │ │ Groq           │
       └───────┬────────┘ └───────┬───────┘ └───────┬────────┘
               │                  │                 │
               └──────────────────┼─────────────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Travel Response   │
                       │                     │
                       │ • Flights           │
                       │ • Hotels            │
                       │ • Itinerary         │
                       │ • Statistics        │
                       │ • Visualizations    │
                       └──────────┬──────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Neon PostgreSQL │
                         │                 │
                         │ Users           │
                         │ Conversations   │
                         │ Messages        │
                         └─────────────────┘

🧠 Agentic AI Workflow

The system uses LangGraph to orchestrate the travel-planning workflow.

A typical request:

"Plan a trip from Lahore to Dubai"

is processed through the agent workflow.

User Query
    │
    ▼
FastAPI /ai
    │
    ▼
LangGraph
    │
    ├──────────────► Flight Agent
    │                    │
    │                    ▼
    │              Flight Search
    │
    ├──────────────► Hotel Agent
    │                    │
    │                    ▼
    │              Hotel Search
    │
    └──────────────► AI Processing
                         │
                         ▼
                    Trip Planning
                         │
                         ▼
                  Itinerary Generation
                         │
                         ▼
                 Statistics & Charts
                         │
                         ▼
                    Final Response

🔄 Request Flow

1. User sends travel request
              ↓
2. FastAPI receives request
              ↓
3. LangGraph initializes state
              ↓
4. Agents analyze the request
              ↓
5. Flight information is collected
              ↓
6. Hotel information is collected
              ↓
7. LLM generates travel information
              ↓
8. Itinerary is generated
              ↓
9. Trip statistics are calculated
              ↓
10. Visualization data is generated
              ↓
11. Structured JSON response returned

🛠️ Tech Stack

Backend

Technology

Purpose

Python

Backend language

FastAPI

REST API framework

Uvicorn

ASGI server

Pydantic

Request validation

Psycopg 3

PostgreSQL database connection

Psycopg Pool

Database connection pooling

AI / Agentic AI

Technology

Purpose

LangGraph

Agent workflow orchestration

LangChain

LLM/agent framework

LangChain Groq

Groq integration

Groq

LLM inference

Tavily

Web search

Database

Technology

Purpose

PostgreSQL

Relational database

Neon

Serverless PostgreSQL

Psycopg

Python PostgreSQL driver

Visualization

Technology

Purpose

Plotly

Interactive chart generation

Custom chart services

Flight/hotel/trip visualizations

📁 Project Structure

ai-travel-agent/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── database.py
│   ├── models.py
│   ├── test_db.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   │
│   │   └── tools/
│   │       ├── tavily_tool.py
│   │       └── flight_tool.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py
│   │
│   └── visualizations/
│       ├── __init__.py
│       └── charts.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md

🔐 Authentication

The API provides basic authentication endpoints.

Signup

POST /auth/signup

Request:

{
  "name": "Hammad",
  "email": "hammad@example.com",
  "password": "123456"
}

Response:

{
  "message": "Signup successful",
  "user": {
    "id": 1,
    "name": "Hammad",
    "email": "hammad@example.com",
    "created_at": "..."
  }
}

Signin

POST /auth/signin

Request:

{
  "email": "hammad@example.com",
  "password": "123456"
}

Response:

{
  "message": "Signin successful",
  "user": {
    "id": 1,
    "name": "Hammad",
    "email": "hammad@example.com"
  }
}

🤖 AI Travel API

POST /ai

The main AI endpoint.

Request:

{
  "query": "Plan a trip from Lahore to Dubai"
}

The LangGraph workflow processes the request and returns structured travel information.

Example response structure:

{
  "success": true,
  "query": "Plan a trip from Lahore to Dubai",
  "response": "Here is your travel plan...",
  "data": {
    "flights": {
      "result": "...",
      "items": []
    },
    "hotels": {
      "result": "...",
      "items": []
    },
    "itinerary": [],
    "trip_stats": {},
    "visualizations": {
      "flights": [],
      "hotels": []
    }
  },
  "meta": {
    "llm_calls": 3
  }
}

🗄️ Database Architecture

The application uses Neon PostgreSQL.

                    ┌──────────────┐
                    │    users     │
                    ├──────────────┤
                    │ id           │
                    │ name         │
                    │ email        │
                    │ password     │
                    │ created_at   │
                    └──────┬───────┘
                           │
                           │ user_id
                           ▼
                ┌─────────────────────┐
                │   conversations     │
                ├─────────────────────┤
                │ id                  │
                │ user_id             │
                │ title               │
                │ created_at          │
                └──────────┬──────────┘
                           │
                           │ conversation_id
                           ▼
                    ┌──────────────┐
                    │   messages   │
                    ├──────────────┤
                    │ id           │
                    │ conversation │
                    │ role         │
                    │ content      │
                    │ created_at   │
                    └──────────────┘

Database relationships

User
 │
 └─── 1 : N ─── Conversations
                    │
                    └─── 1 : N ─── Messages

⚙️ Environment Variables

Create a .env file:

DATABASE_URL=your_neon_database_url

GROQ_API_KEY=your_groq_api_key

TAVILY_API_KEY=your_tavily_api_key

⚠️ Never commit .env to GitHub.

Add this to .gitignore:

.env
.venv/
__pycache__/
*.pyc

📦 Installation

1. Clone the repository

git clone https://github.com/Hammadsoftware/ai-travel-agent.git

cd ai-travel-agent

2. Create virtual environment

python3 -m venv .venv

3. Activate environment

Linux / macOS

source .venv/bin/activate

Windows

.venv\Scripts\activate

4. Install dependencies

pip install -r requirements.txt

🗄️ Database Setup

Make sure your .env contains your Neon PostgreSQL connection string:

DATABASE_URL=postgresql://...

Test the connection:

python -m app.test_db

Expected:

Database connected successfully!
PostgreSQL 18.x

Create the application tables:

python -m app.models

Expected:

Database tables created successfully!

▶️ Run the Application

Start the FastAPI server:

python -m uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

Alternative documentation:

http://127.0.0.1:8000/redoc

📡 API Overview

Method

Endpoint

Description

POST

/auth/signup

Create a new user

POST

/auth/signin

Authenticate user

POST

/ai

AI travel planning

The backend intentionally keeps the public API minimal:

/auth/signup
/auth/signin
/ai

🧩 AI Components

Flight Agent

Responsible for understanding flight-related requests and retrieving flight information.

User Query
    ↓
Flight Agent
    ↓
Flight Tool
    ↓
Flight Data

Hotel Agent

Responsible for extracting the destination and retrieving hotel information.

User Query
    ↓
Hotel Agent
    ↓
Hotel Search
    ↓
Hotel Data

Web Search

Tavily provides web search capabilities for travel-related information.

AI Agent
   ↓
Tavily
   ↓
Web Results
   ↓
Agent Processing

📊 Visualization System

The application generates frontend-ready visualization data.

Supported visualization categories include:

Flight Charts
     │
     ├── Flight comparisons
     └── Flight statistics

Hotel Charts
     │
     ├── Hotel comparisons
     └── Hotel statistics

Trip Statistics
     │
     ├── Flight information
     ├── Hotel information
     └── Overall trip data

The response contains Plotly-compatible data so the frontend can render interactive charts.

🔌 Frontend Integration

The backend is designed to work with a modern frontend such as Next.js.

Example:

const response = await fetch(
  "https://your-api-url.com/ai",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      query: "Plan a trip from Lahore to Dubai"
    })
  }
);

const data = await response.json();

Access the AI response:

data.response

Flights:

data.data.flights

Hotels:

data.data.hotels

Itinerary:

data.data.itinerary

Trip statistics:

data.data.trip_stats

Visualizations:

data.data.visualizations

☁️ Deployment Architecture

Recommended production architecture:

                    Internet
                       │
                       ▼
              ┌─────────────────┐
              │     Vercel      │
              │    Next.js      │
              │    Frontend     │
              └────────┬────────┘
                       │
                       │ HTTPS
                       ▼
              ┌─────────────────┐
              │    Railway      │
              │                 │
              │    FastAPI      │
              │    LangGraph    │
              └───────┬─────────┘
                      │
          ┌───────────┼────────────┐
          │           │            │
          ▼           ▼            ▼
       ┌──────┐   ┌──────┐    ┌─────────┐
       │ Neon │   │ Groq │    │ Tavily  │
       │ DB   │   │ LLM  │    │ Search  │
       └──────┘   └──────┘    └─────────┘

Recommended services

Frontend: Vercel

Backend: Railway

Database: Neon PostgreSQL

LLM: Groq

Web Search: Tavily

🔒 Security Notes

For production deployment:

Store secrets in environment variables.

Never commit .env.

Never expose API keys to the frontend.

Use HTTPS.

Add proper authentication tokens/JWT.

Hash passwords before production use.

Validate user input.

Add rate limiting to AI endpoints.

Restrict CORS to trusted frontend domains.

🚧 Future Improvements

Planned improvements include:

JWT authentication

Secure password hashing

Conversation history

Persistent AI chat sessions

Streaming AI responses

Real-time agent updates

More travel APIs

Flight booking integration

Hotel booking integration

User travel history

Saved trips

Multi-destination planning

Budget optimization

Personalized recommendations

Production monitoring

Rate limiting

Automated tests

🎯 Use Cases

AI Travel Agent can be used for:

✈️ Flight Planning

"Find flights from Lahore to Dubai"

🏨 Hotel Planning

"Find hotels in Dubai"

🗺️ Complete Trip Planning

"Plan a 5-day trip from Lahore to Dubai"

💰 Budget Travel

"Plan a budget trip from Lahore to Istanbul"

🌍 International Travel

"Plan a trip from Pakistan to France"

The agent can transform natural-language requests into structured travel information.

🧠 Why LangGraph?

LangGraph provides a stateful framework for building complex agentic workflows.

Instead of using a single LLM call:

User
 ↓
LLM
 ↓
Response

this application uses:

User
 ↓
LangGraph
 ↓
Agent Workflow
 ├── Flight Agent
 ├── Hotel Agent
 ├── Search
 ├── Planning
 └── Visualization
 ↓
Final AI Response

This makes the system easier to extend with additional agents, tools, memory, and decision-making logic.

📈 Project Vision

The goal is to evolve this backend into a complete AI travel planning platform where users can:

Ask
 ↓
Plan
 ↓
Compare
 ↓
Customize
 ↓
Save
 ↓
Book

The architecture is designed so additional travel agents and external services can be added without rewriting the entire backend.

👨‍💻 Author

Hammad Tariq

Backend / AI Developer

Focused on:

Python
FastAPI
LangChain
LangGraph
Agentic AI
Next.js
PostgreSQL
Cloud Deployment

⭐ Contributing

Contributions, ideas, and improvements are welcome.

Fork the repository

Create a feature branch

git checkout -b feature/new-feature

Commit your changes

git commit -m "add new feature"

Push the branch

git push origin feature/new-feature

Open a Pull Request

📄 License

This project is available for educational and development purposes.


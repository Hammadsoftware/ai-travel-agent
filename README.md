# HackathonAI

## FastAPI Server

This project includes a FastAPI app structured under [app](app), with the main entry point in [app/main.py](app/main.py).

### Setup and run the server

1. Create and activate a virtual environment:

```bash
cd /Project
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Start the server:

```bash
python -m uvicorn app.main:app --reload
```

The server will be available at:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/health

### Endpoints

- GET `/` → returns a welcome message
- GET `/health` → returns the server status
- POST `/travel` → returns flight and hotel summaries, itinerary, `trip_stats`, and Plotly-ready `visualizations`

### Project structure

- [app/api](app/api) for routes and dependencies
- [app/schemas](app/schemas) for request/response models
- [app/models](app/models) for data models
- [app/services](app/services) for business logic
- [app/repositories](app/repositories) for database access logic
- [app/core](app/core) for shared config and utilities

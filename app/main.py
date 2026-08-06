from fastapi import FastAPI

app = FastAPI(
    title="My FastAPI API",
    description="Backend API using FastAPI",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI!"}



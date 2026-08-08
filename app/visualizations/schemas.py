from typing import Any, Literal

from pydantic import BaseModel, Field


class FlightItem(BaseModel):
    airline: str
    flight_number: str | None = None
    origin: str | None = None
    destination: str | None = None
    departure_time: str | None = None
    arrival_time: str | None = None
    departure_hour: int | None = None
    duration_minutes: int | None = None
    estimated_price: float | None = None
    status: str | None = None


class HotelItem(BaseModel):
    name: str
    price_per_night: float | None = None
    rating: float | None = None
    area: str | None = None
    category: str | None = None
    booking_url: str | None = None


class ChartPayload(BaseModel):
    type: Literal["bar", "scatter", "pie", "donut", "line"]
    title: str
    data: list[dict[str, Any]]
    layout: dict[str, Any]
    config: dict[str, Any] = Field(default_factory=dict)
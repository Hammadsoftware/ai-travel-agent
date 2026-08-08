from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from .builder import build_bar_chart, build_pie_chart, build_scatter_chart
from .schemas import ChartPayload, FlightItem, HotelItem


def _normalize_flight_items(flights: list[dict[str, Any]] | list[FlightItem]) -> list[FlightItem]:
    return [item if isinstance(item, FlightItem) else FlightItem.model_validate(item) for item in flights]


def _normalize_hotel_items(hotels: list[dict[str, Any]] | list[HotelItem]) -> list[HotelItem]:
    return [item if isinstance(item, HotelItem) else HotelItem.model_validate(item) for item in hotels]


def build_flight_charts(flights: list[dict[str, Any]] | list[FlightItem]) -> list[ChartPayload]:
    flight_items = _normalize_flight_items(flights)
    if not flight_items:
        return []

    price_by_airline: dict[str, list[float]] = defaultdict(list)
    duration_by_airline: dict[str, list[float]] = defaultdict(list)
    scatter_rows: list[FlightItem] = []

    for item in flight_items:
        if item.estimated_price is not None:
            price_by_airline[item.airline].append(float(item.estimated_price))
        if item.duration_minutes is not None:
            duration_by_airline[item.airline].append(float(item.duration_minutes))
        if item.departure_hour is not None and item.estimated_price is not None:
            scatter_rows.append(item)

    charts: list[ChartPayload] = []

    if price_by_airline:
        airlines = list(price_by_airline.keys())
        avg_prices = [round(mean(values), 2) for values in price_by_airline.values()]
        charts.append(
            build_bar_chart(
                "Estimated Flight Price by Airline",
                airlines,
                avg_prices,
                x_title="Airline",
                y_title="Estimated price",
            )
        )

    if duration_by_airline:
        airlines = list(duration_by_airline.keys())
        avg_durations = [round(mean(values), 2) for values in duration_by_airline.values()]
        charts.append(
            build_bar_chart(
                "Flight Duration by Airline",
                airlines,
                avg_durations,
                x_title="Airline",
                y_title="Average duration (minutes)",
                color="#7c3aed",
            )
        )

    if scatter_rows:
        charts.append(
            build_scatter_chart(
                "Departure Hour vs Estimated Flight Price",
                [item.departure_hour for item in scatter_rows],
                [item.estimated_price for item in scatter_rows],
                text=[item.airline for item in scatter_rows],
                x_title="Departure hour",
                y_title="Estimated price",
            )
        )

    return charts


def build_hotel_charts(hotels: list[dict[str, Any]] | list[HotelItem]) -> list[ChartPayload]:
    hotel_items = _normalize_hotel_items(hotels)
    if not hotel_items:
        return []

    priced_hotels = [item for item in hotel_items if item.price_per_night is not None]
    rated_hotels = [item for item in hotel_items if item.price_per_night is not None and item.rating is not None]

    charts: list[ChartPayload] = []

    if priced_hotels:
        charts.append(
            build_bar_chart(
                "Hotel Price per Night",
                [item.name for item in priced_hotels],
                [float(item.price_per_night) for item in priced_hotels],
                x_title="Hotel",
                y_title="Price per night",
                color="#ea580c",
            )
        )

    if rated_hotels:
        charts.append(
            build_scatter_chart(
                "Hotel Rating vs Price",
                [float(item.rating) for item in rated_hotels],
                [float(item.price_per_night) for item in rated_hotels],
                text=[item.name for item in rated_hotels],
                x_title="Rating",
                y_title="Price per night",
                color="#0f766e",
            )
        )

    category_counts: dict[str, int] = defaultdict(int)
    for item in hotel_items:
        category_counts[(item.category or "Uncategorized").title()] += 1

    charts.append(
        build_pie_chart(
            "Hotel Mix by Category",
            list(category_counts.keys()),
            list(category_counts.values()),
            hole=0.45,
            colors=["#2563eb", "#0f766e", "#ea580c", "#7c3aed"],
        )
    )

    area_counts: dict[str, int] = defaultdict(int)
    for item in hotel_items:
        area_counts[(item.area or "Unknown area").title()] += 1

    charts.append(
        build_bar_chart(
            "Hotel Count by Area",
            list(area_counts.keys()),
            list(area_counts.values()),
            x_title="Area",
            y_title="Hotel count",
            color="#14b8a6",
        )
    )

    return charts


def build_trip_stats(
    flights: list[dict[str, Any]] | list[FlightItem],
    hotels: list[dict[str, Any]] | list[HotelItem],
) -> dict[str, Any]:
    flight_items = _normalize_flight_items(flights)
    hotel_items = _normalize_hotel_items(hotels)

    flight_prices = [item.estimated_price for item in flight_items if item.estimated_price is not None]
    hotel_prices = [item.price_per_night for item in hotel_items if item.price_per_night is not None]

    return {
        "total_flights_found": len(flight_items),
        "cheapest_flight_price": round(min(flight_prices), 2) if flight_prices else None,
        "total_hotels_found": len(hotel_items),
        "avg_hotel_price": round(mean(hotel_prices), 2) if hotel_prices else None,
    }
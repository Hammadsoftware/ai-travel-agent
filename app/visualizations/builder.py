"""Plotly figure helpers.

Presentation note: layout/config are intentionally produced server-side for
now, so color, spacing, and sizing changes require a backend redeploy.
"""

from __future__ import annotations

from typing import Any, Iterable

import plotly.graph_objects as go

from .schemas import ChartPayload


def _payload_from_figure(
    figure: go.Figure,
    chart_type: str,
    title: str,
    config: dict[str, Any] | None = None,
) -> ChartPayload:
    figure_json = figure.to_plotly_json()
    return ChartPayload(
        type=chart_type,
        title=title,
        data=figure_json["data"],
        layout=figure_json["layout"],
        config=config or {"responsive": True},
    )


def build_bar_chart(
    title: str,
    x: Iterable[Any],
    y: Iterable[Any],
    *,
    x_title: str,
    y_title: str,
    color: str = "#2563eb",
    orientation: str = "v",
) -> ChartPayload:
    figure = go.Figure(
        data=[
            go.Bar(
                x=list(x),
                y=list(y),
                marker_color=color,
                orientation=orientation,
            )
        ]
    )
    figure.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white",
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
    )
    return _payload_from_figure(figure, "bar", title)


def build_scatter_chart(
    title: str,
    x: Iterable[Any],
    y: Iterable[Any],
    *,
    x_title: str,
    y_title: str,
    text: Iterable[Any] | None = None,
    color: str = "#0f766e",
) -> ChartPayload:
    scatter = go.Scatter(
        x=list(x),
        y=list(y),
        mode="markers",
        text=list(text) if text is not None else None,
        marker={"size": 12, "color": color, "opacity": 0.85},
    )
    figure = go.Figure(data=[scatter])
    figure.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white",
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
    )
    return _payload_from_figure(figure, "scatter", title)


def build_pie_chart(
    title: str,
    labels: Iterable[Any],
    values: Iterable[Any],
    *,
    hole: float = 0.0,
    colors: list[str] | None = None,
) -> ChartPayload:
    figure = go.Figure(
        data=[
            go.Pie(
                labels=list(labels),
                values=list(values),
                hole=hole,
                marker={"colors": colors} if colors else None,
            )
        ]
    )
    figure.update_layout(
        title=title,
        template="plotly_white",
        margin={"l": 30, "r": 30, "t": 60, "b": 30},
    )
    chart_type = "donut" if hole and hole > 0 else "pie"
    return _payload_from_figure(figure, chart_type, title)
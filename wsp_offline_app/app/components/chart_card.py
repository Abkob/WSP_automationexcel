from __future__ import annotations

from dataclasses import dataclass

import plotly.graph_objects as go

from services.analytics_service import ChartPoint


CHART_COLORS = ("#1f6f8b", "#2f7d57", "#b7791f", "#7c3aed", "#c2410c", "#0f766e")


@dataclass(frozen=True)
class ChartSpec:
    title: str
    chart_type: str
    points: tuple[ChartPoint, ...]


def build_bar_figure(points: tuple[ChartPoint, ...], *, title: str) -> go.Figure:
    figure = go.Figure(
        data=[
            go.Bar(
                x=[point.value for point in points],
                y=[point.label for point in points],
                orientation="h",
                marker_color=CHART_COLORS[0],
            )
        ]
    )
    return style_figure(figure, title=title, height=calculate_bar_height(points))


def build_pie_figure(points: tuple[ChartPoint, ...], *, title: str) -> go.Figure:
    figure = go.Figure(
        data=[
            go.Pie(
                labels=[point.label for point in points],
                values=[point.value for point in points],
                marker={"colors": CHART_COLORS},
                hole=0.35,
            )
        ]
    )
    return style_figure(figure, title=title)


def style_figure(figure: go.Figure, *, title: str, height: int = 260) -> go.Figure:
    figure.update_layout(
        title=None,
        margin={"l": 24, "r": 16, "t": 8, "b": 36},
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=True,
        font={"family": "Inter, Arial, sans-serif", "size": 12, "color": "#1f2933"},
    )
    figure.update_xaxes(title=None)
    figure.update_yaxes(title=None, autorange="reversed")
    figure.update_traces(hovertemplate="%{label}: %{value}<extra></extra>", selector={"type": "pie"})
    figure.update_traces(hovertemplate="%{y}: %{x}<extra></extra>", selector={"type": "bar"})
    figure.layout.meta = {"title": title}
    return figure


def calculate_bar_height(points: tuple[ChartPoint, ...]) -> int:
    return max(260, min(520, 88 + len(points) * 34))


def build_chart_alt_text(spec: ChartSpec, *, max_points: int = 5) -> str:
    if not spec.points:
        return f"{spec.title}: no data."
    visible_points = spec.points[:max_points]
    summary = ", ".join(f"{point.label} {point.value}" for point in visible_points)
    if len(spec.points) > max_points:
        summary = f"{summary}, and {len(spec.points) - max_points} more"
    return f"{spec.title}: {summary}."


def render_chart_card(ui_module, spec: ChartSpec) -> None:
    with ui_module.card().classes("rounded-md shadow-sm border border-gray-100 p-4"):
        ui_module.label(spec.title).classes("text-sm font-semibold text-gray-800")
        ui_module.label(build_chart_alt_text(spec)).classes("sr-only")
        if not spec.points:
            ui_module.label("No data").classes("text-sm text-gray-500 py-8")
            return
        figure = build_pie_figure(spec.points, title=spec.title) if spec.chart_type == "pie" else build_bar_figure(spec.points, title=spec.title)
        ui_module.plotly(figure).classes("w-full")

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricCardData:
    label: str
    value: str
    icon: str
    tone: str = "primary"


TONE_CLASSES = {
    "primary": "text-primary",
    "positive": "text-positive",
    "warning": "text-accent",
    "negative": "text-negative",
}


def render_metric_card(ui_module, metric: MetricCardData) -> None:
    icon_class = TONE_CLASSES.get(metric.tone, TONE_CLASSES["primary"])
    with ui_module.card().classes("rounded-md shadow-sm border border-gray-100 p-4 min-h-[104px]"):
        with ui_module.row().classes("w-full items-start justify-between gap-3"):
            with ui_module.column().classes("gap-1"):
                ui_module.label(metric.label).classes("text-xs uppercase text-gray-500")
                ui_module.label(metric.value).classes("text-2xl font-semibold text-gray-900")
            ui_module.icon(metric.icon).classes(f"text-2xl {icon_class}")

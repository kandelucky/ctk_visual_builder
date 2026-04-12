import tkinter as tk

import customtkinter as ctk

from app.core.project import Project
from app.widgets.registry import get_descriptor


class Workspace(ctk.CTkFrame):
    def __init__(self, master, project: Project):
        super().__init__(master)
        self.project = project
        self.widget_views: dict[str, tuple] = {}

        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.bind("<Button-1>", self._on_canvas_click)

        bus = self.project.event_bus
        bus.subscribe("widget_added", self._on_widget_added)
        bus.subscribe("widget_removed", self._on_widget_removed)
        bus.subscribe("property_changed", self._on_property_changed)
        bus.subscribe("selection_changed", self._on_selection_changed)

        self._selection_rect: int | None = None

    def _on_widget_added(self, node) -> None:
        descriptor = get_descriptor(node.widget_type)
        if descriptor is None:
            return
        widget = descriptor.create_widget(self.canvas, node.properties)
        window_id = self.canvas.create_window(node.x, node.y, anchor="nw", window=widget)
        self.widget_views[node.id] = (widget, window_id)
        widget.bind("<Button-1>",
                    lambda e, nid=node.id: self.project.select_widget(nid),
                    add="+")

    def _on_widget_removed(self, widget_id: str) -> None:
        if widget_id not in self.widget_views:
            return
        widget, window_id = self.widget_views.pop(widget_id)
        self.canvas.delete(window_id)
        widget.destroy()

    def _on_property_changed(self, widget_id: str, prop_name: str, value) -> None:
        if widget_id not in self.widget_views:
            return
        widget, _ = self.widget_views[widget_id]
        try:
            widget.configure(**{prop_name: value})
        except Exception:
            pass
        if widget_id == self.project.selected_id:
            self.after(10, self._draw_selection)

    def _on_canvas_click(self, event) -> None:
        if event.widget is self.canvas:
            self.project.select_widget(None)

    def _on_selection_changed(self, widget_id: str | None) -> None:
        self._draw_selection()

    def _draw_selection(self) -> None:
        if self._selection_rect is not None:
            self.canvas.delete(self._selection_rect)
            self._selection_rect = None

        sid = self.project.selected_id
        if sid is None or sid not in self.widget_views:
            return
        widget, window_id = self.widget_views[sid]
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(window_id)
        if bbox is None:
            return
        x1, y1, x2, y2 = bbox
        pad = 3
        self._selection_rect = self.canvas.create_rectangle(
            x1 - pad, y1 - pad, x2 + pad, y2 + pad,
            outline="#3b8ed0", width=2, dash=(4, 2),
        )

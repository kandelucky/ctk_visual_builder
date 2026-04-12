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
        self._drag: dict | None = None

    def _on_widget_added(self, node) -> None:
        descriptor = get_descriptor(node.widget_type)
        if descriptor is None:
            return
        widget = descriptor.create_widget(self.canvas, node.properties)
        x = int(node.properties.get("x", 0))
        y = int(node.properties.get("y", 0))
        window_id = self.canvas.create_window(x, y, anchor="nw", window=widget)
        self.widget_views[node.id] = (widget, window_id)

        nid = node.id
        widget.bind("<ButtonPress-1>",
                    lambda e, n=nid: self._on_widget_press(e, n), add="+")
        widget.bind("<B1-Motion>",
                    lambda e, n=nid: self._on_widget_motion(e, n), add="+")
        widget.bind("<ButtonRelease-1>",
                    lambda e, n=nid: self._on_widget_release(e, n), add="+")

    def _on_widget_press(self, event, nid: str) -> None:
        self.project.select_widget(nid)
        node = self.project.get_widget(nid)
        if node is None:
            return
        try:
            wx = int(node.properties.get("x", 0))
            wy = int(node.properties.get("y", 0))
        except (ValueError, TypeError):
            wx, wy = 0, 0
        canvas_rx = self.canvas.winfo_rootx()
        canvas_ry = self.canvas.winfo_rooty()
        mx_canvas = event.x_root - canvas_rx
        my_canvas = event.y_root - canvas_ry
        self._drag = {
            "nid": nid,
            "offset_x": mx_canvas - wx,
            "offset_y": my_canvas - wy,
            "press_mx": event.x_root,
            "press_my": event.y_root,
            "moved": False,
        }

    def _on_widget_motion(self, event, nid: str) -> None:
        if self._drag is None or self._drag["nid"] != nid:
            return
        if not self._drag["moved"]:
            if (abs(event.x_root - self._drag["press_mx"]) < 5
                    and abs(event.y_root - self._drag["press_my"]) < 5):
                return
            self._drag["moved"] = True
        canvas_rx = self.canvas.winfo_rootx()
        canvas_ry = self.canvas.winfo_rooty()
        new_x = event.x_root - canvas_rx - self._drag["offset_x"]
        new_y = event.y_root - canvas_ry - self._drag["offset_y"]
        self.project.update_property(nid, "x", new_x)
        self.project.update_property(nid, "y", new_y)

    def _on_widget_release(self, _event, _nid: str) -> None:
        self._drag = None

    def _on_widget_removed(self, widget_id: str) -> None:
        if widget_id not in self.widget_views:
            return
        widget, window_id = self.widget_views.pop(widget_id)
        self.canvas.delete(window_id)
        widget.destroy()

    def _on_property_changed(self, widget_id: str, prop_name: str, value) -> None:
        if widget_id not in self.widget_views:
            return
        widget, window_id = self.widget_views[widget_id]
        node = self.project.get_widget(widget_id)

        if prop_name in ("x", "y") and node is not None:
            try:
                x = int(node.properties.get("x", 0))
                y = int(node.properties.get("y", 0))
                self.canvas.coords(window_id, x, y)
            except Exception:
                pass
            if widget_id == self.project.selected_id:
                self.after(10, self._draw_selection)
            return

        descriptor = get_descriptor(node.widget_type) if node else None

        triggers = getattr(descriptor, "derived_triggers", None) if descriptor else None
        if descriptor and triggers and prop_name in triggers and hasattr(descriptor, "compute_derived"):
            try:
                derived = descriptor.compute_derived(node.properties)
            except Exception:
                derived = {}
            for k, v in derived.items():
                if node.properties.get(k) != v:
                    self.project.update_property(widget_id, k, v)

        try:
            if descriptor is not None:
                transformed = descriptor.transform_properties(node.properties)
                if transformed:
                    widget.configure(**transformed)
            else:
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

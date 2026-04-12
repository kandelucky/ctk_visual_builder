import tkinter as tk
from tkinter import colorchooser

import customtkinter as ctk

from app.core.project import Project
from app.widgets.registry import get_descriptor


class PropertiesPanel(ctk.CTkFrame):
    def __init__(self, master, project: Project):
        super().__init__(master, width=280)
        self.project = project
        self.grid_propagate(False)
        self.current_id: str | None = None
        self._color_buttons: dict[str, ctk.CTkButton] = {}
        self._suspend_trace = False

        title = ctk.CTkLabel(self, text="Properties", font=("", 14, "bold"))
        title.pack(pady=(12, 8), padx=10)

        self.body = ctk.CTkScrollableFrame(self)
        self.body.pack(fill="both", expand=True, padx=8, pady=8)

        self._show_empty()

        self.project.event_bus.subscribe("selection_changed", self._on_selection)

    def _on_selection(self, widget_id: str | None) -> None:
        self.current_id = widget_id
        self._rebuild()

    def _clear_body(self) -> None:
        for child in self.body.winfo_children():
            child.destroy()
        self._color_buttons = {}

    def _show_empty(self) -> None:
        self._clear_body()
        ctk.CTkLabel(self.body, text="No selection", text_color="gray").pack(pady=20)

    def _rebuild(self) -> None:
        if self.current_id is None:
            self._show_empty()
            return

        node = self.project.get_widget(self.current_id)
        if node is None:
            self._show_empty()
            return

        descriptor = get_descriptor(node.widget_type)
        if descriptor is None:
            self._show_empty()
            return

        self._clear_body()

        type_label = ctk.CTkLabel(self.body, text=descriptor.type_name,
                                  font=("", 12, "bold"), text_color="#3b8ed0")
        type_label.pack(pady=(0, 8), padx=4, anchor="w")

        for prop in descriptor.property_schema:
            self._build_editor(prop, node.properties.get(prop["name"]))

    def _build_editor(self, prop: dict, value) -> None:
        row = ctk.CTkFrame(self.body, fg_color="transparent")
        row.pack(fill="x", pady=3, padx=2)

        label = ctk.CTkLabel(row, text=prop["label"], width=100, anchor="w")
        label.pack(side="left")

        ptype = prop["type"]
        pname = prop["name"]

        if ptype == "string":
            var = tk.StringVar(value="" if value is None else str(value))
            entry = ctk.CTkEntry(row, textvariable=var)
            entry.pack(side="left", fill="x", expand=True)
            var.trace_add("write",
                          lambda *_, p=pname, v=var: self._update(p, v.get()))

        elif ptype == "number":
            var = tk.StringVar(value="" if value is None else str(value))
            entry = ctk.CTkEntry(row, textvariable=var, width=80)
            entry.pack(side="left")

            def on_change(*_, p=pname, v=var):
                if self._suspend_trace:
                    return
                text = v.get().strip()
                if not text:
                    return
                try:
                    self._update(p, int(text))
                except ValueError:
                    pass

            var.trace_add("write", on_change)

        elif ptype == "color":
            color_value = value if value else "#1f6aa5"
            btn = ctk.CTkButton(
                row,
                text=str(color_value),
                fg_color=color_value,
                hover_color=color_value,
                width=140,
                command=lambda p=pname: self._pick_color(p),
            )
            btn.pack(side="left")
            self._color_buttons[pname] = btn

    def _pick_color(self, prop_name: str) -> None:
        node = self.project.get_widget(self.current_id) if self.current_id else None
        initial = node.properties.get(prop_name) if node else None
        result = colorchooser.askcolor(color=initial)
        if result and result[1]:
            hex_value = result[1]
            self._update(prop_name, hex_value)
            btn = self._color_buttons.get(prop_name)
            if btn is not None:
                btn.configure(fg_color=hex_value, hover_color=hex_value, text=hex_value)

    def _update(self, prop_name: str, value) -> None:
        if self.current_id is None:
            return
        self.project.update_property(self.current_id, prop_name, value)

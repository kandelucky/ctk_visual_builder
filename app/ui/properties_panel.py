import os
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

from app.core.project import Project
from app.utils.color_picker_dialog import ColorPickerDialog
from app.widgets.registry import get_descriptor

ANCHOR_GRID = [
    ["nw", "n", "ne"],
    ["w", "center", "e"],
    ["sw", "s", "se"],
]
COMPOUND_OPTIONS = ["top", "left", "right", "bottom"]
ANCHOR_SELECTED_COLOR = "#3b8ed0"
ANCHOR_UNSELECTED_COLOR = "#3a3a3a"


class PropertiesPanel(ctk.CTkFrame):
    def __init__(self, master, project: Project):
        super().__init__(master, width=280)
        self.project = project
        self.grid_propagate(False)
        self.current_id: str | None = None
        self._color_buttons: dict[str, ctk.CTkButton] = {}
        self._anchor_groups: dict[str, dict[str, ctk.CTkButton]] = {}
        self._image_labels: dict[str, ctk.CTkLabel] = {}
        self._editor_vars: dict[str, tk.StringVar] = {}
        self._row_padx: int = 2
        self._suspend_trace = False

        title = ctk.CTkLabel(self, text="Properties", font=("", 13, "bold"))
        title.pack(pady=(5, 2), padx=10)

        self.body = ctk.CTkScrollableFrame(self)
        self.body.pack(fill="both", expand=True, padx=6, pady=(0, 4))

        self._show_empty()

        self.project.event_bus.subscribe("selection_changed", self._on_selection)
        self.project.event_bus.subscribe("property_changed", self._on_property_changed)

    def _on_selection(self, widget_id: str | None) -> None:
        self.current_id = widget_id
        self._rebuild()

    def _on_property_changed(self, widget_id: str, prop_name: str, value) -> None:
        if widget_id != self.current_id:
            return
        if prop_name == "font_autofit":
            self._rebuild()
            return
        var = self._editor_vars.get(prop_name)
        if var is None:
            return
        if isinstance(var, ctk.CTkTextbox):
            new_text = "" if value is None else str(value)
            current = var.get("1.0", "end-1c")
            if current == new_text:
                return
            self._suspend_trace = True
            try:
                var.delete("1.0", "end")
                if new_text:
                    var.insert("1.0", new_text)
            finally:
                self._suspend_trace = False
            return
        if isinstance(var, tk.BooleanVar):
            new_val = bool(value)
            if var.get() == new_val:
                return
            self._suspend_trace = True
            try:
                var.set(new_val)
            finally:
                self._suspend_trace = False
            return
        new_text = "" if value is None else str(value)
        if var.get() == new_text:
            return
        self._suspend_trace = True
        try:
            var.set(new_text)
        finally:
            self._suspend_trace = False

    def _clear_body(self) -> None:
        for child in self.body.winfo_children():
            child.destroy()
        self._color_buttons = {}
        self._anchor_groups = {}
        self._image_labels = {}
        self._editor_vars = {}

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
                                  font=("", 11, "bold"), text_color="#3b8ed0",
                                  height=14)
        type_label.pack(pady=(0, 2), padx=4, anchor="w")

        schema = descriptor.property_schema
        current_group = None
        current_subgroup = None
        self._row_padx = 2
        i = 0
        while i < len(schema):
            prop = schema[i]
            group = prop.get("group", "General")
            if group != current_group:
                self._build_group_header(group)
                current_group = group
                current_subgroup = None
                self._row_padx = 2

            subgroup = prop.get("subgroup")
            if subgroup != current_subgroup:
                if subgroup:
                    self._build_subgroup_header(subgroup)
                    self._row_padx = 14
                else:
                    self._row_padx = 2
                current_subgroup = subgroup

            pair_id = prop.get("pair")
            if pair_id:
                items = []
                j = i
                while j < len(schema) and schema[j].get("pair") == pair_id:
                    items.append((schema[j], node.properties.get(schema[j]["name"])))
                    j += 1
                self._build_paired_row(items)
                i = j
            else:
                self._build_editor(prop, node.properties.get(prop["name"]))
                i += 1

    def _build_group_header(self, name: str) -> None:
        wrap = ctk.CTkFrame(self.body, fg_color="transparent", height=14)
        wrap.pack(fill="x", pady=(12, 2), padx=2)
        wrap.pack_propagate(False)
        header = ctk.CTkLabel(
            wrap,
            text=name.upper(),
            font=("", 9, "bold"),
            text_color="#888888",
            anchor="w",
            height=14,
        )
        header.pack(side="left", padx=(2, 6))
        sep = ctk.CTkFrame(wrap, height=1, fg_color="#3a3a3a")
        sep.pack(side="left", fill="x", expand=True, pady=(6, 0))

    def _build_subgroup_header(self, name: str) -> None:
        header = ctk.CTkLabel(
            self.body,
            text=name,
            font=("", 9, "bold"),
            text_color="#aaaaaa",
            anchor="w",
            height=12,
        )
        header.pack(fill="x", pady=(2, 1), padx=4)

    def _build_paired_row(self, items: list) -> None:
        row = ctk.CTkFrame(self.body, fg_color="transparent")
        row.pack(fill="x", pady=1, padx=self._row_padx)
        for i, (prop, value) in enumerate(items):
            cell = ctk.CTkFrame(row, fg_color="transparent")
            cell.pack(side="left", padx=(0 if i == 0 else 6, 0))
            self._build_editor(prop, value, parent=cell, compact=True)

    def _build_editor(self, prop: dict, value, parent=None,
                      compact: bool = False) -> None:
        if parent is None:
            parent = ctk.CTkFrame(self.body, fg_color="transparent")
            parent.pack(fill="x", pady=1, padx=self._row_padx)

        label_w = prop.get("label_width") or (38 if compact else 70)
        entry_w = 52 if compact else 70
        color_w = 65 if compact else 110
        font = ("", 10)

        label = ctk.CTkLabel(parent, text=prop["label"], width=label_w,
                             anchor="w", font=font, height=18)
        label.pack(side="left", anchor="n", pady=(2, 0))

        ptype = prop["type"]
        pname = prop["name"]

        if ptype == "string":
            var = tk.StringVar(value="" if value is None else str(value))
            entry = ctk.CTkEntry(parent, textvariable=var, height=22, font=font)
            entry.pack(side="left", fill="x", expand=True)

            def on_string_change(*_, p=pname, v=var):
                if self._suspend_trace:
                    return
                self._update(p, v.get())

            var.trace_add("write", on_string_change)
            self._editor_vars[pname] = var

        elif ptype == "multiline":
            tb = ctk.CTkTextbox(
                parent,
                height=58,
                font=font,
                wrap="word",
                border_width=1,
                border_color="#5a5a5a",
                corner_radius=4,
            )
            tb.pack(side="left", fill="x", expand=True)
            if value is not None and value != "":
                tb.insert("1.0", str(value))

            def on_multiline_change(_e=None, p=pname, t=tb):
                if self._suspend_trace:
                    return
                text = t.get("1.0", "end-1c")
                self._update(p, text)

            tb.bind("<KeyRelease>", on_multiline_change)
            self._editor_vars[pname] = tb

        elif ptype == "number":
            disabled = self._eval_disabled(prop)
            var = tk.StringVar(value="" if value is None else str(value))
            entry = ctk.CTkEntry(parent, textvariable=var, width=entry_w,
                                 height=22, font=font,
                                 state="disabled" if disabled else "normal")
            entry.pack(side="left")

            if disabled:
                label.configure(text_color="#555555")
            else:
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
                self._make_label_draggable(label, var, prop)
            self._editor_vars[pname] = var

        elif ptype == "boolean":
            var = tk.BooleanVar(value=bool(value))
            cb_text = prop.get("checkbox_text", "")
            cb = ctk.CTkCheckBox(
                parent,
                text=cb_text,
                variable=var,
                height=16,
                checkbox_width=14,
                checkbox_height=14,
                corner_radius=2,
                border_width=2,
                font=font,
                command=lambda p=pname, v=var: self._update(p, v.get()),
            )
            cb.pack(side="left", padx=(0, 4), pady=(1, 0))
            self._editor_vars[pname] = var

        elif ptype == "color":
            color_value = value if value else "#1f6aa5"
            btn = ctk.CTkButton(
                parent,
                text=str(color_value),
                fg_color=color_value,
                hover_color=color_value,
                width=color_w,
                height=20,
                font=font,
                border_width=1,
                border_color="#666666",
                command=lambda p=pname: self._pick_color(p),
            )
            btn.pack(side="left")
            self._color_buttons[pname] = btn

        elif ptype == "anchor":
            self._build_anchor_editor(parent, pname, value or "center")

        elif ptype == "compound":
            self._build_compound_editor(parent, pname, value or "left")

        elif ptype == "image":
            self._build_image_editor(parent, pname, value)

    def _build_anchor_editor(self, row, prop_name: str, current: str) -> None:
        grid = ctk.CTkFrame(row, fg_color="transparent")
        grid.pack(side="left")
        buttons: dict[str, ctk.CTkButton] = {}
        for r, row_anchors in enumerate(ANCHOR_GRID):
            for c, anchor in enumerate(row_anchors):
                is_sel = anchor == current
                btn = ctk.CTkButton(
                    grid,
                    text="•" if is_sel else "",
                    width=16, height=12,
                    corner_radius=2,
                    fg_color=ANCHOR_SELECTED_COLOR if is_sel else ANCHOR_UNSELECTED_COLOR,
                    hover_color="#4a9ee0",
                    border_width=0,
                    font=("", 8),
                    command=lambda a=anchor, p=prop_name: self._set_anchor(p, a),
                )
                btn.grid(row=r, column=c, padx=1, pady=1)
                buttons[anchor] = btn
        self._anchor_groups[prop_name] = buttons

    def _build_compound_editor(self, row, prop_name: str, current: str) -> None:
        menu = ctk.CTkOptionMenu(
            row,
            values=COMPOUND_OPTIONS,
            width=110,
            height=22,
            font=("", 10),
            dropdown_font=("", 10),
            command=lambda v, p=prop_name: self._update(p, v),
        )
        menu.set(current if current in COMPOUND_OPTIONS else "left")
        menu.pack(side="left")

    def _build_image_editor(self, row, prop_name: str, current: str | None) -> None:
        sub = ctk.CTkFrame(row, fg_color="transparent")
        sub.pack(side="left", fill="x", expand=True)

        name_label = ctk.CTkLabel(
            sub,
            text=self._image_display_name(current),
            anchor="w",
            text_color="gray",
            font=("", 9),
            height=12,
        )
        name_label.pack(fill="x")
        self._image_labels[prop_name] = name_label

        btn_row = ctk.CTkFrame(sub, fg_color="transparent")
        btn_row.pack(fill="x", pady=(1, 0))

        browse = ctk.CTkButton(
            btn_row, text="Browse...", width=70, height=20, font=("", 10),
            command=lambda p=prop_name: self._pick_image(p),
        )
        browse.pack(side="left", padx=(0, 4))

        clear = ctk.CTkButton(
            btn_row, text="Clear", width=44, height=20, font=("", 10),
            fg_color="#555555", hover_color="#6a6a6a",
            command=lambda p=prop_name: self._clear_image(p),
        )
        clear.pack(side="left")

    def _set_anchor(self, prop_name: str, anchor: str) -> None:
        self._update(prop_name, anchor)
        buttons = self._anchor_groups.get(prop_name, {})
        for a, btn in buttons.items():
            is_sel = a == anchor
            btn.configure(
                text="•" if is_sel else "",
                fg_color=ANCHOR_SELECTED_COLOR if is_sel else ANCHOR_UNSELECTED_COLOR,
            )

    def _image_display_name(self, value: str | None) -> str:
        if not value:
            return "(no image)"
        return os.path.basename(value)

    def _pick_image(self, prop_name: str) -> None:
        path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        self._update(prop_name, path)
        lbl = self._image_labels.get(prop_name)
        if lbl is not None:
            lbl.configure(text=self._image_display_name(path))

    def _clear_image(self, prop_name: str) -> None:
        self._update(prop_name, None)
        lbl = self._image_labels.get(prop_name)
        if lbl is not None:
            lbl.configure(text=self._image_display_name(None))

    def _eval_disabled(self, prop: dict) -> bool:
        fn = prop.get("disabled_when")
        if not callable(fn):
            return False
        if self.current_id is None:
            return False
        node = self.project.get_widget(self.current_id)
        if node is None:
            return False
        try:
            return bool(fn(node.properties))
        except Exception:
            return False

    def _resolve_bound(self, bound) -> int | None:
        if bound is None:
            return None
        if callable(bound):
            if self.current_id is None:
                return None
            node = self.project.get_widget(self.current_id)
            if node is None:
                return None
            try:
                return int(bound(node.properties))
            except Exception:
                return None
        try:
            return int(bound)
        except (ValueError, TypeError):
            return None

    def _make_label_draggable(self, label: ctk.CTkLabel, var: tk.StringVar,
                              prop: dict) -> None:
        prop_name = prop["name"]
        state = {"dragging": False, "last_x": 0, "current": 0, "accumulator": 0.0}

        def set_cursor(cursor: str) -> None:
            try:
                label.configure(cursor=cursor)
            except Exception:
                pass

        def on_enter(_e):
            if not state["dragging"]:
                set_cursor("sb_h_double_arrow")

        def on_leave(_e):
            if not state["dragging"]:
                set_cursor("")

        def on_press(e):
            value = 0
            if self.current_id is not None:
                node = self.project.get_widget(self.current_id)
                if node is not None:
                    try:
                        value = int(node.properties.get(prop_name, 0))
                    except (ValueError, TypeError):
                        value = 0
            state["current"] = value
            state["last_x"] = e.x_root
            state["accumulator"] = 0.0
            state["dragging"] = True

        def on_motion(e):
            if not state["dragging"]:
                return
            dx = e.x_root - state["last_x"]
            state["last_x"] = e.x_root
            slow = bool(e.state & 0x20000)
            sensitivity = 0.2 if slow else 1.0
            state["accumulator"] += dx * sensitivity
            delta = int(state["accumulator"])
            if delta == 0:
                return
            state["accumulator"] -= delta
            new_val = state["current"] + delta
            min_val = self._resolve_bound(prop.get("min"))
            max_val = self._resolve_bound(prop.get("max"))
            if min_val is not None and new_val < min_val:
                new_val = min_val
            if max_val is not None and new_val > max_val:
                new_val = max_val
            if new_val == state["current"]:
                return
            state["current"] = new_val
            var.set(str(new_val))

        def on_release(_e):
            state["dragging"] = False
            set_cursor("")

        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
        label.bind("<ButtonPress-1>", on_press)
        label.bind("<B1-Motion>", on_motion)
        label.bind("<ButtonRelease-1>", on_release)

    def _pick_color(self, prop_name: str) -> None:
        node = self.project.get_widget(self.current_id) if self.current_id else None
        initial = (node.properties.get(prop_name) if node else None) or "#1f6aa5"
        dialog = ColorPickerDialog(self.winfo_toplevel(), initial_color=initial)
        dialog.wait_window()
        hex_value = dialog.result
        if hex_value:
            self._update(prop_name, hex_value)
            btn = self._color_buttons.get(prop_name)
            if btn is not None:
                btn.configure(fg_color=hex_value, hover_color=hex_value, text=hex_value)

    def _update(self, prop_name: str, value) -> None:
        if self.current_id is None:
            return
        self.project.update_property(self.current_id, prop_name, value)

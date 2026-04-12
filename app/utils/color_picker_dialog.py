import colorsys
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk

from app.utils.color_history import ColorHistory


SV_W = 260
SV_H = 185
SV_REND_W = 130
SV_REND_H = 92

HUE_W = 260
HUE_H = 18

LIGHT_W = 260
LIGHT_H = 18

SWATCH_W = 96
SWATCH_H = 24

SAVED_PER_ROW = 10
SAVED_TOTAL = 20
SAVED_BTN = 18

GRAYSCALE_COUNT = 13
GRAY_BTN_W = 20
GRAY_BTN_H = 16


class ColorPickerDialog(ctk.CTkToplevel):
    def __init__(self, master, initial_color: str = "#1f6aa5"):
        super().__init__(master)
        self.title("Color Picker")
        self.resizable(False, False)
        self.transient(master)

        self.result: str | None = None
        self._initial = initial_color or "#1f6aa5"
        self._history = ColorHistory()

        self._hue = 0.0
        self._saturation = 0.0
        self._value = 0.0
        self._set_from_hex(self._initial)

        try:
            self._scale = ctk.ScalingTracker.get_window_scaling(self) or 1.0
        except Exception:
            self._scale = 1.0
        self._sv_w = int(SV_W * self._scale)
        self._sv_h = int(SV_H * self._scale)
        self._hue_w = int(HUE_W * self._scale)
        self._hue_h = int(HUE_H * self._scale)
        self._light_w = int(LIGHT_W * self._scale)
        self._light_h = int(LIGHT_H * self._scale)

        self._sv_photo: ImageTk.PhotoImage | None = None
        self._hue_photo: ImageTk.PhotoImage | None = None
        self._light_photo: ImageTk.PhotoImage | None = None
        self._saved_swatches: dict[str, ctk.CTkButton] = {}
        self._recent_slots: list[ctk.CTkButton] = []
        self._tint_swatches: list[ctk.CTkButton] = []
        self._suspend_hex = False

        self._build_ui()
        self._render_hue()
        self._render_sv()
        self._render_lightness()
        self._update_preview()
        self._refresh_recents()

        self.update_idletasks()
        self._center_on_parent(master)

        self.after(50, self._grab)
        self.after(500, self._debug_dump_sizes)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind("<Escape>", lambda _e: self._on_cancel())

    def _debug_dump_sizes(self) -> None:
        try:
            self.update_idletasks()
            print(f"[ColorPicker] dialog: {self.winfo_width()}x{self.winfo_height()}")
            print(f"[ColorPicker] sv_canvas: {self.sv_canvas.winfo_width()}x{self.sv_canvas.winfo_height()}")
            print(f"[ColorPicker] hue_canvas: {self.hue_canvas.winfo_width()}x{self.hue_canvas.winfo_height()}")
            print(f"[ColorPicker] light_canvas: {self.light_canvas.winfo_width()}x{self.light_canvas.winfo_height()}")
            print(f"[ColorPicker] new_swatch: {self.new_swatch.winfo_width()}x{self.new_swatch.winfo_height()}")
        except Exception as e:
            print(f"[ColorPicker] debug error: {e}")

    def _grab(self) -> None:
        try:
            self.grab_set()
            self.focus_force()
        except Exception:
            pass

    def _center_on_parent(self, master) -> None:
        try:
            master.update_idletasks()
            mx = master.winfo_rootx()
            my = master.winfo_rooty()
            mw = master.winfo_width()
            mh = master.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = mx + (mw - w) // 2
            y = my + (mh - h) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(padx=4, pady=12)

        compare_row = ctk.CTkFrame(container, fg_color="transparent")
        compare_row.pack(pady=(0, 12))

        ctk.CTkLabel(compare_row, text="New", font=("", 10),
                     text_color="#888", width=28, anchor="w").pack(side="left")
        self.new_swatch = ctk.CTkFrame(
            compare_row, width=SWATCH_W, height=SWATCH_H,
            fg_color=self._initial,
            border_width=1, border_color="#666666", corner_radius=8,
        )
        self.new_swatch.pack(side="left", padx=(0, 12))
        self.new_swatch.pack_propagate(False)

        ctk.CTkLabel(compare_row, text="Old", font=("", 10),
                     text_color="#888", width=28, anchor="w").pack(side="left")
        self.old_swatch = ctk.CTkFrame(
            compare_row, width=SWATCH_W, height=SWATCH_H,
            fg_color=self._initial,
            border_width=1, border_color="#666666", corner_radius=8,
        )
        self.old_swatch.pack(side="left")
        self.old_swatch.pack_propagate(False)

        gray_row = ctk.CTkFrame(container, fg_color="transparent")
        gray_row.pack(pady=(0, 12))
        for i in range(GRAYSCALE_COUNT):
            btn = ctk.CTkButton(
                gray_row, text="",
                width=GRAY_BTN_W, height=GRAY_BTN_H,
                fg_color="#000000", hover_color="#000000",
                border_width=0,
                corner_radius=0,
                command=lambda idx=i: self._click_tint(idx),
            )
            btn.pack(side="left", padx=0)
            self._tint_swatches.append(btn)

        self.sv_canvas = tk.Canvas(
            container, width=self._sv_w, height=self._sv_h,
            highlightthickness=1, highlightbackground="#666666",
            bd=0, bg="#1e1e1e", cursor="crosshair",
        )
        self.sv_canvas.pack()
        self.sv_canvas.bind("<Button-1>", self._on_sv_drag)
        self.sv_canvas.bind("<B1-Motion>", self._on_sv_drag)

        self.light_canvas = tk.Canvas(
            container, width=self._light_w, height=self._light_h,
            highlightthickness=1, highlightbackground="#666666",
            bd=0, bg="#1e1e1e", cursor="sb_h_double_arrow",
        )
        self.light_canvas.pack(pady=(12, 0))
        self.light_canvas.bind("<Button-1>", self._on_lightness_drag)
        self.light_canvas.bind("<B1-Motion>", self._on_lightness_drag)

        self.hue_canvas = tk.Canvas(
            container, width=self._hue_w, height=self._hue_h,
            highlightthickness=1, highlightbackground="#666666",
            bd=0, bg="#1e1e1e", cursor="sb_h_double_arrow",
        )
        self.hue_canvas.pack(pady=(8, 0))
        self.hue_canvas.bind("<Button-1>", self._on_hue_drag)
        self.hue_canvas.bind("<B1-Motion>", self._on_hue_drag)

        hex_row = ctk.CTkFrame(container, fg_color="transparent")
        hex_row.pack(pady=(10, 0), fill="x")

        ctk.CTkLabel(hex_row, text="Hex", font=("", 10), width=28,
                     anchor="w").pack(side="left")

        self.hex_var = tk.StringVar(value=self._initial)
        self.hex_entry = ctk.CTkEntry(
            hex_row, textvariable=self.hex_var,
            height=26, font=("", 11), corner_radius=8,
        )
        self.hex_entry.pack(side="left", fill="x", expand=True)
        self.hex_entry.bind("<Return>", lambda _e: self._on_hex_commit())
        self.hex_entry.bind("<FocusOut>", lambda _e: self._on_hex_commit())

        saved_header = ctk.CTkFrame(container, fg_color="transparent")
        saved_header.pack(fill="x", pady=(14, 4))
        ctk.CTkLabel(
            saved_header, text="SAVED COLORS",
            font=("", 10, "bold"), text_color="#888888", anchor="w",
        ).pack(side="left")
        ctk.CTkButton(
            saved_header, text="+", width=24, height=22,
            font=("", 14, "bold"), corner_radius=8,
            fg_color="#3a3a3a", hover_color="#4a4a4a",
            command=self._save_current,
        ).pack(side="right")

        self.recents_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.recents_frame.pack(fill="x")
        self._build_recents_slots()

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(pady=(14, 0), fill="x")

        ctk.CTkButton(
            btn_row, text="OK", height=30,
            corner_radius=8,
            command=self._on_ok,
        ).pack(fill="x")

    def _make_sv_image(self) -> Image.Image:
        h_byte = min(255, max(0, int(self._hue * 255)))
        data = bytearray(SV_REND_W * SV_REND_H * 3)
        idx = 0
        for y in range(SV_REND_H):
            v_byte = int(255 * (1 - y / (SV_REND_H - 1)))
            for x in range(SV_REND_W):
                s_byte = int(255 * x / (SV_REND_W - 1))
                data[idx] = h_byte
                data[idx + 1] = s_byte
                data[idx + 2] = v_byte
                idx += 3
        img = Image.frombytes("HSV", (SV_REND_W, SV_REND_H), bytes(data))
        img = img.convert("RGB")
        return img.resize((self._sv_w, self._sv_h), Image.BILINEAR)

    def _make_hue_image(self) -> Image.Image:
        w = self._hue_w
        h = self._hue_h
        row = bytearray()
        for x in range(w):
            h_byte = min(255, int(255 * x / (w - 1)))
            row.extend([h_byte, 255, 255])
        data = bytes(row) * h
        img = Image.frombytes("HSV", (w, h), data)
        return img.convert("RGB")

    def _make_lightness_image(self) -> Image.Image:
        w = self._light_w
        h = self._light_h
        r, g, b = colorsys.hsv_to_rgb(self._hue, self._saturation, self._value)
        h_hls, _, s_hls = colorsys.rgb_to_hls(r, g, b)
        row = bytearray()
        for x in range(w):
            l = x / (w - 1)
            rr, gg, bb = colorsys.hls_to_rgb(h_hls, l, s_hls)
            row.extend([int(rr * 255), int(gg * 255), int(bb * 255)])
        data = bytes(row) * h
        return Image.frombytes("RGB", (w, h), data)

    def _render_sv(self) -> None:
        img = self._make_sv_image()
        self._sv_photo = ImageTk.PhotoImage(img)
        self.sv_canvas.delete("gradient")
        self.sv_canvas.create_image(
            0, 0, anchor="nw", image=self._sv_photo, tags="gradient",
        )
        self._draw_sv_indicator()

    def _render_hue(self) -> None:
        img = self._make_hue_image()
        self._hue_photo = ImageTk.PhotoImage(img)
        self.hue_canvas.delete("gradient")
        self.hue_canvas.create_image(
            0, 0, anchor="nw", image=self._hue_photo, tags="gradient",
        )
        self._draw_hue_indicator()

    def _render_lightness(self) -> None:
        img = self._make_lightness_image()
        self._light_photo = ImageTk.PhotoImage(img)
        self.light_canvas.delete("gradient")
        self.light_canvas.create_image(
            0, 0, anchor="nw", image=self._light_photo, tags="gradient",
        )
        self._draw_lightness_indicator()

    def _draw_sv_indicator(self) -> None:
        cx = int(self._saturation * (self._sv_w - 1))
        cy = int((1 - self._value) * (self._sv_h - 1))
        r = max(7, int(7 * self._scale))
        self.sv_canvas.delete("indicator")
        self.sv_canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline="white", width=2, tags="indicator",
        )
        self.sv_canvas.create_oval(
            cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1,
            outline="black", width=1, tags="indicator",
        )

    def _draw_hue_indicator(self) -> None:
        cx = int(self._hue * (self._hue_w - 1))
        self.hue_canvas.delete("indicator")
        self.hue_canvas.create_rectangle(
            cx - 2, 0, cx + 2, self._hue_h,
            outline="white", width=2, tags="indicator",
        )

    def _draw_lightness_indicator(self) -> None:
        r, g, b = colorsys.hsv_to_rgb(self._hue, self._saturation, self._value)
        _, l, _ = colorsys.rgb_to_hls(r, g, b)
        cx = int(l * (self._light_w - 1))
        self.light_canvas.delete("indicator")
        self.light_canvas.create_rectangle(
            cx - 2, 0, cx + 2, self._light_h,
            outline="white", width=2, tags="indicator",
        )

    def _on_sv_drag(self, event) -> None:
        x = max(0, min(self._sv_w - 1, event.x))
        y = max(0, min(self._sv_h - 1, event.y))
        self._saturation = x / (self._sv_w - 1)
        self._value = 1 - y / (self._sv_h - 1)
        self._draw_sv_indicator()
        self._render_lightness()
        self._update_preview()

    def _on_hue_drag(self, event) -> None:
        x = max(0, min(self._hue_w - 1, event.x))
        self._hue = x / (self._hue_w - 1)
        self._render_sv()
        self._render_lightness()
        self._draw_hue_indicator()
        self._update_preview()

    def _on_lightness_drag(self, event) -> None:
        x = max(0, min(self._light_w - 1, event.x))
        new_l = x / (self._light_w - 1)
        r, g, b = colorsys.hsv_to_rgb(self._hue, self._saturation, self._value)
        h_hls, _, s_hls = colorsys.rgb_to_hls(r, g, b)
        nr, ng, nb = colorsys.hls_to_rgb(h_hls, new_l, s_hls)
        new_h, new_s, new_v = colorsys.rgb_to_hsv(nr, ng, nb)
        self._hue = new_h
        self._saturation = new_s
        self._value = new_v
        self._draw_sv_indicator()
        self._draw_lightness_indicator()
        self._update_preview()

    def _on_hex_commit(self) -> None:
        if self._suspend_hex:
            return
        text = self.hex_var.get().strip()
        if not text.startswith("#"):
            text = "#" + text
        if len(text) != 7:
            return
        try:
            int(text[1:], 16)
        except ValueError:
            return
        self._load_color(text.lower())

    def _load_color(self, hex_str: str) -> None:
        self._set_from_hex(hex_str)
        self._render_sv()
        self._render_hue()
        self._render_lightness()
        self._update_preview()

    def _set_from_hex(self, hex_str: str) -> None:
        s = (hex_str or "").strip().lstrip("#")
        if len(s) != 6:
            return
        try:
            r = int(s[0:2], 16) / 255
            g = int(s[2:4], 16) / 255
            b = int(s[4:6], 16) / 255
        except ValueError:
            return
        h, sat, val = colorsys.rgb_to_hsv(r, g, b)
        self._hue = h
        self._saturation = sat
        self._value = val

    def _current_hex(self) -> str:
        r, g, b = colorsys.hsv_to_rgb(self._hue, self._saturation, self._value)
        return "#{:02x}{:02x}{:02x}".format(
            round(r * 255), round(g * 255), round(b * 255))

    def _update_preview(self) -> None:
        hex_color = self._current_hex()
        try:
            self.new_swatch.configure(fg_color=hex_color)
        except Exception:
            pass
        self._suspend_hex = True
        try:
            self.hex_var.set(hex_color)
        finally:
            self._suspend_hex = False
        self._update_recent_highlight()
        self._update_tints()

    def _build_recents_slots(self) -> None:
        for child in self.recents_frame.winfo_children():
            child.destroy()
        self._recent_slots = []

        row1 = ctk.CTkFrame(self.recents_frame, fg_color="transparent")
        row1.pack()
        row2 = ctk.CTkFrame(self.recents_frame, fg_color="transparent")
        row2.pack(pady=(4, 0))

        for i in range(SAVED_TOTAL):
            target = row1 if i < SAVED_PER_ROW else row2
            slot = ctk.CTkButton(
                target, text="",
                width=SAVED_BTN, height=SAVED_BTN,
                fg_color="#2a2a2a", hover_color="#2a2a2a",
                border_width=1, border_color="#3a3a3a",
                corner_radius=2,
                command=lambda: None,
            )
            slot.pack(side="left", padx=3)
            self._recent_slots.append(slot)

    def _refresh_recents(self) -> None:
        self._saved_swatches = {}
        recents = self._history.all()
        for i, slot in enumerate(self._recent_slots):
            if i < len(recents):
                color = recents[i]
                slot.configure(
                    fg_color=color, hover_color=color,
                    border_color="#666666", border_width=1,
                    command=lambda c=color: self._load_color(c),
                )
                self._saved_swatches[color] = slot
            else:
                slot.configure(
                    fg_color="#2a2a2a", hover_color="#2a2a2a",
                    border_color="#3a3a3a", border_width=1,
                    command=lambda: None,
                )
        self._update_recent_highlight()

    def _update_recent_highlight(self) -> None:
        current = self._current_hex()
        for color, btn in self._saved_swatches.items():
            if color == current:
                btn.configure(border_color="#ffffff", border_width=3)
            else:
                btn.configure(border_color="#666666", border_width=1)

    def _compute_tint_colors(self) -> list[str]:
        r, g, b = colorsys.hsv_to_rgb(self._hue, self._saturation, self._value)
        h_hls, current_l, s_hls = colorsys.rgb_to_hls(r, g, b)

        range_width = 0.5
        half = range_width / 2
        l_min = current_l - half
        l_max = current_l + half
        if l_max > 1.0:
            l_min -= (l_max - 1.0)
            l_max = 1.0
        if l_min < 0.0:
            l_max += (0.0 - l_min)
            l_min = 0.0
        l_min = max(0.0, l_min)
        l_max = min(1.0, l_max)

        colors = []
        for i in range(GRAYSCALE_COUNT):
            l = l_max - (l_max - l_min) * i / (GRAYSCALE_COUNT - 1)
            rr, gg, bb = colorsys.hls_to_rgb(h_hls, l, s_hls)
            colors.append("#{:02x}{:02x}{:02x}".format(
                round(rr * 255), round(gg * 255), round(bb * 255)))
        return colors

    def _update_tints(self) -> None:
        colors = self._compute_tint_colors()
        for btn, color in zip(self._tint_swatches, colors):
            try:
                btn.configure(fg_color=color, hover_color=color)
            except Exception:
                pass

    def _click_tint(self, index: int) -> None:
        colors = self._compute_tint_colors()
        if 0 <= index < len(colors):
            self._load_color(colors[index])

    def _save_current(self) -> None:
        self._history.add(self._current_hex())
        self._refresh_recents()

    def _on_ok(self) -> None:
        color = self._current_hex()
        self._history.add(color)
        self.result = color
        self._release_and_destroy()

    def _on_cancel(self) -> None:
        self.result = None
        self._release_and_destroy()

    def _release_and_destroy(self) -> None:
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

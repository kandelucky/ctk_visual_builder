import customtkinter as ctk

from app.widgets.base import WidgetDescriptor


class CTkButtonDescriptor(WidgetDescriptor):
    type_name = "CTkButton"
    display_name = "Button"

    default_properties = {
        "x": 120,
        "y": 120,
        "width": 140,
        "height": 32,
        "corner_radius": 6,
        "border_width": 0,
        "fg_color": "#1f6aa5",
        "hover_color": "#144870",
        "text_color": "#ffffff",
        "text": "CTkButton",
        "anchor": "center",
        "font_size": 13,
        "font_bold": False,
        "font_autofit": False,
        "image": None,
        "compound": "left",
    }

    property_schema = [
        {"name": "x", "type": "number", "label": "X",
         "group": "Position", "pair": "pos"},
        {"name": "y", "type": "number", "label": "Y",
         "group": "Position", "pair": "pos"},

        {"name": "width", "type": "number", "label": "W",
         "group": "Size", "pair": "size", "min": 20, "max": 2000},
        {"name": "height", "type": "number", "label": "H",
         "group": "Size", "pair": "size", "min": 20, "max": 2000},
        {"name": "corner_radius", "type": "number", "label": "Radius",
         "group": "Size", "pair": "rad", "min": 0,
         "max": lambda p: max(0, min(int(p.get("width", 0)), int(p.get("height", 0))) // 2)},
        {"name": "border_width", "type": "number", "label": "Border",
         "group": "Size", "pair": "rad", "min": 0,
         "max": lambda p: max(0, min(int(p.get("width", 0)), int(p.get("height", 0))) // 2)},

        {"name": "fg_color", "type": "color", "label": "BG",
         "group": "Colors", "pair": "col1"},
        {"name": "hover_color", "type": "color", "label": "Hover",
         "group": "Colors", "pair": "col1"},

        {"name": "text", "type": "multiline", "label": "Text",
         "group": "Text"},
        {"name": "font_bold", "type": "boolean", "label": "Style",
         "checkbox_text": "Bold",
         "group": "Text", "subgroup": "Character"},
        {"name": "font_size", "type": "number", "label": "Size",
         "group": "Text", "subgroup": "Character", "pair": "size_fit",
         "min": 6, "max": 96,
         "disabled_when": lambda p: bool(p.get("font_autofit", False))},
        {"name": "font_autofit", "type": "boolean", "label": "Best Fit",
         "group": "Text", "subgroup": "Character", "pair": "size_fit",
         "label_width": 55},
        {"name": "anchor", "type": "anchor", "label": "Align",
         "group": "Text", "subgroup": "Paragraph"},
        {"name": "text_color", "type": "color", "label": "Color",
         "group": "Text"},

        {"name": "image", "type": "image", "label": "Image",
         "group": "Image & Alignment"},
        {"name": "compound", "type": "compound", "label": "Pos",
         "group": "Image & Alignment"},
    ]

    derived_triggers = {"text", "width", "height", "font_bold", "font_autofit"}

    _NODE_ONLY_KEYS = {"x", "y"}
    _FONT_KEYS = {"font_size", "font_bold", "font_autofit"}

    @classmethod
    def compute_derived(cls, properties: dict) -> dict:
        result: dict = {}
        if not properties.get("font_autofit"):
            return result
        text = properties.get("text") or ""
        if not text:
            return result
        try:
            width = int(properties.get("width", 140))
            height = int(properties.get("height", 32))
        except (ValueError, TypeError):
            return result
        bold = bool(properties.get("font_bold", False))
        new_size = cls._compute_autofit_size(text, width, height, bold)
        if new_size > 0:
            result["font_size"] = new_size
        return result

    @classmethod
    def _compute_autofit_size(cls, text: str, width: int, height: int,
                              bold: bool) -> int:
        import tkinter.font as tkfont
        avail_w = max(10, width - 20)
        avail_h = max(10, height - 8)
        weight = "bold" if bold else "normal"
        lo, hi = 6, 96
        best = 6
        while lo <= hi:
            mid = (lo + hi) // 2
            try:
                f = tkfont.Font(size=mid, weight=weight)
                tw = f.measure(text)
                th = f.metrics("linespace")
            except Exception:
                return 13
            if tw <= avail_w and th <= avail_h:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return best

    @classmethod
    def transform_properties(cls, properties: dict) -> dict:
        result = {k: v for k, v in properties.items()
                  if k not in cls._NODE_ONLY_KEYS and k not in cls._FONT_KEYS}

        font_size = properties.get("font_size")
        font_bold = properties.get("font_bold")
        if font_size is not None or font_bold is not None:
            try:
                size = int(font_size) if font_size is not None else 13
            except (ValueError, TypeError):
                size = 13
            weight = "bold" if font_bold else "normal"
            try:
                result["font"] = ctk.CTkFont(size=size, weight=weight)
            except Exception:
                pass

        if "image" in result:
            image_path = result["image"]
            if image_path:
                try:
                    from PIL import Image
                    img = Image.open(image_path)
                    result["image"] = ctk.CTkImage(
                        light_image=img, dark_image=img, size=(20, 20)
                    )
                except Exception:
                    result["image"] = None
            else:
                result["image"] = None
        return result

    @classmethod
    def create_widget(cls, master, properties: dict):
        return ctk.CTkButton(master, **cls.transform_properties(properties))

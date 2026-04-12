import customtkinter as ctk

from app.widgets.base import WidgetDescriptor


class CTkButtonDescriptor(WidgetDescriptor):
    type_name = "CTkButton"
    display_name = "Button"

    default_properties = {
        "text": "CTkButton",
        "width": 140,
        "height": 32,
        "fg_color": "#1f6aa5",
        "hover_color": "#144870",
        "text_color": "#ffffff",
        "corner_radius": 6,
        "border_width": 0,
    }

    property_schema = [
        {"name": "text", "type": "string", "label": "Text"},
        {"name": "width", "type": "number", "label": "Width"},
        {"name": "height", "type": "number", "label": "Height"},
        {"name": "corner_radius", "type": "number", "label": "Corner Radius"},
        {"name": "border_width", "type": "number", "label": "Border Width"},
        {"name": "fg_color", "type": "color", "label": "Background"},
        {"name": "hover_color", "type": "color", "label": "Hover Color"},
        {"name": "text_color", "type": "color", "label": "Text Color"},
    ]

    @classmethod
    def create_widget(cls, master, properties: dict):
        return ctk.CTkButton(master, **properties)

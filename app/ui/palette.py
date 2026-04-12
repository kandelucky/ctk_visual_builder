import customtkinter as ctk

from app.core.project import Project
from app.core.widget_node import WidgetNode
from app.widgets.registry import all_descriptors


class Palette(ctk.CTkFrame):
    def __init__(self, master, project: Project):
        super().__init__(master, width=200)
        self.project = project
        self.grid_propagate(False)

        title = ctk.CTkLabel(self, text="Widgets", font=("", 14, "bold"))
        title.pack(pady=(12, 8), padx=10)

        for descriptor in all_descriptors():
            btn = ctk.CTkButton(
                self,
                text=descriptor.display_name,
                command=lambda d=descriptor: self._add_widget(d),
                anchor="w",
            )
            btn.pack(pady=4, padx=10, fill="x")

    def _add_widget(self, descriptor) -> None:
        node = WidgetNode(
            widget_type=descriptor.type_name,
            properties=dict(descriptor.default_properties),
        )
        self.project.add_widget(node)
        self.project.select_widget(node.id)

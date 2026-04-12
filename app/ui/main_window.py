import customtkinter as ctk

from app.core.project import Project
from app.ui.palette import Palette
from app.ui.properties_panel import PropertiesPanel
from app.ui.workspace import Workspace


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CTk Visual Builder")
        self.geometry("1280x800")
        self.minsize(900, 600)

        self.project = Project()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.palette = Palette(self, self.project)
        self.palette.grid(row=0, column=0, sticky="nsw", padx=(8, 4), pady=8)

        self.workspace = Workspace(self, self.project)
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=4, pady=8)

        self.properties = PropertiesPanel(self, self.project)
        self.properties.grid(row=0, column=2, sticky="nse", padx=(4, 8), pady=8)

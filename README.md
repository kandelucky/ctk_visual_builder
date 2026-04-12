# CTk Visual Builder

A desktop visual designer for **CustomTkinter** that lets you drag-and-drop widgets onto a canvas, edit their properties live, and export the result as clean Python code.

> Status: **early MVP** — three-panel layout, single widget (CTkButton), live property editing.

## Features (current MVP)

- Three-panel layout: widget palette, canvas workspace, properties inspector
- Real CTk widgets rendered on a tkinter Canvas (preview = reality)
- Click a widget on the workspace to select it (dashed selection rectangle)
- Properties panel auto-generates editors from each widget's schema
  - String editor (text)
  - Number editor (width, height, corner radius, border width)
  - Color picker (background, hover, text color)
- Live updates — every property change is reflected on the canvas immediately
- Event-bus architecture (pub/sub) for clean Model → View updates
- JSON-serializable widget tree (save/load coming next)

## Tech stack

- **Python 3.12+** (tested on 3.14)
- **CustomTkinter 5.2.2+**
- **tkinter Canvas** for the workspace surface
- Pure standard library otherwise — no extra dependencies beyond CTk

## Project layout

```
ctk_visual_builder/
├── main.py                    # entry point
├── requirements.txt
└── app/
    ├── core/                  # Model — pure data, no UI deps
    │   ├── event_bus.py       # pub/sub
    │   ├── widget_node.py     # widget tree node + JSON serialization
    │   └── project.py         # project state + selection
    ├── widgets/               # one descriptor file per CTk widget
    │   ├── base.py            # WidgetDescriptor base class
    │   ├── registry.py        # descriptor registry
    │   └── ctk_button.py      # first descriptor
    └── ui/                    # View — everything the user sees
        ├── main_window.py     # three-panel main window
        ├── palette.py         # left — widget palette
        ├── workspace.py       # center — canvas + selection
        └── properties_panel.py# right — dynamic property editors
```

## Architecture

- **MVC + Command pattern** (Commands enable free undo/redo — not yet implemented)
- **Widget Registry** — adding a new CTk widget = creating one descriptor file. No changes anywhere else.
- **Real CTk widgets on Canvas** via `canvas.create_window()` — no separate fake rendering layer.
- **Property panel** reads each descriptor's schema and generates inputs dynamically. No hard-coded UI per widget.
- **Event bus** publishes `widget_added`, `widget_removed`, `selection_changed`, `property_changed` — views subscribe and react.

## Install

```bash
git clone https://github.com/kandelucky/ctk_visual_builder.git
cd ctk_visual_builder
pip install -r requirements.txt
python main.py
```

## Roadmap

- [ ] Drag-to-move widgets on the canvas
- [ ] Resize handles
- [ ] Toolbar — New / Open / Save / Export to Python
- [ ] Undo / Redo (Command pattern)
- [ ] Remaining 15 CTk widget descriptors
- [ ] Layout managers (pack / grid / place) per widget
- [ ] Window settings panel (target window size, title, fg_color, resizable)
- [ ] Multiple selection, context menu, snap-to-grid alignment
- [ ] Live preview window
- [ ] Light / Dark theme toggle for the builder itself

## License

MIT

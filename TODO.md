# TODO / Roadmap

> Personal task list. Edit freely — add, remove, reorder, mark `[x]` when done.
> Format: standard GitHub markdown checkboxes. Works in any editor.

---

## Phase 0 — MVP

- [x] Three-panel layout (palette / workspace / properties)
- [x] Event bus + Project model + WidgetNode
- [x] Widget descriptor pattern + registry
- [x] CTkButton descriptor (first one)
- [x] Click-to-add palette → workspace
- [x] Click-to-select + selection rectangle
- [x] Live property editing (string / number / color)
- [x] GitHub repo

---

## Phase 1 — Core Interactions

- [ ] Drag-to-move widgets on the canvas
- [ ] Resize handles (8 corner/edge handles around selection)
- [ ] Delete key → remove selected widget
- [ ] Right-click context menu (Delete, Duplicate, Bring to Front, Send to Back)
- [ ] Esc key → deselect
- [ ] Real drag-and-drop from palette (instead of click-to-add)

---

## Phase 2 — Toolbar + Persistence

- [ ] Toolbar component at the top (icons + labels)
- [ ] New project (clear workspace)
- [ ] Save project → JSON file (`io/project_saver.py`)
- [ ] Open project ← JSON file (`io/project_loader.py`)
- [ ] Export to Python — clean .py output (`io/code_exporter.py`)
- [ ] Preview — open generated app in a separate window
- [ ] Light / Dark theme toggle (for the builder itself)

---

## Phase 3 — Remaining 15 Widget Descriptors

- [ ] CTkLabel
- [ ] CTkFrame
- [ ] CTkEntry
- [ ] CTkSlider
- [ ] CTkSwitch
- [ ] CTkProgressBar
- [ ] CTkComboBox
- [ ] CTkOptionMenu
- [ ] CTkSegmentedButton
- [ ] CTkCheckBox
- [ ] CTkRadioButton
- [ ] CTkTextbox
- [ ] CTkScrollableFrame
- [ ] CTkTabview
- [ ] Group widgets in palette (Containers / Inputs / Display / Indicators)

---

## Phase 4 — Undo / Redo

- [ ] `commands/base.py` — Command base class
- [ ] `commands/history.py` — undo/redo stacks
- [ ] AddWidgetCommand
- [ ] DeleteWidgetCommand
- [ ] MoveWidgetCommand
- [ ] ResizeWidgetCommand
- [ ] ChangePropertyCommand
- [ ] Ctrl+Z / Ctrl+Y keyboard shortcuts
- [ ] Toolbar undo/redo buttons

---

## Phase 5 — Window Settings

- [ ] Window settings panel (separate tab or area)
- [ ] Target window title
- [ ] Target window size (width, height)
- [ ] `overrideredirect` (frameless)
- [ ] `resizable` toggle
- [ ] Background color (`fg_color`)
- [ ] `appearance_mode` (system / light / dark)

---

## Phase 6 — Layout Managers

- [ ] Add `layout_type` field to each WidgetNode (pack / grid / place)
- [ ] "Layout" section in properties panel
- [ ] pack options (side, anchor, fill, expand, padx, pady)
- [ ] grid options (row, column, rowspan, columnspan, sticky)
- [ ] place options (relx, rely, x, y, anchor)
- [ ] Visual indicator on workspace (which manager is in use)
- [ ] Code exporter respects layout choices

---

## Phase 7 — Polish & Pro Features

- [ ] Multi-selection (Ctrl+click)
- [ ] Marquee selection (drag on empty canvas area)
- [ ] Snap-to-grid (8px grid)
- [ ] Alignment guides (snap to other widgets' edges/centers)
- [ ] Copy / Paste / Cut (Ctrl+C / V / X)
- [ ] Widget tree panel (hierarchical view, parent-child)
- [ ] Z-order management
- [ ] Group / Ungroup widgets
- [ ] Asset manager (images for CTkImage)

---

## Phase 8 — Advanced (later)

- [ ] Custom user-defined widgets / components
- [ ] Variables panel (StringVar, IntVar, BooleanVar — create + bind)
- [ ] Event handlers (generate command callbacks)
- [ ] Templates / Presets for common windows
- [ ] Project settings (Python version, theme, output structure)
- [ ] Plugin system for new widget types

---

## Notes / Ideas

> Free space — add anything that doesn't fit a phase yet.

-
-
-

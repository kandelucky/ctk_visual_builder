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
- [x] Desktop shortcut (run.bat + .lnk)

---

## Phase 0.5 — Property Editor Enhancements

- [x] Drag-to-scrub on number labels (Blender / Photoshop style)
- [x] Alt-key for slow / fine scrub mode
- [x] Min / max constraints on numeric properties (clamped during drag)
- [x] Dynamic max via lambda (e.g. corner_radius capped at min(w,h)/2)
- [x] `transform_properties` hook in WidgetDescriptor (path → CTkImage)
- [x] Anchor editor — 3×3 grid for text / image alignment
- [x] Compound editor — image position dropdown (top / left / right / bottom)
- [x] Image picker editor — Browse / Clear with file dialog
- [x] Pillow dependency for image loading
- [x] Property groups with section headers (Position / Size / Colors / Text / Image & Alignment)
- [x] Subgroups inside groups (Character / Paragraph nested under Text)
- [x] Paired layout — X+Y, W+H, Radius+Border, BG+Hover, Size+Best Fit side by side
- [x] Per-prop `label_width` override in schema (for longer labels in compact pairs)
- [x] Compact font sizes and reduced row padding
- [x] Fixed-height labels + small row pady (visual breathing without elongation)
- [x] Property panel auto-syncs editor vars on `property_changed` (for live drag updates)
- [x] Boolean editor — CTkCheckBox with optional inline text label (e.g. `[☐] Bold`)
- [x] Multi-line text editor — CTkTextbox with border, ~3 visible lines, word wrap
- [x] Color buttons with visible border for fg contrast
- [x] Font size, font bold, font autofit (Best Fit) properties for CTkButton
- [x] Auto-fit text sizing — binary search algorithm computes max size that fits w×h
- [x] `derived_triggers` + `compute_derived` hook in WidgetDescriptor (for autofit)
- [x] `disabled_when` schema field (greys out font_size when autofit is on)
- [x] More vertical spacing between groups (12px gap above each group header)
- [x] Custom Photoshop-style color picker — sat/val square + hue slider + hex input + Old/New comparison
- [x] HSL Lightness slider (black → color → white range, syncs with HSV state)
- [x] Tint strip — 13 swatches showing variations of current color (centered Lightness range, width 0.5)
- [x] Tint strip width matches sliders exactly (DPI-aware, no borders, flush)
- [x] Saved Colors row with + button (max 20 entries, 2 rows × 10, square swatches)
- [x] Selection highlight on saved color swatch matching current pick (white border)
- [x] JSON persistence for saved colors at `~/.ctk_visual_builder/recent_colors.json`
- [x] `ColorHistory` singleton for tracking recent / saved colors
- [x] PIL-based HSV / HSL gradient generation (low-res render + bilinear upscale, ~28ms per redraw)
- [x] DPI-aware Canvas widgets — scale tk.Canvas to match CTk widget DPI scaling
- [x] `round()` instead of `int()` for float→hex conversion (fixes saved color highlight matching after round-trip)
- [x] Persistent recent slots (no destroy/recreate) — eliminates flicker when adding to saved
- [x] Rectangular borders on canvas via `highlightthickness` (no rounded wrapper conflict)
- [x] Layout reorder — New/Old comparison at top, then tint strip, then SV / sliders / hex / saved / OK
- [x] OK-only dialog (Cancel removed, X / Esc still cancel)
- [ ] Reset-to-default button per property
- [ ] Tooltip / hint when hovering over property labels
- [ ] Collapsible property groups
- [ ] Numeric editor: arrow keys (↑/↓ = ±1, Shift+↑/↓ = ±10)
- [ ] Color picker: eyedropper to sample from screen
- [ ] Color picker: RGB / HSV numeric input fields
- [ ] Color picker: alpha channel for widgets that support it
- [ ] Color picker: adjustable tint strip range width

---

## Phase 1 — Core Interactions

- [x] Drag-to-move widgets on the canvas (offset-based, click-vs-drag threshold)
- [x] x / y as editable position properties (live sync with canvas drag)
- [ ] Resize handles (8 corner/edge handles around selection)
- [ ] Delete key → remove selected widget
- [ ] Right-click context menu (Delete, Duplicate, Bring to Front, Send to Back)
- [ ] Esc key → deselect
- [ ] Real drag-and-drop from palette (instead of click-to-add)
- [ ] Arrow keys to nudge selected widget (1px, Shift+arrow = 10px)
- [ ] Cursor change to "fleur" / move icon when hovering a widget

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
- [ ] Asset manager — copy images into project `assets/` folder for portability

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

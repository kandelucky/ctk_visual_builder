import json
import os

MAX_RECENT = 20


def _storage_path() -> str:
    home = os.path.expanduser("~")
    folder = os.path.join(home, ".ctk_visual_builder")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "recent_colors.json")


class ColorHistory:
    _instance: "ColorHistory | None" = None

    def __new__(cls):
        if cls._instance is None:
            inst = super().__new__(cls)
            inst._colors = []
            inst._loaded = False
            cls._instance = inst
        return cls._instance

    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        try:
            with open(_storage_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self._colors = [c.lower() for c in data
                                if isinstance(c, str)][:MAX_RECENT]
        except Exception:
            self._colors = []

    def _save(self) -> None:
        try:
            with open(_storage_path(), "w", encoding="utf-8") as f:
                json.dump(self._colors, f)
        except Exception:
            pass

    def add(self, color: str) -> None:
        if not color:
            return
        self._load()
        color = color.lower()
        if color in self._colors:
            self._colors.remove(color)
        self._colors.insert(0, color)
        self._colors = self._colors[:MAX_RECENT]
        self._save()

    def all(self) -> list[str]:
        self._load()
        return list(self._colors)

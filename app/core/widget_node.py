import uuid


class WidgetNode:
    def __init__(self, widget_type: str, properties: dict | None = None,
                 x: int = 0, y: int = 0):
        self.id: str = str(uuid.uuid4())
        self.widget_type: str = widget_type
        self.properties: dict = dict(properties) if properties else {}
        self.x: int = x
        self.y: int = y
        self.children: list[WidgetNode] = []
        self.parent: WidgetNode | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "widget_type": self.widget_type,
            "properties": self.properties,
            "x": self.x,
            "y": self.y,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WidgetNode":
        node = cls(
            widget_type=data["widget_type"],
            properties=data.get("properties", {}),
            x=data.get("x", 0),
            y=data.get("y", 0),
        )
        node.id = data["id"]
        for child_data in data.get("children", []):
            child = cls.from_dict(child_data)
            child.parent = node
            node.children.append(child)
        return node

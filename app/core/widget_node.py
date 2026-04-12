import uuid


class WidgetNode:
    def __init__(self, widget_type: str, properties: dict | None = None):
        self.id: str = str(uuid.uuid4())
        self.widget_type: str = widget_type
        self.properties: dict = dict(properties) if properties else {}
        self.children: list[WidgetNode] = []
        self.parent: WidgetNode | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "widget_type": self.widget_type,
            "properties": self.properties,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WidgetNode":
        node = cls(
            widget_type=data["widget_type"],
            properties=data.get("properties", {}),
        )
        node.id = data["id"]
        for child_data in data.get("children", []):
            child = cls.from_dict(child_data)
            child.parent = node
            node.children.append(child)
        return node

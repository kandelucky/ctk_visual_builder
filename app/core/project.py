from app.core.event_bus import EventBus
from app.core.widget_node import WidgetNode


class Project:
    def __init__(self):
        self.event_bus = EventBus()
        self.root_widgets: list[WidgetNode] = []
        self.selected_id: str | None = None

    def add_widget(self, node: WidgetNode) -> None:
        self.root_widgets.append(node)
        self.event_bus.publish("widget_added", node)

    def remove_widget(self, widget_id: str) -> None:
        node = self.get_widget(widget_id)
        if node is None:
            return
        self.root_widgets.remove(node)
        if self.selected_id == widget_id:
            self.select_widget(None)
        self.event_bus.publish("widget_removed", widget_id)

    def get_widget(self, widget_id: str) -> WidgetNode | None:
        for node in self.root_widgets:
            if node.id == widget_id:
                return node
        return None

    def select_widget(self, widget_id: str | None) -> None:
        self.selected_id = widget_id
        self.event_bus.publish("selection_changed", widget_id)

    def update_property(self, widget_id: str, prop_name: str, value) -> None:
        node = self.get_widget(widget_id)
        if node is None:
            return
        node.properties[prop_name] = value
        self.event_bus.publish("property_changed", widget_id, prop_name, value)

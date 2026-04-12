class WidgetDescriptor:
    type_name: str = ""
    display_name: str = ""
    default_properties: dict = {}
    property_schema: list[dict] = []

    @classmethod
    def create_widget(cls, master, properties: dict):
        raise NotImplementedError

    @classmethod
    def update_widget(cls, widget, prop_name: str, value) -> None:
        widget.configure(**{prop_name: value})

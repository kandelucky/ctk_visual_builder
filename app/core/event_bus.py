class EventBus:
    def __init__(self):
        self._listeners: dict[str, list] = {}

    def subscribe(self, event: str, callback) -> None:
        self._listeners.setdefault(event, []).append(callback)

    def unsubscribe(self, event: str, callback) -> None:
        if event in self._listeners and callback in self._listeners[event]:
            self._listeners[event].remove(callback)

    def publish(self, event: str, *args, **kwargs) -> None:
        for callback in list(self._listeners.get(event, [])):
            callback(*args, **kwargs)

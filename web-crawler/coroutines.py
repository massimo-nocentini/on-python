
class future:

    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callbacks(self, callback):
        self._callbacks.append(callback)

    def resolve(self, value):
        self.result = value
        for c in self._callbacks: c(resolved_future=self)

class task:

    def __init__(self, coro):
        self.coro = coro

    def start(self):
        self(resolved_future=future())

    def __call__(self, resolved_future, return_value=None):
        try:
            pending_future = self.coro.send(resolved_future.result)
            pending_future.add_done_callbacks(self)
        except StopIteration as stop:
            return getattr(stop, 'value', return_value)


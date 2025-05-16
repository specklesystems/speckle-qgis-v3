from typing import Dict


class CancellationToken:
    _source: "CancellationTokenSource"

    def __init__(self, source: "CancellationTokenSource"):
        self._source = source

    @property
    def is_cancellation_requested(self) -> bool:
        return self._source.is_cancellation_requested

    def throw_if_cancellation_requested(self):
        if self.is_cancellation_requested:
            raise Exception("Operation was cancelled.")


class CancellationTokenSource:
    token: CancellationToken
    is_cancellation_requested: bool = False

    def __init__(self):
        self.token = CancellationToken(self)

    def cancel(self):
        self.is_cancellation_requested = True

    def dispose(self):
        pass


class CancellationManager:
    _operations_in_progress: Dict[str, CancellationTokenSource]
    number_of_operations: int

    def __init__(self):
        self._operations_in_progress = {}
        self.number_of_operations = len(self._operations_in_progress)

    def get_token(self, id: str) -> CancellationToken:
        return self._operations_in_progress[id].token

    def is_exist(self, id: str) -> bool:
        return True if self._operations_in_progress.get(id) else False

    def cancel_all_operations(self):
        for operation_value in self._operations_in_progress.values():
            operation_value.cancel()
            operation_value.dispose()

        self._operations_in_progress.clear()

    def init_cancellation_token_source(self, id: str) -> CancellationToken:
        if self.is_exist(id):
            self.cancel_operation(id)

        cts = CancellationTokenSource()
        self._operations_in_progress[id] = cts
        return cts.token

    def cancel_operation(self, id: str):
        cts = self._operations_in_progress.get(id)
        if cts:
            cts.cancel()
            cts.dispose()
            self._operations_in_progress.pop(id)

    def is_cancellation_requested(self, id: str) -> bool:
        return self._operations_in_progress[id].is_cancellation_requested

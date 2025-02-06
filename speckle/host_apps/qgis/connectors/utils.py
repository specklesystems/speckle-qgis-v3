from typing import Callable

from speckle.sdk.connectors_common.threading import ThreadContext


class QgisThreadContext(ThreadContext):

    def worker_to_main_async(self, action: Callable):
        raise NotImplementedError()

    def main_to_worker_async(self, action: Callable):
        raise NotImplementedError()

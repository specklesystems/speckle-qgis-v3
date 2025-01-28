from abc import ABC, abstractmethod
import threading
from typing import Callable


class ThreadContext(ABC):

    @staticmethod
    def is_main_thread() -> bool:
        if threading.current_thread() is threading.main_thread():
            return True
        return False

    def run_on_thread_async(self, action: Callable, use_main: bool):
        raise NotImplementedError()

    @abstractmethod
    def worker_to_main_async(self, action: Callable):
        raise NotImplementedError()

    @abstractmethod
    def main_to_worker_async(self, action: Callable):
        raise NotImplementedError()

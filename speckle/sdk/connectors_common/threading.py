from abc import ABC, abstractmethod
import threading
from typing import Callable

from qgis.core import (
    QgsTask,
    QgsApplication,
)


class ThreadContext(ABC):

    @staticmethod
    def is_main_thread() -> bool:
        if threading.current_thread() is threading.main_thread():
            return True
        return False

    def run_on_thread_async(self, action: Callable, use_main: bool = False):
        if use_main:
            if self.is_main_thread():
                return action()
            else:
                # we don't send operations to main thread for now
                raise NotImplementedError()
        else:
            if self.is_main_thread():
                task = QgsTask.fromFunction(
                    "Speckle task", action, on_finished=lambda: None
                )
                QgsApplication.taskManager().addTask(task)
            else:
                return action()

    @abstractmethod
    def worker_to_main_async(self, action: Callable):
        raise NotImplementedError()

    @abstractmethod
    def main_to_worker_async(self, action: Callable):
        raise NotImplementedError()

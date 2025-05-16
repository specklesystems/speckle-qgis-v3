from abc import ABC, abstractmethod
import threading
from typing import Callable

from qgis.core import QgsTask, QgsApplication
from PyQt5.QtCore import QObject


class QgisSpeckleTask(QgsTask):

    action: Callable

    def __init__(
        self,
        thread_context: "ThreadContext",
        action: Callable,
        model_card_id: str,
    ):

        super().__init__(f"speckle_{model_card_id}", QgsTask.CanCancel)
        self.exception = None
        self.action = action
        self.thread_context = thread_context

    def run(self):
        try:
            self.action()
        except Exception as e:
            # ignore unhandled or cancellation exceptions
            pass
        return True

    def finished(self, result):
        return


class MetaQObject(type(QObject), type(ABC)):
    # avoiding TypeError: metaclass conflict: the metaclass of a derived class
    # must be a (non-strict) subclass of the metaclasses of all its bases
    pass


class ThreadContext(ABC, QObject, metaclass=MetaQObject):

    @staticmethod
    def is_main_thread() -> bool:
        if threading.current_thread() is threading.main_thread():
            return True
        return False

    def run_on_thread_async(
        self, action: Callable, model_card_id: str, use_main: bool = False
    ):
        if use_main:
            if self.is_main_thread():
                return action()
            else:
                # we don't send operations to main thread for now
                raise NotImplementedError()
        else:
            if self.is_main_thread():

                # QgsApplication.taskManager().cancelAll()
                task = QgisSpeckleTask(
                    self,
                    action=action,
                    model_card_id=model_card_id,
                )
                task.taskTerminated.connect(lambda: self.task_terminated(task))
                QgsApplication.taskManager().addTask(task)

            else:
                return action()

    def task_terminated(self, task: QgsTask):
        # need to find a way to end Task without it emmiting failed signal to Qgis UI
        pass

    @abstractmethod
    def worker_to_main_async(self, action: Callable):
        raise NotImplementedError()

    @abstractmethod
    def main_to_worker_async(self, action: Callable):
        raise NotImplementedError()

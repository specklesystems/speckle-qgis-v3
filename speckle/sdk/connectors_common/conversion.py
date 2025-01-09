from abc import ABC
from dataclasses import dataclass
import traceback
from specklepy.objects.base import Base
from typing import Optional


@dataclass
class ErrorWrapper:
    message: str
    stack_trace: str


class ConversionResult(ABC):
    status: "Status"
    source_id: str
    source_type: str
    result_id: Optional[str]
    result_type: Optional[str]
    error: Optional["ErrorWrapper"]

    def __init__(
        self, *, status, source_id, source_type, result_id, result_type, error
    ):
        self.status = status
        self.source_id = source_id
        self.source_type = source_type
        self.result_id = result_id
        self.result_type = result_type
        self.error = error

    @staticmethod
    def format_error(exception: Optional[Exception] = None) -> ErrorWrapper | None:
        if exception is None:
            return None
        return ErrorWrapper(
            message=str(exception),
            stack_trace=f"{exception}\n{traceback.format_exc()}",
        )


class SendConversionResult(ConversionResult):

    def __init__(
        self,
        *,
        status: str,
        source_id: str,
        source_type: str,
        result: Optional[Base] = None,
        exception: Optional[Exception] = None,
    ):
        super().__init__(
            status=status,
            source_id=source_id,
            source_type=source_type,
            result_id=result.id if result is not None else None,
            result_type=result.speckle_type if result is not None else None,
            error=self.format_error(exception),
        )

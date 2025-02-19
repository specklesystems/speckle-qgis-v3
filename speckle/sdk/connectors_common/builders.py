from abc import ABC, abstractmethod
from dataclasses import dataclass
from speckle.sdk.connectors_common.cancellation import CancellationToken
from speckle.sdk.connectors_common.conversion import SendConversionResult
from specklepy.objects.base import Base
from typing import Any, List


@dataclass
class RootObjectBuilderResult:
    root_object: Base
    conversion_results: List[SendConversionResult]


class IRootObjectBuilder(ABC):
    @abstractmethod
    def build(
        objects: List[Any],
        send_info: str,
        on_operation_progressed: "IProgress[CardProgress]",
        ct: CancellationToken,
    ) -> RootObjectBuilderResult:
        """Placeholder for connector to define."""
        raise NotImplementedError()

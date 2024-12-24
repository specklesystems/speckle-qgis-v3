from abc import ABC
from dataclasses import dataclass
from speckle.connectors.common.conversion import SendConversionResult
from specklepy.objects.base import Base
from typing import Any, List


@dataclass
class RootObjectBuilderResult:
    root_object: Base
    conversion_results: List[SendConversionResult]


class IRootObjectBuilder(ABC):

    def build(
        objects: List[Any],
        send_info: str,
        on_operation_progressed: "IProgress[CardProgress]",
        ct: "CancellationToken",
    ) -> RootObjectBuilderResult:
        """Placeholder for connector to define."""
        raise NotImplementedError

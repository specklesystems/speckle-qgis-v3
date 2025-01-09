from abc import ABC, abstractmethod
from specklepy.objects.base import Base


class IRootToSpeckleConverter(ABC):

    @abstractmethod
    def convert(self, target: object) -> Base:
        raise NotImplementedError()

from abc import ABC, abstractmethod
from specklepy.objects.base import Base


class IToSpeckleTopLevelConverter(ABC, ABC):

    @abstractmethod
    def convert(target: object) -> Base:
        raise NotImplementedError()

from abc import ABC, abstractmethod
from speckle.sdk.converters_common.objects import IToSpeckleTopLevelConverter
from specklepy.objects.base import Base


class IRootToSpeckleConverter(ABC):

    @abstractmethod
    def convert(self, target: object) -> Base:
        raise NotImplementedError()


class RootToSpeckleConverter(IRootToSpeckleConverter):

    _to_speckle_converter: IToSpeckleTopLevelConverter

    def __init__(self):
        self._to_speckle_converter = IToSpeckleTopLevelConverter

    def convert(self, target: object) -> Base:
        converted_object: Base = self._to_speckle_converter.convert(target)
        return converted_object

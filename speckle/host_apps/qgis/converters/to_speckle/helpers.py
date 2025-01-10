from typing import Any, Dict, List
from qgis.core import QgsFeature
from specklepy.objects.base import Base


class DisplayValueExtractor:

    # TODO

    point_converter: "PointConverter"

    def get_display_value(self, core_object) -> List[Base]:
        if isinstance(core_object, QgsFeature):
            pass
        return []


class PropertiesExtractor:

    # TODO

    def get_properties(self, core_object: Any) -> Dict[str, Any]:
        if isinstance(core_object, QgsFeature):
            return {}

        return {}

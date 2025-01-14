from speckle.host_apps.qgis.converters.settings import QgisConversionSettings

from qgis.core import QgsAbstractGeometry
from specklepy.objects.geometry.point import Point


class PointToSpeckleConverter:
    _conversion_settings: QgisConversionSettings

    def __init__(
        self,
        conversion_settings,
    ):
        self._conversion_settings = conversion_settings

    def convert(self, target: QgsAbstractGeometry) -> Point:

        # reproject geometry
        target.transform(self._conversion_settings.activeCrsOffsetRotation.crs)

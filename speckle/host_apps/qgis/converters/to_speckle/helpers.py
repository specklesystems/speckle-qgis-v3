from typing import Any, Dict, List

from speckle.host_apps.qgis.converters.settings import QgisConversionSettings
from speckle.host_apps.qgis.converters.to_speckle.raw import (
    PointToSpeckleConverter,
    PolylineToSpeckleConverter,
    PolygonToSpeckleConverter,
    RasterToSpeckleConverter,
)
from specklepy.objects.base import Base

from qgis.core import (
    QgsFeature,
    QgsRasterLayer,
    QgsGeometry,
    QgsCoordinateTransform,
    QgsPoint,
)
from osgeo import gdal


class DisplayValueExtractor:

    _conversion_settings: QgisConversionSettings

    _point_converter: PointToSpeckleConverter
    _polyline_converter: PolylineToSpeckleConverter
    _polygon_converter: PolygonToSpeckleConverter
    _raster_converter: RasterToSpeckleConverter

    def __init__(self, conversion_settings):
        self._conversion_settings = conversion_settings
        self._point_converter = PointToSpeckleConverter(conversion_settings)
        self._polyline_converter = PolylineToSpeckleConverter(
            conversion_settings, self._point_converter
        )
        self._polygon_converter = PolygonToSpeckleConverter(
            conversion_settings, self._polyline_converter
        )
        self._raster_converter = RasterToSpeckleConverter(
            conversion_settings, self._point_converter
        )

    def get_display_value(
        self, core_object: QgsFeature | QgsRasterLayer, layer_app_id: str
    ) -> List[Base]:

        if isinstance(core_object, QgsFeature):
            return self._get_feature_geometries(core_object, layer_app_id)

        elif isinstance(core_object, QgsRasterLayer):
            return self._get_raster_geometry(core_object)

        raise NotImplementedError(
            f"Cannot extract displayValue from object of type '{type(core_object)}'"
        )

    def _get_layer_transformation(self, layer_app_id: str) -> QgsCoordinateTransform:
        return self._conversion_settings.layers_send_transforms[layer_app_id]

    def _get_feature_geometries(self, feature: QgsFeature, layer_app_id: str):

        geometry: QgsGeometry = feature.geometry()
        geometry_type = geometry.type().value
        # Point: 0, Line: 1, Polygon: 2, Unknown: 3, Null: 4

        abstract_geometry = geometry.get()

        if geometry_type in [0, 1, 2]:
            # reproject geometry: needs to be done here, while we have a layer reference
            transformation = self._get_layer_transformation(layer_app_id)
            abstract_geometry.transform(transformation)

            if geometry_type == 0:
                return self._point_converter.convert(abstract_geometry)
            if geometry_type == 1:
                return self._polyline_converter.convert(abstract_geometry)
            if geometry_type == 2:
                return self._polygon_converter.convert(abstract_geometry)

        elif geometry_type == 3:  # no-geometry table feature
            return []

        raise ValueError(f"Unsupported geometry type: '{geometry.type().name}'")

    def _get_raster_geometry(self, raster: QgsRasterLayer):
        # transformation will be done already in converter
        return [self._raster_converter.convert(raster)]


class PropertiesExtractor:

    def get_properties(self, core_object: Any) -> Dict[str, Any]:

        if isinstance(core_object, QgsFeature):
            return core_object.attributeMap()

        elif isinstance(core_object, QgsRasterLayer):
            return {}  # TODO

        return {}

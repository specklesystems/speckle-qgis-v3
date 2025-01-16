import math
from typing import Dict, List
from speckle.host_apps.qgis.connectors.extensions import get_speckle_app_id
from speckle.host_apps.qgis.converters.settings import QgisConversionSettings

from specklepy.objects.geometry.point import Point
from specklepy.objects.geometry.polyline import Polyline
from specklepy.objects.geometry.mesh import Mesh

from qgis.core import (
    QgsAbstractGeometry,
    QgsWkbTypes,
    QgsPoint,
    QgsRasterLayer,
    QgsPointXY,
    QgsRasterBandStats,
)
from osgeo import gdal


class PointToSpeckleConverter:
    _conversion_settings: QgisConversionSettings

    def __init__(
        self,
        conversion_settings,
    ):
        self._conversion_settings = conversion_settings

    def convert(self, target: QgsAbstractGeometry) -> List[Point]:

        result_geometry = [self.convert_point_to_speckle(pt) for pt in target.parts()]
        return result_geometry

    def convert_point_to_speckle(self, point: QgsPoint) -> Point:
        speckle_point = Point(
            x=point.x(),
            y=point.y(),
            z=0 if math.isnan(point.z()) else point.z(),
            units=self._conversion_settings.speckle_units,
        )
        return speckle_point


class PolylineToSpeckleConverter:
    _conversion_settings: QgisConversionSettings
    _point_converter: PointToSpeckleConverter

    def __init__(
        self,
        conversion_settings: QgisConversionSettings,
        point_converter: PointToSpeckleConverter,
    ):
        self._conversion_settings = conversion_settings
        self._point_converter = point_converter

    def convert(self, target: QgsAbstractGeometry) -> List[Polyline]:

        wkb_type = target.wkbType()
        # WkbTypes: https://qgis.org/pyqgis/master/core/Qgis.html#qgis.core.Qgis.WkbType

        if (
            wkb_type == QgsWkbTypes.LineString
            or wkb_type == QgsWkbTypes.LineString25D
            or wkb_type == QgsWkbTypes.LineStringZ
            or wkb_type == QgsWkbTypes.LineStringM
            or wkb_type == QgsWkbTypes.LineStringZM
            or wkb_type == QgsWkbTypes.MultiLineString
            or wkb_type == QgsWkbTypes.MultiLineString25D
            or wkb_type == QgsWkbTypes.MultiLineStringZ
            or wkb_type == QgsWkbTypes.MultiLineStringM
            or wkb_type == QgsWkbTypes.MultiLineStringZM
            or wkb_type == QgsWkbTypes.MultiCurve
            or wkb_type == QgsWkbTypes.MultiCurveZ
            or wkb_type == QgsWkbTypes.MultiCurveM
            or wkb_type == QgsWkbTypes.MultiCurveZM
        ):
            return [self._convert_linestring(part) for part in target.parts()]

        if (
            wkb_type == QgsWkbTypes.CircularString
            or wkb_type == QgsWkbTypes.CircularStringZ
            or wkb_type == QgsWkbTypes.CircularStringM
            or wkb_type == QgsWkbTypes.CircularStringZM
            or wkb_type == QgsWkbTypes.CompoundCurve
            or wkb_type == QgsWkbTypes.CompoundCurveZ
            or wkb_type == QgsWkbTypes.CompoundCurveM
            or wkb_type == QgsWkbTypes.CompoundCurveZM
        ):
            return [self._convert_circularstring(part) for part in target.parts()]

        raise ValueError(f"Geometry of type '{wkb_type.name}' cannot be converted")

    def _convert_linestring(self, linestring) -> Polyline:

        speckle_points: List[Point] = [
            self._point_converter.convert_point_to_speckle(pt)
            for pt in linestring.points()
        ]
        coord_list = [item for pt in speckle_points for item in [pt.x, pt.y, pt.z]]

        return Polyline(
            value=coord_list,
            units=self._conversion_settings.speckle_units,
            closed=linestring.isClosed(),
        )

    def _convert_circularstring(self, circularstring) -> Polyline:

        new_linestring = circularstring.clone().curveToLine()

        return self._convert_linestring(new_linestring)


class PolygonToSpeckleConverter:
    _conversion_settings: QgisConversionSettings
    _polyline_converter: PolylineToSpeckleConverter

    def __init__(
        self,
        conversion_settings: QgisConversionSettings,
        polyline_converter: PolylineToSpeckleConverter,
    ):
        self._conversion_settings = conversion_settings
        self._polyline_converter = polyline_converter

    def convert(self, target: QgsAbstractGeometry) -> List[Polyline]:

        wkb_type = target.wkbType()

        if (
            wkb_type == QgsWkbTypes.Polygon
            or wkb_type == QgsWkbTypes.PolygonZ
            or wkb_type == QgsWkbTypes.PolygonM
            or wkb_type == QgsWkbTypes.PolygonZM
            or wkb_type == QgsWkbTypes.MultiPolygon
            or wkb_type == QgsWkbTypes.MultiPolygonZ
            or wkb_type == QgsWkbTypes.MultiPolygonM
            or wkb_type == QgsWkbTypes.MultiPolygonZM
            or wkb_type == QgsWkbTypes.CurvePolygon
            or wkb_type == QgsWkbTypes.CurvePolygonZ
            or wkb_type == QgsWkbTypes.CurvePolygonM
            or wkb_type == QgsWkbTypes.CurvePolygonZM
        ):
            all_curves = []
            for part in target.parts():

                all_curves.append(
                    self._polyline_converter.convert(part.exteriorRing())[0]
                )

                for i in range(part.numInteriorRings()):
                    all_curves.append(
                        self._polyline_converter.convert(part.interiorRing(i))[0]
                    )
            return all_curves

        raise ValueError(f"Geometry of type '{type(target)}' cannot be converted")


class RasterToSpeckleConverter:
    _conversion_settings: QgisConversionSettings
    _point_converter: PointToSpeckleConverter

    def __init__(
        self,
        conversion_settings: QgisConversionSettings,
        point_converter: PointToSpeckleConverter,
    ):
        self._conversion_settings = conversion_settings
        self._point_converter = point_converter

    def convert(self, target) -> Mesh:

        # get raster basic info
        ds = gdal.Open(target.source(), gdal.GA_ReadOnly)
        dimension_x = target.width()
        dimension_y = target.height()
        cells_number = dimension_x * dimension_y
        # Geotransforms documentation: https://gdal.org/en/stable/tutorials/geotransforms_tut.html
        min_x, resolution_pixel_x, _, min_y, _, resolution_pixel_y = (
            ds.GetGeoTransform()[:6]
        )

        max_x: float = min_x + resolution_pixel_x * dimension_x
        max_y: float = min_y + resolution_pixel_y * dimension_y

        # reproject raster corner points, taken clockwise
        layer_app_id = get_speckle_app_id(target)
        transformation = self._conversion_settings.layers_send_transforms[layer_app_id]

        corner_pts = []
        for coord in [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]:
            point = QgsPoint(*coord)
            point.transform(transformation)
            corner_pts.append(point)

        # get updated raster resolution (after reprojecting)
        scale_x = (corner_pts[1].x() - corner_pts[0].x()) / (max_x - min_x)
        scale_y = (corner_pts[2].y() - corner_pts[1].y()) / (max_y - min_y)
        resolution_pixel_x *= scale_x
        resolution_pixel_y *= scale_y

        faces_list = self._get_faces_list(cells_number)
        vertices_list = self._get_vertices_list(
            corner_pts, dimension_x, dimension_y, resolution_pixel_x, resolution_pixel_y
        )

        # get bands data
        renderer_type = target.renderer().type()
        colors_list = self._get_colors_list(target, ds, renderer_type, cells_number)

        return Mesh(
            vertices=vertices_list,
            faces=faces_list,
            colors=colors_list,
            units=self._conversion_settings.speckle_units,
        )

    def _get_faces_list(self, cells_number: int) -> List[int]:

        # get faces
        nested_faces_list = [
            (4, 4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3) for i in range(cells_number)
        ]
        faces_list = [item for sublist in nested_faces_list for item in sublist]

        return faces_list

    def _get_vertices_list(
        self,
        corner_pts: List[QgsPoint],
        dimension_x: int,
        dimension_y: int,
        resolution_pixel_x: int,
        resolution_pixel_y: int,
    ) -> List[float]:

        cells_number = dimension_x * dimension_y
        # get vertices
        correction_pixel_x = (corner_pts[3].x() - corner_pts[0].x()) / dimension_x
        correction_pixel_y = (corner_pts[1].y() - corner_pts[0].y()) / dimension_y

        nested_vertices_list = [
            (
                # list of coordinates for 4 vertices of the face, counterclockwise
                # i % dimension_x = current column index (x-dimension)
                corner_pts[0].x()
                + (resolution_pixel_x + correction_pixel_x) * (i % dimension_x),
                # math.floor(ind/sizeX) = current row index (y-dimension)
                corner_pts[0].y()
                + (resolution_pixel_y + correction_pixel_y)
                * math.floor(i / dimension_x),
                0,
                # vertex #2:
                corner_pts[0].x()
                + (resolution_pixel_x + correction_pixel_x) * (i % dimension_x),
                corner_pts[0].y()
                + (resolution_pixel_y + correction_pixel_y)
                * math.floor(1 + i / dimension_x),
                0,
                # vertex #3:
                corner_pts[0].x()
                + (resolution_pixel_x + correction_pixel_x) * (1 + i % dimension_x),
                corner_pts[0].y()
                + (resolution_pixel_y + correction_pixel_y)
                * math.floor(1 + i / dimension_x),
                0,
                # vertex #4:
                corner_pts[0].x()
                + (resolution_pixel_x + correction_pixel_x) * (1 + i % dimension_x),
                corner_pts[0].y()
                + (resolution_pixel_y + correction_pixel_y)
                * math.floor(i / dimension_x),
                0,
            )
            for i in range(cells_number)
        ]
        vertices_list = [item for sublist in nested_vertices_list for item in sublist]

        return vertices_list

    def _get_colors_list(
        self, target: QgsRasterLayer, ds, renderer_type: str, cells_number: int
    ) -> List[int]:

        if renderer_type == "multibandcolor":
            return self._get_colors_multiband_renderer(target, ds, cells_number)
        if renderer_type == "paletted":
            return self._get_colors_paletted_renderer(target, ds, cells_number)
        if renderer_type == "singlebandpseudocolor":
            return self._get_colors_singlebandpseudocolor_renderer(
                target, ds, cells_number
            )
        # if other or 'singlebandgray'
        return self._get_colors_singleband_renderer(target, ds, cells_number)

    def _get_renderer_band_values(self, target, ds, band_index=None):

        # if index not provided, use default renderer band
        if band_index is None:
            band_index = target.renderer().band()

        if band_index < 1:  # not a valid index
            raise IndexError("Band index invalid")

        rb = ds.GetRasterBand(band_index)
        band_values = [
            item for sublist in rb.ReadAsArray().tolist() for item in sublist
        ]
        return rb, band_values

    def _get_min_max_nodata_from_band(self, target: QgsRasterLayer, band_index: int):

        if band_index < 1:  # not a valid index
            raise IndexError("Band index invalid")

        band_min = (
            target.dataProvider()
            .bandStatistics(band_index, QgsRasterBandStats.All)
            .minimumValue
        )
        band_max = (
            target.dataProvider()
            .bandStatistics(band_index, QgsRasterBandStats.All)
            .maximumValue
        )
        vals_range = band_max - band_min

        return band_min, band_max, vals_range

    def _get_colors_singlebandpseudocolor_renderer(
        self, target: QgsRasterLayer, ds, cells_number: int
    ) -> List[int]:
        # get band values
        rb, band_values = self._get_renderer_band_values(target, ds)
        no_data_val = rb.GetNoDataValue()

        # get renderer classes
        renderer_classes = target.renderer().legendSymbologyItems()
        class_rgbs = [
            renderer_classes[class_ind][1].getRgb()
            for class_ind in range(len(renderer_classes))
        ]

        list_colors = []

        for val in band_values:

            for class_ind in range(len(renderer_classes)):

                current_class = renderer_classes[class_ind]
                if class_ind < len(renderer_classes) - 1:  # if not last class

                    next_class = renderer_classes[class_ind + 1]
                    if val >= float(current_class[0]) and val < float(next_class[0]):
                        rgb = class_rgbs[class_ind]
                        color = (255 << 24) | (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
                        break

                elif class_ind == len(renderer_classes) - 1:  # last class
                    if val >= float(current_class[0]):
                        rgb = class_rgbs[class_ind]
                        color = (255 << 24) | (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
                        break
                    else:  # if last class, but value still not found
                        color = (0 << 24) | (0 << 16) | (0 << 8) | 0
                        break

            # assign black transparent color if no data
            if val == no_data_val or val is None:
                color = (0 << 24) | (0 << 16) | (0 << 8) | 0

            # add color value after looping through classes/categories
            list_colors.extend([color, color, color, color])

        return list_colors

    def _get_colors_paletted_renderer(
        self, target: QgsRasterLayer, ds, cells_number: int
    ) -> List[int]:

        # get band values
        rb, band_values = self._get_renderer_band_values(target, ds)
        no_data_val = rb.GetNoDataValue()

        # get renderer classes
        renderer_classes = target.renderer().classes()
        class_rgbs = [
            renderer_classes[class_ind].color.getRgb()
            for class_ind in range(len(renderer_classes))
        ]

        list_colors = []

        # iterate through each value
        for val in band_values:
            # iterate through each renderer class
            for class_ind in range(len(renderer_classes)):

                current_class = renderer_classes[class_ind]
                if class_ind < len(renderer_classes) - 1:  # if not last class

                    next_class = renderer_classes[class_ind + 1]
                    if val >= float(current_class.value) and val < float(
                        next_class.value
                    ):
                        rgb = class_rgbs[class_ind]
                        color = (255 << 24) | (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
                        break

                elif class_ind == len(renderer_classes) - 1:  # last class
                    if val >= float(current_class.value):
                        rgb = class_rgbs[class_ind]
                        color = (255 << 24) | (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
                        break
                    else:  # if last class, but value still not found
                        color = (0 << 24) | (0 << 16) | (0 << 8) | 0
                        break

                # assign black transparent color if no data
                if val == no_data_val or val is None:
                    color = (0 << 24) | (0 << 16) | (0 << 8) | 0

            list_colors.extend([color, color, color, color])

        return list_colors

    def _get_colors_multiband_renderer(
        self, target: QgsRasterLayer, ds, cells_number: int
    ) -> List[int]:

        band_count = target.bandCount()

        # assign correct values to R,G,B channels, where available
        for band_index in range(1, band_count + 1):
            # note: raster stats can be messed up and are not reliable (e.g. Min is larger than Max)

            band_min, band_max, _ = self._get_min_max_nodata_from_band(
                target, band_index
            )
            rb, band_values = self._get_renderer_band_values(target, ds, band_index)
            band_no_data = rb.GetNoDataValue()

            # pre-populate the lists for each color
            vals_red = [0 for _ in range(cells_number)]
            vals_green = [0 for _ in range(cells_number)]
            vals_blue = [0 for _ in range(cells_number)]
            vals_alpha = None

            val_min_red = val_min_green = val_min_blue = val_min_alpha = 0
            vals_range_red = vals_range_green = vals_range_blue = vals_range_alpha = 0
            val_na_red = val_na_green = val_na_blue = val_na_alpha = None

            # if statements are not exclusive, as QGIS allows to assugn 1 band to several color channels
            if band_index == int(target.renderer().redBand()):
                vals_red = band_values
                vals_range_red = band_max - band_min
                val_min_red = band_min
                val_na_red = band_no_data
            if band_index == int(target.renderer().greenBand()):
                vals_green = band_values
                vals_range_green = band_max - band_min
                val_min_green = band_min
                val_na_green = band_no_data
            if band_index == int(target.renderer().blueBand()):
                vals_blue = band_values
                vals_range_blue = band_max - band_min
                val_min_blue = band_min
                val_na_blue = band_no_data
            if band_index == int(target.renderer().alphaBand()):
                vals_alpha = band_values
                vals_range_alpha = band_max - band_min
                val_min_alpha = band_min
                val_na_alpha = band_no_data

        list_colors = [
            (
                (
                    (
                        255 << 24
                        if vals_alpha is None or vals_range_alpha == 0
                        else int(
                            255 * (vals_alpha[ind] - val_min_alpha) / vals_range_alpha
                        )
                        << 24
                    )
                    | (
                        (
                            int(255 * (vals_red[ind] - val_min_red) / vals_range_red)
                            << 16
                        )
                        if vals_range_red != 0
                        else int(vals_red[ind]) << 16
                    )
                    | (
                        int(255 * (vals_green[ind] - val_min_green) / vals_range_green)
                        << 8
                        if vals_range_green != 0
                        else int(vals_green[ind]) << 8
                    )
                    | (
                        int(255 * (vals_blue[ind] - val_min_blue) / vals_range_blue)
                        if vals_range_blue != 0
                        else int(vals_blue[ind])
                    )
                )
                if (
                    vals_red[ind] != val_na_red
                    and vals_green[ind] != val_na_green
                    and vals_blue[ind] != val_na_blue
                )
                else (0 << 24) | (0 << 16) | (0 << 8) | 0
            )
            for ind in range(cells_number)
            for _ in range(4)
        ]

        return list_colors

    def _get_colors_singleband_renderer(self, target, ds, cells_number) -> List[int]:

        # get band values
        band_index = 1
        rb, band_values = self._get_renderer_band_values(target, ds, band_index)
        no_data_band_val = rb.GetNoDataValue()
        band_min, _, vals_range = self._get_min_max_nodata_from_band(target, band_index)

        # get alpha band values
        alpha_band_index = target.renderer().alphaBand()
        if alpha_band_index >= 1:  # valid index
            alpha_min, _, alpha_range = self._get_min_max_nodata_from_band(
                target, alpha_band_index
            )
            _, alpha_band_values = self._get_renderer_band_values(
                target, ds, alpha_band_index
            )
        else:
            alpha_range = None
            alpha_band_values = None

        list_colors: List[int] = [
            (
                (
                    255 << 24
                    if alpha_range is None or alpha_band_values is None
                    else int(255 * (alpha_band_values[ind] - alpha_min) / alpha_range)
                    << 24
                )
                | (int(255 * (band_values[ind] - band_min) / vals_range) << 16)
                | (int(255 * (band_values[ind] - band_min) / vals_range) << 8)
                | int(255 * (band_values[ind] - band_min) / vals_range)
                if band_values[ind] != no_data_band_val
                else (0 << 24) | (0 << 16) | (0 << 8) | 0
            )
            for ind in range(cells_number)
            for _ in range(4)
        ]

        return list_colors

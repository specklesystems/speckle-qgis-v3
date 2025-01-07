from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Generic, TypeVar

from specklepy.objects.geometry import Point
from specklepy.objects.models.units import Units, get_scale_factor

from qgis.core import Qgis

T = TypeVar("T")


@dataclass
class CRSoffsetRotation:
    crs: "QgsCoordinateReferenceSystem"
    lat_offset: float
    lon_offset: float
    true_north_radians: float

    def point_scale(self, point: Point, from_unit: str, to_unit: str) -> Point:
        scale_factor = get_scale_factor(from_unit, to_unit)
        return Point.from_coords(
            x=point.x * scale_factor,
            y=point.y * scale_factor,
            z=point.z * scale_factor,
            units=to_unit,
        )


class IHostToSpeckleUnitConverter(ABC, Generic[T]):

    @abstractmethod
    def convert_or_throw(self, host_unit: T) -> Units:
        raise NotImplementedError


class QgisToSpeckleUnitConverter(IHostToSpeckleUnitConverter[Qgis.DistanceUnit]):

    def s_unit_mapping(self) -> Dict[int, str]:
        units_dict: Dict[int, str] = {
            Qgis.DistanceUnit.DistanceMeters: Units.m,
            Qgis.DistanceUnit.DistanceKilometers: Units.km,
            Qgis.DistanceUnit.DistanceFeet: Units.feet,
            # Qgis.DistanceUnit.DistanceNauticalMiles: ?,
            Qgis.DistanceUnit.DistanceYards: Units.yards,
            Qgis.DistanceUnit.DistanceMiles: Units.miles,
            # Qgis.DistanceUnit.DistanceDegrees: ?,
            Qgis.DistanceUnit.DistanceCentimeters: Units.cm,
            Qgis.DistanceUnit.DistanceMillimeters: Units.mm,
            Qgis.DistanceUnit.Inches: Units.inches,
            # Qgis.DistanceUnit.DistanceUnknownUnit: Units.none,
        }
        return units_dict

    def convert_or_throw(self, host_unit):
        if host_unit == Qgis.DistanceUnit.DistanceDegrees:
            return Units.m
        try:
            return self.s_unit_mapping()[host_unit]
        except KeyError:
            # TODO define exception type
            raise Exception(f"The unit system {host_unit} is not supported")

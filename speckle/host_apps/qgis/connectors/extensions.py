from functools import singledispatch
from qgis.core import QgsLayerTreeGroup, QgsVectorLayer, QgsRasterLayer, QgsFeature


@singledispatch
def get_speckle_app_id(data):
    raise NotImplementedError(
        f"Cannot get application id from data of type {type(data)}"
    )


@get_speckle_app_id.register
def _(data: QgsLayerTreeGroup):
    return data.name()


@get_speckle_app_id.register
def _(data: QgsVectorLayer):
    return data.id()


@get_speckle_app_id.register
def _(data: QgsRasterLayer):
    return f"{data.id()}_0"


@get_speckle_app_id.register
def _(data: QgsFeature, layer_app_id: str):
    return f"{layer_app_id}_{data.id()}"

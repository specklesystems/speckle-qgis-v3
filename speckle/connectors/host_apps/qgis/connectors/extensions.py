from functools import singledispatch
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsFeature


@singledispatch
def get_speckle_app_id(data):
    raise NotImplementedError(
        f"Cannot get application id from data of type {type(data)}"
    )


@get_speckle_app_id.register(int)
def _(data: QgsVectorLayer):
    return data.id()


@get_speckle_app_id.register(int)
def _(data: QgsRasterLayer):
    return f"{data.id()}_0"


@get_speckle_app_id.register(str)
def _(data: QgsFeature, layer_app_id: str):
    return f"{layer_app_id}_{data.id()}"

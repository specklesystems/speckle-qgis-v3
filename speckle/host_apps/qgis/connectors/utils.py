from typing import Callable

from speckle.sdk.connectors_common.threading import ThreadContext

from qgis.core import Qgis

UNSUPPORTED_PROVIDERS = ["WFS", "wms", "wcs", "vectortile"]
HOST_APP_FULL_VERSION = (
    Qgis.QGIS_VERSION.encode("iso-8859-1", errors="ignore")
    .decode("utf-8")
    .split("-")[0]
)


class QgisThreadContext(ThreadContext):

    def worker_to_main_async(self, action: Callable):
        raise NotImplementedError()

    def main_to_worker_async(self, action: Callable):
        raise NotImplementedError()

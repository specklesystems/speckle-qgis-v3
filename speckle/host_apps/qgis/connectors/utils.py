from typing import Callable
from pathlib import Path
from specklepy.logging import metrics

from speckle.sdk.connectors_common.threading import ThreadContext

from qgis.core import Qgis

HOST_APP_FULL_VERSION = (
    Qgis.QGIS_VERSION.encode("iso-8859-1", errors="ignore")
    .decode("utf-8")
    .split("-")[0]
)
CORE_VERSION = "3.0.099"

UNSUPPORTED_PROVIDERS = ["WFS", "wms", "wcs", "vectortile"]


def get_core_version():

    metadata_path = Path(Path(__file__).parent, "metadata.txt")
    core_version = "3.0.099"
    with open(metadata_path, "r") as file:
        for i, line in enumerate(file.readlines()):
            if "version=" in line:
                core_version = line.replace("version=", "").replace("\n", "")
    file.close()

    return core_version


def setup_metrics():

    # set hostApp and hostAppVersion
    version = (
        Qgis.QGIS_VERSION.encode("iso-8859-1", errors="ignore")
        .decode("utf-8")
        .split(".")[0]
    )
    metrics.set_host_app("qgis", version)

    global CORE_VERSION
    CORE_VERSION = get_core_version()


class QgisThreadContext(ThreadContext):

    def worker_to_main_async(self, action: Callable):
        raise NotImplementedError()

    def main_to_worker_async(self, action: Callable):
        raise NotImplementedError()

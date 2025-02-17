import sys
import os
from typing import Optional

from specklepy.core.api.client import SpeckleClient

MESSAGE_CATEGORY = "Speckle"


def get_project_workspace_id(client: SpeckleClient, project_id: str) -> Optional[str]:
    workspace_id = None
    server_version = client.project.server_version or client.server.version()

    # Local yarn builds of server will report a server version of "dev"
    # We'll assume that local builds are up-to-date with the latest features
    if server_version[0] == "dev":
        maj = 999
        min = 999
    else:
        maj = server_version[0]
        min = server_version[1]

    if maj > 2 or (maj == 2 and min > 20):
        workspace_id = client.project.get(project_id).workspaceId
    return workspace_id


def get_qgis_python_path():
    if sys.platform.startswith("linux"):
        return sys.executable
    pythonExec = os.path.dirname(sys.executable)
    if sys.platform == "win32":
        pythonExec += "\\python3"
    else:
        pythonExec += "/bin/python3"
    return pythonExec

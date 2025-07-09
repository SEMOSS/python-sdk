"""Main entrypoint into package."""

import warnings
from importlib import metadata
from typing import Any

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = "0.0.25"
del metadata  # optional, avoids polluting the results of dir(__package__)


def __getattr__(name: str) -> Any:
    if name == "RESTServer":
        warnings.warn(
            "Use of RESTServer is deprecated. Please update your code to use ServerClient instead."
        )

        from .server_resources.server_client import ServerClient

        return ServerClient
    elif name == "ServerClient":
        from .server_resources.server_client import ServerClient

        return ServerClient
    elif name == "ModelEngine":
        from .py_client.gaas.model import ModelEngine

        return ModelEngine
    elif name == "StorageEngine":
        from .py_client.gaas.storage import StorageEngine

        return StorageEngine
    elif name == "DatabaseEngine":
        from .py_client.gaas.database import DatabaseEngine

        return DatabaseEngine
    elif name == "VectorEngine":
        from .py_client.gaas.vector import VectorEngine

        return VectorEngine
    elif name == "FunctionEngine":
        from .py_client.gaas.function import FunctionEngine

        return FunctionEngine
    else:
        raise AttributeError(f"Could not find: {name}")


__all__ = [
    "RESTServer",
    "ServerClient",
    "ModelEngine",
    "StorageEngine",
    "DatabaseEngine",
    "VectorEngine",
]

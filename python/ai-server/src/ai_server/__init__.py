"""Main entrypoint into package."""

import warnings
from importlib import metadata

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = "0.0.25"
del metadata

from .server_resources.server_client import ServerClient
from .py_client.gaas.model import ModelEngine
from .py_client.gaas.storage import StorageEngine
from .py_client.gaas.database import DatabaseEngine
from .py_client.gaas.vector import VectorEngine
from .py_client.gaas.function import FunctionEngine


def RESTServer(*args, **kwargs):
    warnings.warn(
        "Use of RESTServer is deprecated. Please update your code to use ServerClient instead."
    )
    return ServerClient(*args, **kwargs)


__all__ = [
    "RESTServer",
    "ServerClient",
    "ModelEngine",
    "StorageEngine",
    "DatabaseEngine",
    "VectorEngine",
    "FunctionEngine",
]

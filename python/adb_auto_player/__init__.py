"""ADB Auto Player Package."""

from .command import Command
from .config_loader import ConfigLoader
from .device_stream import DeviceStream, StreamingNotSupported
from .exceptions import (
    GenericAdbError,
    NoPreviousScreenshotError,
    NotFoundError,
    NotInitializedError,
    TimeoutError,
    UnsupportedResolutionError,
)
from .game import Game

__all__: list[str] = [
    "Command",
    "ConfigLoader",
    "DeviceStream",
    "Game",
    "GenericAdbError",
    "NoPreviousScreenshotError",
    "NotFoundError",
    "NotInitializedError",
    "StreamingNotSupported",
    "TimeoutError",
    "UnsupportedResolutionError",
]

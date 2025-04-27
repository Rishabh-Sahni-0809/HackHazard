"""Terminator Python SDK"""

__version__ = "0.1.0"

from .client import DesktopUseClient, Locator, sleep
from .exceptions import ApiError, ConnectionError
from .models import (
    BasicResponse, BooleanResponse, TextResponse, ElementResponse, ElementsResponse,
    ClickResponse, AttributesResponse, BoundsResponse
    # Expose models selectively if needed, or keep them internal
)

__all__ = [
    "DesktopUseClient",
    "Locator",
    "ApiError",
    "ConnectionError",
    "sleep",
    # Add response models to __all__ if they should be public API
    "BasicResponse",
    "BooleanResponse",
    "TextResponse",
    "ElementResponse",
    "ElementsResponse",
    "ClickResponse",
    "AttributesResponse",
    "BoundsResponse",
] 
"""Common functions, classes and modules."""

from . import levels as CompressionLevel
from .methods import (
    Codec,
    CodecDefines,
    CompressionMethod,
    auto_detector,
)
from .types import (
    CompressorType,
    DecompressorType,
)


__all__ = (
    "Codec",
    "CodecDefines",
    "CompressionLevel",
    "CompressionMethod",
    "CompressorType",
    "DecompressorType",
    "auto_detector",
)

"""Simple stream readers for compressed buffers."""

from .gzip import GZIPCompressor
from .lz4 import LZ4Compressor
from .zstd import ZSTDCompressor


__all__ = (
    "GZIPCompressor",
    "LZ4Compressor",
    "ZSTDCompressor",
)

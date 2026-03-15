"""Simple stream readers for compressed buffers."""

from . import levels as CompressionLevel
from .gzip import GZIPCompressor
from .lz4 import LZ4Compressor
from .snappy import SNAPPYCompressor
from .zstd import ZSTDCompressor


__all__ = (
    "CompressionLevel",
    "GZIPCompressor",
    "LZ4Compressor",
    "SNAPPYCompressor",
    "ZSTDCompressor",
)

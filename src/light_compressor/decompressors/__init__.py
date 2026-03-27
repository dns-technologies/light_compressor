"""Simple stream readers for compressed buffers."""

from .decompressor import (
    DecompressReader,
    SnappyReader,
)
from .gzip import GZIPDecompressor
from .lz4 import LZ4Decompressor
from .reader import LimitedReader
from .snappy import SNAPDecompressor
from .zstd import ZSTDDecompressor


__all__ = (
    "DecompressReader",
    "GZIPDecompressor",
    "LimitedReader",
    "LZ4Decompressor",
    "SNAPDecompressor",
    "SnappyReader",
    "ZSTDDecompressor",
)

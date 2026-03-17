"""Simple stream readers for compressed buffers."""

from .decompressor import DecompressReader
from .gzip import GZIPDecompressor
from .lz4 import LZ4Decompressor
from .snappy import SNAPDecompressor
from .zstd import ZSTDDecompressor


__all__ = (
    "DecompressReader",
    "GZIPDecompressor",
    "LZ4Decompressor",
    "SNAPDecompressor",
    "ZSTDDecompressor",
)

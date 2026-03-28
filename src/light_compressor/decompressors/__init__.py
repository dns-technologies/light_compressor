"""Simple stream decompressors."""

from .gzip import GZIPDecompressor
from .lz4 import LZ4Decompressor
from .snappy import SNAPDecompressor
from .zstd import ZSTDDecompressor


__all__ = (
    "GZIPDecompressor",
    "LZ4Decompressor",
    "SNAPDecompressor",
    "ZSTDDecompressor",
)

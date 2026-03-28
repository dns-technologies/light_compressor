"""Simple stream compressors."""

from .gzip import GZIPCompressor
from .lz4 import LZ4Compressor
from .snappy import SNAPCompressor
from .zstd import ZSTDCompressor


__all__ = (
    "GZIPCompressor",
    "LZ4Compressor",
    "SNAPCompressor",
    "ZSTDCompressor",
)

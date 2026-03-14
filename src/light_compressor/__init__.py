"""Library for read compressed stream and write compressed chunks."""

from .compressor_method import (
    auto_detector,
    CompressionMethod,
)
from .compressors import (
    GZIPCompressor,
    LZ4Compressor,
    SNAPPYCompressor,
    ZSTDCompressor,
)
from .decompressors import (
    DecompressReader,
    GZIPDecompressor,
    LZ4Decompressor,
    SNAPPYDecompressor,
    ZSTDDecompressor,
)
from .reader import define_reader
from .writer import define_writer


__all__ = (
    "CompressionMethod",
    "DecompressReader",
    "GZIPCompressor",
    "GZIPDecompressor",
    "LZ4Compressor",
    "LZ4Decompressor",
    "SNAPPYCompressor",
    "SNAPPYDecompressor",
    "ZSTDCompressor",
    "ZSTDDecompressor",
    "auto_detector",
    "define_reader",
    "define_writer",
)
__version__ = "0.1.0.dev1"

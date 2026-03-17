"""Library for read compressed stream and write compressed chunks."""

from .compression_method import (
    auto_detector,
    CompressionMethod,
)
from .compressors import (
    CompressionLevel,
    GZIPCompressor,
    LZ4Compressor,
    SNAPCompressor,
    ZSTDCompressor,
)
from .decompressors import (
    DecompressReader,
    GZIPDecompressor,
    LZ4Decompressor,
    SNAPDecompressor,
    ZSTDDecompressor,
)
from .reader import define_reader
from .writer import define_writer


__all__ = (
    "CompressionLevel",
    "CompressionMethod",
    "DecompressReader",
    "GZIPCompressor",
    "GZIPDecompressor",
    "LZ4Compressor",
    "LZ4Decompressor",
    "SNAPCompressor",
    "SNAPDecompressor",
    "ZSTDCompressor",
    "ZSTDDecompressor",
    "auto_detector",
    "define_reader",
    "define_writer",
)
__version__ = "0.1.0.dev3"

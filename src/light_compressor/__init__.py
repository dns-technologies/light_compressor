"""Library for read compressed stream and write compressed chunks."""

from .common import (
    CompressionLevel,
    CompressionMethod,
    auto_detector,
)
from .common.types import (
    CompressorType,
    DecompressorType,
)
from .compressors import (
    GZIPCompressor,
    LZ4Compressor,
    SNAPCompressor,
    ZSTDCompressor,
)
from .decompressors import (
    GZIPDecompressor,
    LZ4Decompressor,
    SNAPDecompressor,
    ZSTDDecompressor,
)
from .openers import (
    DecompressReader,
    LimitedReader,
    SnappyReader,
)
from .reader import define_reader
from .writer import define_writer


__all__ = (
    "CompressionLevel",
    "CompressionMethod",
    "CompressorType",
    "DecompressorType",
    "DecompressReader",
    "GZIPCompressor",
    "GZIPDecompressor",
    "LimitedReader",
    "LZ4Compressor",
    "LZ4Decompressor",
    "SNAPCompressor",
    "SNAPDecompressor",
    "SnappyReader",
    "ZSTDCompressor",
    "ZSTDDecompressor",
    "auto_detector",
    "define_reader",
    "define_writer",
)
__version__ = "0.1.1.dev2"

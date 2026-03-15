from collections.abc import Iterable
from typing import Generator

from .compression_method import CompressionMethod
from .compressors import (
    CompressionLevel,
    GZIPCompressor,
    LZ4Compressor,
    SNAPPYCompressor,
    ZSTDCompressor,
)


def define_writer(
    bytes_data: Iterable[bytes],
    compressor_method: CompressionMethod = CompressionMethod.NONE,
    compressor_level: int = CompressionLevel.DEFAULT_COMPRESSION,
) -> Generator[bytes, None, None]:
    """Select current method for stream object."""

    if compressor_method is CompressionMethod.NONE:
        return bytes_data

    if compressor_method is CompressionMethod.GZIP:
        Compressor = GZIPCompressor
    elif compressor_method is CompressionMethod.LZ4:
        Compressor = LZ4Compressor
    elif compressor_method is CompressionMethod.SNAPPY:
        Compressor = SNAPPYCompressor
    elif compressor_method is CompressionMethod.ZSTD:
        Compressor = ZSTDCompressor
    else:
        raise ValueError(f"Unsupported compression method {compressor_method}")

    return Compressor(compressor_level).send_chunks(bytes_data)

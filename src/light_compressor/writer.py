from collections.abc import Iterable
from typing import Generator

from .compression_method import CompressionMethod
from .compressors import (
    CompressionLevel,
    GZIPCompressor,
    LZ4Compressor,
    SNAPCompressor,
    ZSTDCompressor,
)


def define_writer(
    bytes_data: Iterable[bytes],
    compressor_method: CompressionMethod = CompressionMethod.NONE,
    compressor_level: int = CompressionLevel.DEFAULT_COMPRESSION,
) -> Generator[bytes, None, None]:
    """Select current method for stream object."""

    if compressor_method.__class__ != CompressionMethod:
        raise ValueError(
            f"Unsupported compression method {compressor_method}",
        )

    if compressor_method is CompressionMethod.NONE:
        return bytes_data

    compressor: (
        GZIPCompressor | LZ4Compressor | SNAPCompressor | ZSTDCompressor
    ) = compressor_method.compressor(compressor_level)
    return compressor.send_chunks(bytes_data)

from collections.abc import (
    Generator,
    Iterable,
)
from typing import TYPE_CHECKING

from .compression_method import CompressionMethod
from .compressors import CompressionLevel

if TYPE_CHECKING:
    from .types import CompressorType


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

    compressor: CompressorType = compressor_method.compressor(compressor_level)
    return compressor.send_chunks(bytes_data)

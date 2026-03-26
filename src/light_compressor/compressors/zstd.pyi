from collections.abc import Generator
from typing import Iterable

from .levels import DEFAULT_COMPRESSION


class ZSTDCompressor:
    """ZSTD data_chunk compressor."""

    context: object
    compression_level: int
    decompressed_size: int
    _out_buffer_struct: object
    _in_buffer_struct: object
    _dst_buffer: object
    _src_buffer: object
    _dst_capacity: int

    def __init__(
        self,
        compression_level: int = DEFAULT_COMPRESSION,
    ) -> None:
        """Class initialization."""

        ...

    def send_chunks(
        self,
        bytes_data: Iterable[bytes],
    ) -> Generator[bytes, None, None]:
        """Generate compressed chunks from bytes chunks."""

        ...

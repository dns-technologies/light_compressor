from collections.abc import Generator
from typing import Iterable

from ..common import CompressionLevel


class GZIPCompressor:
    """Gzip chunk compressor."""

    compression_level: int
    context: object
    decompressed_size: int

    def __init__(
        self,
        compression_level: int = CompressionLevel.DEFAULT_COMPRESSION,
    ) -> None:
        """Class initialization."""

        ...

    def send_chunks(
        self,
        bytes_data: Iterable[bytes],
    ) -> Generator[bytes, None, None]:
        """Generate compressed chunks from bytes chunks."""

        ...

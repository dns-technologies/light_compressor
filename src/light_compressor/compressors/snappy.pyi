from collections.abc import Iterator
from typing import Iterable

from ..common import CompressionLevel


class SNAPCompressor:
    """Snappy chunk compressor."""

    def __init__(
        self,
        compression_level: int = CompressionLevel.DEFAULT_COMPRESSION,
    ) -> None:
        """Class initialization."""

        ...

    @property
    def compression_level(self) -> int:
        """Get compressor level value."""

        ...

    @property
    def decompressed_size(self) -> int:
        """Get decompressed size."""

        ...

    def send_chunks(
        self,
        bytes_data: Iterable[bytes],
    ) -> Iterator[bytes]:
        """Generate compressed chunks from bytes chunks."""

        ...

    def create_empty_frame(self) -> bytes:
        """Create snappy header."""

        ...

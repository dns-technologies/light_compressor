from collections.abc import Generator
from typing import Iterable

from .levels import DEFAULT_COMPRESSION


class SNAPCompressor:
    """Snappy chunk compressor."""

    compression_level: int
    decompressed_size: int

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

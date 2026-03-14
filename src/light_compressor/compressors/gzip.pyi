from collections.abc import Generator
from typing import Iterable


class GZIPCompressor:
    """Gzip chunk compressor."""

    def __init__(
        self,
        compression_level: int = -1,
    ) -> None:
        """Class initialization."""

        self.context: object
        self.decompressed_size: int
        ...

    def send_chunks(
        self,
        bytes_data: Iterable[bytes],
    ) -> Generator[bytes, None, None]:
        """Generate compressed chunks from bytes chunks."""

        ...

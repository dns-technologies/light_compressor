from collections.abc import Generator
from typing import Iterable


class SNAPPYCompressor:
    """Snappy chunk compressor."""

    def __init__(self) -> None:
        """Class initialization."""

        self.decompressed_size: int
        ...

    def send_chunks(
        self,
        bytes_data: Iterable[bytes],
    ) -> Generator[bytes, None, None]:
        """Generate compressed chunks from bytes chunks."""

        ...

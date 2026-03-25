from collections.abc import (
    Generator,
    Iterable,
)
from typing import (
    Protocol,
    runtime_checkable,
)


@runtime_checkable
class CompressorType(Protocol):
    """Protocol for compressor implementations."""

    compression_level: int
    decompressed_size: int

    def send_chunks(
        self,
        bytes_data: Iterable[bytes],
    ) -> Generator[bytes, None, None]:
        """Generate compressed chunks from bytes chunks."""
        ...


@runtime_checkable
class DecompressorType(Protocol):
    """Protocol for decompressor implementations."""

    eof: bool
    needs_input: bool
    unused_data: bytes

    def __enter__(self) -> "DecompressorType":
        """Enter context manager."""
        ...

    def __exit__(
        self,
        exception_type,
        exception,
        traceback,
    ) -> None:
        """Exit context manager."""
        ...

    def reset(self) -> None:
        """Reset the decompressor state."""
        ...

    def decompress(
        self,
        data: bytes | bytearray,
        max_length: int = -1,
    ) -> bytes:
        """Decompress part or all of a compressed frame."""
        ...

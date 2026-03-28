

class LZ4Decompressor:
    """LZ4 frame cython decompressor."""

    _context: object
    eof: bool
    needs_input: bool
    unused_data: bytes
    _unconsumed_data: bytes
    _return_bytearray: bool

    def __init__(self) -> None:
        """Class initialization."""

        ...

    def __enter__(self) -> "LZ4Decompressor":
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
        data: bytes | bytearray | memoryview,
        max_length: int = -1,
    ) -> bytes:
        """Decompresses part or all of an LZ4 frame of compressed data."""

        ...

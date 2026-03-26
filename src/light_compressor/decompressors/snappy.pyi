class SNAPDecompressor:
    """Snappy frame rust decompressor."""

    eof: bool
    needs_input: bool
    unused_data: bytes
    _unconsumed_data: bytes
    _return_bytearray: bool

    def __init__(self) -> None:
        """Class initialization."""

        ...

    def __enter__(self) -> "SNAPDecompressor":
        """Enter context manager."""
        ...

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
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
        """Decompresses part or all of a Snappy frame of compressed data."""
        ...

class SNAPPYDecompressor:
    """Snappy frame rust decompressor."""

    def __init__(self) -> None:
        """Class initialization."""

        self.eof: bool
        self.needs_input: bool
        self.unused_data: bytes
        self._unconsumed_data: bytes
        self._return_bytearray: bool

    def __enter__(self) -> "SNAPPYDecompressor":
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

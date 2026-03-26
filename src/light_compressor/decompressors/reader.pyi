from io import BufferedReader


class LimitedReader:
    """BufferedReader wrapper with read restrictions."""

    _reader: BufferedReader
    _limit: int
    _read: int

    def __init__(self, reader: BufferedReader, limit: int) -> None:
        """Class initialization."""
        ...

    def read(self, size: int = -1) -> bytes:
        """Read bytes data."""
        ...

    def readline(self, size: int = -1) -> bytes:
        """Read a lines of bytes data."""
        ...

    def readlines(self, hint: int = -1) -> list[bytes]:
        """Read a lines of bytes data."""
        ...

    def __iter__(self) -> "LimitedReader":
        """Return iterator."""
        ...

    def __next__(self) -> bytes:
        """Return next line."""
        ...

    def seekable(self) -> bool:
        """Check if reader is seekable."""
        ...

    def readable(self) -> bool:
        """Check if reader is readable."""
        ...

    def tell(self) -> int:
        """Return current position."""
        ...

    def close(self) -> None:
        """Close reader."""
        ...

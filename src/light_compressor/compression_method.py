from io import BufferedReader
from enum import Enum


class CompressionMethod(Enum):
    """List of compression codecs."""

    NONE = 0x02
    LZ4 = 0x82
    ZSTD = 0x90
    GZIP = 0x99
    SNAPPY = 0x9f

    @property
    def method(self) -> str:
        """return selected method."""

        return self.name.lower()


def auto_detector(fileobj: BufferedReader) -> CompressionMethod:
    """Auto detect method section from file signature.
    Warning!!! Not work with stream objects!!!"""

    pos = fileobj.tell()
    signature = fileobj.read(10)
    fileobj.seek(pos)

    if signature == b"\xff\x06\x00\x00sNaPpY":
        return CompressionMethod.SNAPPY
    if signature[:4] == b"\x04\"M\x18":
        return CompressionMethod.LZ4
    if signature[:4] == b"(\xb5/\xfd":
        return CompressionMethod.ZSTD
    if signature[:2] == b"\x1f\x8b":
        return CompressionMethod.GZIP
    return CompressionMethod.NONE

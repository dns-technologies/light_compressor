from enum import Enum
from io import BufferedReader
from typing import NamedTuple

from .compressors import (
    GZIPCompressor,
    LZ4Compressor,
    SNAPCompressor,
    ZSTDCompressor,
)
from .decompressors import (
    GZIPDecompressor,
    LZ4Decompressor,
    SNAPDecompressor,
    ZSTDDecompressor,
)
from .types import (
    CompressorType,
    DecompressorType,
)


class Codec(NamedTuple):
    """Define codec data."""

    signature: bytes
    compressor: CompressorType
    decompressor: DecompressorType


CODEC_DEFINES = {
    0x02: None,
    0x82: Codec(b"\x04\"M\x18", LZ4Compressor, LZ4Decompressor),
    0x90: Codec(b"(\xb5/\xfd", ZSTDCompressor, ZSTDDecompressor),
    0x99: Codec(b"\x1f\x8b", GZIPCompressor, GZIPDecompressor),
    0x9f: Codec(b"\xff\x06\x00\x00sNaPpY", SNAPCompressor, SNAPDecompressor),
}


class CodecDefines:
    """Base codec class."""

    name: str
    value: int
    _define: Codec | None = None

    @property
    def define(self) -> Codec:
        """return selected define."""

        if not self._define:
            self._define = CODEC_DEFINES[self.value]

        return self._define

    @property
    def method(self) -> str:
        """return selected method."""

        return self.name.lower()

    @property
    def signature(self) -> bytes:
        """return selected signature."""

        return self.define.signature

    @property
    def compressor(self) -> object:
        """return selected compressor."""

        return self.define.compressor

    @property
    def decompressor(self) -> object:
        """return selected decompressor."""

        return self.define.decompressor


class CompressionMethod(CodecDefines, Enum):
    """List of compression codecs."""

    NONE = 0x02
    LZ4 = 0x82
    ZSTD = 0x90
    GZIP = 0x99
    SNAPPY = 0x9f


def auto_detector(fileobj: BufferedReader) -> CompressionMethod:
    """Auto detect method section from file signature.
    Warning!!! Not work with stream objects!!!"""

    pos = fileobj.tell()
    signature = fileobj.read(10)
    fileobj.seek(pos)

    if signature == CompressionMethod.SNAPPY.signature:
        return CompressionMethod.SNAPPY
    if signature[:4] == CompressionMethod.LZ4.signature:
        return CompressionMethod.LZ4
    if signature[:4] == CompressionMethod.ZSTD.signature:
        return CompressionMethod.ZSTD
    if signature[:2] == CompressionMethod.GZIP.signature:
        return CompressionMethod.GZIP
    return CompressionMethod.NONE

"""Quick stream reader from compress file objects."""

from io import BufferedReader

from .compression_method import (
    auto_detector,
    CompressionMethod,
)
from .decompressors import (
    DecompressReader,
    SnappyReader,
)


READER = {CompressionMethod.SNAPPY: SnappyReader}


def define_reader(
    fileobj: BufferedReader,
    compressor_method: CompressionMethod | None = None,
) -> BufferedReader:
    """Select current method for stream object."""

    if not compressor_method:
        compressor_method = auto_detector(fileobj)

    if compressor_method is CompressionMethod.NONE:
        return fileobj

    raw = READER.get(compressor_method, DecompressReader)(
        fileobj,
        compressor_method.decompressor,
    )
    return BufferedReader(raw)

"""Quick stream reader from compress file objects."""

from io import BufferedReader

from .common.methods import (
    auto_detector,
    CompressionMethod,
)
from .openers import (
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

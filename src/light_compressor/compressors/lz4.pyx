from lz4.frame._frame import (
    create_compression_context,
    compress_begin,
    compress_chunk,
    compress_flush,
)

from light_compressor.common.levels import DEFAULT_COMPRESSION


cdef class LZ4Compressor:
    """LZ4 chunk compressor."""

    def __init__(
        self,
        short compression_level = DEFAULT_COMPRESSION,
    ):
        """Class initialization."""

        self.compression_level = compression_level
        self.context = create_compression_context()
        self.decompressed_size = 0

    def send_chunks(
        self,
        object bytes_data,
    ):
        """Generate compressed chunks from bytes chunks."""

        cdef bytes data_chunk

        yield compress_begin(
            self.context,
            compression_level=self.compression_level,
        )

        for data_chunk in bytes_data:
            yield compress_chunk(self.context, data_chunk)
            self.decompressed_size += len(data_chunk)

        yield compress_flush(self.context)

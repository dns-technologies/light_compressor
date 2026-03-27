from zlib import compressobj

from light_compressor.compressors.levels import DEFAULT_COMPRESSION


cdef class GZIPCompressor:
    """Gzip chunk compressor."""

    def __init__(
        self,
        short compression_level = DEFAULT_COMPRESSION,
    ):
        """Class initialization."""

        self.compression_level = compression_level
        self.context = compressobj(
            level=self.compression_level,
            method=8,
            wbits=31,
            memLevel=8,
            strategy=0
        )
        self.decompressed_size = 0

    def send_chunks(
        self,
        object bytes_data,
    ):
        """Generate compressed chunks from bytes chunks."""

        cdef bytes data_chunk

        for data_chunk in bytes_data:
            yield self.context.compress(data_chunk)
            self.decompressed_size += len(data_chunk)

        yield self.context.flush()

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

        cdef list compressed_chunks = []
        cdef bytes data_chunk, compressed
        self.decompressed_size = 0

        for data_chunk in bytes_data:
            if len(compressed_chunks) > 128:
                yield b"".join(compressed_chunks)
                compressed_chunks.clear()

            self.decompressed_size += len(data_chunk)
            compressed = self.context.compress(data_chunk)

            if compressed:
                compressed_chunks.append(compressed)

        compressed = self.context.flush()

        if compressed:
            compressed_chunks.append(compressed)

        if compressed_chunks:
            yield b"".join(compressed_chunks)

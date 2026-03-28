from zstandard._cffi import (
    ffi,
    lib,
)

from light_compressor.common.levels import DEFAULT_COMPRESSION


cdef class ZSTDCompressor:
    """ZSTD data_chunk compressor."""

    def __init__(
        self,
        short compression_level = DEFAULT_COMPRESSION,
    ):
        """Class initialization."""

        self.context = lib.ZSTD_createCCtx()
        self.compression_level = compression_level
        self.decompressed_size = 0
        self._out_buffer_struct = ffi.new("ZSTD_outBuffer *", {
            "dst": ffi.NULL,
            "size": 0,
            "pos": 0
        })
        self._in_buffer_struct = ffi.new("ZSTD_inBuffer *", {
            "src": ffi.NULL,
            "size": 0, 
            "pos": 0
        })
        self._dst_buffer = None
        self._src_buffer = None
        self._dst_capacity = 0

        if self.context == ffi.NULL:
            raise MemoryError("Failed to create compression context")

        lib.ZSTD_CCtx_setParameter(
            self.context,
            lib.ZSTD_c_compressionLevel,
            self.compression_level,
        )

    cdef void _setup_buffers(self, unsigned long long data_chunk_size):
        """Setup buffers for size."""

        cdef object dst_capacity = lib.ZSTD_compressBound(data_chunk_size)

        if dst_capacity > self._dst_capacity:
            self._dst_buffer = ffi.new("char[]", dst_capacity)
            self._dst_capacity = dst_capacity

        self._out_buffer_struct.dst = self._dst_buffer
        self._out_buffer_struct.size = self._dst_capacity
        self._out_buffer_struct.pos = 0

    cdef unsigned long long _setup_input_buffer(self, bytes data_chunk):
        """Setup input buffer for data."""

        cdef unsigned long long data_chunk_size = len(data_chunk)
        self._src_buffer = ffi.from_buffer(data_chunk)
        self._in_buffer_struct.src = self._src_buffer
        self._in_buffer_struct.size = data_chunk_size
        self._in_buffer_struct.pos = 0
        return data_chunk_size

    cdef list _compress_stream(self, object operation):
        """Compressed chunks."""

        cdef list compressed_chunks = []
        cdef object remaining, error_name
        cdef bytes compressed

        while self._in_buffer_struct.pos < self._in_buffer_struct.size:
            remaining = lib.ZSTD_compressStream2(
                self.context,
                self._out_buffer_struct,
                self._in_buffer_struct,
                operation,
            )

            if lib.ZSTD_isError(remaining):
                error_name = ffi.string(lib.ZSTD_getErrorName(remaining))
                raise ValueError(f"Compression error: {error_name}")

            if self._out_buffer_struct.pos > 0:
                compressed = bytes(ffi.buffer(
                    self._out_buffer_struct.dst,
                    self._out_buffer_struct.pos,
                ))
                compressed_chunks.append(compressed)
                self._out_buffer_struct.pos = 0

        return compressed_chunks

    cdef list _end_compression(self):
        """Finalize compression."""

        cdef list compressed_chunks = []
        cdef object remaining, error_name
        cdef bytes compressed

        self._in_buffer_struct.src = ffi.NULL
        self._in_buffer_struct.size = 0
        self._in_buffer_struct.pos = 0
        self._out_buffer_struct.pos = 0

        while 1:
            remaining = lib.ZSTD_compressStream2(
                self.context,
                self._out_buffer_struct,
                self._in_buffer_struct,
                lib.ZSTD_e_end,
            )

            if lib.ZSTD_isError(remaining):
                error_name = ffi.string(lib.ZSTD_getErrorName(remaining))
                raise ValueError(f"Compression end error: {error_name}")

            if self._out_buffer_struct.pos > 0:
                compressed = bytes(ffi.buffer(
                    self._out_buffer_struct.dst,
                    self._out_buffer_struct.pos,
                ))
                compressed_chunks.append(compressed)
                self._out_buffer_struct.pos = 0

            if remaining == 0:
                break

        return compressed_chunks

    def send_chunks(
        self,
        object bytes_data,
    ):
        """Generate compressed chunks from bytes chunks."""

        cdef list compressed_chunks = []
        cdef bytes data_chunk
        cdef unsigned long long data_chunk_size
        cdef bint has_data = False
        cdef object iterator
        cdef size_t compressed_size
        cdef bytes empty_frame

        self.decompressed_size = 0
        iterator = iter(bytes_data)

        try:
            first = next(iterator)
            has_data = True
        except StopIteration:
            has_data = False

        if not has_data:
            compressed_size = lib.ZSTD_compressBound(0)
            out_buffer = ffi.new("char[]", compressed_size)
            compressed_size = lib.ZSTD_compress(
                out_buffer, compressed_size,
                ffi.NULL, 0,
                self.compression_level
            )

            if lib.ZSTD_isError(compressed_size):
                error_name = ffi.string(
                    lib.ZSTD_getErrorName(compressed_size),
                )
                raise ValueError(
                    f"Empty frame compression error: {error_name}",
                )

            empty_frame = bytes(ffi.buffer(out_buffer, compressed_size))
            yield empty_frame
            lib.ZSTD_freeCCtx(self.context)
            return

        data_chunk_size = self._setup_input_buffer(first)
        self.decompressed_size += data_chunk_size
        self._setup_buffers(data_chunk_size)

        for chunk in self._compress_stream(lib.ZSTD_e_continue):
            yield chunk

        for data_chunk in iterator:
            data_chunk_size = self._setup_input_buffer(data_chunk)
            self.decompressed_size += data_chunk_size
            self._setup_buffers(data_chunk_size)

            for chunk in self._compress_stream(lib.ZSTD_e_continue):
                yield chunk

        for chunk in self._end_compression():
            yield chunk

        lib.ZSTD_freeCCtx(self.context)

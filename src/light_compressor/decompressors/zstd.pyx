from zstandard._cffi import (
    ffi,
    lib,
)


cdef long BUFFER = 65536


cdef class ZSTDDecompressor:
    """ZSTD frame cython decompressor."""

    def __init__(self):

        self._dctx = lib.ZSTD_createDCtx()

        if self._dctx == ffi.NULL:
            raise MemoryError("Unable to create ZSTD decompression context")

        self._dctx = ffi.gc(
            self._dctx, 
            lib.ZSTD_freeDCtx, 
            size=lib.ZSTD_sizeof_DCtx(self._dctx)
        )
        self.eof = False
        self.needs_input = True
        self.unused_data = b""
        self._unconsumed_data = b""
        self._return_bytearray = False
        self._in_buffer = ffi.new("ZSTD_inBuffer *")
        self._input_buffer = None
        self._input_data = None

    def __enter__(self):

        return self

    def __exit__(
        self,
        object exception_type,
        object exception,
        object traceback,
    ):

        self._dctx = None
        self.eof = None
        self.needs_input = None
        self.unused_data = None
        self._unconsumed_data = None
        self._return_bytearray = None
        self._input_buffer = None
        self._input_data = None

    cpdef void reset(self):
        """Reset the decompressor state."""

        cdef unsigned long long decompressed_size

        decompressed_size = lib.ZSTD_DCtx_reset(self._dctx, lib.ZSTD_reset_session_only)

        if lib.ZSTD_isError(decompressed_size):
            raise RuntimeError("Unable to reset ZSTD context")

        self.eof = False
        self.needs_input = True
        self.unused_data = None
        self._unconsumed_data = None
        self._in_buffer.pos = 0
        self._in_buffer.size = 0
        self._input_buffer = None
        self._input_data = None

    cpdef bytes decompress(
        self,
        object data,
        long long max_length = -1,
    ):
        """Decompresses part or all of ZSTD compressed data."""

        cdef object out_buffer, out_data, input_cdata
        cdef size_t output_size
        cdef unsigned long long decompressed_size
        cdef list result_parts = []
        cdef size_t total_decompressed = 0
        cdef size_t last_pos

        if max_length == -1:
            output_size = BUFFER
        else:
            if max_length > 0:
                output_size = max_length
            else:
                output_size = BUFFER

        if data.__class__ not in (bytes, bytearray):
            data = memoryview(data).tobytes()

        if self._unconsumed_data:
            data = self._unconsumed_data + data
            self._unconsumed_data = b""

        if data:
            self._input_data = data
            input_cdata = ffi.from_buffer(self._input_data)
            self._in_buffer.src = input_cdata
            self._in_buffer.size = len(data)
            self._in_buffer.pos = 0
        else:
            self._in_buffer.src = ffi.NULL
            self._in_buffer.size = 0
            self._in_buffer.pos = 0
            self._input_data = None

        last_pos = 0

        while True:
            out_data = ffi.new("char[]", output_size)
            out_buffer = ffi.new("ZSTD_outBuffer *")
            out_buffer.dst = out_data
            out_buffer.size = output_size
            out_buffer.pos = 0
            decompressed_size = lib.ZSTD_decompressStream(
                self._dctx,
                out_buffer,
                self._in_buffer,
            )

            if lib.ZSTD_isError(decompressed_size):
                if self._in_buffer.pos < self._in_buffer.size:
                    self.unused_data = data[self._in_buffer.pos:] if data else b""
                    self._unconsumed_data = b""
                self.eof = True
                self.needs_input = False
                break

            if out_buffer.pos > 0:
                result_parts.append(ffi.buffer(out_data, out_buffer.pos)[:])
                total_decompressed += out_buffer.pos

            if decompressed_size == 0:
                if self._in_buffer.pos < self._in_buffer.size:
                    self.unused_data = data[self._in_buffer.pos:] if data else b""
                    self._unconsumed_data = b""
                else:
                    self.unused_data = b""
                    self._unconsumed_data = b""
                self.eof = True
                self.needs_input = False
                break

            if max_length != -1 and total_decompressed >= max_length:
                if self._in_buffer.pos < self._in_buffer.size:
                    self._unconsumed_data = data[self._in_buffer.pos:] if data else b""
                self.needs_input = False
                break

            if self._in_buffer.pos >= self._in_buffer.size:
                self.needs_input = True
                break

        result = b"".join(result_parts)

        if max_length != -1 and len(result) > max_length:
            result = result[:max_length]

        return result

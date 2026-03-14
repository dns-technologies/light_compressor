from zlib import decompressobj


cdef class GZIPDecompressor:
    """Gzip frame cython decompressor."""

    def __init__(self):
        """Initialize the decompressor."""

        self._decompressor = decompressobj(31)
        self.eof = False
        self.needs_input = True
        self.unused_data = b""
        self._unconsumed_data = b""
        self._return_bytearray = False

    def __enter__(self):

        return self

    def __exit__(
        self,
        object exception_type,
        object exception,
        object traceback,
    ):

        self._decompressor = None
        self.eof = None
        self.needs_input = None
        self.unused_data = None
        self._unconsumed_data = None
        self._return_bytearray = None

    cpdef void reset(self):
        """Reset the decompressor state."""

        self._decompressor = decompressobj(31)
        self.eof = False
        self.needs_input = True
        self.unused_data = b""
        self._unconsumed_data = b""

    cpdef bytes decompress(
        self,
        object data,
        long long max_length = -1,
    ):
        """Decompresses part or all of a gzip frame of compressed data."""

        cdef bytes decompressed
        cdef bytes result

        if not isinstance(data, (bytes, bytearray)):
            data = memoryview(data).tobytes()

        if self._unconsumed_data:
            data = self._unconsumed_data + data

        if max_length > 0:
            decompressed = self._decompressor.decompress(data, max_length)
        else:
            decompressed = self._decompressor.decompress(data)

        unconsumed = self._decompressor.unconsumed_tail
        eoframe = self._decompressor.eof

        if unconsumed:
            self._unconsumed_data = unconsumed
            self.needs_input = False
        else:
            self._unconsumed_data = b""
            self.needs_input = True

        if eoframe:
            self.unused_data = self._decompressor.unused_data
            self.eof = True
        else:
            self.unused_data = b""

        return decompressed

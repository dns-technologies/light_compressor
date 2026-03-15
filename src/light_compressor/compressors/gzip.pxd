cdef class GZIPCompressor:

    cdef public short compression_level
    cdef public object context
    cdef public unsigned long long decompressed_size

cdef class LZ4Compressor:

    cdef public short compression_level
    cdef public object context
    cdef public unsigned long long decompressed_size

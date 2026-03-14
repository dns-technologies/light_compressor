cdef class GZIPCompressor:

    cdef public object context
    cdef public unsigned long long decompressed_size

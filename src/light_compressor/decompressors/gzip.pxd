cdef class GZIPDecompressor:

    cdef public object _decompressor
    cdef public object eof
    cdef public object needs_input
    cdef public bytes unused_data
    cdef public bytes _unconsumed_data
    cdef public object _return_bytearray

    cpdef void reset(self)
    cpdef bytes decompress(
        self,
        object data,
        long long max_length=*,
    )

cdef class DecompressReader:

    cdef public object _fp
    cdef public bint _eof
    cdef public long long _pos
    cdef public long long _size
    cdef public object _decomp_factory
    cdef public dict _decomp_args
    cdef public object _decompressor
    cdef public tuple _trailing_error

    cdef void _rewind(self)

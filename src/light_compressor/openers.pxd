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


cdef class SnappyReader:

    cdef public object _fp
    cdef public bint _eof
    cdef public long long _pos
    cdef public long long _size
    cdef public object _decompressor
    cdef public object _decomp_factory
    cdef public dict _decomp_args
    cdef public bytes _unconsumed_data
    
    cdef void _rewind(self)


cdef class LimitedReader:

    cdef public object _reader
    cdef public long long _limit
    cdef public long long _read

    cpdef bytes read(self, int size=*)
    cpdef bytes readline(self, int size=*)
    cpdef list readlines(self, int hint=*)
    cpdef bint seekable(self)
    cpdef bint readable(self)
    cpdef long long tell(self)
    cpdef void close(self)

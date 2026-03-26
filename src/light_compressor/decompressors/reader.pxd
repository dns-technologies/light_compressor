cdef class LimitedReader:
    """BufferedReader wrapper with read restrictions."""

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

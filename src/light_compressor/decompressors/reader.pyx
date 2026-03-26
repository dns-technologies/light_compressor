cdef class LimitedReader:
    """BufferedReader wrapper with read restrictions."""

    def __init__(self, object reader, long long limit):
        """Class initialization."""

        self._reader = reader
        self._limit = limit
        self._read = reader.tell()

    cpdef bytes read(self, int size = -1):
        """Read bytes data."""

        cdef int remaining, to_read
        cdef bytes data

        if self._read >= self._limit:
            return b""

        if size < 0:
            remaining = self._limit - self._read
            data = self._reader.read(remaining)
        else:
            to_read = min(size, self._limit - self._read)
            if to_read <= 0:
                return b""
            data = self._reader.read(to_read)

        self._read += len(data)
        return data

    cpdef bytes readline(self, int size = -1):
        """Read a lines of bytes data."""

        cdef int remaining, to_read
        cdef bytes line

        if self._read >= self._limit:
            return b""

        remaining = self._limit - self._read

        if size > 0:
            to_read = min(size, remaining)
            line = self._reader.readline(to_read)
        else:
            line = self._reader.readline(remaining)

        self._read += len(line)
        return line

    cpdef list readlines(self, int hint = -1):
        """Read a lines of bytes data."""

        cdef list lines = []

        while True:
            line = self.readline()

            if not line:
                break

            lines.append(line)

            if hint > 0 and len(b"".join(lines)) >= hint:
                break

        return lines

    def __iter__(self):
        """Return iterator."""

        return self

    def __next__(self):
        """Return next line."""

        cdef bytes line = self.readline()

        if not line:
            raise StopIteration

        return line

    cpdef bint seekable(self):
        """Check if reader is seekable."""

        return False

    cpdef bint readable(self):
        """Check if reader is readable."""

        return self._reader.readable()

    cpdef long long tell(self):
        """Return current position."""

        return self._read

    cpdef void close(self):
        """Close reader."""

        self._reader.close()

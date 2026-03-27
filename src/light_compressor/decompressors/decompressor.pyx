from io import (
    DEFAULT_BUFFER_SIZE,
    SEEK_CUR,
    SEEK_END,
    SEEK_SET,
)
from sys import maxsize

from cython cimport (
    boundscheck,
    wraparound,
)


cdef class DecompressReader:
    """Adapts the decompressor reader API."""

    def __cinit__(self):
        """Cython initialization."""

        self._fp = None
        self._eof = False
        self._pos = 0
        self._size = -1
        self._decomp_factory = None
        self._decomp_args = None
        self._decompressor = None
        self._trailing_error = None

    def __init__(
        self,
        object fp,
        object decomp_factory,
        tuple trailing_error = (),
        **decomp_args
    ):
        """Class initialization."""

        self._fp = fp
        self._eof = False
        self._pos = 0
        self._size = -1
        self._decomp_factory = decomp_factory
        self._decomp_args = decomp_args
        self._decompressor = decomp_factory(**decomp_args)
        self._trailing_error = trailing_error

    def close(self):
        """Close the stream."""

        self._decompressor = None
        self._fp = None

    @property
    def closed(self):
        """Check if the stream is closed."""

        return self._fp is None

    def fileno(self):
        """Return the underlying file descriptor."""

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        if hasattr(self._fp, 'fileno'):
            return self._fp.fileno()

        raise OSError("fileno not supported on underlying stream")

    def flush(self):
        """Flush the stream."""

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        if hasattr(self._fp, 'flush'):
            self._fp.flush()

    def isatty(self):
        """Check if the stream is interactive."""

        if self._fp is None:
            return False

        if hasattr(self._fp, 'isatty'):
            return self._fp.isatty()

        return False

    def readable(self):
        """Check if the stream is readable."""

        return True

    def readline(self, size: int = -1):
        """Read a line of decompressed data."""

        cdef:
            list chunks = []
            bytes data, result
            Py_ssize_t total = 0
            Py_ssize_t nl_pos, excess

        if not self.readable():
            raise OSError("Stream not readable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        while True:
            data = self.read(1024)

            if not data:
                break

            chunks.append(data)
            total += len(data)
            nl_pos = data.find(b'\n')

            if nl_pos != -1:
                excess = len(data) - (nl_pos + 1)

                if excess > 0:
                    self.seek(-excess, SEEK_CUR)
                break

            if size != -1 and total >= size:
                break

        result = b''.join(chunks)

        if size != -1 and len(result) > size:
            result = result[:size]

        return result

    def readlines(self, hint: int = -1):
        """Read lines from the stream."""

        cdef:
            list lines = []
            bytes line
            Py_ssize_t total = 0

        if not self.readable():
            raise OSError("Stream not readable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        while True:
            line = self.readline()
            if not line:
                break

            lines.append(line)
            total += len(line)

            if hint != -1 and total >= hint:
                break

        return lines

    def seekable(self):
        """Check if the stream is seekable."""

        if self._fp is None:
            return False

        return self._fp.seekable()

    def tell(self):
        """Return current position."""

        return self._pos

    def truncate(self, size: int | None = None):
        """Truncate the stream."""

        raise OSError("truncate not supported on decompression stream")

    def writable(self):
        """Check if the stream is writable."""

        return False

    def writelines(self, lines: list):
        """Write lines to the stream."""

        raise OSError("write not supported on decompression stream")

    def write(self, b: memoryview):
        """Write to the stream."""

        raise OSError("write not supported on decompression stream")

    @boundscheck(False)
    @wraparound(False)
    def readinto(self, b: memoryview):
        """Read data into a buffer."""

        cdef:
            bytes data
            Py_ssize_t length

        if not self.readable():
            raise OSError("Stream not readable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        if isinstance(b, bytearray):
            data = self.read(len(b))
            length = len(data)
            (<bytearray>b)[:length] = data
            return length

        if isinstance(b, memoryview):
            with memoryview(b) as view, view.cast("B") as byte_view:
                data = self.read(len(byte_view))
                length = len(data)
                byte_view[:length] = data
            return length

        with memoryview(b) as view, view.cast("B") as byte_view:
            data = self.read(len(byte_view))
            length = len(data)
            byte_view[:length] = data

        return length

    def read(self, size: int = -1):
        """Read decompressed data."""

        cdef:
            bytes rawblock
            bytes data
            bint needs_input

        if not self.readable():
            raise OSError("Stream not readable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        if size < 0:
            return self.readall()

        if not size or self._eof:
            return b""

        data = None

        while True:
            if self._decompressor.eof:
                rawblock = self._decompressor.unused_data

                if not rawblock:
                    rawblock = self._fp.read(DEFAULT_BUFFER_SIZE)

                if not rawblock:
                    break

                self._decompressor = self._decomp_factory(
                    **self._decomp_args
                )

                try:
                    data = self._decompressor.decompress(rawblock, size)
                except self._trailing_error:
                    break
            else:
                needs_input = self._decompressor.needs_input
                if needs_input:
                    rawblock = self._fp.read(DEFAULT_BUFFER_SIZE)
                    if not rawblock:
                        # Проверяем, есть ли накопленные данные
                        if self._decompressor._unconsumed_data:
                            break
                        raise EOFError(
                            "Compressed file ended before the "
                            "end-of-stream marker was reached"
                        )
                else:
                    rawblock = b""

                data = self._decompressor.decompress(rawblock, size)

            if data:
                break

        if not data:
            self._eof = True
            self._size = self._pos
            return b""

        self._pos += len(data)

        return data

    def readall(self):
        """Read all decompressed data."""

        cdef:
            list chunks = []
            bytes data

        if not self.readable():
            raise OSError("Stream not readable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        while True:
            data = self.read(maxsize)

            if not data:
                break

            chunks.append(data)

        return b"".join(chunks)

    cdef void _rewind(self):
        """Rewind the stream to the beginning."""

        if self._fp is None:
            return

        self._fp.seek(0)
        self._eof = False
        self._pos = 0
        self._decompressor = self._decomp_factory(**self._decomp_args)

    def seek(self, offset: int, whence: int = SEEK_SET):
        """Seek to a position in the stream."""

        cdef:
            long long target_pos
            long long bytes_to_skip
            bytes data

        if not self.seekable():
            raise OSError("Stream not seekable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        if whence == SEEK_SET:
            target_pos = offset
        elif whence == SEEK_CUR:
            target_pos = self._pos + offset
        elif whence == SEEK_END:
            if self._size < 0:
                while self.read(DEFAULT_BUFFER_SIZE):
                    pass
            target_pos = self._size + offset
        else:
            raise ValueError("Invalid value for whence: {}".format(whence))

        if target_pos < 0:
            raise ValueError("Negative seek position")

        # Если позиция не изменилась, ничего не делаем
        if target_pos == self._pos:
            return self._pos

        # Если seek назад (меньше текущей позиции) - пересоздаем декомпрессор
        if target_pos < self._pos:
            self._rewind()
            bytes_to_skip = target_pos
        else:
            # Если seek вперед - просто читаем нужное количество байт
            bytes_to_skip = target_pos - self._pos

        # Пропускаем bytes_to_skip байт
        while bytes_to_skip > 0:
            data = self.read(min(DEFAULT_BUFFER_SIZE, bytes_to_skip))
            if not data:
                break
            bytes_to_skip -= len(data)

        return self._pos

    def __enter__(self):
        """Context manager entry."""

        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object):
        """Context manager exit."""

        self.close()

    def __iter__(self):
        """Return iterator."""

        return self

    def __next__(self):
        """Return next line."""

        cdef bytes line = self.readline()

        if not line:
            raise StopIteration

        return line


cdef class SnappyReader:
    """Snappy-specific decompressor reader."""
    
    def __cinit__(self):
        """Cython initialization."""

        self._fp = None
        self._eof = False
        self._pos = 0
        self._size = -1
        self._decompressor = None
        self._decomp_factory = None
        self._decomp_args = None
        self._unconsumed_data = b""

    def __init__(self, fp, decomp_factory, **decomp_args):
        """Class initialization."""

        self._fp = fp
        self._decomp_factory = decomp_factory
        self._decomp_args = decomp_args
        self._decompressor = decomp_factory(**decomp_args)
        self._unconsumed_data = b""

    def close(self):
        """Close the stream."""

        self._decompressor = None
        self._fp = None

    @property
    def closed(self):
        """Check if the stream is closed."""

        return self._fp is None

    def fileno(self):
        """Return the underlying file descriptor."""

        if self._fp is None:
            raise ValueError("I/O operation on closed file")
        if hasattr(self._fp, 'fileno'):
            return self._fp.fileno()
        raise OSError("fileno not supported on underlying stream")

    def flush(self):
        """Flush the stream."""

        if self._fp is None:
            raise ValueError("I/O operation on closed file")
        if hasattr(self._fp, 'flush'):
            self._fp.flush()

    def isatty(self):
        """Check if the stream is interactive."""

        if self._fp is None:
            return False
        if hasattr(self._fp, 'isatty'):
            return self._fp.isatty()
        return False

    def readable(self):
        """Check if the stream is readable."""

        return True

    def readline(self, size: int = -1):
        """Read a line of decompressed data."""

        cdef:
            list chunks = []
            bytes data, result
            Py_ssize_t total = 0
            Py_ssize_t nl_pos, excess

        if not self.readable():
            raise OSError("Stream not readable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        while True:
            data = self.read(1024)
            if not data:
                break
            chunks.append(data)
            total += len(data)
            nl_pos = data.find(b'\n')
            if nl_pos != -1:
                excess = len(data) - (nl_pos + 1)
                if excess > 0:
                    self.seek(-excess, SEEK_CUR)
                break
            if size != -1 and total >= size:
                break

        result = b''.join(chunks)
        if size != -1 and len(result) > size:
            result = result[:size]
        return result

    def readlines(self, hint: int = -1):
        """Read lines from the stream."""

        cdef:
            list lines = []
            bytes line
            Py_ssize_t total = 0

        if not self.readable():
            raise OSError("Stream not readable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        while True:
            line = self.readline()
            if not line:
                break
            lines.append(line)
            total += len(line)
            if hint != -1 and total >= hint:
                break
        return lines

    def seekable(self):
        """Check if the stream is seekable."""

        if self._fp is None:
            return False
        return self._fp.seekable()

    def tell(self):
        """Return current position."""

        return self._pos

    def truncate(self, size: int | None = None):
        """Truncate the stream."""

        raise OSError("truncate not supported on decompression stream")

    def writable(self):
        """Check if the stream is writable."""

        return False

    def writelines(self, lines: list):
        """Write lines to the stream."""

        raise OSError("write not supported on decompression stream")

    def write(self, b: memoryview):
        """Write to the stream."""

        raise OSError("write not supported on decompression stream")

    @boundscheck(False)
    @wraparound(False)
    def readinto(self, b: memoryview):
        """Read data into a buffer."""

        cdef:
            bytes data
            Py_ssize_t length

        if not self.readable():
            raise OSError("Stream not readable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        if isinstance(b, bytearray):
            data = self.read(len(b))
            length = len(data)
            (<bytearray>b)[:length] = data
            return length

        if isinstance(b, memoryview):
            with memoryview(b) as view, view.cast("B") as byte_view:
                data = self.read(len(byte_view))
                length = len(data)
                byte_view[:length] = data
            return length

        with memoryview(b) as view, view.cast("B") as byte_view:
            data = self.read(len(byte_view))
            length = len(data)
            byte_view[:length] = data
        return length

    def read(self, size: int = -1):
        """Read decompressed data."""

        if not self.readable():
            raise OSError("Stream not readable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        if size < 0:
            return self.readall()

        if not size:
            return b""

        result = bytearray()
        remaining = size

        if self._unconsumed_data:
            take = min(remaining, len(self._unconsumed_data))
            result.extend(self._unconsumed_data[:take])
            self._unconsumed_data = self._unconsumed_data[take:]
            remaining -= take

            if remaining == 0:
                self._pos += len(result)
                return bytes(result)

        if self._eof:
            self._pos += len(result)
            return bytes(result) if result else b""

        compressed_data = self._fp.read()

        if not compressed_data:
            self._eof = True
            self._pos += len(result)
            return bytes(result) if result else b""

        try:
            decompressed = self._decompressor.decompress(compressed_data)
        except Exception as e:
            self._pos += len(result)
            return bytes(result) if result else b""

        if not decompressed:
            self._eof = True
            self._pos += len(result)
            return bytes(result) if result else b""

        take = min(remaining, len(decompressed))
        result.extend(decompressed[:take])

        if take < len(decompressed):
            self._unconsumed_data = decompressed[take:]

        self._pos += len(result)
        return bytes(result)

    def readall(self):
        """Read all decompressed data."""

        cdef:
            list chunks = []
            bytes data

        if not self.readable():
            raise OSError("Stream not readable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        while True:
            data = self.read(maxsize)
            if not data:
                break
            chunks.append(data)
        return b"".join(chunks)

    cdef void _rewind(self):
        """Rewind the stream to the beginning."""

        if self._fp is None:
            return

        self._fp.seek(0)
        self._eof = False
        self._pos = 0
        self._decompressor = self._decomp_factory(**self._decomp_args)
        self._unconsumed_data = b""

    def seek(self, offset: int, whence: int = SEEK_SET):
        """Seek to a position in the stream."""

        cdef:
            long long target_pos
            long long bytes_to_skip
            bytes data

        if not self.seekable():
            raise OSError("Stream not seekable")

        if self._fp is None:
            raise ValueError("I/O operation on closed file")

        if whence == SEEK_SET:
            target_pos = offset
        elif whence == SEEK_CUR:
            target_pos = self._pos + offset
        elif whence == SEEK_END:
            if self._size < 0:

                while self.read(DEFAULT_BUFFER_SIZE):
                    pass

            target_pos = self._size + offset
        else:
            raise ValueError("Invalid value for whence: {}".format(whence))

        if target_pos < 0:
            raise ValueError("Negative seek position")

        if target_pos < self._pos:
            self._rewind()
            bytes_to_skip = target_pos
        else:
            bytes_to_skip = target_pos - self._pos

        while bytes_to_skip > 0:
            data = self.read(min(DEFAULT_BUFFER_SIZE, bytes_to_skip))

            if not data:
                break

            bytes_to_skip -= len(data)

        return self._pos

    def __enter__(self):
        """Context manager entry."""

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""

        self.close()

    def __iter__(self):
        """Return iterator."""

        return self

    def __next__(self):
        """Return next line."""

        cdef bytes line = self.readline()

        if not line:
            raise StopIteration

        return line

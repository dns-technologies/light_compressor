import pytest
from random import randbytes, randint
from light_compressor import (
    define_reader,
    CompressionMethod,
    SNAPPYCompressor,
)
from io import BytesIO


@pytest.fixture
def small_data():
    """Фиксированные данные малого размера."""

    return [
        b"Hello, world!",
        b"Small test message",
        b"Snappy compression",
        b"Another chunk",
    ]


@pytest.fixture
def medium_data():
    """Данные среднего размера (50 чанков)."""

    return [randbytes(randint(20, 40)) for _ in range(50)]  # noqa: S311


@pytest.fixture
def large_data():
    """Данные большого размера (200 чанков)."""
    return [randbytes(randint(20, 40)) for _ in range(200)]  # noqa: S311


def test_snappy_small_data(small_data):
    """Тест Snappy на малых данных."""

    fileobj = BytesIO()
    compressor = SNAPPYCompressor()

    for data in compressor.send_chunks(small_data):
        fileobj.write(data)

    assert len(b"".join(small_data)) == compressor.decompressed_size  # noqa: S101

    fileobj.seek(0)
    stream = define_reader(fileobj, CompressionMethod.SNAPPY)
    result = stream.read()

    assert b"".join(small_data) == result  # noqa: S101


def test_snappy_medium_data(medium_data):
    """Тест Snappy на данных среднего размера."""

    fileobj = BytesIO()
    compressor = SNAPPYCompressor()

    for data in compressor.send_chunks(medium_data):
        fileobj.write(data)

    assert len(b"".join(medium_data)) == compressor.decompressed_size  # noqa: S101

    fileobj.seek(0)
    stream = define_reader(fileobj, CompressionMethod.SNAPPY)
    result = stream.read()

    assert b"".join(medium_data) == result  # noqa: S101


def test_snappy_large_data(large_data):
    """Тест Snappy на данных большого размера."""

    fileobj = BytesIO()
    compressor = SNAPPYCompressor()

    for data in compressor.send_chunks(large_data):
        fileobj.write(data)

    assert len(b"".join(large_data)) == compressor.decompressed_size  # noqa: S101

    fileobj.seek(0)
    stream = define_reader(fileobj, CompressionMethod.SNAPPY)
    result = stream.read()

    assert b"".join(large_data) == result  # noqa: S101


def test_snappy_compression_decompression_cycle():
    """Полный цикл компрессии-декомпрессии с разными размерами."""

    for size in [10, 50, 100, 150, 200, 250]:
        data = [randbytes(randint(20, 40)) for _ in range(size)]  # noqa: S311
        fileobj = BytesIO()
        compressor = SNAPPYCompressor()

        for compressed in compressor.send_chunks(data):
            fileobj.write(compressed)

        assert len(b"".join(data)) == compressor.decompressed_size  # noqa: S101

        fileobj.seek(0)
        stream = define_reader(fileobj, CompressionMethod.SNAPPY)
        result = stream.read()

        assert b"".join(data) == result, f"Failed for size {size}"  # noqa: S101

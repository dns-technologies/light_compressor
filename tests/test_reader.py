import pytest

from io import BytesIO
from light_compressor import (
    define_reader,
    define_writer,
    CompressionMethod,
    CompressorType,
)


fileobj = BytesIO()
bytes_data = [
    b"id,name,age,email,address,phone,created_at\n",
    b"1,John Doe,25,john.doe@example.com,123 "
    b"Main St,555-0101,2024-01-15 10:30:00\n",
    b"2,Jane Smith,30,jane.smith@example.com,456 Oak "
    b"Ave,555-0102,2024-01-15 11:45:00\n",
    b"3,Bob Johnson,35,bob.johnson@example.com,789 "
    b"Pine Rd,555-0103,2024-01-15 14:20:00\n",
    b"4,Alice Brown,28,alice.brown@example.com,321 "
    b"Elm St,555-0104,2024-01-16 09:15:00\n",
    b"5,Charlie Wilson,32,charlie.wilson@example.com,654 "
    b"Maple Dr,555-0105,2024-01-16 13:30:00\n",
    b"6,Diana Miller,27,diana.miller@example.com,987 Cedar "
    b"Ln,555-0106,2024-01-17 08:45:00\n",
    b"7,Edward Davis,40,edward.davis@example.com,147 "
    b"Birch Ct,555-0107,2024-01-17 16:00:00\n",
    b"8,Fiona Garcia,33,fiona.garcia@example.com,258 "
    b"Spruce Way,555-0108,2024-01-18 10:00:00\n",
    b"9,George Rodriguez,38,george.rodriguez@example.com,369 "
    b"Willow St,555-0109,2024-01-18 15:30:00\n",
    b"10,Helen Martinez,29,helen.martinez@example.com,741 "
    b"Ash Ave,555-0110,2024-01-19 11:15:00\n",
] * 1000


def generate_realistic_data(num_rows: int = 1000) -> list[bytes]:
    """Генерирует реалистичные CSV данные с повторяющимися паттернами."""
    header = b"id,name,age,email,address,phone,created_at\n"
    result = [header]

    names = [
        "John Doe",
        "Jane Smith",
        "Bob Johnson",
        "Alice Brown",
        "Charlie Wilson",
        "Diana Miller",
        "Edward Davis",
        "Fiona Garcia",
        "George Rodriguez",
        "Helen Martinez",
        "Ivan Petrov",
        "Maria Sidorova",
        "Alexey Ivanov",
        "Elena Kuznetsova",
        "Dmitry Smirnov",
    ]
    domains = [
        "example.com",
        "test.com",
        "sample.org",
        "demo.net",
        "data.io",
    ]
    streets = [
        "Main St",
        "Oak Ave",
        "Pine Rd",
        "Elm St",
        "Maple Dr",
        "Cedar Ln",
        "Birch Ct",
        "Spruce Way",
        "Willow St",
        "Ash Ave",
    ]
    cities = ["Moscow", "SPb", "Novosibirsk", "Ekaterinburg", "Kazan"]

    for i in range(1, num_rows + 1):
        name = names[i % len(names)]
        age = 20 + (i % 50)
        email = f"{name.lower().replace(' ', '.')}@{domains[i % len(domains)]}"
        street = streets[i % len(streets)]
        city = cities[i % len(cities)]
        address = f"{i * 100} {street}, {city}"
        phone = f"555-{i:04d}"
        date = (
            f"2024-{1 + (i % 12):02d}-{1 + (i % 28):02d} "
            f"{10 + (i % 12):02d}:{i % 60:02d}:00"
        )

        row = f"{i},{name},{age},{email},{address},{phone},{date}\n".encode(
            "utf-8"
        )
        result.append(row)

    return result


def decompress(compression_method: CompressionMethod) -> None:
    fileobj.seek(0)
    full_data = b"".join(bytes_data)
    decompressed_size = len(full_data)
    stream = define_reader(fileobj, compression_method)
    assert full_data == stream.read(decompressed_size)  # noqa: S101


class TestBufferedReader:
    """Тесты для DecompressReader/SnappyReader."""

    def test_file(self) -> None:
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()
            full_data = b"".join(bytes_data)
            decompressed_size = len(full_data)
            compressor: CompressorType = compression_method.compressor()

            for data in compressor.send_chunks(bytes_data):
                fileobj.write(data)

            assert decompressed_size == compressor.decompressed_size  # noqa: S101
            decompress(compression_method)

    def test_stream(self) -> None:
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            decompress(compression_method)

    def test_autodetection(self) -> None:
        for compression_method in (
            CompressionMethod.NONE,
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            fileobj.seek(0)
            full_data = b"".join(bytes_data)
            decompressed_size = len(full_data)
            stream = define_reader(fileobj)
            assert full_data == stream.read(decompressed_size)  # noqa: S101

    def test_read_partial(self):
        """Тест чтения данных частями."""
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            # Сжимаем данные
            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            fileobj.seek(0)
            stream = define_reader(fileobj, compression_method)
            full_data = b"".join(bytes_data)

            # Читаем частями
            chunk_size = 1000
            result_parts = []
            while True:
                chunk = stream.read(chunk_size)
                if not chunk:
                    break
                result_parts.append(chunk)

            result = b"".join(result_parts)
            assert result == full_data  # noqa: S101

    def test_readline(self):
        """Тест чтения построчно."""
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            fileobj.seek(0)
            stream = define_reader(fileobj, compression_method)

            lines = []
            while True:
                line = stream.readline()
                if not line:
                    break
                lines.append(line)

            result = b"".join(lines)
            assert result == b"".join(bytes_data)  # noqa: S101

    def test_readlines(self):
        """Тест чтения всех строк."""
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            fileobj.seek(0)
            stream = define_reader(fileobj, compression_method)
            lines = stream.readlines()
            result = b"".join(lines)
            assert result == b"".join(bytes_data)  # noqa: S101

    def test_read_with_hint(self):
        """Тест чтения с подсказкой размера."""
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            fileobj.seek(0)
            stream = define_reader(fileobj, compression_method)
            hint = 5000
            result = stream.read(hint)
            assert len(result) <= hint  # noqa: S101

    def test_readinto(self):
        """Тест чтения в буфер."""
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            fileobj.seek(0)
            stream = define_reader(fileobj, compression_method)
            full_data = b"".join(bytes_data)
            buffer = bytearray(len(full_data))
            bytes_read = stream.readinto(buffer)
            assert bytes_read == len(full_data)  # noqa: S101
            assert bytes(buffer) == full_data  # noqa: S101

    def test_seek_absolute_forward(self):
        """Тест абсолютного позиционирования вперед."""
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            fileobj.seek(0)
            stream = define_reader(fileobj, compression_method)
            full_data = b"".join(bytes_data)
            first_part = stream.read(100)
            assert first_part == full_data[:100]  # noqa: S101
            assert stream.tell() == 100  # noqa: S101
            stream.seek(50, 1)
            assert stream.tell() == 150  # noqa: S101
            part = stream.read(50)
            assert part == full_data[150:200]  # noqa: S101

    def test_seek_absolute_from_start(self):
        """Тест абсолютного позиционирования от начала."""
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            fileobj.seek(0)
            stream = define_reader(fileobj, compression_method)
            full_data = b"".join(bytes_data)
            stream.seek(100, 0)
            assert stream.tell() == 100  # noqa: S101
            part = stream.read(50)
            assert part == full_data[100:150]  # noqa: S101

    def test_iterator(self):
        """Тест итератора."""
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            fileobj.seek(0)
            stream = define_reader(fileobj, compression_method)
            lines = list(stream)
            result = b"".join(lines)
            assert result == b"".join(bytes_data)  # noqa: S101

    def test_tell_after_read(self):
        """Тест позиции после чтения."""
        for compression_method in (
            CompressionMethod.GZIP,
            CompressionMethod.LZ4,
            CompressionMethod.ZSTD,
            CompressionMethod.SNAPPY,
        ):
            fileobj.seek(0)
            fileobj.truncate()

            for data in define_writer(bytes_data, compression_method):
                fileobj.write(data)

            fileobj.seek(0)
            stream = define_reader(fileobj, compression_method)
            full_data = b"".join(bytes_data)
            positions = []

            for _ in range(0, len(full_data), 1000):
                stream.read(1000)  # noqa: S101
                positions.append(stream.tell())

            assert positions[-1] == len(full_data)  # noqa: S101


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

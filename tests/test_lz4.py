import pytest
import random
import time

from light_compressor import (
    LZ4Compressor,
    LZ4Decompressor,
)


Compressor = LZ4Compressor
Decompressor = LZ4Decompressor


class TestLZ4Compressor:
    """Тесты для компрессора Lz4."""

    def test_compress_empty_data(self):
        """Тест сжатия пустых данных."""

        compressor = Compressor()
        chunks = list(compressor.send_chunks([]))
        assert len(chunks) == 2  # noqa: S101
        assert len(chunks[0]) > 0  # noqa: S101
        assert chunks[0][:4] == b'\x04"M\x18'  # noqa: S101
        decompressor = Decompressor()
        result = decompressor.decompress(chunks[0])
        assert result == b""  # noqa: S101

    def test_compress_single_chunk(self):
        """Тест сжатия одного чанка данных."""

        compressor = Compressor()
        test_data = b"Hello, World! " * 1000
        chunks = list(compressor.send_chunks([test_data]))
        assert len(chunks) >= 1  # noqa: S101
        compressed_data = b"".join(chunks)
        assert len(compressed_data) < len(  # noqa: S101
            test_data
        )
        decompressor = Decompressor()
        decompressed = decompressor.decompress(compressed_data)
        assert decompressed == test_data  # noqa: S101
        assert decompressor.eof is True  # noqa: S101

    def test_compress_multiple_chunks(self):
        """Тест сжатия нескольких чанков данных."""

        compressor = Compressor()
        chunks = [b"A" * 1000, b"B" * 1000, b"C" * 1000]
        original_data = b"".join(chunks)
        compressed_chunks = list(compressor.send_chunks(chunks))
        compressed_data = b"".join(compressed_chunks)
        decompressor = Decompressor()
        decompressed = decompressor.decompress(compressed_data)
        assert decompressed == original_data  # noqa: S101
        assert decompressor.eof is True  # noqa: S101

    def test_compress_generator(self):
        """Тест сжатия с генератором на входе."""

        def data_generator():
            for i in range(10):
                yield b"test" * 1000

        compressor = Compressor()
        compressed_chunks = list(compressor.send_chunks(data_generator()))
        compressed_data = b"".join(compressed_chunks)
        decompressor = Decompressor()
        decompressed = decompressor.decompress(compressed_data)
        assert decompressed == b"test" * 10000  # noqa: S101
        assert decompressor.eof is True  # noqa: S101

    def test_decompressed_size(self):
        """Тест подсчета размера исходных данных."""

        compressor = Compressor()
        test_data = b"X" * 5000
        list(compressor.send_chunks([test_data]))
        assert compressor.decompressed_size == 5000  # noqa: S101

    def test_large_data(self):
        """Тест обработки больших данных (1MB)."""
        compressor = Compressor()
        test_data = bytes(random.randint(0, 255) for _ in range(1024 * 1024))  # noqa: S311
        compressed_chunks = list(compressor.send_chunks([test_data]))
        compressed_data = b"".join(compressed_chunks)
        decompressor = Decompressor()
        decompressed = decompressor.decompress(compressed_data)
        assert decompressed == test_data  # noqa: S101

    def test_very_large_data(self):
        """Тест обработки очень больших данных (100MB)."""

        compressor = Compressor()
        data_size = 100 * 1024 * 1024
        print(f"\nGenerating {data_size / 1024 / 1024:.0f}MB of test data...")
        test_data = b"X" * data_size
        print("Compressing...")
        start_compress = time.time()
        compressed_chunks = []

        for chunk in compressor.send_chunks([test_data]):
            compressed_chunks.append(chunk)

        compress_time = time.time() - start_compress
        compressed_data = b"".join(compressed_chunks)
        print(f"Compression time: {compress_time:.2f}s")
        print(f"Compressed size: {len(compressed_data) / 1024 / 1024:.2f}MB")
        print("Decompressing...")
        decompressor = Decompressor()
        start_decompress = time.time()
        decompressed = decompressor.decompress(compressed_data)

        if not decompressor.eof:
            remaining = decompressor.decompress(b"")
            if remaining:
                decompressed += remaining

        decompress_time = time.time() - start_decompress
        print(f"Decompression time: {decompress_time:.3f}s")
        print(f"Total decompressed: {len(decompressed)} bytes")
        assert decompressed == test_data  # noqa: S101

        if decompress_time > 0:
            speed = data_size / decompress_time / 1024 / 1024
            print(f"Decompression speed: {speed:.2f}MB/s")

        print(f"✓ Large data test passed with {data_size / 1024 / 1024:.0f}MB")

    def test_debug_compress_decompress(self):
        """Отладочный тест для проверки целостности данных."""

        compressor = Compressor()
        test_data = b"X" * 100000
        print(f"\nTest data size: {len(test_data)} bytes")
        compressed_chunks = list(compressor.send_chunks([test_data]))
        compressed_data = b"".join(compressed_chunks)
        print(f"Compressed size: {len(compressed_data)} bytes")
        print(f"Number of compressed chunks: {len(compressed_chunks)}")
        decompressor = Decompressor()
        decompressed_parts = []

        for i, chunk in enumerate(compressed_chunks):
            result = decompressor.decompress(chunk)
            print(f"Chunk {i}: size={len(chunk)}, decompressed={len(result)}")

            if result:
                decompressed_parts.append(result)

        remaining = decompressor.decompress(b"")
        if remaining:
            print(f"Remaining after all chunks: {len(remaining)}")
            decompressed_parts.append(remaining)

        decompressed_data = b"".join(decompressed_parts)
        print(f"Total decompressed: {len(decompressed_data)}")
        assert decompressed_data == test_data, (  # noqa: S101
            f"Data mismatch! Got {len(decompressed_data)}, "
            f"expected {len(test_data)}"
        )
        print("✓ Debug test passed")


class TestLZ4Decompressor:
    """Тесты для декомпрессора Lz4."""

    def test_decompress_empty(self):
        """Тест декомпрессии пустых данных."""

        decompressor = Decompressor()
        result = decompressor.decompress(b"")
        assert result == b""  # noqa: S101
        assert decompressor.eof is False  # noqa: S101
        assert decompressor.needs_input is True  # noqa: S101

    def test_decompress_framed_format(self):
        """Тест декомпрессии framed формата."""

        compressor = Compressor()
        test_data = b"Test framed format data " * 100
        compressed = list(compressor.send_chunks([test_data]))
        compressed_data = b"".join(compressed)
        decompressor = Decompressor()
        decompressed = decompressor.decompress(compressed_data)
        assert decompressed == test_data  # noqa: S101
        assert decompressor.eof is True  # noqa: S101

    def test_decompress_streaming(self):
        """Тест потоковой декомпрессии с несколькими вызовами."""

        compressor = Compressor()
        test_data = b"Streaming test data " * 1000
        compressed_chunks = list(compressor.send_chunks([test_data]))
        decompressor = Decompressor()
        decompressed_parts = []

        for chunk in compressed_chunks:
            part = decompressor.decompress(chunk)
            if part:
                decompressed_parts.append(part)

        decompressed = b"".join(decompressed_parts)
        assert decompressed == test_data  # noqa: S101

    def test_decompress_with_unused_data(self):
        """Тест обработки неиспользованных данных после декомпрессии."""

        compressor = Compressor()
        test_data = b"Main data " * 100
        extra_data = b"EXTRA DATA AFTER STREAM"
        compressed = list(compressor.send_chunks([test_data]))
        compressed_with_extra = b"".join(compressed) + extra_data
        decompressor = Decompressor()
        decompressed = decompressor.decompress(compressed_with_extra)
        assert decompressed == test_data  # noqa: S101
        assert decompressor.unused_data == extra_data  # noqa: S101
        assert decompressor.eof is True  # noqa: S101

    def test_decompress_empty_frame(self):
        """Тест декомпрессии пустого фрейма."""

        compressor = Compressor()
        empty_compressed = list(compressor.send_chunks([]))
        empty_frame = b"".join(empty_compressed)
        decompressor = Decompressor()
        result = decompressor.decompress(empty_frame)
        assert result == b""  # noqa: S101
        assert decompressor.eof is True  # noqa: S101

    def test_decompress_max_length(self):
        """Тест параметра max_length."""

        compressor = Compressor()
        test_data = b"X" * 10000
        compressed = list(compressor.send_chunks([test_data]))
        compressed_data = b"".join(compressed)
        decompressor = Decompressor()
        first_part = decompressor.decompress(compressed_data, max_length=1000)
        assert len(first_part) <= 1000  # noqa: S101
        second_part = decompressor.decompress(b"")
        full_data = first_part + second_part
        assert full_data == test_data  # noqa: S101

    def test_reset_decompressor(self):
        """Тест сброса состояния декомпрессора."""

        decompressor = Decompressor()
        compressor1 = Compressor()
        test_data1 = b"First test data " * 50
        compressed1 = list(compressor1.send_chunks([test_data1]))
        result1 = decompressor.decompress(b"".join(compressed1))
        assert result1 == test_data1  # noqa: S101
        decompressor.reset()
        compressor2 = Compressor()
        test_data2 = b"Second test data " * 50
        compressed2 = list(compressor2.send_chunks([test_data2]))
        result2 = decompressor.decompress(b"".join(compressed2))
        assert result2 == test_data2  # noqa: S101

    def test_context_manager(self):
        """Тест протокола контекстного менеджера."""

        with Decompressor() as decompressor:
            assert decompressor is not None  # noqa: S101
            compressor = Compressor()
            test_data = b"Context manager test " * 50
            compressed = list(compressor.send_chunks([test_data]))
            result = decompressor.decompress(b"".join(compressed))
            assert result == test_data  # noqa: S101


class TestLZ4Integration:
    """Интеграционные тесты."""

    def test_compress_decompress_cycle_with_random_data(self):
        """Тест полного цикла сжатия-декомпрессии на случайных данных."""

        for size in [0, 1, 100, 1000, 10000, 100000]:
            test_data = bytes(random.randint(0, 255) for _ in range(size))  # noqa: S311
            compressor = Compressor()
            decompressor = Decompressor()
            compressed_chunks = list(compressor.send_chunks([test_data]))
            compressed = b"".join(compressed_chunks)
            decompressed = decompressor.decompress(compressed)
            assert decompressed == test_data, f"Failed for size {size}"  # noqa: S101

    def test_chunked_processing(self):
        """Тест обработки данных чанками."""

        large_data = b"X" * (10 * 1024 * 1024)
        compressor = Compressor()
        decompressor = Decompressor()
        chunk_size = 1024 * 1024
        chunks = []

        for i in range(0, len(large_data), chunk_size):
            chunks.append(large_data[i : i + chunk_size])

        compressed_chunks = list(compressor.send_chunks(chunks))
        compressed_data = b"".join(compressed_chunks)
        decompressed = decompressor.decompress(compressed_data)
        assert decompressed == large_data  # noqa: S101

    def test_performance(self):
        """Тест производительности сжатия/декомпрессии."""

        sizes = [1, 10, 50, 100, 200, 500, 1000]
        results = []
        print("\n" + "=" * 80)
        print(
            f"{'Size':>8} {'Compress':>12} {'Decompress':>12} "
            f"{'Ratio':>8} {'Speed(MB/s)':>12}"
        )
        print("=" * 80)

        for size_mb in sizes:
            data_size = size_mb * 1024 * 1024
            test_data = b"A" * data_size
            compressor = Compressor()
            start = time.time()
            compressed_chunks = []

            for chunk in compressor.send_chunks([test_data]):
                compressed_chunks.append(chunk)

            compress_time = time.time() - start
            compressed_size = sum(len(chunk) for chunk in compressed_chunks)
            compressed_data = b"".join(compressed_chunks)
            decompressor = Decompressor()
            start = time.time()
            decompressed = decompressor.decompress(compressed_data)
            remaining = decompressor.decompress(b"")

            if remaining:
                decompressed += remaining

            decompress_time = time.time() - start
            compression_ratio = compressed_size / data_size * 100
            compress_speed = (
                data_size / compress_time / 1024 / 1024
                if compress_time > 0
                else 0
            )
            decompress_speed = (
                data_size / decompress_time / 1024 / 1024
                if decompress_time > 0
                else 0
            )
            results.append(
                {
                    "size": size_mb,
                    "compress_time": compress_time,
                    "decompress_time": decompress_time,
                    "ratio": compression_ratio,
                    "compress_speed": compress_speed,
                    "decompress_speed": decompress_speed,
                }
            )
            print(
                f"{size_mb:>8}MB "
                f"{compress_time:>11.2f}s "
                f"{decompress_time:>11.2f}s "
                f"{compression_ratio:>7.1f}% "
                f"{decompress_speed:>11.1f}"
            )
            assert decompressed == test_data, (  # noqa: S101
                f"Data mismatch for size {size_mb}MB"
            )

        print("=" * 80)

        for result in results:
            if result["size"] == 1000:
                assert result["decompress_speed"] > 50, (  # noqa: S101
                    "Decompress speed too low: "
                    f"{result['decompress_speed']:.1f}MB/s"
                )
                print(
                    "\n✓ Performance test passed: "
                    f"{result['decompress_speed']:.1f}MB/s decompression speed"
                )
                break

    def test_random_large_data(self):
        """Тест обработки больших случайных данных (50MB)."""

        data_size = 50 * 1024 * 1024
        print(
            f"\nGenerating {data_size / 1024 / 1024:.0f}MB of random data..."
        )
        start_gen = time.time()
        chunk_size = 1024 * 1024
        random_data = bytearray()

        for _ in range(data_size // chunk_size):
            random_data.extend(random.randbytes(chunk_size))  # noqa: S311

        remaining = data_size % chunk_size

        if remaining:
            random_data.extend(random.randbytes(remaining))  # noqa: S311

        test_data = bytes(random_data)
        print(f"Generation time: {time.time() - start_gen:.2f}s")
        compressor = Compressor()
        decompressor = Decompressor()
        print("Compressing random data...")
        start = time.time()
        compressed_chunks = list(compressor.send_chunks([test_data]))
        compress_time = time.time() - start
        compressed_size = sum(len(chunk) for chunk in compressed_chunks)
        print(f"Compression time: {compress_time:.2f}s")
        print(f"Compressed size: {compressed_size / 1024 / 1024:.2f}MB")
        print(f"Compression ratio: {compressed_size / data_size * 100:.1f}%")
        print("Decompressing random data...")
        start = time.time()
        decompressed = decompressor.decompress(b"".join(compressed_chunks))
        decompress_time = time.time() - start
        print(f"Decompression time: {decompress_time:.2f}s")
        print(
            "Decompression speed: "
            f"{data_size / decompress_time / 1024 / 1024:.2f}MB/s"
        )
        assert decompressed == test_data  # noqa: S101
        print(
            "✓ Random large data test passed with "
            f"{data_size / 1024 / 1024:.0f}MB"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

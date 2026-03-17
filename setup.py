from setuptools import (
    Extension,
    setup,
)
from setuptools_rust import RustExtension
from Cython.Build import cythonize


extensions = [
    Extension(
        "light_compressor.compressors.gzip",
        ["src/light_compressor/compressors/gzip.pyx"],
    ),
    Extension(
        "light_compressor.compressors.lz4",
        ["src/light_compressor/compressors/lz4.pyx"],
    ),
    Extension(
        "light_compressor.compressors.zstd",
        ["src/light_compressor/compressors/zstd.pyx"],
    ),
    Extension(
        "light_compressor.decompressors.decompressor",
        ["src/light_compressor/decompressors/decompressor.pyx"],
    ),
    Extension(
        "light_compressor.decompressors.gzip",
        ["src/light_compressor/decompressors/gzip.pyx"],
    ),
    Extension(
        "light_compressor.decompressors.lz4",
        ["src/light_compressor/decompressors/lz4.pyx"],
    ),
    Extension(
        "light_compressor.decompressors.zstd",
        ["src/light_compressor/decompressors/zstd.pyx"],
    ),
]


setup(
    name="light_compressor",
    version="0.1.0.dev3",
    package_dir={"": "src"},
    ext_modules=cythonize(extensions, language_level="3"),
    rust_extensions=[
        RustExtension(
            "light_compressor.compressors.snappy",
            path="src/light_compressor/compressors/snappy/Cargo.toml",
            debug=False,
        ),
        RustExtension(
            "light_compressor.decompressors.snappy",
            path="src/light_compressor/decompressors/snappy/Cargo.toml",
            debug=False,
        ),
    ],
    packages=[
        "light_compressor.decompressors",
    ],
    package_data={
        "light_compressor": [
            "**/*.pyx", "**/*.pxd", "*.pxd", "*.pyd", "*.md", "*.txt",
        ]
    },
    exclude_package_data={
        "": ["*.c"],
        "light_compressor": ["**/*.c"],
    },
    include_package_data=True,
    setup_requires=["Cython>=0.29.33"],
    zip_safe=False,
)

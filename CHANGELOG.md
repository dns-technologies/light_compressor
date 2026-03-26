# Version History

## 0.1.0.dev4

* Developer release (not public to pip)
* Add CompressorType for type hinting
* Add DecompressorType for type hinting
* Refactor Codec class
* Refactor define_writer function
* Remove Rust and Cython source code from wheel package
* Fix SNAPCompressor work with bytes_data as Generator object

## 0.1.0.dev3

* Developer release (not public to pip)
* Change CompressionMethod struct
* Change DecompressReader language python -> cython
* Refactor detect compressors/decompressors
* Rename SNAPPYCompressor -> SNAPCompressor
* Rename SNAPPYDecompressor -> SNAPDecompressor

## 0.1.0.dev2

* Developer release (not public to pip)
* Add CompressionLevel constants for define compression level
* Add optional parameter compression_level for all compressors. Default is 6
* Update README.md
* Update MANIFEST.in
* Rename compressor_method.py -> compression_method.py
* Add trigger for update developer pypi indexes
* Refactor workers

## 0.1.0.dev1

* Developer release (not public to pip)
* Add SNAPPYCompressor
* Add SNAPPYDecompressor
* Refactor GZIPDecompressor
* Improve misprints inialization -> initialization
* Rename tests_all -> test_gzip_lz4_zstd.py
* Add tests for snappy test_snappy.py
* Update .gitignore
* Update github links
* Update README.md

## 0.1.0.dev0

* Developer release (not public to pip)
* Improve docstrings
* Add GZIPCompressor
* Add GZIPDecompressor
* Add Gzip checker to test_all.py

## 0.0.2.2

* Change documentation link

## 0.0.2.1

* Update depends latest setuptools
* Make wheels for python 3.10-3.14
* Add tests for python 3.14
* Make custom DecompressReader class

## 0.0.2.0

* Downgrade compile depends to cython==0.29.33
* Make wheels for python 3.10 and 3.11 only

## 0.0.1.9

* Update depends setuptools>=80.9.0
* Update depends cffi>=1.17.1
* Update depends lz4>=4.4.3
* Update depends zstandard>=0.23.0
* Precompiled wheels are now compatible with airflow >= 2.4.3
without change any constraits

## 0.0.1.8

* Add python 3.14 support
* Add wheels automake
* Add auto upload to pip

## 0.0.1.7

* Add *.pyi files for cython modules descriptions
* Fix tests
* Update MANIFEST.in

## 0.0.1.6

* Refactor functions check: replace == to is

## 0.0.1.5

* Add MANIFEST.in
* Add CHANGELOG.md to pip package
* Improve pyproject.toml license file approve

## 0.0.1.4

* Add auto_detector(fileobj) function to detect compression from file
* Update README.md

## 0.0.1.3

* Refactor ZSTDCompressor
* Add test auto compression detection
* Rename tests/tests.py to tests/test_all.py
* Update README.md

## 0.0.1.2

* Add MIT License
* Update depends in pyproject.toml

## 0.0.1.1

* Fix & Refactor define_writer
* Add cffi to requirements.txt
* Add tests
* Add attribute decompressed_size for LZ4Compressor & ZSTDCompressor
* Change error message for define_reader & define_writer
* Change chunk size to 128 items in list of compressed_chunks
* Translate README.md to english and add more examples
* Development Status change to 4 (Beta)
* Revision python versions

## 0.0.1.0

* Improve dependencies in pyproject.toml
* Change compression method select from method_type to CompressionMethod
* Add compressors
* Add define_writer
* Update README.md

## 0.0.0.1

First version of the library

* Light versions of lz4 and zstandard streams for read only objects

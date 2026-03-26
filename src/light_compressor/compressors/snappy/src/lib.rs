use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyAny};
use snap::write::FrameEncoder;
use std::io::Write;

const MAX_BLOCK_SIZE: usize = 65536;
const MAX_TOTAL_SIZE: usize = 104857600;

#[pyclass]
pub struct SNAPCompressor {
    decompressed_size: u64,
    buffer: Vec<u8>,
    encoder: FrameEncoder<Vec<u8>>,
    current_chunk: Vec<u8>,
    compression_level: i32,
}

#[pyclass]
struct CompressionIter {
    chunks: Vec<Vec<u8>>,
    index: usize,
}

#[pymethods]
impl CompressionIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>, py: Python<'_>) -> PyResult<Option<Py<PyBytes>>> {
        if slf.index < slf.chunks.len() {
            let chunk = PyBytes::new(py, &slf.chunks[slf.index]);
            slf.index += 1;
            Ok(Some(chunk.into()))
        } else {
            Ok(None)
        }
    }
}

#[pymethods]
impl SNAPCompressor {
    #[new]
    #[pyo3(signature = (compression_level=6))]
    fn new(compression_level: i32) -> Self {
        SNAPCompressor {
            compression_level,
            decompressed_size: 0,
            buffer: Vec::with_capacity(MAX_BLOCK_SIZE),
            encoder: FrameEncoder::new(Vec::new()),
            current_chunk: Vec::new(),
        }
    }

    fn send_chunks(
        &mut self,
        py: Python<'_>,
        bytes_data: &Bound<'_, PyAny>,
    ) -> PyResult<Py<CompressionIter>> {
        self.decompressed_size = 0;
        self.buffer.clear();
        self.current_chunk.clear();
        *self.encoder.get_mut() = Vec::new();
        let mut compressed_chunks = Vec::new();
        let mut total_size = 0;
        let iter = bytes_data.call_method0("__iter__")?;
        let mut has_data = false;

        loop {
            let next_item = iter.call_method0("__next__");

            match next_item {
                Ok(item) => {
                    has_data = true;
                    let data: Vec<u8> = item.extract()?;
                    total_size += data.len();
                    if total_size > MAX_TOTAL_SIZE {
                        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                            format!("Data size exceeds maximum allowed ({} bytes)", MAX_TOTAL_SIZE)
                        ));
                    }

                    self.decompressed_size += data.len() as u64;
                    self.buffer.extend_from_slice(&data);

                    while self.buffer.len() >= MAX_BLOCK_SIZE {
                        let block = self.buffer[..MAX_BLOCK_SIZE].to_vec();
                        self.buffer = self.buffer[MAX_BLOCK_SIZE..].to_vec();
                        self.encoder.write_all(&block)
                            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                                format!("Snappy compression error: {}", e)
                            ))?;
                        self.encoder.flush()
                            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                                format!("Snappy compression error: {}", e)
                            ))?;
                        let compressed = self.encoder.get_ref().clone();

                        if !compressed.is_empty() {
                            self.current_chunk.extend_from_slice(&compressed);
                            *self.encoder.get_mut() = Vec::new();
                        }
                    }
                }
                Err(e) => {
                    if e.is_instance_of::<pyo3::exceptions::PyStopIteration>(py) {
                        break;
                    }
                    return Err(e);
                }
            }
        }

        if !self.buffer.is_empty() {
            self.encoder.write_all(&self.buffer)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Snappy compression error: {}", e)
                ))?;
            self.encoder.flush()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Snappy compression error: {}", e)
                ))?;
            let compressed = self.encoder.get_ref().clone();

            if !compressed.is_empty() {
                self.current_chunk.extend_from_slice(&compressed);
            }
        }

        self.encoder.flush()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Snappy compression error: {}", e)
            ))?;
        let final_compressed = self.encoder.get_ref().clone();

        if !final_compressed.is_empty() {
            self.current_chunk.extend_from_slice(&final_compressed);
        }

        if !self.current_chunk.is_empty() {
            compressed_chunks.push(std::mem::take(&mut self.current_chunk));
        } else if has_data {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Compression failed: no data produced".to_string()
            ));
        } else {
            let empty_frame = self.create_empty_frame();
            compressed_chunks.push(empty_frame);
        }

        let iter = CompressionIter {
            chunks: compressed_chunks,
            index: 0,
        };

        Ok(Py::new(py, iter)?)
    }

    fn create_empty_frame(&self) -> Vec<u8> {
        let mut frame = Vec::new();
        frame.extend_from_slice(&[0xff, 0x06, 0x00, 0x00]);
        frame
    }

    #[getter]
    fn compression_level(&self) -> i32 {
        self.compression_level
    }

    #[getter]
    fn decompressed_size(&self) -> u64 {
        self.decompressed_size
    }
}

#[pymodule]
fn snappy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SNAPCompressor>()?;
    Ok(())
}

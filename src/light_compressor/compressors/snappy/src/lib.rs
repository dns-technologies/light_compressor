use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList};
use snap::write::FrameEncoder;
use std::io::Write;

const MAX_BLOCK_SIZE: usize = 65536;
const MAX_TOTAL_SIZE: usize = 104857600;

#[pyclass]
pub struct SNAPPYCompressor {
    decompressed_size: u64,
    buffer: Vec<u8>,
    encoder: FrameEncoder<Vec<u8>>,
    current_chunk: Vec<u8>,
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
impl SNAPPYCompressor {
    #[new]
    fn new() -> Self {
        SNAPPYCompressor {
            decompressed_size: 0,
            buffer: Vec::with_capacity(MAX_BLOCK_SIZE),
            encoder: FrameEncoder::new(Vec::new()),
            current_chunk: Vec::new(),
        }
    }

    fn send_chunks(
        &mut self,
        py: Python<'_>,
        bytes_data: &Bound<'_, PyList>,
    ) -> PyResult<Py<CompressionIter>> {
        self.decompressed_size = 0;
        self.buffer.clear();
        self.current_chunk.clear();
        let mut compressed_chunks = Vec::new();
        let mut total_size = 0;

        // В PyO3 0.26.0 итератор возвращает Bound<'_, PyAny> напрямую, без Result
        for item in bytes_data.iter() {
            let data: Vec<u8> = item.extract()?;
            total_size += data.len();
            if total_size > MAX_TOTAL_SIZE {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Data size exceeds maximum allowed ({} bytes)", MAX_TOTAL_SIZE)
                ));
            }
        }

        // Компрессия
        for item in bytes_data.iter() {
            let data: Vec<u8> = item.extract()?;
            self.decompressed_size += data.len() as u64;
            self.buffer.extend_from_slice(&data);

            while self.buffer.len() >= MAX_BLOCK_SIZE {
                let block = self.buffer[..MAX_BLOCK_SIZE].to_vec();
                self.buffer = self.buffer[MAX_BLOCK_SIZE..].to_vec();

                if let Err(e) = self.encoder.write_all(&block) {
                    return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        format!("Snappy compression error: {}", e)
                    ));
                }

                if let Err(e) = self.encoder.flush() {
                    return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        format!("Snappy compression error: {}", e)
                    ));
                }

                let compressed = self.encoder.get_ref().clone();

                if !compressed.is_empty() {
                    self.current_chunk.extend_from_slice(&compressed);
                    *self.encoder.get_mut() = Vec::new();
                }
            }
        }

        // Сжимаем остаток
        if !self.buffer.is_empty() {
            if let Err(e) = self.encoder.write_all(&self.buffer) {
                return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Snappy compression error: {}", e)
                ));
            }

            if let Err(e) = self.encoder.flush() {
                return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Snappy compression error: {}", e)
                ));
            }

            let compressed = self.encoder.get_ref().clone();
            if !compressed.is_empty() {
                self.current_chunk.extend_from_slice(&compressed);
            }
        }

        if !self.current_chunk.is_empty() {
            compressed_chunks.push(self.current_chunk.clone());
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Compression failed: no data produced".to_string()
            ));
        }

        let iter = CompressionIter {
            chunks: compressed_chunks,
            index: 0,
        };
        
        Ok(Py::new(py, iter)?)
    }

    #[getter]
    fn decompressed_size(&self) -> u64 {
        self.decompressed_size
    }
}

#[pymodule]
fn snappy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SNAPPYCompressor>()?;
    Ok(())
}

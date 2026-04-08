use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyAny};
use snap::write::FrameEncoder;
use std::io::Write;
use std::sync::Arc;
use std::sync::atomic::{AtomicU64, Ordering};


const MAX_CHUNK_SIZE: usize = 65536;


struct CompressionState {
    encoder: FrameEncoder<Vec<u8>>,
    buffer: Vec<u8>,
    pending: Vec<u8>,
    decompressed_size: u64,
    has_data: bool,
}


impl CompressionState {
    fn new() -> Self {
        CompressionState {
            encoder: FrameEncoder::new(Vec::new()),
            buffer: Vec::with_capacity(MAX_CHUNK_SIZE),
            pending: Vec::new(),
            decompressed_size: 0,
            has_data: false,
        }
    }

    fn feed_data(&mut self, data: &[u8]) -> Result<Option<Vec<u8>>, String> {
        self.decompressed_size += data.len() as u64;
        self.buffer.extend_from_slice(data);

        while self.buffer.len() >= MAX_CHUNK_SIZE {
            let chunk = self.buffer[..MAX_CHUNK_SIZE].to_vec();
            self.buffer = self.buffer[MAX_CHUNK_SIZE..].to_vec();
            self.encoder.write_all(&chunk).map_err(|e| e.to_string())?;
            let compressed = self.encoder.get_ref();

            if !compressed.is_empty() {
                self.pending.extend_from_slice(compressed);
                *self.encoder.get_mut() = Vec::new();
            }

            if !self.pending.is_empty() {
                return Ok(Some(std::mem::take(&mut self.pending)));
            }
        }

        Ok(None)
    }

    fn finalize(&mut self) -> Option<Vec<u8>> {
        if !self.buffer.is_empty() {
            if let Err(_) = self.encoder.write_all(&self.buffer) {
                return None;
            }
            self.buffer.clear();
            let compressed = self.encoder.get_ref();

            if !compressed.is_empty() {
                self.pending.extend_from_slice(compressed);
                *self.encoder.get_mut() = Vec::new();
            }
        }

        if self.has_data {
            if let Err(_) = self.encoder.flush() {
                return None;
            }

            let final_compressed = self.encoder.get_ref();
            if !final_compressed.is_empty() {
                self.pending.extend_from_slice(final_compressed);
                *self.encoder.get_mut() = Vec::new();
            }
        } else {
            self.pending.extend_from_slice(&[0xff, 0x06, 0x00, 0x00]);
            self.pending.extend_from_slice(b"sNaPpY");
        }

        if !self.pending.is_empty() {
            Some(std::mem::take(&mut self.pending))
        } else {
            None
        }
    }
}


#[pyclass]
struct CompressorIterator {
    state: CompressionState,
    input_data: Vec<Vec<u8>>,
    current_index: usize,
    finished: bool,
    size_ref: Arc<AtomicU64>,
}


#[pymethods]
impl CompressorIterator {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(
        mut slf: PyRefMut<'_, Self>,
        py: Python<'_>,
    ) -> PyResult<Option<Py<PyBytes>>> {
        if slf.finished {
            return Ok(None);
        }

        if !slf.state.pending.is_empty() {
            let chunk = std::mem::take(&mut slf.state.pending);
            return Ok(Some(PyBytes::new(py, &chunk).into()));
        }

        while slf.current_index < slf.input_data.len() {
            let data = slf.input_data[slf.current_index].clone();
            slf.current_index += 1;
            slf.state.has_data = true;
            let result = slf.state.feed_data(&data).map_err(
                |e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e),
            )?;
            slf.size_ref.store(
                slf.state.decompressed_size,
                Ordering::Relaxed,
            );

            if let Some(chunk) = result {
                return Ok(Some(PyBytes::new(py, &chunk).into()));
            }
        }

        slf.finished = true;
        slf.size_ref.store(slf.state.decompressed_size, Ordering::Relaxed);

        if let Some(chunk) = slf.state.finalize() {
            Ok(Some(PyBytes::new(py, &chunk).into()))
        } else {
            Ok(None)
        }
    }
}


#[pyclass]
pub struct SNAPCompressor {
    compression_level: i32,
    decompressed_size: Arc<AtomicU64>,
}


#[pymethods]
impl SNAPCompressor {

    #[new]
    #[pyo3(signature = (compression_level=6))]
    fn new(compression_level: i32) -> Self {
        SNAPCompressor {
            compression_level,
            decompressed_size: Arc::new(AtomicU64::new(0)),
        }
    }

    fn send_chunks(
        &mut self,
        py: Python<'_>,
        bytes_data: &Bound<'_, PyAny>,
    ) -> PyResult<Py<CompressorIterator>> {
        let iterator = bytes_data.call_method0("__iter__")?;
        let mut input_data = Vec::new();

        loop {
            let next_item = match iterator.call_method0("__next__") {
                Ok(item) => item,
                Err(e) => {
                    if e.is_instance_of::<pyo3::exceptions::PyStopIteration>(
                        py,
                    ) {
                        break;
                    }
                    return Err(e);
                }
            };
            let data: Vec<u8> = next_item.extract()?;
            input_data.push(data);
        }
        let iter = CompressorIterator {
            state: CompressionState::new(),
            input_data,
            current_index: 0,
            finished: false,
            size_ref: self.decompressed_size.clone(),
        };
        Ok(Py::new(py, iter)?)
    }

    #[getter]
    fn decompressed_size(&self) -> u64 {
        self.decompressed_size.load(Ordering::Relaxed)
    }

    #[getter]
    fn compression_level(&self) -> i32 {
        self.compression_level
    }

    #[staticmethod]
    fn create_empty_frame() -> Vec<u8> {
        let mut frame = Vec::with_capacity(10);
        frame.extend_from_slice(&[0xff, 0x06, 0x00, 0x00]);
        frame.extend_from_slice(b"sNaPpY");
        frame
    }
}


#[pymodule]
fn snappy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SNAPCompressor>()?;
    m.add_class::<CompressorIterator>()?;
    Ok(())
}

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyByteArray};
use snap::read::FrameDecoder;
use std::io::{Read, Cursor};

#[pyclass]
pub struct SNAPPYDecompressor {
    decoder: Option<FrameDecoder<Cursor<Vec<u8>>>>,
    eof: bool,
    needs_input: bool,
    unused_data: Vec<u8>,
    unconsumed_data: Vec<u8>,
    #[pyo3(get, set)]
    _return_bytearray: bool,
}

#[pymethods]
impl SNAPPYDecompressor {
    #[new]
    fn new() -> Self {
        SNAPPYDecompressor {
            decoder: None,
            eof: false,
            needs_input: true,
            unused_data: Vec::new(),
            unconsumed_data: Vec::new(),
            _return_bytearray: false,
        }
    }

    fn __enter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __exit__(
        mut slf: PyRefMut<'_, Self>,
        _exc_type: Option<&Bound<'_, PyAny>>,
        _exc_value: Option<&Bound<'_, PyAny>>,
        _traceback: Option<&Bound<'_, PyAny>>,
    ) {
        slf.reset();
    }

    fn reset(&mut self) {
        self.decoder = None;
        self.eof = false;
        self.needs_input = true;
        self.unused_data.clear();
        self.unconsumed_data.clear();
        self._return_bytearray = false;
    }

    fn decompress(
        &mut self,
        py: Python<'_>,
        data: &Bound<'_, PyAny>,
        max_length: Option<i64>,
    ) -> PyResult<Py<PyBytes>> {
        let input_bytes = if data.is_instance_of::<PyBytes>() || data.is_instance_of::<PyByteArray>() {
            data.extract::<Vec<u8>>()?
        } else {
            let bytes = data.call_method0("tobytes")?;
            bytes.extract::<Vec<u8>>()?
        };

        if self.eof {
            self.needs_input = false;
            return Ok(PyBytes::new(py, &[]).into());
        }

        let mut full_data = Vec::new();

        if !self.unconsumed_data.is_empty() {
            full_data.append(&mut self.unconsumed_data);
        }

        full_data.extend_from_slice(&input_bytes);

        if self.decoder.is_none() {
            if full_data.is_empty() {
                self.needs_input = true;
                return Ok(PyBytes::new(py, &[]).into());
            }
            let cursor = Cursor::new(full_data.clone());
            self.decoder = Some(FrameDecoder::new(cursor));
        }

        let decoder = self.decoder.as_mut().unwrap();
        let max_out = if let Some(limit) = max_length {
            if limit <= 0 {
                usize::MAX
            } else {
                limit as usize
            }
        } else {
            usize::MAX
        };

        let mut result = Vec::new();
        let mut temp_buf = [0u8; 8192];

        while result.len() < max_out {
            let to_read = std::cmp::min(temp_buf.len(), max_out - result.len());

            match decoder.read(&mut temp_buf[..to_read]) {
                Ok(0) => {
                    self.eof = true;
                    self.needs_input = false;
                    let pos = decoder.get_ref().position() as usize;

                    if pos < full_data.len() {
                        self.unused_data = full_data[pos..].to_vec();
                    }
                    break;
                }
                Ok(n) => {
                    result.extend_from_slice(&temp_buf[..n]);

                    if n < to_read {
                        self.eof = true;
                        self.needs_input = false;
                        break;
                    }
                }
                Err(_) => {
                    self.eof = true;
                    self.needs_input = false;
                    break;
                }
            }
        }

        Ok(PyBytes::new(py, &result).into())
    }

    #[getter]
    fn eof(&self) -> PyResult<bool> {
        Ok(self.eof)
    }

    #[getter]
    fn needs_input(&self) -> PyResult<bool> {
        Ok(self.needs_input)
    }

    #[getter]
    fn unused_data(&self, py: Python<'_>) -> PyResult<Py<PyBytes>> {
        Ok(PyBytes::new(py, &self.unused_data).into())
    }

    #[getter]
    fn _unconsumed_data(&self, py: Python<'_>) -> PyResult<Py<PyBytes>> {
        Ok(PyBytes::new(py, &self.unconsumed_data).into())
    }
}

#[pymodule]
fn snappy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SNAPPYDecompressor>()?;
    Ok(())
}

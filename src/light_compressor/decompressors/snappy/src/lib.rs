use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyByteArray, PyAny};
use snap::read::FrameDecoder;
use snap::raw::Decoder as RawDecoder;
use std::io::{Read, Cursor};
use std::collections::VecDeque;


#[pyclass]
pub struct SNAPDecompressor {
    decoder: Option<FrameDecoder<Cursor<Vec<u8>>>>,
    eof: bool,
    needs_input: bool,
    unused_data: Vec<u8>,
    unconsumed_data: Vec<u8>,
    decompressed_buffer: VecDeque<u8>,
    #[pyo3(get, set)]
    _return_bytearray: bool,
    is_raw_format: bool,
}


#[pymethods]
impl SNAPDecompressor {

    #[new]
    fn new() -> Self {
        SNAPDecompressor {
            decoder: None,
            eof: false,
            needs_input: true,
            unused_data: Vec::new(),
            unconsumed_data: Vec::new(),
            decompressed_buffer: VecDeque::new(),
            _return_bytearray: false,
            is_raw_format: false,
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
        self.decompressed_buffer.clear();
        self._return_bytearray = false;
        self.is_raw_format = false;
    }

    #[pyo3(signature = (data, max_length=None))]
    fn decompress(
        &mut self,
        py: Python<'_>,
        data: &Bound<'_, PyAny>,
        max_length: Option<i64>,
    ) -> PyResult<Py<PyBytes>> {

        if self.eof {
            self.needs_input = false;
            return Ok(PyBytes::new(py, &[]).into());
        }

        let mut input_bytes = if data.is_instance_of::<PyBytes>() ||
            data.is_instance_of::<PyByteArray>() {
            data.extract::<Vec<u8>>()?
        } else {
            let bytes = data.call_method0("tobytes")?;
            bytes.extract::<Vec<u8>>()?
        };

        if !self.unconsumed_data.is_empty() {
            input_bytes.splice(0..0, self.unconsumed_data.drain(..));
        }

        if input_bytes.is_empty() && self.decoder.is_none() {
            self.needs_input = true;
            return Ok(PyBytes::new(py, &[]).into());
        }

        if self.decoder.is_none() && !input_bytes.is_empty() {
            self.is_raw_format = Self::detect_format(&input_bytes);

            if self.is_raw_format {
                let max_out = if let Some(limit) = max_length {
                    if limit <= 0 { usize::MAX } else { limit as usize }
                } else { usize::MAX };
                let decompressed = Self::decompress_raw(
                    &input_bytes,
                    max_out,
                )?;
                self.eof = true;
                self.needs_input = false;
                return Ok(PyBytes::new(py, &decompressed).into());
            } else {
                if let Some(pos) = Self::find_stream_start(&input_bytes) {
                    let remaining = input_bytes.split_off(pos);
                    let cursor = Cursor::new(remaining);
                    self.decoder = Some(FrameDecoder::new(cursor));
                    input_bytes.clear();
                } else if !Self::is_stream_identifier(&input_bytes) {
                    let max_out = if let Some(limit) = max_length {
                        if limit <= 0 { usize::MAX } else { limit as usize }
                    } else { usize::MAX };
                    let decompressed = Self::decompress_raw(
                        &input_bytes,
                        max_out,
                    )?;
                    self.eof = true;
                    self.needs_input = false;
                    return Ok(PyBytes::new(py, &decompressed).into());
                }
            }
        }

        if !input_bytes.is_empty() && self.decoder.is_some() {
            let decoder = self.decoder.as_mut().unwrap();
            let pos = decoder.get_ref().position() as usize;
            let mut full_data = decoder.get_ref().get_ref().clone();
            full_data.extend_from_slice(&input_bytes);
            *decoder.get_mut() = Cursor::new(full_data);
            decoder.get_mut().set_position(pos as u64);
        }

        let max_out = if let Some(limit) = max_length {
            if limit <= 0 {usize::MAX} else {limit as usize}
        } else {usize::MAX};

        let mut result = Vec::new();
        let mut temp_buf = [0u8; 8192];

        while !self.decompressed_buffer.is_empty() && result.len() < max_out {
            result.push(self.decompressed_buffer.pop_front().unwrap());
        }

        if result.len() < max_out && self.decoder.is_some() {
            let decoder = self.decoder.as_mut().unwrap();

            while result.len() < max_out {
                let to_read = std::cmp::min(
                    temp_buf.len(),
                    max_out - result.len(),
                );

                match decoder.read(&mut temp_buf[..to_read]) {
                    Ok(0) => {
                        self.eof = true;
                        self.needs_input = false;
                        let pos = decoder.get_ref().position() as usize;
                        let all_data = decoder.get_ref().get_ref();
                        if pos < all_data.len() {
                            self.unused_data = all_data[pos..].to_vec();
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
                    Err(_e) => {
                        if result.is_empty() &&
                            self.decompressed_buffer.is_empty() {
                            self.eof = true;
                            self.needs_input = false;
                            return Ok(PyBytes::new(py, &[]).into());
                        }
                        self.eof = true;
                        self.needs_input = false;
                        break;
                    }
                }
            }
        }

        if let Some(decoder) = &mut self.decoder {
            let pos = decoder.get_ref().position() as usize;
            let all_data = decoder.get_ref().get_ref();
            if pos < all_data.len() {
                if self.eof {
                    self.unused_data = all_data[pos..].to_vec();
                    self.unconsumed_data.clear();
                } else {
                    self.unconsumed_data = all_data[pos..].to_vec();
                    self.needs_input = false;
                }
            } else {
                self.unconsumed_data.clear();
                self.needs_input = true;
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


impl SNAPDecompressor {
    fn decompress_raw(data: &[u8], max_out: usize) -> PyResult<Vec<u8>> {
        let mut decoder = RawDecoder::new();
        match decoder.decompress_vec(data) {
            Ok(decompressed) => {
                if decompressed.len() <= max_out {
                    Ok(decompressed)
                } else {
                    Ok(decompressed[..max_out].to_vec())
                }
            }
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Raw Snappy decompression error: {:?}", e)
            ))
        }
    }

    fn detect_format(data: &[u8]) -> bool {

        if Self::is_stream_identifier(data) {
            return false;
        }

        if data.len() >= 4 {
            let chunk_type = data[0];
            if chunk_type == 0x00 || chunk_type == 0x01 {
                return false;
            }
        }

        if !data.is_empty() && data[0] < 0x80 {
            return true;
        }
        
        false
    }

    fn is_stream_identifier(data: &[u8]) -> bool {
        data.len() >= 10 && 
        data[0] == 0xff && 
        data[1] == 0x06 && 
        data[2] == 0x00 && 
        data[3] == 0x00 && 
        &data[4..10] == b"sNaPpY"
    }

    fn find_stream_start(data: &[u8]) -> Option<usize> {
        for i in 0..data.len().saturating_sub(9) {
            if Self::is_stream_identifier(&data[i..]) {
                return Some(i);
            }
        }
        None
    }
}


#[pymodule]
fn snappy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SNAPDecompressor>()?;
    Ok(())
}

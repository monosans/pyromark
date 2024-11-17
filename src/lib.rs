mod class_api;
mod common;
mod function_api;
use pyo3::prelude::*;

#[pymodule]
fn _pyromark(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_function(wrap_pyfunction!(crate::function_api::events, m)?)?;
    m.add_function(wrap_pyfunction!(crate::function_api::html, m)?)?;
    m.add_class::<crate::class_api::Markdown>()?;
    Ok(())
}

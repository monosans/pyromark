use pyo3::prelude::*;

/// Examples:
///     ```python
///     for event in pyromark.events(
///         "# Hello world",
///         extensions=(
///             pyromark.Extensions.ENABLE_TABLES
///             | pyromark.Extensions.ENABLE_MATH
///             | pyromark.Extensions.ENABLE_GFM
///         )
///     ):
///         # All event types are fully type annotated
///         # so you will get static type checking
///         # and Tab completions in your IDE!
///         match event:
///             case ("Start", ("Heading", {"level": heading_level})):
///                 print(f"Heading with {heading_level} level started")
///             case ("Text", text):
///                 print(f"Got {text!r} text")
///             case ("End", ("Heading", heading_level)):
///                 print(f"Heading with {heading_level} level ended")
///             case other_event:
///                 print(f"Got {other_event!r}")
///     ```
#[pyfunction]
#[pyo3(signature = (text, /, *, extensions = None, merge_text = true))]
pub(crate) fn events(
    py: Python<'_>,
    text: &str,
    extensions: Option<u32>,
    merge_text: bool,
) -> PyResult<PyObject> {
    let serde_value = py.allow_threads(move || {
        crate::common::parse_events(
            text,
            crate::common::get_options(extensions),
            merge_text,
        )
    })?;
    crate::common::serde_json_value_to_pyobject(py, &serde_value)
}

/// Examples:
///     ```python
///     html = pyromark.markdown(
///         "# Hello world",
///         # See pyromark.Extensions for all available extensions
///         extensions=(
///             pyromark.Extensions.ENABLE_TABLES
///             | pyromark.Extensions.ENABLE_MATH
///             | pyromark.Extensions.ENABLE_GFM
///         )
///     )
///     assert html == "<h1>Hello world</h1>\n"
///     ```
#[pyfunction]
#[pyo3(signature = (text, *, extensions = None))]
pub(crate) fn markdown(
    py: Python<'_>,
    text: &str,
    extensions: Option<u32>,
) -> String {
    py.allow_threads(move || {
        crate::common::convert_to_html(
            text,
            crate::common::get_options(extensions),
        )
    })
}

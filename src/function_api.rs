use pyo3::prelude::*;

/// Examples:
///     ```python
///     for event in pyromark.events(
///         "# Hello world",
///         options=(
///             pyromark.Options.ENABLE_TABLES
///             | pyromark.Options.ENABLE_MATH
///             | pyromark.Options.ENABLE_GFM
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
#[pyo3(signature = (markdown, /, *, options = None, merge_text = true))]
pub(crate) fn events<'py>(
    py: Python<'py>,
    markdown: &str,
    options: Option<u32>,
    merge_text: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let v = py.allow_threads(move || {
        crate::common::parse_events(
            markdown,
            crate::common::build_options(options),
            merge_text,
        )
    })?;
    crate::common::serde_into_py(py, &v)
}

/// Examples:
///     ```python
///     html = pyromark.html(
///         "# Hello world",
///         # See pyromark.Options for all available options
///         options=(
///             pyromark.Options.ENABLE_TABLES
///             | pyromark.Options.ENABLE_MATH
///             | pyromark.Options.ENABLE_GFM
///         )
///     )
///     assert html == "<h1>Hello world</h1>\n"
///     ```
#[pyfunction]
#[pyo3(signature = (markdown, /, *, options = None))]
pub(crate) fn html(
    py: Python<'_>,
    markdown: &str,
    options: Option<u32>,
) -> String {
    py.allow_threads(move || {
        crate::common::html(markdown, crate::common::build_options(options))
    })
}

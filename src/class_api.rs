use pyo3::prelude::*;

#[pyclass(frozen, module = "pyromark._pyromark")]
pub(crate) struct Markdown(pulldown_cmark::Options);

#[pymethods]
impl Markdown {
    #[new]
    #[pyo3(signature = (*, extensions = None))]
    fn new(extensions: Option<u32>) -> Self {
        Self(crate::common::get_options(extensions))
    }

    /// Examples:
    ///     ```python
    ///     html = md.convert("# Hello world")
    ///     assert html == "<h1>Hello world</h1>\n"
    ///     ```
    fn convert(&self, py: Python<'_>, text: &str) -> String {
        py.allow_threads(move || crate::common::convert_to_html(text, self.0))
    }

    /// Examples:
    ///     ```python
    ///     for event in md.events(
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
    #[pyo3(signature = (text, /, *, merge_text = true))]
    fn events(
        &self,
        py: Python<'_>,
        text: &str,
        merge_text: bool,
    ) -> PyResult<PyObject> {
        let serde_value = py.allow_threads(move || {
            crate::common::parse_events(text, self.0, merge_text)
        })?;
        crate::common::serde_json_value_to_pyobject(py, &serde_value)
    }
}

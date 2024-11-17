use pyo3::prelude::*;

#[pyclass(frozen, module = "pyromark._pyromark")]
pub(crate) struct Markdown(pulldown_cmark::Options);

#[pymethods]
impl Markdown {
    #[new]
    #[pyo3(signature = (*, options = None))]
    fn new(options: Option<u32>) -> Self {
        Self(crate::common::build_options(options))
    }

    /// Examples:
    ///     ```python
    ///     for event in md.events(
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
    #[pyo3(signature = (markdown, /, *, merge_text = true))]
    fn events<'py>(
        &self,
        py: Python<'py>,
        markdown: &str,
        merge_text: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let v = py.allow_threads(move || {
            crate::common::parse_events(markdown, self.0, merge_text)
        })?;
        crate::common::serde_into_py(py, &v)
    }

    /// Examples:
    ///     ```python
    ///     html = md.html("# Hello world")
    ///     assert html == "<h1>Hello world</h1>\n"
    ///     ```
    #[pyo3(signature = (markdown, /))]
    fn html(&self, py: Python<'_>, markdown: &str) -> String {
        py.allow_threads(move || crate::common::html(markdown, self.0))
    }
}

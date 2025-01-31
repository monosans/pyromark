use pyo3::prelude::*;

#[pyclass(frozen, module = "pyromark._pyromark")]
pub(crate) struct Markdown(pulldown_cmark::Options);

#[pymethods]
impl Markdown {
    #[new]
    #[pyo3(signature = (*, options = 0))]
    fn new(options: u32) -> Self {
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
    ///             case {"Start": {"Heading": {"level": heading_level}}}:
    ///                 print(f"Heading with {heading_level} level started")
    ///             case {"Text": text}:
    ///                 print(f"Got {text!r} text")
    ///             case {"End": {"Heading": heading_level}}:
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
    ) -> pythonize::Result<Bound<'py, PyAny>> {
        let v = py.allow_threads(move || {
            crate::common::events(markdown, self.0, merge_text)
        });
        pythonize::pythonize_custom::<crate::common::PythonizeCustom, _>(py, &v)
    }

    /// Examples:
    ///     ```python
    ///     for event, range_ in md.events_with_range(
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
    ///             case {"Start": {"Heading": {"level": heading_level}}}:
    ///                 print(
    ///                     f"Heading with {heading_level} level started, "
    ///                     f"{range_=}"
    ///                 )
    ///             case {"Text": text}:
    ///                 print(f"Got {text!r} text, {range_=}")
    ///             case {"End": {"Heading": heading_level}}:
    ///                 print(
    ///                     f"Heading with {heading_level} level ended, "
    ///                     f"{range_=}"
    ///                 )
    ///             case other_event:
    ///                 print(f"Got {other_event!r}, {range_=}")
    ///     ```
    #[pyo3(signature = (markdown, /))]
    fn events_with_range<'py>(
        &self,
        py: Python<'py>,
        markdown: &str,
    ) -> pythonize::Result<Bound<'py, PyAny>> {
        let v = py.allow_threads(move || {
            crate::common::events_with_range(markdown, self.0)
        });
        pythonize::pythonize_custom::<crate::common::PythonizeCustom, _>(py, &v)
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

use pyo3::prelude::*;

#[pyclass(frozen, module = "pyromark._pyromark")]
pub struct Markdown(pulldown_cmark::Options);

#[pymethods]
impl Markdown {
    #[new]
    #[pyo3(signature = (*, options = 0))]
    fn new(options: u32) -> PyResult<Self> {
        crate::common::build_options(options).map(Self)
    }

    /// Same as [`pyromark.events`][], with these settings.
    #[pyo3(signature = (markdown, /, *, merge_text = true))]
    fn events(
        &self,
        py: Python<'_>,
        markdown: pyo3::pybacked::PyBackedStr,
        merge_text: bool,
    ) -> crate::lazy_api::Events {
        crate::lazy_api::new(py, markdown, self.0, merge_text, false)
    }

    /// Same as [`pyromark.events_with_range`][], with these settings.
    #[pyo3(signature = (markdown, /, *, merge_text = false))]
    fn events_with_range(
        &self,
        py: Python<'_>,
        markdown: pyo3::pybacked::PyBackedStr,
        merge_text: bool,
    ) -> crate::lazy_api::Events {
        crate::lazy_api::new(py, markdown, self.0, merge_text, true)
    }

    /// Examples:
    ///     ```python
    ///     html = md.html("# Hello world")
    ///     assert html == "<h1>Hello world</h1>\n"
    ///     ```
    #[pyo3(signature = (markdown, /))]
    fn html(&self, py: Python<'_>, markdown: &str) -> String {
        py.detach(move || crate::common::html(markdown, self.0))
    }
}

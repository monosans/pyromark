use pyo3::prelude::*;

/// Parser settings, given once and reused for every call.
///
/// Takes the same keyword arguments as `html`; `highlight` only affects
/// `html` and `write_html`. Instances are immutable, so one can be shared
/// between threads.
///
/// Examples:
///     ```python
///     md = pyromark.Markdown(options=pyromark.Options.ENABLE_TABLES)
///     assert md.html("# Hello world") == "<h1>Hello world</h1>\n"
///     ```
#[pyclass(frozen, module = "pyromark._pyromark")]
pub struct Markdown {
    options: pulldown_cmark::Options,
    broken_link_callback: Option<Py<PyAny>>,
    highlighter: Option<crate::highlight::Highlighter>,
}

fn broken_link_callback<'a, 'py>(
    markdown: &'a Markdown,
    py: Python<'py>,
) -> Option<&'a Bound<'py, PyAny>> {
    markdown.broken_link_callback.as_ref().map(|callback| callback.bind(py))
}

#[pymethods]
impl Markdown {
    #[new]
    #[pyo3(signature = (
        *,
        options = 0,
        broken_link_callback = None,
        highlight = None
    ))]
    fn new(
        options: u32,
        broken_link_callback: Option<&Bound<'_, PyAny>>,
        highlight: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
        crate::common::check_broken_link_callback(broken_link_callback)?;
        Ok(Self {
            options: crate::common::build_options(options)?,
            broken_link_callback: broken_link_callback
                .map(|callback| callback.clone().unbind()),
            highlighter: crate::highlight::build_highlighter(highlight)?,
        })
    }

    fn __traverse__(
        &self,
        visit: pyo3::pyclass::PyVisit<'_>,
    ) -> Result<(), pyo3::pyclass::PyTraverseError> {
        visit.call(&self.broken_link_callback)?;
        visit.call(
            self.highlighter
                .as_ref()
                .and_then(crate::highlight::Highlighter::callback),
        )
    }

    /// Same as [`pyromark.events`][], with these settings.
    #[pyo3(signature = (markdown, /, *, merge_text = true))]
    fn events(
        &self,
        py: Python<'_>,
        markdown: pyo3::pybacked::PyBackedStr,
        merge_text: bool,
    ) -> crate::lazy_api::Events {
        crate::lazy_api::new(
            py,
            markdown,
            self.options,
            merge_text,
            false,
            broken_link_callback(self, py),
        )
    }

    /// Same as [`pyromark.events_with_range`][], with these settings.
    #[pyo3(signature = (markdown, /, *, merge_text = false))]
    fn events_with_range(
        &self,
        py: Python<'_>,
        markdown: pyo3::pybacked::PyBackedStr,
        merge_text: bool,
    ) -> crate::lazy_api::Events {
        crate::lazy_api::new(
            py,
            markdown,
            self.options,
            merge_text,
            true,
            broken_link_callback(self, py),
        )
    }

    /// Same as [`pyromark.html`][], with these settings.
    #[pyo3(signature = (markdown, /))]
    fn html(&self, py: Python<'_>, markdown: &str) -> PyResult<String> {
        crate::common::html(
            py,
            markdown,
            self.options,
            broken_link_callback(self, py),
            self.highlighter.as_ref(),
        )
    }

    /// Same as [`pyromark.write_html`][], with these settings.
    #[pyo3(signature = (markdown, file, /))]
    fn write_html(
        &self,
        py: Python<'_>,
        markdown: &str,
        file: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        crate::common::write_html(
            py,
            markdown,
            file,
            self.options,
            broken_link_callback(self, py),
            self.highlighter.as_ref(),
        )
    }

    /// Same as [`pyromark.reference_definitions`][], with these settings.
    #[pyo3(signature = (markdown, /))]
    fn reference_definitions<'py>(
        &self,
        py: Python<'py>,
        markdown: &str,
    ) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
        crate::common::reference_definitions(py, markdown, self.options)
    }
}

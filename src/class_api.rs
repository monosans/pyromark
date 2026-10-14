use pyo3::prelude::*;

/// Parser settings, given once and reused for every call.
///
/// Takes the same keyword arguments as `html`. Instances are immutable, so
/// one can be shared between threads.
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
        broken_link_callback = None
    ))]
    fn new(
        options: u32,
        broken_link_callback: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
        crate::common::check_broken_link_callback(broken_link_callback)?;
        Ok(Self {
            options: crate::common::build_options(options)?,
            broken_link_callback: broken_link_callback
                .map(|callback| callback.clone().unbind()),
        })
    }

    fn __traverse__(
        &self,
        visit: pyo3::pyclass::PyVisit<'_>,
    ) -> Result<(), pyo3::pyclass::PyTraverseError> {
        visit.call(&self.broken_link_callback)
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
        )
    }
}

use pyo3::prelude::*;

#[pyclass(frozen, module = "pyromark._pyromark")]
pub struct Markdown(pulldown_cmark::Options);

#[pymethods]
impl Markdown {
    #[new]
    #[pyo3(signature = (*, options = 0))]
    const fn new(options: u32) -> Self {
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
    #[pyo3(signature = (markdown, /, *, merge_text = true, broken_link_callback = None))]
    fn events<'py>(
        &self,
        py: Python<'py>,
        markdown: &str,
        merge_text: bool,
        broken_link_callback: Option<Bound<'py, PyAny>>,
    ) -> pythonize::Result<Bound<'py, PyAny>> {
        // Need to own markdown string so closure can reference it - keep it alive for entire function
        let markdown_owned = markdown.to_string();
        let markdown_ref = markdown_owned.as_str();

        let v = if let Some(callback) = broken_link_callback {
            crate::common::events_with_broken_link_callback(
                markdown_ref,
                self.0,
                merge_text,
                |broken_link| {
                    // We're already in a GIL context, just use py
                    // Create a dict with broken link information
                    let link_info = pyo3::types::PyDict::new(py);
                    link_info.set_item("reference", broken_link.reference.as_ref()).ok()?;
                    link_info.set_item("span", (broken_link.span.start, broken_link.span.end)).ok()?;

                    // Call the Python callback
                    let result = callback.call1((link_info,)).ok()?;

                    // Check if result is None
                    if result.is_none() {
                        return None;
                    }

                    // Extract (url, title) tuple
                    let tuple = result.cast::<pyo3::types::PyTuple>().ok()?;
                    if tuple.len() != 2 {
                        return None;
                    }

                    let url = tuple.get_item(0).ok()?.extract::<String>().ok()?;
                    let title = tuple.get_item(1).ok()?.extract::<String>().ok()?;

                    Some((pulldown_cmark::CowStr::Boxed(url.into()), pulldown_cmark::CowStr::Boxed(title.into())))
                },
            )
        } else {
            py.detach(move || {
                crate::common::events(markdown, self.0, merge_text)
            })
        };
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
    #[pyo3(signature = (markdown, /, *, broken_link_callback = None))]
    fn events_with_range<'py>(
        &self,
        py: Python<'py>,
        markdown: &str,
        broken_link_callback: Option<Bound<'py, PyAny>>,
    ) -> pythonize::Result<Bound<'py, PyAny>> {
        // Need to own markdown string so closure can reference it - keep it alive for entire function
        let markdown_owned = markdown.to_string();
        let markdown_ref = markdown_owned.as_str();

        let v = if let Some(callback) = broken_link_callback {
            crate::common::events_with_range_and_broken_link_callback(
                markdown_ref,
                self.0,
                |broken_link| {
                    // We're already in a GIL context, just use py
                    // Create a dict with broken link information
                    let link_info = pyo3::types::PyDict::new(py);
                    link_info.set_item("reference", broken_link.reference.as_ref()).ok()?;
                    link_info.set_item("span", (broken_link.span.start, broken_link.span.end)).ok()?;

                    // Call the Python callback
                    let result = callback.call1((link_info,)).ok()?;

                    // Check if result is None
                    if result.is_none() {
                        return None;
                    }

                    // Extract (url, title) tuple
                    let tuple = result.cast::<pyo3::types::PyTuple>().ok()?;
                    if tuple.len() != 2 {
                        return None;
                    }

                    let url = tuple.get_item(0).ok()?.extract::<String>().ok()?;
                    let title = tuple.get_item(1).ok()?.extract::<String>().ok()?;

                    Some((pulldown_cmark::CowStr::Boxed(url.into()), pulldown_cmark::CowStr::Boxed(title.into())))
                },
            )
        } else {
            py.detach(move || crate::common::events_with_range(markdown, self.0))
        };
        pythonize::pythonize_custom::<crate::common::PythonizeCustom, _>(py, &v)
    }

    /// Examples:
    ///     ```python
    ///     html = md.html("# Hello world")
    ///     assert html == "<h1>Hello world</h1>\n"
    ///     ```
    #[pyo3(signature = (markdown, /, *, broken_link_callback = None))]
    fn html<'py>(
        &self,
        py: Python<'py>,
        markdown: &str,
        broken_link_callback: Option<Bound<'py, PyAny>>,
    ) -> String {
        // Need to own markdown string so closure can reference it - keep it alive for entire function
        let markdown_owned = markdown.to_string();
        let markdown_ref = markdown_owned.as_str();

        if let Some(callback) = broken_link_callback {
            crate::common::html_with_broken_link_callback(
                markdown_ref,
                self.0,
                |broken_link| {
                    // We're already in a GIL context, just use py
                    // Create a dict with broken link information
                    let link_info = pyo3::types::PyDict::new(py);
                    link_info.set_item("reference", broken_link.reference.as_ref()).ok()?;
                    link_info.set_item("span", (broken_link.span.start, broken_link.span.end)).ok()?;

                    // Call the Python callback
                    let result = callback.call1((link_info,)).ok()?;

                    // Check if result is None
                    if result.is_none() {
                        return None;
                    }

                    // Extract (url, title) tuple
                    let tuple = result.cast::<pyo3::types::PyTuple>().ok()?;
                    if tuple.len() != 2 {
                        return None;
                    }

                    let url = tuple.get_item(0).ok()?.extract::<String>().ok()?;
                    let title = tuple.get_item(1).ok()?.extract::<String>().ok()?;

                    Some((pulldown_cmark::CowStr::Boxed(url.into()), pulldown_cmark::CowStr::Boxed(title.into())))
                },
            )
        } else {
            py.detach(move || crate::common::html(markdown, self.0))
        }
    }
}

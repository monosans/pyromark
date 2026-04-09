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
///             case {"Start": {"Heading": {"level": heading_level}}}:
///                 print(f"Heading with {heading_level} level started")
///             case {"Text": text}:
///                 print(f"Got {text!r} text")
///             case {"End": {"Heading": heading_level}}:
///                 print(f"Heading with {heading_level} level ended")
///             case other_event:
///                 print(f"Got {other_event!r}")
///     ```
#[pyfunction]
#[pyo3(signature = (markdown, /, *, options = 0, merge_text = true, broken_link_callback = None))]
pub fn events<'py>(
    py: Python<'py>,
    markdown: &str,
    options: u32,
    merge_text: bool,
    broken_link_callback: Option<Bound<'py, PyAny>>,
) -> pythonize::Result<Bound<'py, PyAny>> {
    // Need to own markdown string so closure can reference it - keep it alive for entire function
    let markdown_owned = markdown.to_string();
    let markdown_ref = markdown_owned.as_str();

    let v = if let Some(callback) = broken_link_callback {
        crate::common::events_with_broken_link_callback(
            markdown_ref,
            crate::common::build_options(options),
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
            crate::common::events(
                markdown,
                crate::common::build_options(options),
                merge_text,
            )
        })
    };
    pythonize::pythonize_custom::<crate::common::PythonizeCustom, _>(py, &v)
}

/// Examples:
///     ```python
///     for event, range_ in pyromark.events_with_range(
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
///                     f"Heading with {heading_level} level started, {range_=}"
///                 )
///             case {"Text": text}:
///                 print(f"Got {text!r} text, {range_=}")
///             case {"End": {"Heading": heading_level}}:
///                 print(
///                     f"Heading with {heading_level} level ended, {range_=}"
///                 )
///             case other_event:
///                 print(f"Got {other_event!r}, {range_=}")
///     ```
#[pyfunction]
#[pyo3(signature = (markdown, /, *, options = 0, broken_link_callback = None))]
pub fn events_with_range<'py>(
    py: Python<'py>,
    markdown: &str,
    options: u32,
    broken_link_callback: Option<Bound<'py, PyAny>>,
) -> pythonize::Result<Bound<'py, PyAny>> {
    // Need to own markdown string so closure can reference it - keep it alive for entire function
    let markdown_owned = markdown.to_string();
    let markdown_ref = markdown_owned.as_str();

    let v = if let Some(callback) = broken_link_callback {
        crate::common::events_with_range_and_broken_link_callback(
            markdown_ref,
            crate::common::build_options(options),
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
            crate::common::events_with_range(
                markdown,
                crate::common::build_options(options),
            )
        })
    };
    pythonize::pythonize_custom::<crate::common::PythonizeCustom, _>(py, &v)
}

/// Examples:
///     ```python
///     html = pyromark.html(
///         "# Hello world",
///         options=(
///             pyromark.Options.ENABLE_TABLES
///             | pyromark.Options.ENABLE_MATH
///             | pyromark.Options.ENABLE_GFM
///         )
///     )
///     assert html == "<h1>Hello world</h1>\n"
///     ```
#[pyfunction]
#[pyo3(signature = (markdown, /, *, options = 0, broken_link_callback = None))]
pub fn html<'py>(
    py: Python<'py>,
    markdown: &str,
    options: u32,
    broken_link_callback: Option<Bound<'py, PyAny>>,
) -> String {
    // Need to own markdown string so closure can reference it - keep it alive for entire function
    let markdown_owned = markdown.to_string();
    let markdown_ref = markdown_owned.as_str();

    if let Some(callback) = broken_link_callback {
        crate::common::html_with_broken_link_callback(
            markdown_ref,
            crate::common::build_options(options),
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
            crate::common::html(markdown, crate::common::build_options(options))
        })
    }
}

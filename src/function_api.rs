use pyo3::prelude::*;

/// Iterate over the document's events.
///
/// Returns a lazy iterator: wrap it in `tuple()` if you need a sequence.
/// Adjacent text events are merged unless `merge_text=False`.
///
/// Examples:
///     ```python
///     for event in pyromark.events("# Hello world"):
///         match event:
///             case {"Start": {"Heading": {"level": level}}}:
///                 print(f"{level} heading started")
///             case {"Text": text}:
///                 print(f"Got {text!r}")
///             case {"End": {"Heading": level}}:
///                 print(f"{level} heading ended")
///     ```
#[pyfunction]
#[pyo3(signature = (
    markdown,
    /,
    *,
    options = 0,
    merge_text = true,
    broken_link_callback = None
))]
pub fn events(
    py: Python<'_>,
    markdown: pyo3::pybacked::PyBackedStr,
    options: u32,
    merge_text: bool,
    broken_link_callback: Option<&Bound<'_, PyAny>>,
) -> PyResult<crate::lazy_api::Events> {
    crate::common::check_broken_link_callback(broken_link_callback)?;
    Ok(crate::lazy_api::new(
        py,
        markdown,
        crate::common::build_options(options)?,
        merge_text,
        false,
        broken_link_callback,
    ))
}

/// Like `events`, but yields `(event, range)` pairs.
///
/// Ranges are UTF-8 byte offsets: slice `markdown.encode()`, not
/// `markdown`. Text is not merged by default, because each piece has its
/// own range.
///
/// Examples:
///     ```python
///     markdown = "# Hello world"
///     for event, range_ in pyromark.events_with_range(markdown):
///         source = markdown.encode()[range_["start"] : range_["end"]]
///         print(event, source.decode())
///     ```
#[pyfunction]
#[pyo3(signature = (
    markdown,
    /,
    *,
    options = 0,
    merge_text = false,
    broken_link_callback = None
))]
pub fn events_with_range(
    py: Python<'_>,
    markdown: pyo3::pybacked::PyBackedStr,
    options: u32,
    merge_text: bool,
    broken_link_callback: Option<&Bound<'_, PyAny>>,
) -> PyResult<crate::lazy_api::Events> {
    crate::common::check_broken_link_callback(broken_link_callback)?;
    Ok(crate::lazy_api::new(
        py,
        markdown,
        crate::common::build_options(options)?,
        merge_text,
        true,
        broken_link_callback,
    ))
}

/// Render Markdown to HTML.
///
/// The output is not sanitized: raw HTML passes through, as `CommonMark`
/// requires.
///
/// Examples:
///     ```python
///     html = pyromark.html("# Hello world")
///     assert html == "<h1>Hello world</h1>\n"
///     ```
///
///     Resolve references the document does not define:
///
///     ```python
///     html = pyromark.html(
///         "[Hello]",
///         broken_link_callback=lambda link: (f"/{link['reference']}", ""),
///     )
///     assert html == '<p><a href="/Hello">Hello</a></p>\n'
///     ```
#[pyfunction]
#[pyo3(signature = (
    markdown,
    /,
    *,
    options = 0,
    broken_link_callback = None
))]
pub fn html(
    py: Python<'_>,
    markdown: &str,
    options: u32,
    broken_link_callback: Option<&Bound<'_, PyAny>>,
) -> PyResult<String> {
    crate::common::check_broken_link_callback(broken_link_callback)?;
    crate::common::html(
        py,
        markdown,
        crate::common::build_options(options)?,
        broken_link_callback,
    )
}

/// Return the document's link reference definitions, keyed by label.
///
/// They come in document order. Labels match case-insensitively, and the
/// first definition wins. Only the block level pass runs, so this is cheaper
/// than `events`.
///
/// Examples:
///     ```python
///     definitions = pyromark.reference_definitions("[foo]: /a 'A'")
///     assert definitions == {
///         "foo": {"dest": "/a", "title": "A", "span": {"start": 0, "end": 13}}
///     }
///     ```
#[pyfunction]
#[pyo3(signature = (markdown, /, *, options = 0))]
pub fn reference_definitions<'py>(
    py: Python<'py>,
    markdown: &str,
    options: u32,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    crate::common::reference_definitions(
        py,
        markdown,
        crate::common::build_options(options)?,
    )
}

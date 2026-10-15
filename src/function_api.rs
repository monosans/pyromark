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
#[pyo3(signature = (markdown, /, *, options = 0, merge_text = true))]
pub fn events(
    py: Python<'_>,
    markdown: pyo3::pybacked::PyBackedStr,
    options: u32,
    merge_text: bool,
) -> PyResult<crate::lazy_api::Events> {
    Ok(crate::lazy_api::new(
        py,
        markdown,
        crate::common::build_options(options)?,
        merge_text,
        false,
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
#[pyo3(signature = (markdown, /, *, options = 0, merge_text = false))]
pub fn events_with_range(
    py: Python<'_>,
    markdown: pyo3::pybacked::PyBackedStr,
    options: u32,
    merge_text: bool,
) -> PyResult<crate::lazy_api::Events> {
    Ok(crate::lazy_api::new(
        py,
        markdown,
        crate::common::build_options(options)?,
        merge_text,
        true,
    ))
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
#[pyo3(signature = (markdown, /, *, options = 0))]
pub fn html(py: Python<'_>, markdown: &str, options: u32) -> PyResult<String> {
    let options = crate::common::build_options(options)?;
    Ok(py.detach(move || crate::common::html(markdown, options)))
}

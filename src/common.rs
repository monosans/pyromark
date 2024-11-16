use pyo3::prelude::*;

pub(crate) fn build_options(options: Option<u32>) -> pulldown_cmark::Options {
    match options {
        None => pulldown_cmark::Options::empty(),
        Some(value) => pulldown_cmark::Options::from_bits_truncate(value),
    }
}

pub(crate) fn html(markdown: &str, options: pulldown_cmark::Options) -> String {
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    let mut html_output = String::new();
    pulldown_cmark::html::push_html(&mut html_output, parser);
    html_output
}

pub(crate) fn parse_events(
    markdown: &str,
    options: pulldown_cmark::Options,
    merge_text: bool,
) -> PyResult<crate::serde_to_py::SerdeValueWrapper> {
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    let iterator: Box<dyn Iterator<Item = pulldown_cmark::Event>> =
        if merge_text {
            Box::new(pulldown_cmark::TextMergeStream::new(parser))
        } else {
            Box::new(parser)
        };
    Ok(crate::serde_to_py::SerdeValueWrapper(
        serde_json::to_value(iterator.collect::<Vec<_>>()).map_err(
            move |err| pyo3::exceptions::PyValueError::new_err(err.to_string()),
        )?,
    ))
}

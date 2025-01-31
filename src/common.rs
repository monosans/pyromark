pub(crate) struct PythonizeCustom;

impl<'py> pythonize::PythonizeTypes<'py> for PythonizeCustom {
    type List = pyo3::types::PyTuple;
    type Map = pyo3::types::PyDict;
    type NamedMap =
        pythonize::PythonizeUnnamedMappingAdapter<'py, pyo3::types::PyDict>;
}

pub(crate) fn build_options(options: u32) -> pulldown_cmark::Options {
    pulldown_cmark::Options::from_bits_truncate(options)
}

pub(crate) fn html(markdown: &str, options: pulldown_cmark::Options) -> String {
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    let mut html_output = String::new();
    pulldown_cmark::html::push_html(&mut html_output, parser);
    html_output
}

pub(crate) fn events(
    markdown: &str,
    options: pulldown_cmark::Options,
    merge_text: bool,
) -> Vec<pulldown_cmark::Event> {
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    if merge_text {
        pulldown_cmark::TextMergeStream::new(parser).collect()
    } else {
        parser.collect()
    }
}

pub(crate) fn events_with_range(
    markdown: &str,
    options: pulldown_cmark::Options,
) -> Vec<(pulldown_cmark::Event, std::ops::Range<usize>)> {
    pulldown_cmark::Parser::new_ext(markdown, options)
        .into_offset_iter()
        .collect()
}

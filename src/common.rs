pub struct PythonizeCustom;

impl pythonize::PythonizeTypes for PythonizeCustom {
    type List = pyo3::types::PyTuple;
    type Map = pyo3::types::PyDict;
    type NamedMap =
        pythonize::PythonizeUnnamedMappingAdapter<pyo3::types::PyDict>;
}

pub const fn build_options(options: u32) -> pulldown_cmark::Options {
    pulldown_cmark::Options::from_bits_truncate(options)
}

pub fn html(markdown: &str, options: pulldown_cmark::Options) -> String {
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    let mut html_output = String::new();
    pulldown_cmark::html::push_html(&mut html_output, parser);
    html_output
}

pub fn html_with_broken_link_callback<'a, F>(
    markdown: &'a str,
    options: pulldown_cmark::Options,
    callback: F,
) -> String
where
    F: FnMut(pulldown_cmark::BrokenLink<'a>) -> Option<(pulldown_cmark::CowStr<'a>, pulldown_cmark::CowStr<'a>)>,
{
    let parser = pulldown_cmark::Parser::new_with_broken_link_callback(
        markdown,
        options,
        Some(callback),
    );
    let mut html_output = String::new();
    pulldown_cmark::html::push_html(&mut html_output, parser);
    html_output
}

pub fn events(
    markdown: &str,
    options: pulldown_cmark::Options,
    merge_text: bool,
) -> Vec<pulldown_cmark::Event<'_>> {
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    if merge_text {
        pulldown_cmark::TextMergeStream::new(parser).collect()
    } else {
        parser.collect()
    }
}

pub fn events_with_broken_link_callback<'a, F>(
    markdown: &'a str,
    options: pulldown_cmark::Options,
    merge_text: bool,
    callback: F,
) -> Vec<pulldown_cmark::Event<'a>>
where
    F: FnMut(pulldown_cmark::BrokenLink<'a>) -> Option<(pulldown_cmark::CowStr<'a>, pulldown_cmark::CowStr<'a>)>,
{
    let parser = pulldown_cmark::Parser::new_with_broken_link_callback(
        markdown,
        options,
        Some(callback),
    );
    if merge_text {
        pulldown_cmark::TextMergeStream::new(parser).collect()
    } else {
        parser.collect()
    }
}

pub fn events_with_range(
    markdown: &str,
    options: pulldown_cmark::Options,
) -> Vec<(pulldown_cmark::Event<'_>, std::ops::Range<usize>)> {
    pulldown_cmark::Parser::new_ext(markdown, options)
        .into_offset_iter()
        .collect()
}

pub fn events_with_range_and_broken_link_callback<'a, F>(
    markdown: &'a str,
    options: pulldown_cmark::Options,
    callback: F,
) -> Vec<(pulldown_cmark::Event<'a>, std::ops::Range<usize>)>
where
    F: FnMut(pulldown_cmark::BrokenLink<'a>) -> Option<(pulldown_cmark::CowStr<'a>, pulldown_cmark::CowStr<'a>)>,
{
    pulldown_cmark::Parser::new_with_broken_link_callback(
        markdown,
        options,
        Some(callback),
    )
    .into_offset_iter()
    .collect()
}

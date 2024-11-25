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

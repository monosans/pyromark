pub const fn build_options(options: u32) -> pulldown_cmark::Options {
    pulldown_cmark::Options::from_bits_truncate(options)
}

pub fn html(markdown: &str, options: pulldown_cmark::Options) -> String {
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    let mut html_output = String::with_capacity(
        markdown.len().saturating_add(markdown.len().div_euclid(4)),
    );
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

pub fn events_with_range(
    markdown: &str,
    options: pulldown_cmark::Options,
) -> Vec<(pulldown_cmark::Event<'_>, std::ops::Range<usize>)> {
    pulldown_cmark::Parser::new_ext(markdown, options)
        .into_offset_iter()
        .collect()
}

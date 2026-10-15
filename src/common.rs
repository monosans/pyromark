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

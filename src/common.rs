use pyo3::prelude::*;

pub fn build_options(options: u32) -> PyResult<pulldown_cmark::Options> {
    pulldown_cmark::Options::from_bits(options).ok_or_else(move || {
        let unknown = options & !pulldown_cmark::Options::all().bits();
        pyo3::exceptions::PyValueError::new_err(format!(
            "options has bits pulldown-cmark does not define: {unknown:#x}"
        ))
    })
}

pub fn html(markdown: &str, options: pulldown_cmark::Options) -> String {
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    let mut html_output = String::with_capacity(
        markdown.len().saturating_add(markdown.len().div_euclid(4)),
    );
    pulldown_cmark::html::push_html(&mut html_output, parser);
    html_output
}

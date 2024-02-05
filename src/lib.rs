use pyo3::prelude::*;

/// Examples:
///     ```python
///     md = pyromark.Markdown(
///         # Optional, include the ones you want
///         extensions=(
///             pyromark.Extensions.ENABLE_TABLES
///             | pyromark.Extensions.ENABLE_FOOTNOTES
///             | pyromark.Extensions.ENABLE_STRIKETHROUGH
///             | pyromark.Extensions.ENABLE_TASKLISTS
///             | pyromark.Extensions.ENABLE_SMART_PUNCTUATION
///             | pyromark.Extensions.ENABLE_HEADING_ATTRIBUTES
///             | pyromark.Extensions.ENABLE_YAML_STYLE_METADATA_BLOCKS
///             | pyromark.Extensions.ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS
///             | pyromark.Extensions.ENABLE_OLD_FOOTNOTES
///         )
///     )
///     ```
#[pyclass(frozen, module = "pyromark._pyromark")]
struct Markdown {
    options: pulldown_cmark::Options,
}

#[pymethods]
impl Markdown {
    #[new]
    #[pyo3(signature = (*, extensions = None))]
    fn new(extensions: Option<u32>) -> Self {
        Self { options: get_options(extensions) }
    }

    /// Examples:
    ///     ```python
    ///     html = md.convert("# Hello world")
    ///     print(html)  # <h1>Hello world</h1>\n
    ///     ```
    fn convert(&self, py: Python, text: &str) -> String {
        py.allow_threads(move || {
            let parser = pulldown_cmark::Parser::new_ext(text, self.options);
            html_from_parser(parser)
        })
    }
}

/// Examples:
///     ```python
///     html = pyromark.markdown(
///         "# Hello world",
///         # Optional, include the ones you want
///         extensions=(
///             pyromark.Extensions.ENABLE_TABLES
///             | pyromark.Extensions.ENABLE_FOOTNOTES
///             | pyromark.Extensions.ENABLE_STRIKETHROUGH
///             | pyromark.Extensions.ENABLE_TASKLISTS
///             | pyromark.Extensions.ENABLE_SMART_PUNCTUATION
///             | pyromark.Extensions.ENABLE_HEADING_ATTRIBUTES
///             | pyromark.Extensions.ENABLE_YAML_STYLE_METADATA_BLOCKS
///             | pyromark.Extensions.ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS
///             | pyromark.Extensions.ENABLE_OLD_FOOTNOTES
///         )
///     )
///     print(html)  # <h1>Hello world</h1>\n
///     ```
#[pyfunction]
#[pyo3(signature = (text, *, extensions = None))]
fn markdown(py: Python, text: &str, extensions: Option<u32>) -> String {
    py.allow_threads(move || {
        let options = get_options(extensions);
        let parser = pulldown_cmark::Parser::new_ext(text, options);
        html_from_parser(parser)
    })
}

fn get_options(extensions: Option<u32>) -> pulldown_cmark::Options {
    match extensions {
        None => pulldown_cmark::Options::empty(),
        Some(value) => pulldown_cmark::Options::from_bits_truncate(value),
    }
}

fn html_from_parser(parser: pulldown_cmark::Parser) -> String {
    let mut html_output = String::new();
    pulldown_cmark::html::push_html(&mut html_output, parser);
    html_output
}

#[pymodule]
fn _pyromark(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_class::<Markdown>()?;
    m.add_function(wrap_pyfunction!(markdown, m)?)?;
    Ok(())
}

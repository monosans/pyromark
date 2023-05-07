use pulldown_cmark::{html, Options, Parser};
use pyo3::{exceptions::PyValueError, prelude::*};

#[pyclass(frozen)]
struct Markdown {
    options: Options,
}

#[pymethods]
impl Markdown {
    #[new]
    #[pyo3(signature = (*, extensions = None))]
    fn py_new(extensions: Option<Vec<&str>>) -> PyResult<Self> {
        let options = get_options(extensions)?;
        Ok(Self { options })
    }

    fn convert(&self, text: &str) -> String {
        let parser = Parser::new_ext(text, self.options);
        html_from_parser(parser)
    }
}

#[pyfunction]
#[pyo3(signature = (text, *, extensions = None))]
fn markdown(text: &str, extensions: Option<Vec<&str>>) -> PyResult<String> {
    let options = get_options(extensions)?;
    let parser = Parser::new_ext(text, options);
    Ok(html_from_parser(parser))
}

fn get_options(extensions: Option<Vec<&str>>) -> PyResult<Options> {
    let mut options = Options::empty();
    if let Some(exts) = extensions {
        for ext in exts {
            let option = match ext {
                "tables" => Options::ENABLE_TABLES,
                "footnotes" => Options::ENABLE_FOOTNOTES,
                "strikethrough" => Options::ENABLE_STRIKETHROUGH,
                "tasklists" => Options::ENABLE_TASKLISTS,
                "smart_punctuation" => Options::ENABLE_SMART_PUNCTUATION,
                "heading_attributes" => Options::ENABLE_HEADING_ATTRIBUTES,
                _ => return Err(PyValueError::new_err(format!("unknown extension: '{ext}'"))),
            };
            options.insert(option);
        }
    }
    Ok(options)
}

fn html_from_parser(parser: Parser) -> String {
    let mut html_output = String::new();
    html::push_html(&mut html_output, parser);
    html_output
}

/// Blazingly fast Markdown parser for Python.
#[pymodule]
fn pyromark(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_class::<Markdown>()?;
    m.add_function(wrap_pyfunction!(markdown, m)?)?;
    Ok(())
}

use pyo3::{prelude::*, BoundObject};

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
) -> PyResult<serde_json::Value> {
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    let iterator: Box<dyn Iterator<Item = pulldown_cmark::Event>> =
        if merge_text {
            Box::new(pulldown_cmark::TextMergeStream::new(parser))
        } else {
            Box::new(parser)
        };
    serde_json::to_value(iterator.collect::<Vec<_>>()).map_err(move |e| {
        pyo3::exceptions::PyValueError::new_err(format!(
            "failed to serialize markdown events to json: {e}"
        ))
    })
}

pub(crate) fn serde_into_py<'py>(
    py: Python<'py>,
    v: &serde_json::Value,
) -> PyResult<Bound<'py, PyAny>> {
    match v {
        serde_json::Value::Null => Ok(py.None().into_bound(py).into_any()),
        serde_json::Value::Bool(b) => {
            Ok(b.into_pyobject(py)?.into_bound().into_any())
        }
        serde_json::Value::Number(n) => {
            if let Some(u) = n.as_u64() {
                Ok(u.into_pyobject(py)?.into_any())
            } else if let Some(i) = n.as_i64() {
                Ok(i.into_pyobject(py)?.into_any())
            } else if let Some(f) = n.as_f64() {
                Ok(f.into_pyobject(py)?.into_any())
            } else {
                Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "invalid number: '{n}'"
                )))
            }
        }
        serde_json::Value::String(s) => Ok(s.into_pyobject(py)?.into_any()),
        serde_json::Value::Array(arr) => Ok(pyo3::types::PyTuple::new(
            py,
            arr.iter()
                .map(move |v| serde_into_py(py, v))
                .collect::<Result<Vec<_>, _>>()?,
        )?
        .into_any()),
        serde_json::Value::Object(obj) => Ok(
            // Return tuple instead of a dict if dict contains one key
            if obj.len() == 1 {
                let (k, v) = obj.iter().next().unwrap();
                pyo3::types::PyTuple::new(
                    py,
                    &[k.into_pyobject(py)?.into_any(), serde_into_py(py, v)?],
                )?
                .into_any()
            } else {
                let py_dict = pyo3::types::PyDict::new(py);
                for (k, v) in obj {
                    py_dict.set_item(k, serde_into_py(py, v)?)?;
                }
                py_dict.into_any()
            },
        ),
    }
}

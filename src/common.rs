use pyo3::prelude::*;

/// What one parse shares with the Python callbacks it runs: the broken link
/// callback, and the first exception any of them raised, which ends the
/// output.
pub struct Shared {
    broken_link_callback: Option<Py<PyAny>>,
    error: std::sync::OnceLock<PyErr>,
}

impl Shared {
    pub fn new(
        broken_link_callback: Option<&Bound<'_, PyAny>>,
    ) -> std::sync::Arc<Self> {
        std::sync::Arc::new(Self {
            broken_link_callback: broken_link_callback
                .map(|callback| callback.clone().unbind()),
            error: std::sync::OnceLock::new(),
        })
    }

    pub fn failed(&self) -> bool {
        self.error.get().is_some()
    }

    /// Records `error` unless an earlier one is already recorded.
    pub fn fail(&self, py: Python<'_>, error: PyErr) {
        self.error.get_or_init(move || {
            // Raised from `__next__`, a `StopIteration` would end the loop
            // silently instead of reaching the caller.
            if !error.is_instance_of::<pyo3::exceptions::PyStopIteration>(py) {
                return error;
            }
            let wrapped = pyo3::exceptions::PyRuntimeError::new_err(
                "callback raised StopIteration",
            );
            wrapped.set_cause(py, Some(error));
            wrapped
        });
    }

    /// Returns the recorded error. The parser holding the other reference
    /// must already be dropped.
    pub fn into_error(this: std::sync::Arc<Self>) -> Option<PyErr> {
        std::sync::Arc::into_inner(this)?.error.into_inner()
    }

    pub fn traverse(
        &self,
        visit: pyo3::pyclass::PyVisit<'_>,
    ) -> Result<(), pyo3::pyclass::PyTraverseError> {
        visit.call(&self.broken_link_callback)
    }
}

pub struct BrokenLinkCallback(std::sync::Arc<Shared>);

impl<'input> pulldown_cmark::BrokenLinkCallback<'input> for BrokenLinkCallback {
    fn handle_broken_link(
        &mut self,
        link: pulldown_cmark::BrokenLink<'input>,
    ) -> Option<(pulldown_cmark::CowStr<'input>, pulldown_cmark::CowStr<'input>)>
    {
        let shared = &*self.0;
        let callback = shared.broken_link_callback.as_ref()?;
        if shared.failed() {
            return None;
        }
        Python::attach(move |py| {
            call_broken_link_callback(callback.bind(py), &link).unwrap_or_else(
                move |err| {
                    shared.fail(py, err);
                    None
                },
            )
        })
    }
}

pub type Parser<'input> = pulldown_cmark::Parser<'input, BrokenLinkCallback>;

pub fn parser<'input>(
    markdown: &'input str,
    options: pulldown_cmark::Options,
    shared: &std::sync::Arc<Shared>,
) -> Parser<'input> {
    let callback = shared
        .broken_link_callback
        .is_some()
        .then(|| BrokenLinkCallback(std::sync::Arc::clone(shared)));
    Parser::new_with_broken_link_callback(markdown, options, callback)
}

/// Re-raises `err` with `expected` prepended to its message.
pub fn callback_error(py: Python<'_>, expected: &str, err: PyErr) -> PyErr {
    let error = PyErr::from_type(
        err.get_type(py),
        format!("{expected}: {}", err.value(py)),
    );
    error.set_cause(py, Some(err));
    error
}

fn call_broken_link_callback<'input>(
    callback: &Bound<'_, PyAny>,
    link: &pulldown_cmark::BrokenLink<'_>,
) -> PyResult<
    Option<(pulldown_cmark::CowStr<'input>, pulldown_cmark::CowStr<'input>)>,
> {
    let py = callback.py();
    let broken_link = pyo3::types::PyDict::new(py);
    broken_link.set_item(
        pyo3::intern!(py, "span"),
        crate::convert::range(py, &link.span)?,
    )?;
    broken_link.set_item(
        pyo3::intern!(py, "link_type"),
        crate::convert::link_type(py, link.link_type)?,
    )?;
    broken_link.set_item(pyo3::intern!(py, "reference"), &*link.reference)?;
    let resolved = callback
        .call1((broken_link,))?
        .extract::<Option<(String, String)>>()
        .map_err(move |err| {
            callback_error(
                py,
                "broken link callback must return a (destination_url, title) \
                 tuple of str, or None",
                err,
            )
        })?;
    Ok(resolved.map(|(dest_url, title)| (dest_url.into(), title.into())))
}

pub fn build_options(options: u32) -> PyResult<pulldown_cmark::Options> {
    pulldown_cmark::Options::from_bits(options).ok_or_else(move || {
        let unknown = options & !pulldown_cmark::Options::all().bits();
        pyo3::exceptions::PyValueError::new_err(format!(
            "options has bits pulldown-cmark does not define: {unknown:#x}"
        ))
    })
}

pub fn check_broken_link_callback(
    broken_link_callback: Option<&Bound<'_, PyAny>>,
) -> PyResult<()> {
    if broken_link_callback.is_none_or(Bound::is_callable) {
        return Ok(());
    }
    Err(pyo3::exceptions::PyTypeError::new_err(
        "broken_link_callback must be callable",
    ))
}

pub fn html(
    py: Python<'_>,
    markdown: &str,
    options: pulldown_cmark::Options,
    broken_link_callback: Option<&Bound<'_, PyAny>>,
) -> PyResult<String> {
    let shared = Shared::new(broken_link_callback);
    let output = py.detach(|| {
        let mut output = String::with_capacity(
            markdown.len().saturating_add(markdown.len().div_euclid(4)),
        );
        let events =
            parser(markdown, options, &shared).take_while(|_| !shared.failed());
        pulldown_cmark::html::push_html(&mut output, events);
        output
    });
    Shared::into_error(shared).map_or(Ok(output), Err)
}

pub fn reference_definitions<'py>(
    py: Python<'py>,
    markdown: &str,
    options: pulldown_cmark::Options,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let parser =
        py.detach(move || pulldown_cmark::Parser::new_ext(markdown, options));
    crate::convert::reference_definitions(py, parser.reference_definitions())
}

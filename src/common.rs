use pyo3::prelude::*;

const WRITE_BUFFER_CAPACITY: usize = 64 * 1024;

/// What one parse shares with the Python callbacks it runs: the broken link
/// callback, and the first exception any of them raised, which ends the
/// output.
pub struct Shared {
    broken_link_callback: Option<Py<PyAny>>,
    error: std::sync::OnceLock<PyErr>,
}

impl Shared {
    pub fn new(broken_link_callback: Option<&Bound<'_, PyAny>>) -> std::sync::Arc<Self> {
        std::sync::Arc::new(Self {
            broken_link_callback: broken_link_callback.map(|callback| callback.clone().unbind()),
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
            let wrapped =
                pyo3::exceptions::PyRuntimeError::new_err("callback raised StopIteration");
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
    ) -> Option<(pulldown_cmark::CowStr<'input>, pulldown_cmark::CowStr<'input>)> {
        let shared = &*self.0;
        let callback = shared.broken_link_callback.as_ref()?;
        if shared.failed() {
            return None;
        }
        Python::attach(move |py| {
            call_broken_link_callback(callback.bind(py), &link).unwrap_or_else(move |err| {
                shared.fail(py, err);
                None
            })
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

/// Copies `value`: inline if it is short enough, else into one allocation of
/// the exact size.
pub fn cow_str(value: &str) -> pulldown_cmark::CowStr<'static> {
    pulldown_cmark::InlineStr::try_from(value).map_or_else(
        move |_| pulldown_cmark::CowStr::Boxed(value.into()),
        pulldown_cmark::CowStr::Inlined,
    )
}

/// Re-raises `err` with `expected` prepended to its message.
pub fn callback_error(py: Python<'_>, expected: &str, err: PyErr) -> PyErr {
    let error = PyErr::from_type(err.get_type(py), format!("{expected}: {}", err.value(py)));
    error.set_cause(py, Some(err));
    error
}

fn call_broken_link_callback<'input>(
    callback: &Bound<'_, PyAny>,
    link: &pulldown_cmark::BrokenLink<'_>,
) -> PyResult<Option<(pulldown_cmark::CowStr<'input>, pulldown_cmark::CowStr<'input>)>> {
    let py = callback.py();
    let broken_link = pyo3::types::PyDict::new(py);
    broken_link.set_item(pyo3::intern!(py, "span"), crate::convert::range(py, &link.span)?)?;
    broken_link
        .set_item(pyo3::intern!(py, "link_type"), crate::convert::link_type(py, link.link_type)?)?;
    broken_link.set_item(pyo3::intern!(py, "reference"), &*link.reference)?;
    let resolved = callback
        .call1((broken_link,))?
        .extract::<Option<(pyo3::pybacked::PyBackedStr, pyo3::pybacked::PyBackedStr)>>()
        .map_err(move |err| {
            callback_error(
                py,
                "broken link callback must return a (destination_url, title) tuple of str, or None",
                err,
            )
        })?;
    Ok(resolved.map(|(dest_url, title)| (cow_str(&dest_url), cow_str(&title))))
}

pub fn build_options(options: u32) -> PyResult<pulldown_cmark::Options> {
    pulldown_cmark::Options::from_bits(options).ok_or_else(move || {
        let unknown = options & !pulldown_cmark::Options::all().bits();
        pyo3::exceptions::PyValueError::new_err(format!(
            "options has bits pulldown-cmark does not define: {unknown:#x}"
        ))
    })
}

pub fn check_broken_link_callback(broken_link_callback: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
    if broken_link_callback.is_none_or(Bound::is_callable) {
        return Ok(());
    }
    Err(pyo3::exceptions::PyTypeError::new_err("broken_link_callback must be callable"))
}

/// The events `html` and `write_html` render: the parser's, with code blocks
/// highlighted, ending early once a callback has raised.
struct Render<'a, 'input> {
    parser: Parser<'input>,
    shared: &'a Shared,
    highlighter: Option<&'a crate::highlight::Highlighter>,
    pending: Vec<pulldown_cmark::Event<'input>>,
    /// The text of the code block being highlighted, kept between blocks to
    /// reuse its allocation.
    code: String,
}

#[expect(clippy::missing_trait_methods)]
impl<'input> Iterator for Render<'_, 'input> {
    type Item = pulldown_cmark::Event<'input>;

    fn next(&mut self) -> Option<Self::Item> {
        if let Some(event) = self.pending.pop() {
            return Some(event);
        }
        let event = self.parser.next()?;
        if self.shared.failed() {
            return None;
        }
        let Some(highlighter) = self.highlighter else {
            return Some(event);
        };
        let pulldown_cmark::Event::Start(pulldown_cmark::Tag::CodeBlock(kind)) = &event else {
            return Some(event);
        };
        self.code.clear();
        // A code block holds nothing but text, up to its end, which this
        // consumes.
        while let Some(pulldown_cmark::Event::Text(text)) = self.parser.next() {
            self.code.push_str(&text);
        }
        let language = match kind {
            pulldown_cmark::CodeBlockKind::Indented => None,
            pulldown_cmark::CodeBlockKind::Fenced(info) => info.split_whitespace().next(),
        };
        if let Some(html) = highlighter.highlight(language, &self.code, self.shared) {
            return Some(pulldown_cmark::Event::Html(html));
        }
        if self.shared.failed() {
            return None;
        }
        self.pending.push(pulldown_cmark::Event::End(pulldown_cmark::TagEnd::CodeBlock));
        self.pending.push(pulldown_cmark::Event::Text(core::mem::take(&mut self.code).into()));
        Some(event)
    }
}

/// Runs `sink` over the rendered events with the interpreter detached, then
/// raises whatever a callback raised.
fn render<'input, R, S>(
    py: Python<'_>,
    markdown: &'input str,
    options: pulldown_cmark::Options,
    broken_link_callback: Option<&Bound<'_, PyAny>>,
    highlighter: Option<&crate::highlight::Highlighter>,
    sink: S,
) -> PyResult<R>
where
    R: Send,
    S: FnOnce(&mut dyn Iterator<Item = pulldown_cmark::Event<'input>>, &Shared) -> R + Send,
{
    let shared = Shared::new(broken_link_callback);
    let output = py.detach(|| {
        let mut events = Render {
            parser: parser(markdown, options, &shared),
            shared: &shared,
            highlighter,
            pending: Vec::new(),
            code: String::new(),
        };
        sink(&mut events, &shared)
    });
    Shared::into_error(shared).map_or(Ok(output), Err)
}

/// Room for the HTML of `markdown`. Over thousands of READMEs and their
/// paragraphs, it fits the HTML of 99% of them.
const fn html_capacity(markdown: &str) -> usize {
    markdown.len().saturating_add(markdown.len().div_euclid(2)).saturating_add(32)
}

pub fn html(
    py: Python<'_>,
    markdown: &str,
    options: pulldown_cmark::Options,
    broken_link_callback: Option<&Bound<'_, PyAny>>,
    highlighter: Option<&crate::highlight::Highlighter>,
) -> PyResult<String> {
    let mut output = String::with_capacity(html_capacity(markdown));
    render(py, markdown, options, broken_link_callback, highlighter, |events, _| {
        pulldown_cmark::html::push_html(&mut output, events);
    })?;
    Ok(output)
}

struct PyWriter<'a> {
    file: &'a Py<PyAny>,
    shared: &'a Shared,
}

#[expect(clippy::missing_trait_methods)]
impl std::io::Write for PyWriter<'_> {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        if self.shared.failed() {
            return Err(std::io::Error::other("a callback raised"));
        }
        Python::attach(move |py| {
            call_write(self.file.bind(py), buf).map_err(move |err| {
                self.shared.fail(py, err);
                std::io::Error::other("file.write() raised")
            })
        })
    }

    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}

fn call_write(file: &Bound<'_, PyAny>, buf: &[u8]) -> PyResult<usize> {
    let py = file.py();
    let bytes = pyo3::types::PyBytes::new(py, buf);
    let written = file.call_method1(pyo3::intern!(py, "write"), (bytes,))?;
    // Plenty of file-like objects return None after writing everything.
    if written.is_none() {
        return Ok(buf.len());
    }
    match written.extract::<usize>()? {
        0 => Err(pyo3::exceptions::PyOSError::new_err("file.write() wrote nothing")),
        written => Ok(written.min(buf.len())),
    }
}

pub fn write_html(
    py: Python<'_>,
    markdown: &str,
    file: &Bound<'_, PyAny>,
    options: pulldown_cmark::Options,
    broken_link_callback: Option<&Bound<'_, PyAny>>,
    highlighter: Option<&crate::highlight::Highlighter>,
) -> PyResult<()> {
    let file = file.as_unbound();
    render(py, markdown, options, broken_link_callback, highlighter, |events, shared| {
        // Small documents need no more than their HTML.
        let mut writer = std::io::BufWriter::with_capacity(
            html_capacity(markdown).min(WRITE_BUFFER_CAPACITY),
            PyWriter { file, shared },
        );
        pulldown_cmark::html::write_html_io(&mut writer, events)?;
        std::io::Write::flush(&mut writer)
    })?
    .map_err(Into::into)
}

pub fn reference_definitions<'py>(
    py: Python<'py>,
    markdown: &str,
    options: pulldown_cmark::Options,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let parser = py.detach(move || pulldown_cmark::Parser::new_ext(markdown, options));
    crate::convert::reference_definitions(py, parser.reference_definitions())
}

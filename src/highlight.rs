use pyo3::prelude::*;

static SYNTAXES: std::sync::LazyLock<syntect::parsing::SyntaxSet> =
    std::sync::LazyLock::new(two_face::syntax::extra_newlines);

static THEMES: std::sync::LazyLock<syntect::highlighting::ThemeSet> =
    std::sync::LazyLock::new(syntect::highlighting::ThemeSet::load_defaults);

/// Common fence languages that no syntax lists as its name or extension,
/// and the token of the syntax they mean.
const ALIASES: [(&str, &str); 9] = [
    ("batch", "bat"),
    ("csharp", "cs"),
    ("docker", "dockerfile"),
    ("fsharp", "f#"),
    ("jsonc", "json"),
    ("objc", "objective-c"),
    ("pwsh", "ps1"),
    ("python3", "py"),
    ("shell", "bash"),
];

fn find_syntax(
    language: &str,
) -> Option<&'static syntect::parsing::SyntaxReference> {
    let token = ALIASES
        .iter()
        .find(|(alias, _)| alias.eq_ignore_ascii_case(language))
        .map_or(language, |(_, token)| token);
    SYNTAXES.find_syntax_by_token(token)
}

pub enum Highlighter {
    Theme(&'static syntect::highlighting::Theme),
    Callback(Py<PyAny>),
}

impl Highlighter {
    pub const fn callback(&self) -> Option<&Py<PyAny>> {
        match self {
            Self::Theme(_) => None,
            Self::Callback(callback) => Some(callback),
        }
    }

    /// Returns the block's HTML, or `None` to render it unhighlighted. A
    /// callback that raises records the error in `shared`.
    pub fn highlight(
        &self,
        language: Option<&str>,
        code: &str,
        shared: &crate::common::Shared,
    ) -> Option<String> {
        match self {
            Self::Theme(theme) => {
                let syntax = language
                    .and_then(find_syntax)
                    .unwrap_or_else(|| SYNTAXES.find_syntax_plain_text());
                syntect::html::highlighted_html_for_string(
                    code, &SYNTAXES, syntax, theme,
                )
                .ok()
            }
            Self::Callback(callback) => Python::attach(move |py| {
                call_highlight_callback(callback.bind(py), language, code)
                    .unwrap_or_else(move |err| {
                        shared.fail(py, err);
                        None
                    })
            }),
        }
    }
}

pub fn build_highlighter(
    highlight: Option<&Bound<'_, PyAny>>,
) -> PyResult<Option<Highlighter>> {
    let Some(highlight) = highlight else {
        return Ok(None);
    };
    if let Ok(name) = highlight.cast::<pyo3::types::PyString>() {
        let name = name.to_str()?;
        let themes = highlight.py().detach(|| &*THEMES);
        let theme = themes.themes.get(name).ok_or_else(move || {
            pyo3::exceptions::PyValueError::new_err(format!(
                "unknown highlighting theme {name:?}, expected one of {:?}",
                themes.themes.keys().collect::<Vec<_>>()
            ))
        })?;
        return Ok(Some(Highlighter::Theme(theme)));
    }
    if highlight.is_callable() {
        return Ok(Some(Highlighter::Callback(highlight.clone().unbind())));
    }
    Err(pyo3::exceptions::PyTypeError::new_err(
        "highlight must be a pyromark.Theme or a callable",
    ))
}

fn call_highlight_callback(
    callback: &Bound<'_, PyAny>,
    language: Option<&str>,
    code: &str,
) -> PyResult<Option<String>> {
    callback.call1((language, code))?.extract::<Option<String>>().map_err(
        move |err| {
            crate::common::callback_error(
                callback.py(),
                "highlight callback must return the block's HTML as str, or \
                 None to leave the block alone",
                err,
            )
        },
    )
}

use syntect::html::highlighted_html_for_string;
use syntect::parsing::SyntaxSet;
use syntect::highlighting::ThemeSet;

fn escape_html(text: &str) -> String {
    text.chars()
        .map(|c| match c {
            '&' => "&amp;".to_string(),
            '<' => "&lt;".to_string(),
            '>' => "&gt;".to_string(),
            '"' => "&quot;".to_string(),
            '\'' => "&#x27;".to_string(),
            _ => c.to_string(),
        })
        .collect()
}

pub struct PythonizeCustom;

impl<'py> pythonize::PythonizeTypes<'py> for PythonizeCustom {
    type List = pyo3::types::PyTuple;
    type Map = pyo3::types::PyDict;
    type NamedMap =
        pythonize::PythonizeUnnamedMappingAdapter<'py, pyo3::types::PyDict>;
}

pub const fn build_options(options: u32) -> pulldown_cmark::Options {
    pulldown_cmark::Options::from_bits_truncate(options)
}

pub fn html(markdown: &str, options: pulldown_cmark::Options) -> String {
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    let mut html_output = String::new();
    pulldown_cmark::html::push_html(&mut html_output, parser);
    html_output
}

pub fn html_with_syntax_highlighting(
    markdown: &str, 
    options: pulldown_cmark::Options,
    _syntax_theme: Option<&str>
) -> String {
    let syntax_set = SyntaxSet::load_defaults_newlines();
    let theme_set = ThemeSet::load_defaults();
    let theme = &theme_set.themes["base16-ocean.dark"];
    
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    let events: Vec<_> = parser.collect();
    
    // Process events to find and highlight code blocks
    let mut highlighted_events = Vec::new();
    let mut i = 0;
    
    while i < events.len() {
        match &events[i] {
            pulldown_cmark::Event::Start(pulldown_cmark::Tag::CodeBlock(pulldown_cmark::CodeBlockKind::Fenced(lang))) => {
                // Skip the original start tag - we'll create our own HTML
                i += 1;
                
                // Collect all text content until we hit the end tag
                let mut code_content = String::new();
                while i < events.len() {
                    match &events[i] {
                        pulldown_cmark::Event::Text(text) => {
                            code_content.push_str(text);
                            i += 1;
                        }
                        pulldown_cmark::Event::End(pulldown_cmark::TagEnd::CodeBlock) => {
                            // Found the end tag, break out
                            i += 1; // Skip the end tag
                            break;
                        }
                        _ => {
                            // Skip any other events between start and end
                            i += 1;
                        }
                    }
                }
                
                // Apply syntax highlighting
                let highlighted_html = if !lang.is_empty() {
                    if let Some(syntax) = syntax_set.find_syntax_by_token(lang) {
                        match highlighted_html_for_string(&code_content, &syntax_set, syntax, theme) {
                            Ok(html) => {
                                // Remove the outer <pre> tags from syntect's output and add our own structure
                                let html_trimmed = html
                                    .trim_start_matches("<pre style=\"background-color:#2b303b;\">\n")
                                    .trim_end_matches("\n</pre>\n")
                                    .trim_end_matches("</pre>\n")
                                    .trim_end_matches("\n</pre>")
                                    .trim_end_matches("</pre>");
                                format!("<pre style=\"background-color:#2b303b;\"><code class=\"language-{}\">{}</code></pre>", 
                                       lang, html_trimmed)
                            },
                            Err(_) => format!("<pre><code class=\"language-{}\">{}</code></pre>", 
                                            lang, escape_html(&code_content))
                        }
                    } else {
                        format!("<pre><code class=\"language-{}\">{}</code></pre>", 
                                lang, escape_html(&code_content))
                    }
                } else {
                    format!("<pre><code>{}</code></pre>", 
                            escape_html(&code_content))
                };
                
                // Add as raw HTML - this replaces the entire code block
                highlighted_events.push(pulldown_cmark::Event::Html(highlighted_html.into()));
            }
            _ => {
                // For all other events, just copy them
                highlighted_events.push(events[i].clone());
                i += 1;
            }
        }
    }
    
    let mut html_output = String::new();
    pulldown_cmark::html::push_html(&mut html_output, highlighted_events.into_iter());
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

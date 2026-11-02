use pyo3::prelude::*;

fn name<'py>(value: &Bound<'py, pyo3::types::PyString>) -> Bound<'py, PyAny> {
    value.clone().into_any()
}

fn tagged<'py>(
    py: Python<'py>,
    tag: &Bound<'py, pyo3::types::PyString>,
    value: impl IntoPyObject<'py>,
) -> PyResult<Bound<'py, PyAny>> {
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(tag, value)?;
    Ok(dict.into_any())
}

fn heading_level(
    py: Python<'_>,
    level: pulldown_cmark::HeadingLevel,
) -> Bound<'_, PyAny> {
    name(match level {
        pulldown_cmark::HeadingLevel::H1 => pyo3::intern!(py, "H1"),
        pulldown_cmark::HeadingLevel::H2 => pyo3::intern!(py, "H2"),
        pulldown_cmark::HeadingLevel::H3 => pyo3::intern!(py, "H3"),
        pulldown_cmark::HeadingLevel::H4 => pyo3::intern!(py, "H4"),
        pulldown_cmark::HeadingLevel::H5 => pyo3::intern!(py, "H5"),
        pulldown_cmark::HeadingLevel::H6 => pyo3::intern!(py, "H6"),
    })
}

fn block_quote_kind(
    py: Python<'_>,
    kind: pulldown_cmark::BlockQuoteKind,
) -> Bound<'_, PyAny> {
    name(match kind {
        pulldown_cmark::BlockQuoteKind::Note => pyo3::intern!(py, "Note"),
        pulldown_cmark::BlockQuoteKind::Tip => pyo3::intern!(py, "Tip"),
        pulldown_cmark::BlockQuoteKind::Important => {
            pyo3::intern!(py, "Important")
        }
        pulldown_cmark::BlockQuoteKind::Warning => pyo3::intern!(py, "Warning"),
        pulldown_cmark::BlockQuoteKind::Caution => pyo3::intern!(py, "Caution"),
    })
}

fn metadata_block_kind(
    py: Python<'_>,
    kind: pulldown_cmark::MetadataBlockKind,
) -> Bound<'_, PyAny> {
    name(match kind {
        pulldown_cmark::MetadataBlockKind::YamlStyle => {
            pyo3::intern!(py, "YamlStyle")
        }
        pulldown_cmark::MetadataBlockKind::PlusesStyle => {
            pyo3::intern!(py, "PlusesStyle")
        }
    })
}

fn alignment(
    py: Python<'_>,
    alignment: pulldown_cmark::Alignment,
) -> Bound<'_, PyAny> {
    name(match alignment {
        pulldown_cmark::Alignment::None => pyo3::intern!(py, "None"),
        pulldown_cmark::Alignment::Left => pyo3::intern!(py, "Left"),
        pulldown_cmark::Alignment::Center => pyo3::intern!(py, "Center"),
        pulldown_cmark::Alignment::Right => pyo3::intern!(py, "Right"),
    })
}

fn code_block_kind<'py>(
    py: Python<'py>,
    kind: &pulldown_cmark::CodeBlockKind<'_>,
) -> PyResult<Bound<'py, PyAny>> {
    match kind {
        pulldown_cmark::CodeBlockKind::Indented => {
            Ok(name(pyo3::intern!(py, "Indented")))
        }
        pulldown_cmark::CodeBlockKind::Fenced(language) => {
            tagged(py, pyo3::intern!(py, "Fenced"), &**language)
        }
    }
}

pub fn link_type(
    py: Python<'_>,
    link_type: pulldown_cmark::LinkType,
) -> PyResult<Bound<'_, PyAny>> {
    Ok(name(match link_type {
        pulldown_cmark::LinkType::Inline => pyo3::intern!(py, "Inline"),
        pulldown_cmark::LinkType::Reference => pyo3::intern!(py, "Reference"),
        pulldown_cmark::LinkType::ReferenceUnknown => {
            pyo3::intern!(py, "ReferenceUnknown")
        }
        pulldown_cmark::LinkType::Collapsed => pyo3::intern!(py, "Collapsed"),
        pulldown_cmark::LinkType::CollapsedUnknown => {
            pyo3::intern!(py, "CollapsedUnknown")
        }
        pulldown_cmark::LinkType::Shortcut => pyo3::intern!(py, "Shortcut"),
        pulldown_cmark::LinkType::ShortcutUnknown => {
            pyo3::intern!(py, "ShortcutUnknown")
        }
        pulldown_cmark::LinkType::Autolink => pyo3::intern!(py, "Autolink"),
        pulldown_cmark::LinkType::Email => pyo3::intern!(py, "Email"),
        pulldown_cmark::LinkType::WikiLink { has_pothole } => {
            let data = pyo3::types::PyDict::new(py);
            data.set_item(pyo3::intern!(py, "has_pothole"), has_pothole)?;
            return tagged(py, pyo3::intern!(py, "WikiLink"), data);
        }
    }))
}

fn link_data<'py>(
    py: Python<'py>,
    link: pulldown_cmark::LinkType,
    dest_url: &str,
    title: &str,
    id: &str,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let data = pyo3::types::PyDict::new(py);
    data.set_item(pyo3::intern!(py, "link_type"), link_type(py, link)?)?;
    data.set_item(pyo3::intern!(py, "dest_url"), dest_url)?;
    data.set_item(pyo3::intern!(py, "title"), title)?;
    data.set_item(pyo3::intern!(py, "id"), id)?;
    Ok(data)
}

fn tag<'py>(
    py: Python<'py>,
    tag: &pulldown_cmark::Tag<'_>,
) -> PyResult<Bound<'py, PyAny>> {
    match tag {
        pulldown_cmark::Tag::Paragraph => {
            Ok(name(pyo3::intern!(py, "Paragraph")))
        }
        pulldown_cmark::Tag::Heading { level, id, classes, attrs } => {
            let classes = pyo3::types::PyTuple::new(
                py,
                classes.iter().map(|class| &**class),
            )?;
            let attrs =
                attrs.iter().map(|(key, value)| (&**key, value.as_deref()));
            let attrs = pyo3::types::PyTuple::new(py, attrs)?;
            let data = pyo3::types::PyDict::new(py);
            data.set_item(
                pyo3::intern!(py, "level"),
                heading_level(py, *level),
            )?;
            data.set_item(pyo3::intern!(py, "id"), id.as_deref())?;
            data.set_item(pyo3::intern!(py, "classes"), classes)?;
            data.set_item(pyo3::intern!(py, "attrs"), attrs)?;
            tagged(py, pyo3::intern!(py, "Heading"), data)
        }
        pulldown_cmark::Tag::BlockQuote(kind) => tagged(
            py,
            pyo3::intern!(py, "BlockQuote"),
            kind.map(move |kind| block_quote_kind(py, kind)),
        ),
        pulldown_cmark::Tag::CodeBlock(kind) => tagged(
            py,
            pyo3::intern!(py, "CodeBlock"),
            code_block_kind(py, kind)?,
        ),
        pulldown_cmark::Tag::HtmlBlock => {
            Ok(name(pyo3::intern!(py, "HtmlBlock")))
        }
        pulldown_cmark::Tag::List(first_item_number) => {
            tagged(py, pyo3::intern!(py, "List"), *first_item_number)
        }
        pulldown_cmark::Tag::Item => Ok(name(pyo3::intern!(py, "Item"))),
        pulldown_cmark::Tag::FootnoteDefinition(label) => {
            tagged(py, pyo3::intern!(py, "FootnoteDefinition"), &**label)
        }
        pulldown_cmark::Tag::DefinitionList => {
            Ok(name(pyo3::intern!(py, "DefinitionList")))
        }
        pulldown_cmark::Tag::DefinitionListTitle => {
            Ok(name(pyo3::intern!(py, "DefinitionListTitle")))
        }
        pulldown_cmark::Tag::DefinitionListDefinition => {
            Ok(name(pyo3::intern!(py, "DefinitionListDefinition")))
        }
        pulldown_cmark::Tag::Table(alignments) => tagged(
            py,
            pyo3::intern!(py, "Table"),
            pyo3::types::PyTuple::new(
                py,
                alignments.iter().map(|&column| alignment(py, column)),
            )?,
        ),
        pulldown_cmark::Tag::TableHead => {
            Ok(name(pyo3::intern!(py, "TableHead")))
        }
        pulldown_cmark::Tag::TableRow => {
            Ok(name(pyo3::intern!(py, "TableRow")))
        }
        pulldown_cmark::Tag::TableCell => {
            Ok(name(pyo3::intern!(py, "TableCell")))
        }
        pulldown_cmark::Tag::Emphasis => {
            Ok(name(pyo3::intern!(py, "Emphasis")))
        }
        pulldown_cmark::Tag::Strong => Ok(name(pyo3::intern!(py, "Strong"))),
        pulldown_cmark::Tag::Strikethrough => {
            Ok(name(pyo3::intern!(py, "Strikethrough")))
        }
        pulldown_cmark::Tag::Superscript => {
            Ok(name(pyo3::intern!(py, "Superscript")))
        }
        pulldown_cmark::Tag::Subscript => {
            Ok(name(pyo3::intern!(py, "Subscript")))
        }
        pulldown_cmark::Tag::Link { link_type: link, dest_url, title, id } => {
            tagged(
                py,
                pyo3::intern!(py, "Link"),
                link_data(py, *link, dest_url, title, id)?,
            )
        }
        pulldown_cmark::Tag::Image { link_type: link, dest_url, title, id } => {
            tagged(
                py,
                pyo3::intern!(py, "Image"),
                link_data(py, *link, dest_url, title, id)?,
            )
        }
        pulldown_cmark::Tag::MetadataBlock(kind) => tagged(
            py,
            pyo3::intern!(py, "MetadataBlock"),
            metadata_block_kind(py, *kind),
        ),
    }
}

fn tag_end(
    py: Python<'_>,
    tag_end: pulldown_cmark::TagEnd,
) -> PyResult<Bound<'_, PyAny>> {
    Ok(name(match tag_end {
        pulldown_cmark::TagEnd::Paragraph => pyo3::intern!(py, "Paragraph"),
        pulldown_cmark::TagEnd::Heading(level) => {
            return tagged(
                py,
                pyo3::intern!(py, "Heading"),
                heading_level(py, level),
            );
        }
        pulldown_cmark::TagEnd::BlockQuote(kind) => {
            return tagged(
                py,
                pyo3::intern!(py, "BlockQuote"),
                kind.map(move |kind| block_quote_kind(py, kind)),
            );
        }
        pulldown_cmark::TagEnd::CodeBlock => pyo3::intern!(py, "CodeBlock"),
        pulldown_cmark::TagEnd::HtmlBlock => pyo3::intern!(py, "HtmlBlock"),
        pulldown_cmark::TagEnd::List(ordered) => {
            return tagged(py, pyo3::intern!(py, "List"), ordered);
        }
        pulldown_cmark::TagEnd::Item => pyo3::intern!(py, "Item"),
        pulldown_cmark::TagEnd::FootnoteDefinition => {
            pyo3::intern!(py, "FootnoteDefinition")
        }
        pulldown_cmark::TagEnd::DefinitionList => {
            pyo3::intern!(py, "DefinitionList")
        }
        pulldown_cmark::TagEnd::DefinitionListTitle => {
            pyo3::intern!(py, "DefinitionListTitle")
        }
        pulldown_cmark::TagEnd::DefinitionListDefinition => {
            pyo3::intern!(py, "DefinitionListDefinition")
        }
        pulldown_cmark::TagEnd::Table => pyo3::intern!(py, "Table"),
        pulldown_cmark::TagEnd::TableHead => pyo3::intern!(py, "TableHead"),
        pulldown_cmark::TagEnd::TableRow => pyo3::intern!(py, "TableRow"),
        pulldown_cmark::TagEnd::TableCell => pyo3::intern!(py, "TableCell"),
        pulldown_cmark::TagEnd::Emphasis => pyo3::intern!(py, "Emphasis"),
        pulldown_cmark::TagEnd::Strong => pyo3::intern!(py, "Strong"),
        pulldown_cmark::TagEnd::Strikethrough => {
            pyo3::intern!(py, "Strikethrough")
        }
        pulldown_cmark::TagEnd::Superscript => pyo3::intern!(py, "Superscript"),
        pulldown_cmark::TagEnd::Subscript => pyo3::intern!(py, "Subscript"),
        pulldown_cmark::TagEnd::Link => pyo3::intern!(py, "Link"),
        pulldown_cmark::TagEnd::Image => pyo3::intern!(py, "Image"),
        pulldown_cmark::TagEnd::MetadataBlock(kind) => {
            return tagged(
                py,
                pyo3::intern!(py, "MetadataBlock"),
                metadata_block_kind(py, kind),
            );
        }
    }))
}

pub fn event<'py>(
    py: Python<'py>,
    event: &pulldown_cmark::Event<'_>,
) -> PyResult<Bound<'py, PyAny>> {
    match event {
        pulldown_cmark::Event::Start(start) => {
            tagged(py, pyo3::intern!(py, "Start"), tag(py, start)?)
        }
        pulldown_cmark::Event::End(end) => {
            tagged(py, pyo3::intern!(py, "End"), tag_end(py, *end)?)
        }
        pulldown_cmark::Event::Text(text) => {
            tagged(py, pyo3::intern!(py, "Text"), &**text)
        }
        pulldown_cmark::Event::Code(code) => {
            tagged(py, pyo3::intern!(py, "Code"), &**code)
        }
        pulldown_cmark::Event::InlineMath(math) => {
            tagged(py, pyo3::intern!(py, "InlineMath"), &**math)
        }
        pulldown_cmark::Event::DisplayMath(math) => {
            tagged(py, pyo3::intern!(py, "DisplayMath"), &**math)
        }
        pulldown_cmark::Event::Html(html) => {
            tagged(py, pyo3::intern!(py, "Html"), &**html)
        }
        pulldown_cmark::Event::InlineHtml(html) => {
            tagged(py, pyo3::intern!(py, "InlineHtml"), &**html)
        }
        pulldown_cmark::Event::FootnoteReference(label) => {
            tagged(py, pyo3::intern!(py, "FootnoteReference"), &**label)
        }
        pulldown_cmark::Event::SoftBreak => {
            Ok(name(pyo3::intern!(py, "SoftBreak")))
        }
        pulldown_cmark::Event::HardBreak => {
            Ok(name(pyo3::intern!(py, "HardBreak")))
        }
        pulldown_cmark::Event::Rule => Ok(name(pyo3::intern!(py, "Rule"))),
        pulldown_cmark::Event::TaskListMarker(checked) => {
            tagged(py, pyo3::intern!(py, "TaskListMarker"), *checked)
        }
    }
}

pub fn range<'py>(
    py: Python<'py>,
    range: &core::ops::Range<usize>,
) -> PyResult<Bound<'py, PyAny>> {
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(pyo3::intern!(py, "start"), range.start)?;
    dict.set_item(pyo3::intern!(py, "end"), range.end)?;
    Ok(dict.into_any())
}

pub fn event_with_range<'py>(
    py: Python<'py>,
    event_with_range: &(pulldown_cmark::Event<'_>, core::ops::Range<usize>),
) -> PyResult<Bound<'py, PyAny>> {
    let (parsed, span) = event_with_range;
    Ok(pyo3::types::PyTuple::new(py, [event(py, parsed)?, range(py, span)?])?
        .into_any())
}

pub fn reference_definitions<'py>(
    py: Python<'py>,
    definitions: &pulldown_cmark::RefDefs<'_>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mut definitions = definitions.iter().collect::<Vec<_>>();
    definitions.sort_unstable_by_key(|(_, definition)| definition.span.start);
    let dict = pyo3::types::PyDict::new(py);
    for (label, definition) in definitions {
        let value = pyo3::types::PyDict::new(py);
        value.set_item(pyo3::intern!(py, "dest"), &*definition.dest)?;
        value.set_item(
            pyo3::intern!(py, "title"),
            definition.title.as_deref(),
        )?;
        value.set_item(
            pyo3::intern!(py, "span"),
            range(py, &definition.span)?,
        )?;
        dict.set_item(label, value)?;
    }
    Ok(dict)
}

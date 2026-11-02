//! The Rust side of `pyromark`: Markdown parsing and HTML rendering with
//! `pulldown-cmark`, exposed to Python as the `pyromark._pyromark` module.

mod class_api;
mod common;
mod convert;
mod function_api;
mod highlight;
mod lazy_api;
use pyo3::prelude::*;

#[pymodule]
mod _pyromark {
    #[pymodule_export]
    #[expect(nonstandard_style)]
    const __version__: &str = env!("CARGO_PKG_VERSION");

    #[pymodule_export]
    use {
        crate::class_api::Markdown,
        crate::function_api::{events, events_with_range, html, reference_definitions, write_html},
    };
}

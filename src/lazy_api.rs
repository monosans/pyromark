use pyo3::prelude::*;

type Parser<'input> = pulldown_cmark::Parser<'input>;

type OffsetIter<'input> = pulldown_cmark::OffsetIter<
    'input,
    pulldown_cmark::DefaultBrokenLinkCallback,
>;

enum Stream<'input> {
    Events(Parser<'input>),
    MergedEvents(pulldown_cmark::TextMergeStream<'input, Parser<'input>>),
    EventsWithRange(OffsetIter<'input>),
    MergedEventsWithRange(
        pulldown_cmark::TextMergeWithOffset<'input, OffsetIter<'input>>,
    ),
}

impl Stream<'_> {
    fn next<'py>(
        &mut self,
        py: Python<'py>,
    ) -> Option<PyResult<Bound<'py, PyAny>>> {
        match self {
            Self::Events(iter) => {
                iter.next().map(|event| crate::convert::event(py, &event))
            }
            Self::MergedEvents(iter) => {
                iter.next().map(|event| crate::convert::event(py, &event))
            }
            Self::EventsWithRange(iter) => iter
                .next()
                .map(|event| crate::convert::event_with_range(py, &event)),
            Self::MergedEventsWithRange(iter) => iter
                .next()
                .map(|event| crate::convert::event_with_range(py, &event)),
        }
    }
}

#[expect(
    clippy::mem_forget,
    clippy::impl_trait_in_params,
    clippy::inline_modules
)]
mod cell {
    use super::Stream;

    self_cell::self_cell!(
        pub struct Cell {
            owner: pyo3::pybacked::PyBackedStr,
            #[not_covariant]
            dependent: Stream,
        }
    );
}

/// Iterator returned by `events` and `events_with_range`.
///
/// The parser is dropped as soon as iteration ends.
#[pyclass(module = "pyromark._pyromark")]
pub struct Events(Option<cell::Cell>);

pub fn new(
    py: Python<'_>,
    markdown: pyo3::pybacked::PyBackedStr,
    options: pulldown_cmark::Options,
    merge_text: bool,
    with_range: bool,
) -> Events {
    // Creating the parser runs the block level pass over the whole document.
    let cell = py.detach(|| {
        cell::Cell::new(markdown, |markdown| {
            let parser = Parser::new_ext(markdown, options);
            match (with_range, merge_text) {
                (false, false) => Stream::Events(parser),
                (false, true) => Stream::MergedEvents(
                    pulldown_cmark::TextMergeStream::new(parser),
                ),
                (true, false) => {
                    Stream::EventsWithRange(parser.into_offset_iter())
                }
                (true, true) => Stream::MergedEventsWithRange(
                    pulldown_cmark::TextMergeWithOffset::new(
                        parser.into_offset_iter(),
                    ),
                ),
            }
        })
    });
    Events(Some(cell))
}

#[pymethods]
impl Events {
    const fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__<'py>(
        &mut self,
        py: Python<'py>,
    ) -> PyResult<Option<Bound<'py, PyAny>>> {
        let Some(cell) = &mut self.0 else {
            return Ok(None);
        };
        match cell.with_dependent_mut(|_, stream| stream.next(py)) {
            Some(Ok(event)) => Ok(Some(event)),
            next => {
                self.0 = None;
                next.transpose()
            }
        }
    }

    fn __traverse__(
        &self,
        visit: pyo3::pyclass::PyVisit<'_>,
    ) -> Result<(), pyo3::pyclass::PyTraverseError> {
        let Some(cell) = &self.0 else {
            return Ok(());
        };
        visit.call(cell.borrow_owner().as_py_str())
    }

    fn __clear__(&mut self) {
        self.0 = None;
    }
}

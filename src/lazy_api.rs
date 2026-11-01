use pyo3::prelude::*;

type OffsetIter<'input> = pulldown_cmark::OffsetIter<'input, crate::common::BrokenLinkCallback>;

enum Stream<'input> {
    Events(crate::common::Parser<'input>),
    MergedEvents(pulldown_cmark::TextMergeStream<'input, crate::common::Parser<'input>>),
    EventsWithRange(OffsetIter<'input>),
    MergedEventsWithRange(pulldown_cmark::TextMergeWithOffset<'input, OffsetIter<'input>>),
}

/// The parser is `Send` but not `Sync`, which a pyclass must be. The mutex
/// makes it `Sync` yet is never locked: `__next__` holds `&mut self`, so
/// `get_mut` reaches the stream without synchronization.
type SyncStream<'input> = std::sync::Mutex<Stream<'input>>;

impl Stream<'_> {
    fn next<'py>(&mut self, py: Python<'py>) -> Option<PyResult<Bound<'py, PyAny>>> {
        match self {
            Self::Events(iter) => iter.next().map(|event| crate::convert::event(py, &event)),
            Self::MergedEvents(iter) => iter.next().map(|event| crate::convert::event(py, &event)),
            Self::EventsWithRange(iter) => {
                iter.next().map(|event| crate::convert::event_with_range(py, &event))
            }
            Self::MergedEventsWithRange(iter) => {
                iter.next().map(|event| crate::convert::event_with_range(py, &event))
            }
        }
    }
}

#[expect(clippy::mem_forget, clippy::impl_trait_in_params, clippy::inline_modules)]
mod cell {
    use super::SyncStream;

    self_cell::self_cell!(
        pub struct Cell {
            owner: pyo3::pybacked::PyBackedStr,
            #[not_covariant]
            dependent: SyncStream,
        }
    );
}

struct Inner {
    cell: cell::Cell,
    shared: std::sync::Arc<crate::common::Shared>,
}

/// Iterator returned by `events` and `events_with_range`.
///
/// Iteration ends at the first exception, and the parser is dropped as soon
/// as iteration ends.
#[pyclass(module = "pyromark._pyromark")]
pub struct Events(Option<Inner>);

pub fn new(
    py: Python<'_>,
    markdown: pyo3::pybacked::PyBackedStr,
    options: pulldown_cmark::Options,
    merge_text: bool,
    with_range: bool,
    broken_link_callback: Option<&Bound<'_, PyAny>>,
) -> Events {
    let shared = crate::common::Shared::new(broken_link_callback);
    // Creating the parser runs the block level pass over the whole document.
    let cell = py.detach(|| {
        cell::Cell::new(markdown, |markdown| {
            let parser = crate::common::parser(markdown, options, &shared);
            SyncStream::new(match (with_range, merge_text) {
                (false, false) => Stream::Events(parser),
                (false, true) => Stream::MergedEvents(pulldown_cmark::TextMergeStream::new(parser)),
                (true, false) => Stream::EventsWithRange(parser.into_offset_iter()),
                (true, true) => Stream::MergedEventsWithRange(
                    pulldown_cmark::TextMergeWithOffset::new(parser.into_offset_iter()),
                ),
            })
        })
    });
    Events(Some(Inner { cell, shared }))
}

#[pymethods]
impl Events {
    const fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__<'py>(&mut self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyAny>>> {
        let Some(inner) = &mut self.0 else {
            return Ok(None);
        };
        let next = match inner.cell.with_dependent_mut(|_, stream| {
            stream.get_mut().unwrap_or_else(std::sync::PoisonError::into_inner).next(py)
        }) {
            Some(Ok(event)) if !inner.shared.failed() => {
                return Ok(Some(event));
            }
            next => next.transpose(),
        };
        let Some(Inner { cell, shared }) = self.0.take() else {
            return next;
        };
        drop(cell);
        crate::common::Shared::into_error(shared).map_or(next, Err)
    }

    fn __traverse__(
        &self,
        visit: pyo3::pyclass::PyVisit<'_>,
    ) -> Result<(), pyo3::pyclass::PyTraverseError> {
        let Some(inner) = &self.0 else {
            return Ok(());
        };
        visit.call(inner.cell.borrow_owner().as_py_str())?;
        inner.shared.traverse(visit)
    }

    fn __clear__(&mut self) {
        self.0 = None;
    }
}

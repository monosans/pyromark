# Home

pyromark (stands for Python Rust Optimized Markdown) is a blazingly fast CommonMark-compliant Markdown parser for Python, built on the [pulldown-cmark](https://github.com/pulldown-cmark/pulldown-cmark) Rust crate.

## The output is not sanitized

Raw HTML, `<script>` and `javascript:` URLs pass through, as CommonMark requires. Run the output of untrusted Markdown through a sanitizer such as [nh3](https://pypi.org/project/nh3/).

## Events are a stream

[`events`][pyromark.events] yields a flat stream (`Start`, `Text`, `End`, …) rather than a tree, so track nesting between a `Start` and its `End` yourself. Iteration is lazy, but the block level pass over the whole document runs when the iterator is created.

## Threads

[`html`][pyromark.html] and [`write_html`][pyromark.write_html] release the GIL except while calling your callbacks or `file.write`. Event iterators hold it on every `next()`, so they only scale on free-threaded Python. A [`Markdown`][pyromark.Markdown] can be shared between threads; an iterator cannot.

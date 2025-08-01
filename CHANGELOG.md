# Changelog

[Semantic Versioning](https://semver.org/)

## [0.9.3] - 2025-07-29

- Remove loongarch64-unknown-linux-gnu target as it is not supported by PyPI.

## [0.9.2] - 2025-07-29

- Add CPython 3.14 and free-threaded CPython 3.14 support.
- Add riscv64gc-unknown-linux-gnu and loongarch64-unknown-linux-gnu targets support.
- Don't build x86_64-unknown-linux-gnu and aarch64-unknown-linux-gnu manylinux_2_34 wheels as they are in alpha.

## [0.9.1] - 2025-02-25

- Add support for PyPy 3.11 and free-threaded CPython 3.13.

## [0.9.0] - 2025-02-13

This release does not contain any breaking changes.

- Bump pulldown-cmark from v0.12.2 to v0.13.0. See <https://github.com/pulldown-cmark/pulldown-cmark/releases/tag/v0.13.0>.
- Add new options from pulldown-cmark v0.13.0: ENABLE_SUPERSCRIPT, ENABLE_SUBSCRIPT, ENABLE_WIKILINKS.
- Add new event types associated with the new options.
- Add a simple script to the documentation to compare performance with other libraries.

## [0.8.0] - 2025-02-01

- Add `events_with_range` which returns `(Event, Range)` pairs.
- Build for more platforms and more manylinux versions to improve performance on modern systems.

## [0.7.1] - 2024-12-24

- Don't close input file in CLI if it is stdin.

## [0.7.0] - 2024-11-26

Breaking:

- The `options` argument can no longer be `None`. Use `Options(0)` instead.
- `pyromark.events` now uses `pythonize` Rust crate, the output will be different and more correct.
- The only exported member of `pyromark.event` is now `Event`.

Feature:

- Support for the `--output` flag in the CLI.
- Backport `__str__` and `__format__` behavior for `pyromark.Options` from Python 3.11.

Fix:

- Ensure that the input file is always closed in the CLI.

## [0.6.2] - 2024-11-18

- Improve error messages.

## [0.6.1] - 2024-11-17

- Bump `pyo3` from `v0.22.5` to `v0.23.1`.

## [0.6.0] - 2024-11-03

### Breaking

- Rename `extensions` to `options`.
- Rename `pyromark.markdown` to `pyromark.html`.
- Rename `pyromark.Markdown.convert` to `pyromark.Markdown.html`.

### Feature

- Add `pyromark.events` and `pyromark.Markdown.events` to iterate over Markdown elements. See docs for example.

## [0.5.1] - 2024-10-21

- Drop Python 3.7 and 3.8 support.
- Bump pulldown-cmark from 0.12.0 to 0.12.2. See <https://github.com/pulldown-cmark/pulldown-cmark/releases/tag/v0.12.1> and <https://github.com/pulldown-cmark/pulldown-cmark/releases/tag/v0.12.2>.

## [0.5.0] - 2024-08-20

- Bump pulldown-cmark from 0.11.0 to 0.12.0. See <https://github.com/pulldown-cmark/pulldown-cmark/releases/tag/v0.12.0>.
- Add new extension: `ENABLE_DEFINITION_LIST`.
- Add Python 3.13 support.

## [0.4.0] - 2024-05-18

- Bump pulldown-cmark from 0.10.3 to 0.11.0. See <https://github.com/pulldown-cmark/pulldown-cmark/releases/tag/v0.11.0>.

## [0.3.2] - 2024-04-26

- Bump pulldown-cmark from 0.10.2 to 0.10.3. See <https://github.com/pulldown-cmark/pulldown-cmark/releases/tag/v0.10.3>.

## [0.3.1] - 2024-04-02

- Bump pulldown-cmark from 0.10.0 to 0.10.2. See <https://github.com/pulldown-cmark/pulldown-cmark/releases/tag/v0.10.2>.

## [0.3.0] - 2024-02-05

- Bump pulldown-cmark from 0.9.5 to 0.10.0. See <https://github.com/raphlinus/pulldown-cmark/releases/tag/v0.10.0>.
- Add new extensions: `ENABLE_YAML_STYLE_METADATA_BLOCKS`, `ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS`, `ENABLE_OLD_FOONOTES`.

## [0.2.6] - 2024-01-28

- Bump pulldown-cmark from 0.9.3 to 0.9.5.
- Bump pyo3 from 0.20.0 to 0.20.2.

## [0.2.5] - 2023-12-21

- Build wheels for more platforms and Python versions.

## [0.2.4] - 2023-12-12

- Rebuild with updated Rust compiler and updated dependencies.

## [0.2.3] - 2023-10-16

- Rebuild with updated Rust compiler and updated dependencies.

## [0.2.2] - 2023-08-17

- Rebuild with updated Rust compiler and updated dependencies.

## [0.2.1] - 2023-07-09

- Add CLI.
- Add @typing.final to pyromark.Markdown.
- Update dependencies.

## [0.2.0] - 2023-06-29

- Use enum.IntFlag instead of a string sequence to define extensions.
- Fix pyromark.Markdown's \_\_module\_\_ attribute.
- New full-fledged documentation and docstrings instead of README.md.

## [0.1.4] - 2023-06-27

- Rebuild with PyPy 3.10 wheels for x86_64 and i686.
- Update dependencies.

## [0.1.3] - 2023-05-31

- Update dependencies (most importantly, PyO3 from 0.18.3 to 0.19.0).

## [0.1.2] - 2023-05-21

- Update pulldown-cmark from 0.9.2 to 0.9.3.

## [0.1.1] - 2023-05-19

- Release the GIL while parsing.

## [0.1.0] - 2023-05-07

- Initial release.

# Changelog

[Semantic Versioning](https://semver.org/)

## [0.2.7] - 2024-02-05

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

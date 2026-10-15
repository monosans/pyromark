from __future__ import annotations

import ast
import inspect
import re
import textwrap
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TypeAlias

import pyromark
import pyromark._options
import pyromark.event
import pytest

README = Path(__file__).parent.parent / "README.md"


def _python_blocks(source: str) -> list[str]:
    """The python code blocks, fenced by three or more backticks.

    A block whose own content contains a fence is opened with a longer one,
    so the closing fence has to match the opening one exactly.
    """
    blocks = []
    lines = source.splitlines()
    index = 0
    while index < len(lines):
        opening = re.match(r"^(`{3,})python$", lines[index])
        if opening is not None:
            closing = lines.index(opening[1], index + 1)
            blocks.append("\n".join(lines[index + 1 : closing]))
            index = closing
        index += 1
    return blocks


def test_readme_examples_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    blocks = _python_blocks(README.read_text("utf-8"))
    assert blocks
    monkeypatch.chdir(tmp_path)

    for block in blocks:
        exec(compile(block, str(README), "exec"), {})  # noqa: S102


_PYTHON_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def _documented_examples() -> dict[str, str]:
    examples: dict[str, str] = {}
    seen = set()
    for module in (pyromark, pyromark.event):
        for name in module.__all__:
            obj = getattr(module, name)
            members = vars(obj) if isinstance(obj, type) else {}
            for member_name, member in ((name, obj), *members.items()):
                if member_name.startswith("_"):
                    continue
                doc = getattr(member, "__doc__", None) or ""
                for index, block in enumerate(_PYTHON_BLOCK.findall(doc)):
                    code = textwrap.dedent(block)
                    if code in seen:
                        continue
                    seen.add(code)
                    examples[f"{name}.{member_name}[{index}]"] = code
    return examples


_DOCUMENTED_EXAMPLES = _documented_examples()


def test_every_public_object_documents_an_example() -> None:
    documented = {name.partition(".")[0] for name in _DOCUMENTED_EXAMPLES}
    assert documented >= set(pyromark.__all__)


@pytest.mark.parametrize(
    "code", _DOCUMENTED_EXAMPLES.values(), ids=_DOCUMENTED_EXAMPLES
)
def test_documented_examples_run(code: str) -> None:
    namespace = {
        "pyromark": pyromark,
        "md": pyromark.Markdown(),
        "markdown": "# Hello world",
        "range_": {"start": 0, "end": 13},
    }
    exec(code, namespace)  # noqa: S102


STUB = Path(pyromark.__file__).parent / "_pyromark.pyi"


def _stub_names() -> set[str]:
    names = set()
    for node in ast.parse(STUB.read_text("utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.AnnAssign) and isinstance(
            node.target, ast.Name
        ):
            names.add(node.target.id)
    return names


def test_stub_declares_exactly_what_the_extension_exposes() -> None:
    exposed = {
        name
        for name in vars(pyromark._pyromark)  # noqa: SLF001
        if not name.startswith("_") or name == "__version__"
    }

    assert exposed == _stub_names()


ROOT = Path(__file__).parent.parent


def _search(pattern: str, path: str, /) -> str:
    match = re.search(pattern, (ROOT / path).read_text("utf-8"))
    assert match is not None, path
    return match[1]


def test_the_crate_and_the_package_declare_one_version() -> None:
    declared = r'(?m)^version = "([^"]+)"$'

    assert (
        _search(declared, "Cargo.toml")
        == _search(declared, "pyproject.toml")
        == pyromark.__version__
    )


def test_option_docs_link_to_the_pinned_pulldown_cmark() -> None:
    pinned = _search(r'pulldown-cmark = \{ version = "=([^"]+)"', "Cargo.toml")
    options = Path(pyromark._options.__file__).read_text("utf-8")  # noqa: SLF001

    linked = set(re.findall(r"docs\.rs/pulldown-cmark/([^/]+)/", options))

    assert linked == {pinned}


_Params: TypeAlias = list[tuple[str, str, object]]


def _stub_params(function: ast.FunctionDef) -> _Params:
    namespace: dict[str, object] = {"Options": pyromark.Options}

    def value(node: ast.expr) -> object:
        return eval(compile(ast.Expression(node), str(STUB), "eval"), namespace)  # noqa: S307

    arguments = function.args
    positional = arguments.posonlyargs + arguments.args
    missing = len(positional) - len(arguments.defaults)
    defaults = [inspect.Parameter.empty] * missing + [
        value(node) for node in arguments.defaults
    ]
    params: _Params = [
        (arg.arg, "POSITIONAL_ONLY", default)
        for arg, default in zip(
            arguments.posonlyargs,
            defaults[: len(arguments.posonlyargs)],
            strict=True,
        )
    ]
    params += [
        (arg.arg, "POSITIONAL_OR_KEYWORD", default)
        for arg, default in zip(
            arguments.args, defaults[len(arguments.posonlyargs) :], strict=True
        )
    ]
    params += [
        (
            arg.arg,
            "KEYWORD_ONLY",
            inspect.Parameter.empty if node is None else value(node),
        )
        for arg, node in zip(
            arguments.kwonlyargs, arguments.kw_defaults, strict=True
        )
    ]
    return params


def _runtime_params(obj: Callable[..., object]) -> _Params:
    return [
        (param.name, param.kind.name, param.default)
        for param in inspect.signature(obj).parameters.values()
    ]


def _stub_callables() -> Iterator[tuple[str, Callable[..., object], _Params]]:
    for node in ast.parse(STUB.read_text("utf-8")).body:
        if isinstance(node, ast.FunctionDef):
            yield node.name, getattr(pyromark, node.name), _stub_params(node)
        elif isinstance(node, ast.ClassDef):
            cls = getattr(pyromark, node.name)
            for method in node.body:
                if not isinstance(method, ast.FunctionDef):
                    continue
                if method.name == "__init__":
                    yield f"{node.name}()", cls, _stub_params(method)[1:]
                else:
                    yield (
                        f"{node.name}.{method.name}",
                        getattr(cls, method.name),
                        _stub_params(method),
                    )


_STUB_CALLABLES = list(_stub_callables())


@pytest.mark.parametrize(
    ("obj", "declared"),
    [(obj, declared) for _, obj, declared in _STUB_CALLABLES],
    ids=[name for name, _, _ in _STUB_CALLABLES],
)
def test_stub_signatures_match_the_extension(
    obj: Callable[..., object], declared: _Params
) -> None:
    assert _runtime_params(obj) == declared


def _stub_docstrings() -> Iterator[tuple[str, object, str | None]]:
    for node in ast.parse(STUB.read_text("utf-8")).body:
        if isinstance(node, ast.FunctionDef):
            yield (
                node.name,
                getattr(pyromark, node.name),
                ast.get_docstring(node),
            )
        elif isinstance(node, ast.ClassDef):
            cls = getattr(pyromark, node.name)
            yield node.name, cls, ast.get_docstring(node)
            for method in node.body:
                if (
                    isinstance(method, ast.FunctionDef)
                    and method.name != "__init__"
                ):
                    yield (
                        f"{node.name}.{method.name}",
                        getattr(cls, method.name),
                        ast.get_docstring(method),
                    )


_STUB_DOCSTRINGS = list(_stub_docstrings())


@pytest.mark.parametrize(
    ("obj", "declared"),
    [(obj, declared) for _, obj, declared in _STUB_DOCSTRINGS],
    ids=[name for name, _, _ in _STUB_DOCSTRINGS],
)
def test_stub_docstrings_match_the_extension(
    obj: object, declared: str | None
) -> None:
    assert declared is not None
    assert obj.__doc__ is not None
    assert inspect.cleandoc(obj.__doc__) == declared

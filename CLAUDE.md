# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This is a brand-new `uv`-managed Python project (src layout). The only code so far is a
`main()` stub in `src/text_to_audio/__init__.py` that prints a greeting. There are no
tests, no `tests/` directory, and no CI configured yet — set these up as the project grows
rather than assuming they exist.

## Commands

This project uses **uv** exclusively for environment, dependency, and script management — do
not use bare `pip`/`python`, and do not mix in Poetry or other tooling.

```bash
uv run text-to-audio        # run the CLI entry point (defined in [project.scripts])
uv run pytest -q            # run tests
uv run pytest -q path/to/test_file.py::test_name   # run a single test
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv add <package>            # add a runtime dependency
uv add --dev <package>      # add a dev dependency
```

Before considering any task done, run format check, lint, mypy, and pytest (in that order) and
make sure all pass — see `.claude/rules/python.md` §7 for the exact sequence.

`pyproject.toml` is the single source of config truth (deps, ruff, mypy, pytest). `uv.lock` is
committed since this is an application, not a library.

## Architecture

The project targets a `src/<package>/` layout with these intended layers (see
`.claude/rules/python.md` §3 for the full target tree):

- `domain/` — pure logic and entities, no I/O, no external deps beyond the stdlib
- `services/` — use-case orchestration; wires domain + adapters together
- `adapters/` — I/O boundaries: DB, HTTP, filesystem, queues
- `cli.py` / `api/` — entry points; translate input/output only, no business rules

Only `src/text_to_audio/__init__.py` exists today, so this structure hasn't been built out yet
— follow it as new modules are added rather than treating it as already in place.

## Conventions

Full project rules live in `.claude/rules/python.md` (auto-loaded for `**/*.py` and
`pyproject.toml`) — read it for the complete rationale and pattern examples. Highlights:

- Python 3.13+, strict type annotations on every public function (modern syntax: `list[str]`,
  `str | None`, no `typing.List`/`Optional`/`Union`).
- `pathlib.Path` everywhere, never `os.path` or string concatenation for paths.
- `pydantic` / `pydantic-settings` at boundaries (parsing external data, config from env);
  `dataclass(frozen=True, slots=True)` for pure in-domain values.
- Domain-specific exceptions; `raise ... from err` when re-wrapping; never a bare `except:` or
  `except Exception: pass`.
- `logging` with a per-module logger, never `print`, for anything beyond the CLI entry point.
- `Decimal` for money, timezone-aware `datetime` (`datetime.now(UTC)`), never naive.
- Ask before adding a dependency (check the stdlib first) and before touching
  `pyproject.toml`, CI, or running `git commit`/`push` — see §10 of the rules file for the full
  list of actions that need explicit permission.

Note: `.gitignore` currently excludes `.claude/`, which means these rules and any project
config under `.claude/` are not tracked in git. Flag this to the user if it looks unintentional.
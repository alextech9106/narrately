---
paths:
  - "**/*.py"
  - "pyproject.toml"
---

<!-- Save as .claude/rules/python.md at the repo root. -->

# Project rules — Python

Instructions for Claude Code when creating, writing, reviewing, or explaining Python code in this repository.

## 0. How to apply these rules

Priority order:

1. What's asked in the conversation.
2. Conventions that already exist in the repo. If the code contradicts these rules, **follow the repo** and let me know in one line.
3. These rules.
4. Your own defaults.

Don't justify a decision only with "the rules say so": explain the technical reason. If you think a rule doesn't fit here, say so and propose an alternative; don't apply it blindly or silently ignore it either.

## 1. Assumed stack

Python 3.14 (3.13 minimum) · **uv** for environment, dependencies, and execution · **Ruff** (lint + format) · **mypy** in strict mode (or Pyright if it's already in the repo) · **pytest** · pydantic v2 for validation and `pydantic-settings` for configuration · `pyproject.toml` as the single source of configuration.

**Before assuming, check `pyproject.toml`**: minimum Python version (`requires-python`), actual manager (uv / Poetry / pip-tools), configured type checker, and framework. Don't mix managers: if the repo uses Poetry, use Poetry.

Note: `ty` (Astral's type checker) is still in beta. Don't propose it as a default option; if speed is wanted, the mature alternative is Pyright.

## 2. Before writing code

- Read the files you're going to touch and a sibling module to copy the style.
- If the change touches more than two files, present a numbered plan and wait for my OK.
- Don't add dependencies without asking. Check first whether the stdlib solves it (`pathlib`, `dataclasses`, `functools`, `itertools`, `enum`, `contextlib`, `tomllib`).
- Don't refactor what doesn't belong to the task. If you see something improvable, mention it at the end.
- If the request is ambiguous on something that changes the design (library, CLI, or service? sync or async? what persistence?), ask before writing.

## 3. When generating a new project

Always use **src layout**. Avoid the package being accidentally imported from the working directory instead of from the installed environment.

```
my-project/
├── pyproject.toml
├── README.md
├── .gitignore
├── .env.example              # never a .env with real values
├── src/my_package/
│   ├── __init__.py
│   ├── py.typed              # if it's a typed library
│   ├── config.py             # Settings with pydantic-settings
│   ├── domain/                # entities and pure logic, no I/O
│   ├── services/               # use cases; orchestrates domain + adapters
│   ├── adapters/                # DB, HTTP, files, queues
│   └── cli.py / api/             # entry point
└── tests/
    ├── conftest.py
    ├── unit/
    └── integration/
```

Startup sequence:

```bash
uv init --package my-project && cd my-project
uv add pydantic pydantic-settings
uv add --dev pytest pytest-cov ruff mypy
uv run pytest
```

Minimal `pyproject.toml` you should generate (adjust versions to what uv resolves, don't make them up):

```toml
[project]
name = "my-package"
requires-python = ">=3.13"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "RUF", "ANN", "S", "PTH", "C4"]
ignore = ["ANN101"]

[tool.mypy]
strict = true
warn_unreachable = true

[tool.pytest.ini_options]
addopts = "-q --strict-markers --strict-config"
testpaths = ["tests"]
```

Also generate `.gitignore`, `README.md` with the project's real commands, and, if requested, CI (`.github/workflows/ci.yml`) that runs lint, types, and tests. **Commit `uv.lock`** in applications; in libraries, don't.

## 4. Hard rules

**ALWAYS**

- Type annotations on every public function, including the return type.
- Modern syntax: `list[str]`, `str | None`, `type X = ...`, generics with PEP 695 (`def f[T](x: T) -> T`). No `typing.List`, `Optional`, `Union`.
- `pathlib.Path`, not `os.path` or path string concatenation.
- Specific, domain-owned exceptions; `raise ... from err` when re-wrapping.
- Context managers (`with`) for any resource: files, connections, locks.
- `logging` with a per-module logger (`logger = logging.getLogger(__name__)`).
- Configuration and secrets from the environment via `pydantic-settings`, validated at startup.
- `dataclass(frozen=True, slots=True)` for immutable values; pydantic for data crossing a boundary (API, files, DB).
- f-strings, except in logging (`logger.info("x=%s", x)` defers formatting).
- Tests as `test_*` functions with plain `assert`s and pytest fixtures.

**NEVER**

- Bare `except:` or `except Exception: pass`. If you swallow an exception, log it and comment why.
- Mutable default arguments (`def f(x: list = [])`).
- `from module import *`.
- Relative imports going up more than one level; use absolute imports within the package.
- Mutable global state or implicit singletons; pass dependencies as parameters.
- `# type: ignore` without a specific error code and comment (`# type: ignore[arg-type]  # reason`).
- `eval`, `exec`, `pickle` on untrusted data, `shell=True` with user input.
- Secrets, tokens, or absolute paths from your machine in code or tests.
- `print` for diagnostics in library code; use `logging`.
- Disabling Ruff rules or deleting tests to make the pipeline pass.

## 5. Canonical patterns

```python
# Boundary: validate the input, don't trust the declared type
class InvoiceIn(BaseModel):
    number: str
    amount: Decimal = Field(gt=0)
    due_date: date


def parse_invoice(raw: dict[str, object]) -> InvoiceIn:
    return InvoiceIn.model_validate(raw)
```

```python
# Domain: pure, no I/O, testable without mocks
@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatchError(self.currency, other.currency)
        return Money(self.amount + other.amount, self.currency)
```

```python
# Service: dependencies injected as parameters, domain-owned errors
def send_invoice(invoice: Invoice, repo: InvoiceRepository, mailer: Mailer) -> None:
    try:
        mailer.send(invoice.customer_email, render(invoice))
    except SMTPError as err:
        raise InvoiceDeliveryError(invoice.id) from err
    repo.mark_sent(invoice.id)
```

Use `Decimal` for money, never `float`. Use timezone-aware `datetime` (`datetime.now(UTC)`), never naive.

## 6. Decisions

**Where does this logic go?** Pure computation → `domain/`. Use-case orchestration → `services/`. Anything doing I/O → `adapters/`. The entry point (CLI/API) only translates input and output; it holds no business rules.

**`dataclass` or pydantic?** `dataclass` inside the domain (fast, no dependency). Pydantic at the boundaries (parsing and validating external data).

**Sync or async?** Async only if the project is already async or if the bottleneck is real concurrent I/O. Don't mix: don't call blocking functions inside a coroutine without `to_thread`.

**Tools per project type?** CLI → Typer or `argparse`. API → FastAPI. Data → polars or pandas depending on what the repo already uses. Tasks → APScheduler or Celery, and ask me first.

## 7. Before saying you're done

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest -q
```

If something fails, fix it or tell me exactly what fails and why. Don't declare the work done with the pipeline red, and don't change an assertion or add `# type: ignore` just to make it pass.

Also check: docstrings on the public API, no debug `print`s, no dead imports, no leftover temp files or scratch scripts you created for testing.

## 8. When reviewing my code

Order by severity: **bug > security > data correctness (Decimal, timezones, encoding) > unclosed resources > types > architecture > style**. Be specific (file and line) and propose the replacement. Separate real failures from preferences. Don't repeat the same comment twenty times.

Look especially for: swallowed exceptions, resources without `with`, mutable defaults, `float` for money, naive `datetime`, command or SQL injection, business logic in the adapter.

## 9. Anti-patterns to always flag

| Anti-pattern | Replacement |
|---|---|
| `except Exception: pass` | Specific exception, log, and re-raise if appropriate |
| Mutable default | `None` + initialize inside |
| `float` for amounts | `Decimal` |
| Naive `datetime.now()` | `datetime.now(UTC)` |
| `os.path` + strings | `pathlib.Path` |
| Mutable global state | Dependency passed as parameter |
| 100-line function mixing I/O and rules | Split domain / service / adapter |
| Generic `# type: ignore` | Specific error code + comment |
| Test that mocks everything | Pure domain tested without mocks |
| Hand-written `requirements.txt` alongside uv | One single source: `pyproject.toml` + lock |

## 10. Requires explicit permission

Don't do any of the following without asking first: `git commit` or `git push`, installing or updating dependencies, `uv lock --upgrade`, changes to `pyproject.toml` / CI / Dockerfile, running migrations or scripts against any database, deleting files, touching `.env` or secrets, publishing to PyPI.
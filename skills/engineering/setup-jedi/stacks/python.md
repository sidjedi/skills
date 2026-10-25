# Python (uv)

## Create
`uv` manages the interpreter, the venv and the lockfile in one tool, so nothing is activated by hand.
```bash
uv init --app --name <name> .
uv add --dev pytest pytest-xdist ruff import-linter
```
The app package lives at the repo root (`<name>/`) so `lint-imports` finds it.

## Tests
`pytest-xdist` splits the suite across cores; it is what makes the full run tolerable at ~1000 tests.
```bash
uv run pytest -n auto
```
Smoke test: `tests/test_smoke.py` with one passing test.

## Fast checks (run with lint)
`ruff` replaces linter, import sorter and formatter in one fast binary; `C901` is its cyclomatic-complexity rule.
```bash
uv run ruff check .
uv run ruff format --check .
```
```toml
# pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "I", "C901"]

[tool.ruff.lint.mccabe]
max-complexity = 10
```

## Slow checks (PR, listed in `quality.md`)
`import-linter` makes the layer order a failing check instead of a convention; `jscpd` finds copy-paste.
```bash
uv run lint-imports
pnpm dlx jscpd <name> --min-lines 8 --threshold 3   # needs Node; skip without it
```
```toml
# pyproject.toml
[tool.importlinter]
root_package = "<name>"

[[tool.importlinter.contracts]]
name = "layers"
type = "layers"
layers = ["<name>.api", "<name>.services", "<name>.repositories"]   # highest to lowest
```

## Camadas (text for `AGENTS.md`)
```
Caminho de uma requisição: routes → services → repositories. O próximo recurso copia esse trio.
Erros: exceção de domínio; um handler único responde.
```

## Suggest, do not install by default
`fastapi[standard]` (API), `pydantic-settings` (config por env), `sqlmodel` ou `sqlalchemy` + `alembic` (banco), `httpx` (cliente HTTP).

## Look up
docs.astral.sh/uv, docs.astral.sh/ruff, import-linter.readthedocs.io

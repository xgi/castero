# Coding Conventions

## Core Sections (Required)

### 1) Naming Rules

| Item | Rule | Example | Evidence |
|------|------|---------|----------|
| Files | lowercase, usually concatenated words | `downloadqueue.py`, `chronoperspective.py` | `castero/`, `castero/perspectives/` |
| Functions/methods | snake_case; leading underscore for internal methods | `replace_episodes`, `_reload_feed_data` | `castero/database.py` |
| Types/interfaces | PascalCase; exception classes end in `Error` | `DownloadedPerspective`, `FeedParseError` | `castero/perspectives/downloadedperspective.py`, `castero/feed.py` |
| Constants/env vars | UPPER_SNAKE_CASE | `MILLISECONDS_IN_SECOND`, `XDG_DATA_HOME` | `castero/constants.py`, `castero/datafile.py` |

Private object fields use a single leading underscore, and public read access is commonly exposed with properties.

### 2) Formatting and Linting

- Formatter: none configured.
- Linter: flake8 4.0.1 configured by `.flake8`.
- Most relevant enforced rules: default flake8 rules with `E221` and `W503` ignored, build/venv directories excluded, and `E501` ignored only in `castero/database.py`.
- Run commands: `flake8 castero tests`; `python -m pytest tests`.

### 3) Import and Module Conventions

- Import grouping/order: standard-library, third-party, then `castero` imports is common, but not consistently blank-line separated.
- Alias vs relative import policy: source uses absolute `castero.*` imports; no relative imports or configured path aliases were found.
- Public exports/barrel policy: none; callers import concrete modules. Runtime player/perspective discovery imports modules by filename.

### 4) Error and Logging Conventions

- Error strategy by layer: domain/integration modules define small exception hierarchies; `Display` converts feed failures into status messages; CLI import/export lets user-facing exceptions terminate the process. Assertions enforce many programmer preconditions.
- Logging style and required context fields: no logging framework is used. Interactive messages go through `Display.change_status`; CLI import/export uses `print`; native stderr is redirected to a temporary file.
- Sensitive-data redaction rules: [TODO] no explicit policy or logger exists. Proxy URLs may contain credentials in the local config.

### 5) Testing Conventions

- Test file naming/location rule: `tests/test_<module>.py`, separate from source; binary/XML/file fixtures live under `tests/` subdirectories.
- Mocking strategy norm: `unittest.mock` patches curses, HTTP, and media backends; pytest fixtures protect the user's database and reset global configuration.
- Coverage expectation: coverage XML is uploaded to Code Climate, but no threshold is configured.

### 6) Evidence

- `.flake8`
- `requirements.txt`
- `castero/feed.py`
- `castero/display.py`
- `tests/conftest.py`
- `.github/workflows/ci.yml`

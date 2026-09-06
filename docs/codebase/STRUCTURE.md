# Codebase Structure

## Core Sections (Required)

### 1) Top-Level Map

| Path | Purpose | Evidence |
|------|---------|----------|
| `castero/` | Application, domain, persistence, TUI, networking, and playback source | `castero/__main__.py`, package modules |
| `castero/menus/` | Concrete menu data sources and list rendering models | `castero/menu.py`, `castero/menus/*.py` |
| `castero/perspectives/` | Five switchable TUI layouts and their input handlers | `castero/perspective.py`, `castero/perspectives/*.py` |
| `castero/players/` | VLC and mpv adapters | `castero/player.py`, `castero/players/*.py` |
| `castero/templates/` | Default configuration and ordered SQLite migrations shipped as package data | `setup.py`, `castero/templates/castero.conf`, `castero/templates/migrations/*.sql` |
| `tests/` | pytest suite plus RSS, OPML, database, and downloaded-media fixtures | `tests/conftest.py`, `tests/test_*.py`, `tests/datafiles/` |
| `.github/workflows/` | GitHub Actions test/coverage pipeline | `.github/workflows/ci.yml` |
| `res/` | README screenshot asset | `README.md`, `res/client_example.png` |
| `setup.py`, `requirements.txt` | Distribution metadata and pinned CI/development environment | `setup.py`, `requirements.txt` |

### 2) Entry Points

- Main runtime entry: `castero/__main__.py:main`.
- Secondary entry points: `import_subscriptions` and `export_subscriptions` in `castero/__main__.py`, selected by `--import` and `--export`.
- How entry is selected: setuptools installs `castero=castero.__main__:main`; running `python -m castero` also executes the module. The module calls `main()` unconditionally at import time.

### 3) Module Boundaries

| Boundary | What belongs here | What must not be here |
|----------|-------------------|------------------------|
| `castero/__main__.py` | CLI parsing, process bootstrap, main loop | Feed parsing, SQL, and curses layout details |
| `display.py`, `perspective.py`, `menu.py` and subpackages | Terminal input, layout, rendering, and presentation state | Network transport and SQL implementation |
| `feed.py`, `episode.py`, `queue.py` | Feed/episode/playback-queue state and behavior | Curses window creation |
| `database.py` | SQLite schema lifecycle and persistence API | TUI status changes and feed HTTP orchestration; these are present today and are refactoring targets |
| `net.py`, `subscriptions.py`, `datafile.py` | HTTP defaults, OPML transfer, filesystem paths/downloads | Screen rendering |
| `player.py`, `players/` | Playback interface, selection, and backend adapters | Feed persistence |

### 4) Naming and Organization Rules

- File naming pattern: lowercase module names, usually concatenated domain names such as `downloadqueue.py` and `queueperspective.py`.
- Directory organization pattern: primarily technical layers (`menus`, `perspectives`, `players`), with remaining domain and service modules at package root.
- Import convention: absolute `castero.*` imports; there are no aliases or barrel modules.

### 5) Evidence

- `README.md`
- `setup.py`
- `castero/__main__.py`
- `castero/display.py`
- `castero/database.py`
- `tests/conftest.py`

# Technology Stack

## Core Sections (Required)

### 1) Runtime Summary

| Area | Value | Evidence |
|------|-------|----------|
| Primary language | Python | `setup.py`, `castero/*.py` |
| Runtime + version | Python 3.9+ is the chosen refactoring target. Current repository declarations are inconsistent: CI exercises 3.7-3.10, `setup.py` says `>=3`, and the README says `>=3.5`. | User decision (2026-09-06), `setup.py`, `README.md`, `.github/workflows/ci.yml` |
| Package manager | pip-compatible requirements plus setuptools packaging | `requirements.txt`, `setup.py` |
| Module/build system | setuptools package with a `castero` console-script entry point | `setup.py` |

### 2) Production Frameworks and Dependencies

The install metadata leaves production dependency versions unconstrained. The versions below are the development/CI pins in `requirements.txt`.

| Dependency | Version | Role in system | Evidence |
|------------|---------|----------------|----------|
| requests | 2.24.0 | Synchronous HTTP transport | `requirements.txt`, `castero/net.py` |
| grequests | 0.6.0 | Concurrent feed HTTP requests | `requirements.txt`, `castero/database.py` |
| lxml | 4.9.1 | RSS and OPML XML parsing/writing | `requirements.txt`, `castero/feed.py`, `castero/subscriptions.py` |
| beautifulsoup4 | 4.10.0 | HTML-to-text conversion for metadata | `requirements.txt`, `castero/helpers.py` |
| python-vlc | 3.0.12118 | VLC playback adapter | `requirements.txt`, `castero/players/vlcplayer.py` |
| python-mpv | 0.5.2 | mpv playback adapter | `requirements.txt`, `castero/players/mpvplayer.py` |
| CJKwrap | 2.2 | Terminal-width-aware metadata wrapping | `requirements.txt`, `castero/perspective.py` |
| pytz | 2021.3 | Normalizes parsed feed timestamps | `requirements.txt`, `castero/helpers.py` |

The Python standard-library `curses` and `sqlite3` modules provide the TUI and persistence layers. There is no application framework or ORM.

### 3) Development Toolchain

| Tool | Purpose | Evidence |
|------|---------|----------|
| pytest 7.1.2 | Test runner | `requirements.txt`, `README.md` |
| coverage.py 6.0.2 | Coverage collection and Code Climate XML reporting | `requirements.txt`, `.github/workflows/ci.yml` |
| flake8 4.0.1 | Linting; maximum line length is 109 and selected rules are ignored | `requirements.txt`, `.flake8` |
| GitHub Actions | CI across Python 3.7-3.10 | `.github/workflows/ci.yml` |
| setuptools | Build/install metadata and console entry point | `setup.py` |

### 4) Key Commands

```bash
pip install -r requirements.txt
pip install .
python -m pytest tests
coverage run -m pytest
flake8 castero tests
```

The repository does not define a dedicated build command or task runner.

### 5) Environment and Config

- Config sources: `castero/templates/castero.conf`, copied to `${XDG_CONFIG_HOME:-~/.config}/castero/castero.conf`; package metadata is in `setup.py`.
- Environment variables read: `HOME`, `XDG_CONFIG_HOME`, and `XDG_DATA_HOME`.
- Required secrets: none. Proxy credentials may be embedded in the user configuration file.
- Deployment/runtime constraints: refactors may require Python 3.9+; repository metadata and CI still need aligning with that decision. SQLite is required; at least one of VLC or mpv and its native library must be installed. CI installs both with apt.

### 6) Evidence

- `setup.py`
- `requirements.txt`
- `.github/workflows/ci.yml`
- `.flake8`
- `castero/datafile.py`
- `castero/templates/castero.conf`

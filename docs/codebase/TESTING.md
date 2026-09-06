# Testing Patterns

## Core Sections (Required)

### 1) Test Stack and Commands

- Primary test framework: pytest 7.1.2 in the pinned requirements.
- Assertion/mocking tools: plain `assert`, `pytest.raises`, pytest fixtures, and `unittest.mock`.
- Commands:

```bash
python -m pytest tests
python -m pytest tests/test_feed.py
# No separately configured integration/e2e command
coverage run -m pytest
```

### 2) Test Layout

- Test file placement pattern: separate `tests/` directory mirroring production modules by name.
- Naming convention: `test_<module>.py` files and `test_<behavior>` functions.
- Setup files and where they run: `tests/conftest.py` supplies curses/display/database fixtures and an autouse global-config reset. RSS, OPML, SQLite, and downloaded media fixtures live in `tests/feeds`, `tests/subscriptions`, `tests/datafiles`, and `tests/downloaded`.

### 3) Test Scope Matrix

| Scope | Covered? | Typical target | Notes |
|-------|----------|----------------|-------|
| Unit | yes | Helpers, feed parsing, domain classes, menus, players | Heavy use of mocks for curses/media/network boundaries |
| Integration | yes, locally scoped | Real SQLite fixtures, filesystem fixtures, RSS/OPML parsing | No external service is intentionally required |
| E2E | no | Full interactive terminal and real player workflow | No PTY-based or installed-console-script test exists |

### 4) Mocking and Isolation Strategy

- Main mocking approach: patch curses globally in a `stdscr` fixture; mock requests/player objects at module boundaries; move the user's fixed-path database aside for tests.
- Isolation guarantees: `prevent_modification` renames/restores the user database and the autouse fixture reconstructs global `Config.data`. Tests do not consistently close every database or join every spawned thread.
- Common failure mode in tests: asynchronous menu tests use real threads and one uses `time.sleep(1)` as synchronization. On Python 3.14, worker threads emitted unhandled curses initialization errors during the review run.

### 5) Coverage and Quality Signals

- Coverage tool + threshold: coverage.py 6.0.2; no enforced threshold.
- Current reported coverage: [TODO] CI uploads XML but no percentage is stored in the repository.
- Review-run result: 232 passed and 2 failed on Python 3.14. Both failures use the invalid mock expression `display._footer_window.called_with(...)`; the run also emitted 66 warnings, including unhandled worker-thread exceptions and deprecated pytest/thread APIs.
- Known gaps/flaky areas: real curses lifecycle, task cancellation/joining, concurrent SQLite access, abrupt-shutdown durability, and real VLC/mpv behavior.

### 6) Evidence

- `requirements.txt`
- `README.md`
- `tests/conftest.py`
- `tests/test_display.py`
- `tests/test_menu_episode.py`
- `tests/test_database.py`
- `.github/workflows/ci.yml`
- Terminal output from `uv run pytest -q` on 2026-09-06

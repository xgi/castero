# Codebase Concerns

## Core Sections (Required)

### 1) Top Risks (Prioritized)

| Severity | Concern | Evidence | Impact | Suggested action |
|----------|---------|----------|--------|------------------|
| high | Background threads mutate curses/menu state and share one SQLite connection without an ownership protocol | `display.py`, `menus/episodemenu.py`, `menus/chronomenu.py`; pytest worker exceptions | Terminal corruption, races, nondeterministic tests, unsafe shutdown | Introduce a task coordinator whose workers return events consumed on the UI thread |
| high | Default in-memory persistence is flushed to disk only by orderly `Database.close()` | `database.py:close`, `display.py:terminate` | Crashes or forced termination can lose the session's feed/progress/queue changes | Add transaction-scoped persistence and an atomic checkpoint/lifecycle abstraction |
| medium | `Display` and `Database` mix unrelated responsibilities | 803 and 657 lines respectively; methods span rendering, commands, HTTP, SQL, migration, and subprocesses | High coupling and risky feature changes | Extract application commands/services and repository/migration components incrementally |
| medium | Importing configuration or `castero.__main__` performs filesystem/process work | `Config = _Config()`, unconditional `main()` | Hard-to-isolate tests and unsafe library imports | Build an explicit application factory and inject typed settings/dependencies |
| medium | Episode/download file policy is duplicated and embedded in domain/UI objects | `episode.py`, `datafile.py`, `menus/downloadedmenu.py` | Inconsistent discovery, partial-file handling, and difficult alternate storage support | Extract episode storage and download manager interfaces |

### 2) Technical Debt

| Debt item | Why it exists | Where | Risk if ignored | Suggested fix |
|-----------|---------------|-------|-----------------|---------------|
| Repeated perspective layout and key-dispatch code | Each screen implements the same lifecycle independently | `castero/perspectives/*.py`, `castero/perspective.py` | Fixes diverge across five layouts | Introduce reusable pane/layout rendering and command routing |
| Repeated episode-list presentation | Chronological, feed, and downloaded lists duplicate filtering/count/item metadata | `castero/menus/chronomenu.py`, `episodemenu.py`, `downloadedmenu.py` | Behavioral inconsistencies and repeated tests | Extract an `EpisodeListMenu` base/view model with injectable loading/sorting |
| Global mutable settings | Convenience singleton established early | `castero/config.py`, imports throughout | Hidden dependencies and test filesystem manipulation | Parse settings at bootstrap and pass a read-only settings object |
| Persistence plus refresh orchestration | Feed update behavior accumulated in `Database` | `castero/database.py:reload` | SQL changes and network behavior cannot evolve independently | Split repositories, unit of work, and feed-refresh service |
| Runtime discovery by filename/class-name convention | Avoids maintaining registries | `castero/display.py:_load_perspectives`, `_load_players` | Renames/import helpers can break startup opaquely | Replace with explicit built-in registries, per the user decision on 2026-09-06 |

### 3) Security Concerns

| Risk | OWASP category (if applicable) | Evidence | Current mitigation | Gap |
|------|--------------------------------|----------|--------------------|-----|
| Episode-controlled text is interpolated into a shell command | A03 Injection | `castero/display.py:execute_command` | Feature is opt-in and config warns users | Replace it with argument-vector execution; this direction was confirmed by the user on 2026-09-06 |
| Proxy credentials may be stored in plaintext config | A02 Cryptographic Failures | `castero/templates/castero.conf`, `castero/net.py` | File resides in user config directory | No explicit permission check or credential-provider alternative |
| XML parser configuration is implicit | A05 Security Misconfiguration | `castero/feed.py`, `castero/subscriptions.py` | Network requests have a timeout | Parser limits/entity/network settings are not explicitly documented or centralized |

### 4) Performance and Scaling Concerns

| Concern | Evidence | Current symptom | Scaling risk | Suggested improvement |
|---------|----------|-----------------|-------------|-----------------------|
| Downloaded menu does one DB lookup per discovered file | `DownloadedMenu._find_downloaded_episodes` calls `Database.episode` in a filesystem loop | Repeated SQLite queries while scanning downloads | Slow layout refresh with large libraries | Index stored downloads once and bulk-fetch episode IDs |
| Default database repeatedly copies the full SQLite database | `Database.__init__`, `Database.close`, `_copy_database` | Startup/shutdown cost grows with library size | Long startup/exit and larger loss window | Benchmark direct SQLite/WAL versus periodic atomic checkpoints |
| All perspective menus refresh when one invalidation flag changes | `Display.update` iterates every perspective | Work is performed for inactive screens | Cost grows with episode count and added layouts | Use scoped state-change events and refresh only affected views |
| Filter properties rebuild lists on each access | `_filtered_episodes`/`_filtered_feeds` properties | Repeated allocation during length, title, item, metadata, and drawing | Extra CPU for large collections | Cache view models until source/filter changes |

### 5) Fragile/High-Churn Areas

| Area | Why fragile | Churn signal | Safe change strategy |
|------|-------------|-------------|----------------------|
| `castero/display.py` | Central mutable coordinator with 803 lines and many integration edges | Highest all-history source churn (114 path occurrences); no changes in the scan's last 90-day window | Characterization tests, then extract one command/rendering responsibility at a time |
| `castero/database.py` | Schema, object mapping, memory-copy lifecycle, network reload, and UI callbacks share one connection | 48 all-history path occurrences; second-largest source module | Preserve public API behind repositories and add transaction/concurrency tests |
| `castero/perspective.py` and subclasses | Base handler assumes screen-specific fields; subclasses duplicate lifecycle and special-case no-op keys | Base has 37 all-history occurrences; each layout has a separate test module | Introduce command objects and pane primitives behind existing screen IDs |
| Worker-backed menus | Threads write menu/curses state directly and tests do not join them | Pytest emitted unhandled thread exceptions during review | Return immutable results through a UI event queue and test with deterministic executors |

The scan found no production `TODO`, `FIXME`, or `HACK` markers and no source-file churn in the last 90 days.

### 6) `[ASK USER]` Questions

None. The intent-dependent questions raised during this review have been resolved.

Resolved decisions:

- Refactoring compatibility target: Python 3.9+.
- Replace arbitrary shell execution with argument-vector execution and a documented migration path.
- Replace filename-based player/perspective discovery with explicit built-in registries; third-party plugins are not part of the current contract.

### 7) Evidence

- Generated scan output and `wc -l`/git-history terminal output from 2026-09-06
- `castero/display.py`
- `castero/database.py`
- `castero/config.py`
- `castero/episode.py`
- `castero/datafile.py`
- `castero/menus/episodemenu.py`
- `tests/conftest.py`
- `tests/test_menu_episode.py`
- `castero/templates/castero.conf`

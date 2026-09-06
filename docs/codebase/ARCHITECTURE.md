# Architecture

## Core Sections (Required)

### 1) Architectural Style

- Primary style: single-process, layered TUI with object-oriented view abstractions and shared mutable application state.
- Why this classification: `__main__.py` constructs one `Database` and one `Display`; `Display` owns queues and perspectives; perspectives own menus; domain and integration objects are called directly from those presentation objects.
- Primary constraints: curses operations are tied to terminal windows; playback depends on native VLC/mpv libraries; SQLite may run from an in-memory copy and is shared with background threads.

### 2) System Flow

```text
console entry -> Display event loop -> Perspective/Menu command -> domain or integration operation -> SQLite/player/filesystem -> curses output
```

1. The setuptools console script enters `castero.__main__:main`, creates `Database`, initializes curses, and creates `Display`.
2. `Display` dynamically discovers perspective and player modules, restores the saved queue, and constructs windows/menus.
3. The main loop calls `Display.display()`, reads a key, and forwards it to the active `Perspective`.
4. Perspective handlers mutate `Queue`, call `Display` workflows, or read/write `Database`; some menu and reload work starts unmanaged threads.
5. Feed operations use `Net`/grequests and `Feed` XML parsing; playback uses a `Player` adapter; downloads use `DataFile` and the filesystem.
6. The display polls mutable state, persists modified episode state, and redraws curses windows.

### 3) Layer/Module Responsibilities

| Layer or module | Owns | Must not own | Evidence |
|-----------------|------|--------------|----------|
| Bootstrap (`__main__.py`) | CLI mode selection, lifecycle, event loop | Business rules and persistence queries | `castero/__main__.py` |
| Presentation (`display.py`, perspectives, menus) | Input, windows, selection, status, formatting | HTTP/SQL/filesystem implementations | `castero/display.py`, `castero/perspective.py`, `castero/menu.py` |
| Domain (`Feed`, `Episode`, `Queue`) | Podcast and playback state | Curses lifecycle | `castero/feed.py`, `castero/episode.py`, `castero/queue.py` |
| Persistence (`Database`) | SQLite connection, migrations, object mapping | Feed download orchestration and UI callbacks | `castero/database.py` |
| Integrations (`Net`, `DataFile`, `Subscriptions`) | HTTP defaults, files/downloads, OPML | Layout/input handling | `castero/net.py`, `castero/datafile.py`, `castero/subscriptions.py` |
| Playback adapters | Common playback contract plus VLC/mpv calls | Persistence and UI layout | `castero/player.py`, `castero/players/*.py` |

### 4) Reused Patterns

| Pattern | Where found | Why it exists |
|---------|-------------|---------------|
| Global singleton | `Config = _Config()` in `castero/config.py` | Makes configuration available through imports |
| Adapter/strategy | `Player` with `MPVPlayer` and `VLCPlayer` | Supports alternative native playback libraries |
| Template method/base class | `Menu` and `Perspective` subclasses | Shares navigation and generic key handling across layouts |
| Repository/data mapper | `Database` query methods construct `Feed`/`Episode` objects | Hides most SQL from callers |
| Polling worker queues | `Queue`, `DownloadQueue`, `Display.update()` | Advances playback/download work within the UI loop |
| Runtime discovery | `Display._load_players/_load_perspectives` | Finds package modules without an explicit registry |

### 5) Known Architectural Risks

- `Display` is an 803-line coordinator that owns curses setup/rendering, command workflows, plugin discovery, queues, persistence flushing, subprocesses, and shutdown. Most features therefore require presentation-aware tests and broad edits.
- `Database` is a 657-line persistence object that also performs HTTP concurrency, feed reconciliation, legacy conversion, migration, UI status reporting, and configuration decisions.
- Worker threads call `Menu.display()`/curses and share a SQLite connection created with `check_same_thread=False`; there is no task ownership, synchronization, cancellation, or main-thread event handoff.
- Import-time `Config` construction and unconditional `main()` execution make application modules depend on filesystem and process side effects.

### 6) Evidence

- `setup.py`
- `castero/__main__.py`
- `castero/display.py`
- `castero/perspective.py`
- `castero/database.py`
- `castero/downloadqueue.py`
- `castero/players/mpvplayer.py`
- `castero/players/vlcplayer.py`

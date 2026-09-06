# External Integrations

## Core Sections (Required)

### 1) Integration Inventory

| System | Type (API/DB/Queue/etc) | Purpose | Auth model | Criticality | Evidence |
|--------|---------------------------|---------|------------|-------------|----------|
| Podcast RSS endpoints | HTTP/XML | Fetch feed metadata and episodes | None; optional HTTP/SOCKS proxy may carry credentials | high | `castero/net.py`, `castero/feed.py` |
| Local SQLite | embedded DB | Persist feeds, episodes, queue, played state, and progress | Local filesystem permissions | high | `castero/database.py`, migrations |
| VLC/libVLC | native media backend | Audio playback | None | medium; one playback backend is required | `castero/players/vlcplayer.py` |
| mpv/libmpv | native media backend | Audio playback | None | medium; one playback backend is required | `castero/players/mpvplayer.py` |
| Local filesystem | file store | Config, database, OPML, and downloaded episodes | OS permissions | high | `castero/datafile.py`, `castero/episode.py`, `castero/subscriptions.py` |
| User-configured shell | subprocess | Run a configured command with episode fields | Local user authority | optional | `castero/display.py`, `castero/templates/castero.conf` |
| Code Climate reporter | CI SaaS | Upload coverage XML | GitHub Actions secret | low at runtime | `.github/workflows/ci.yml` |

### 2) Data Stores

| Store | Role | Access layer | Key risk | Evidence |
|-------|------|--------------|----------|----------|
| `castero.db` SQLite file | Durable feed/application state | `Database` | Default mode copies data to memory and writes it back only during orderly shutdown | `castero/database.py` |
| In-memory SQLite connection | Default active runtime store | `Database` | Shared across background threads without explicit synchronization | `castero/database.py`, `castero/display.py` |
| Download directory | Offline media | `Episode`/`DataFile` and `DownloadedMenu` | File naming/discovery logic is repeated and coupled to episode IDs | `castero/episode.py`, `castero/menus/downloadedmenu.py` |
| User config file | Runtime preferences/keybindings/proxy | global `Config` singleton | Parsed and migrated during module import | `castero/config.py` |

### 3) Secrets and Credentials Handling

- Credential sources: no application secrets are required. Proxy URLs, including possible inline credentials, are read from the local config; Code Climate uses `CC_TEST_REPORTER_ID` in CI.
- Hardcoding checks: no committed credentials were found in application config. Service URLs in project metadata and CI are public endpoints.
- Rotation or lifecycle notes: [TODO] no proxy-credential or CI-secret rotation policy is documented.

### 4) Reliability and Failure Behavior

- Retry/backoff behavior: none for RSS or media downloads. Feed reload limits grequests concurrency to three.
- Timeout policy: `request_timeout` from the config is applied by `Net.Get` and `Net.GGet` as a single requests timeout value.
- Circuit-breaker or fallback behavior: player creation tries the configured backend, then every discovered backend. Feed/download network calls have no circuit breaker; feed reload counts failures and continues.

### 5) Observability for Integrations

- Logging around external calls: user-facing status strings report feed/download operations; there is no structured logging.
- Metrics/tracing coverage: none in runtime code.
- Missing visibility gaps: worker exceptions, HTTP status/latency, SQLite contention, and incomplete download state are not centrally recorded.

### 6) Evidence

- `castero/net.py`
- `castero/database.py`
- `castero/datafile.py`
- `castero/episode.py`
- `castero/players/mpvplayer.py`
- `castero/players/vlcplayer.py`
- `castero/templates/castero.conf`
- `.github/workflows/ci.yml`

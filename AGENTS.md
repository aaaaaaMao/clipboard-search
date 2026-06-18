# AGENTS.md

## Quickstart

```bash
pip install -r requirements.txt
python main.py                  # run the app
```

## Dev commands

```bash
pytest tests/                   # run all tests
pytest tests/test_anki_connect_client.py -v  # verbose, single file
pytest tests/test_anki_connect_client.py::test_search_jp_words  # single test

./build.ps1                     # PyInstaller single-file .exe build
```

There is **no lint, typecheck, or formatter** configured in this repo.

## Tech stack

- **Python 3.13** (dev; `requirements.txt` says >= 3.10.4)
- **PyQt5** GUI, **PyInstaller** packaging
- **pytest + pytest-qt** (4 tests, integration-style — see below)
- **peewee** ORM on SQLite (favorites)
- **fugashi + unidic-lite** for Japanese tokenization
- **mdict-query-r** for local MDict dictionaries
- **pynput** (global mouse hook), **keyboard** (global hotkey), **pywin32** (clipboard)
- **DeepSeek** via `openai` library for AI translation

## Architecture

Entrypoint: `main.py` → `src/main_window.py` (central orchestrator).

### Module-level singletons in `src/__init__.py`

`ctx`, `config_manager`, and `anki_client` are instantiated at import time. Other modules import them directly:

```python
from src import config_manager, ctx, anki_client
```

### Config loading (`src/config.py`)

1. Load `configs/config.default.json`
2. Merge `configs/config.local.json` on top (`dict.update()`) — this file is **gitignored** and holds API keys.
3. Dot-notation access: `config_manager.get('main_window.width')`

### Search pipeline (`src/widgets/word_list/search_service.py`)

`SearchService` uses `ThreadPoolExecutor(max_workers=3)` to query Anki, MDict, and HuJiang in parallel. MDict init (`init_mdict_querier()`) runs via `asyncio.run()` in the constructor — synchronous blocking.

### Mouse monitoring (`src/services/mouse_monitor_worker.py`)

`MouseMonitorWorker` is a **QThread** that starts a `pynput.mouse.Listener` in `run()`, blocking via `listener.join()`. It also registers a global `keyboard` Alt hotkey. Signals cross the thread boundary via Qt signals.

## Test prerequisites

Tests in `tests/test_anki_connect_client.py` are **integration tests** that call the real AnkiConnect HTTP API. Anki must be running locally with the AnkiConnect add-on listening on `localhost:8765`.

## External data

- **MDict dictionaries** (`.mdx`, `.db`, `.css`) belong in `resources/dictionaries/` — **gitignored**.
- **Favorites database** at `data/favorites.db` — auto-created by peewee on first import, **gitignored**.
- **AI API keys** go in `configs/config.local.json` — **gitignored**.

## Windows-only

The app uses `pywin32` for clipboard access and `pynput` for global mouse hooks. It will not run on macOS or Linux.

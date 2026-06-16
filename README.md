# Downloads Warden — MCP Server

An MCP server for automatic and intelligent management of your Downloads folder via Claude Desktop.

---

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Claude Desktop Setup](#claude-desktop-setup)
- [Testing with MCP Inspector](#testing-with-mcp-inspector)
- [Running Tests](#running-tests)
- [Available Tools](#available-tools)

---

## Features

Downloads Warden provides 8 tools for managing your Downloads folder:

| # | Tool | Description |
|---|------|-------------|
| 1 | `scan_downloads_tool` | Scan folder and return detailed statistics |
| 2 | `smart_sort_files_tool` | Sort files by type (Documents, Media, Installers, Code, Archives, Other) |
| 3 | `sort_by_date_tool` | Sort files into year-month folders (YYYY-MM) |
| 4 | `deduplicate_by_hash_tool` | Remove duplicate files using SHA-256 |
| 5 | `deduplicate_folders_tool` | Remove folders with identical content |
| 6 | `auto_extract_and_cleanup_tool` | Extract ZIP archives and delete them afterwards |
| 7 | `clear_installers_tool` | Delete old installer files |
| 8 | `find_large_files_tool` | Find files above a size threshold |

---

## Architecture

The project follows a strict 4-layer clean architecture:

```
src/
├── domain/               # Domain layer — pure business logic
│   ├── config.py         # All categories, extensions and thresholds (frozen dataclasses)
│   ├── exceptions.py     # Custom exception hierarchy (WardenError → ...)
│   ├── events.py         # Observer pattern — EventBus + event dataclasses
│   ├── strategies.py     # Strategy pattern — SortStrategy ABC + StrategyFactory
│   └── models.py         # Immutable domain models (frozen dataclasses)
│
├── infrastructure/       # Infrastructure layer — all file-system I/O
│   └── file_repository.py  # BaseFileRepository ABC + LocalFileRepository
│
├── application/          # Application layer — Use Cases (orchestrators)
│   ├── base_sort_use_case.py   # Template Method — sort pipeline skeleton
│   ├── sort_use_case.py        # SmartSortUseCase + DateSortUseCase
│   ├── scan_use_case.py
│   ├── deduplicate_use_case.py
│   ├── extract_use_case.py
│   └── clean_use_case.py
│
├── container.py          # DI Container — wires all dependencies
└── server.py             # MCP interface — thin adapter only
```

### Design Principles
- **Strategy Pattern** — `ExtensionSortStrategy` / `DateSortStrategy` with a `StrategyFactory` registry
- **Template Method** — `BaseSortUseCase` defines the pipeline; subclasses inject only a strategy
- **Observer / EventBus** — Use Cases publish events; logging is subscribed separately in the container
- **Repository Pattern** — `BaseFileRepository` ABC allows swapping the file system for a mock without changing any business logic
- **Immutability** — All domain models and config objects are `@dataclass(frozen=True)`
- **Custom Exceptions** — `WardenError → FolderNotFoundError / HashComputationError / ExtractionError / ...`
- **Collision Resolution** — Sequential counter (`_1` … `_99`) → microsecond timestamp fallback → `CollisionError`

---

## Installation

### Prerequisites
- Python 3.11 or higher
- Claude Desktop

### Steps

```bash
# 1. Enter the project directory
cd downloads-warden

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 4. Install the project with dev dependencies
pip install -e ".[dev]"

# 5. Verify the server starts correctly
python run_server.py
```

---

## Claude Desktop Setup

Open the Claude Desktop config file:
```
%APPDATA%\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```

Add the following:
```json
{
  "mcpServers": {
    "downloads-warden": {
      "command": "C:\\path\\to\\downloads-warden\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\downloads-warden\\run_server.py"]
    }
  }
}
```

> ⚠️ Replace `C:\\path\\to\\downloads-warden` with the actual path on your machine.

Restart Claude Desktop, then go to Settings → Developer → Local MCP servers — "downloads-warden" should appear with a green ✓.

---

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

- **Transport Type:** STDIO
- **Command:** `.venv\Scripts\python.exe`
- **Arguments:** `run_server.py`

Click **Connect** and verify all 8 tools appear.

---

## Running Tests

```bash
# All tests (unit + integration) with coverage
python -m pytest

# Unit tests only (no disk I/O)
python -m pytest tests/unit

# Integration tests only
python -m pytest tests/integration
```

Expected result: **47 passed — 92% coverage**

---

## Available Tools

| Tool | Key Parameters | Defaults |
|------|---------------|----------|
| `scan_downloads_tool` | `folder_path` | User Downloads folder |
| `smart_sort_files_tool` | `folder_path`, `dry_run` | `dry_run=true` |
| `sort_by_date_tool` | `folder_path`, `dry_run` | `dry_run=true` |
| `deduplicate_by_hash_tool` | `folder_path`, `dry_run` | `dry_run=true` |
| `deduplicate_folders_tool` | `folder_path`, `dry_run` | `dry_run=true` |
| `auto_extract_and_cleanup_tool` | `folder_path`, `dry_run` | `dry_run=true` |
| `clear_installers_tool` | `folder_path`, `days_old`, `dry_run` | `days_old=30`, `dry_run=true` |
| `find_large_files_tool` | `folder_path`, `min_size_mb` | `min_size_mb=500` |

> ⚠️ **Always run with `dry_run=true` first** before any destructive operation.

---

## Troubleshooting

**Server does not connect in Claude Desktop**
- Verify the paths in `claude_desktop_config.json` are correct and the virtual environment exists

**`ModuleNotFoundError: No module named 'src'`**
- Make sure you installed with `pip install -e ".[dev]"` and not just `pip install -r requirements.txt`

**Tools do not appear in Inspector**
- Click Disconnect → Connect again and check the server starts without errors

---

## License

MIT License

---

**Built with ❤️ using FastMCP**

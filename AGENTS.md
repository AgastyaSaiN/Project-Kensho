# Repository Guidelines

## Project Structure & Module Organization
- `src/kensho/` holds the application code: `app.py` bootstraps the Tk UI, `models.py` contains timer logic, `notifications.py` and `storage.py` wrap Windows-oriented toasts and state I/O.
- UI widgets live in `src/kensho/ui/`, with `clock_card.py` and `settings_dialog.py` composing the interface.
- Persisted data is written to `data/app_state.json` at runtime; the directory is created on demand.
- No dedicated test suite or assets directory exists yet—add new modules under `src/` and keep UI elements grouped in `ui/`.

## Build, Test, and Development Commands
- `python -m venv .venv && .\.venv\Scripts\activate` sets up the required virtual environment on Windows.
- `pip install -r requirements.txt` installs the lone runtime dependency (`win10toast`).
- `python -m src.kensho.app` launches the desktop app with the current UI changes.
- `python3 -m compileall src` provides a quick syntax check across modules when running in WSL or other POSIX shells.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, type hints where practical, and descriptive function names (`_set_minimal_mode`, `_refresh_identifier_labels`).
- Keep UI constants uppercase (`ACCENT_BLUE`, `CARD_BG`) and module globals confined to a small block near the top of each file.
- Prefer Tkinter widgets configured via keyword arguments for clarity; add concise comments before complex layout or state logic only when necessary.

## Testing Guidelines
- Manual verification is the norm: run `python -m src.kensho.app` and toggle timers, minimize mode, and export flows.
- For automated smoke checks before PRs, run `python3 -m compileall src` (or the Windows equivalent) to ensure the codebase remains importable.
- Naming for future tests should mirror module under test (e.g., `tests/test_models.py`).

## Commit & Pull Request Guidelines
- Use short, imperative commit subjects (e.g., “Add minimize toggle to shell UI”) and group related edits by feature.
- Reference issue IDs in the body when applicable, and include brief context on UX changes or regression risk.
- PRs should describe the UI flow touched, list manual verification steps, and attach screenshots or GIFs when altering visible components.

## Platform & Configuration Notes
- Notification features depend on Windows-only libraries (`win10toast`, `winsound`); expect graceful no-ops on other platforms but flag regressions in reviews.
- When extending persistence, prefer JSON-friendly types so `storage.py` can serialize state without explicit migrations.

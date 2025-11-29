# Packaging Kenshō

## Prerequisites
- Windows host with Python 3.11+ installed (the build script defaults to `python` on PATH).
- Virtual environment activated and dependencies installed:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\activate
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  ```

## Build Steps
1. From the repository root, run the helper script:
   ```powershell
   packaging\build_windows_exe.bat
   ```
   Supply a custom interpreter if needed, e.g. `packaging\build_windows_exe.bat .venv\Scripts\python`.
2. The script invokes PyInstaller in one-folder mode, producing a distributable under `dist\Kensho\`.
3. Share `dist\Kensho\Kensho.exe` alongside its generated support files. Users can launch the timer directly from that folder.

## Runtime Data
- App state persists to `%APPDATA%\Kensho\app_state.json`. Override the location by setting `KENSHO_DATA_DIR` before starting the app.
- When packaging, no additional assets need bundling—the application generates state files on demand.

## Verification
- After building, double-click `dist\Kensho\Kensho.exe` to confirm the UI launches, the minimize toggle works, and clocks retain state between runs.
- Run the executable on a clean Windows profile to ensure `win10toast` notifications display and the state file creates without elevation.

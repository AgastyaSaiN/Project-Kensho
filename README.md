# Kenshō

A minimalist, Zen-inspired focus timer application built with Python and PySide6.

## Features
- **Concentric Timers**: Visual representation of multiple timers.
- **Widget Mode**: Always-on-top, translucent mini-timer.
- **Soundscapes**: Zen instruments (Piano, Guitar, Kalimba, etc.) for notifications.
- **History**: Track your daily focus sessions.
- **Persistence**: Auto-save state.

## � Build (Single-File EXE)

To create a standalone `Kensho.exe` that runs on any Windows PC without installation:

1.  **Build**:
    ```powershell
    python build.py
    ```
2.  **Run**:
    - The output file is `dist/Kensho.exe`.
    - You can move this file anywhere (Desktop, USB drive, etc.) and run it.

### Persistence
Your clocks and history are saved in `~/.kensho` (User Home Directory) and persist between runs.

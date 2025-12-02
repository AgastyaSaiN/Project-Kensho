# Kenshō

A minimalist, Zen-inspired focus timer application built with Python and PySide6.

## Features
- **Concentric Timers**: Visual representation of multiple timers.
- **Widget Mode**: Always-on-top, translucent mini-timer.
- **Soundscapes**: Zen instruments (Piano, Guitar, Kalimba, etc.) for notifications.
- **History**: Track your daily focus sessions.
- **Persistence**: Auto-save state.

## 💿 Build (Windows Installer)

To create a professional Windows Installer (`.msi`) that installs Kensho to Program Files:

1.  **Build**:
    ```powershell
    python setup.py bdist_msi
    ```
2.  **Install**:
    - The output file is `dist/Kensho-1.0-win64.msi`.
    - Double-click to install.
    - It creates shortcuts on your **Desktop** and **Start Menu**.
    - You can uninstall it via Windows Settings like any other app.

### Persistence
Your clocks and history are saved in `~/.kensho` (User Home Directory) and persist between runs.

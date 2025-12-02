# Kenshō

A minimalist, Zen-inspired focus timer application built with Python and PySide6.

## Features
- **Concentric Timers**: Visual representation of multiple timers.
- **Widget Mode**: Always-on-top, translucent mini-timer.
- **Soundscapes**: Zen instruments (Piano, Guitar, Kalimba, etc.) for notifications.
- **History**: Track your daily focus sessions.
- **Persistence**: Auto-save state.

## 🐳 Running with Docker

This application is containerized for consistency.

### Prerequisites
1.  **Docker Desktop** installed.
2.  **X Server** (for Windows):
    - Install [VcXsrv](https://sourceforge.net/projects/vcxsrv/).
    - Launch **XLaunch** with these settings:
        - **Multiple windows**
        - **Start no client**
        - **Disable access control** (Check this box!)

### Run
```bash
docker-compose up --build
```
The application window should appear on your desktop.

### Persistence
Your clocks and history are saved in a Docker volume (`kensho_data`) and persist between restarts.

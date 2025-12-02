import sys
import os
from cx_Freeze import setup, Executable

# Add src to path so cx_Freeze can find kensho package
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "sys", "kensho"],
    "includes": ["PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets", "PySide6.QtMultimedia"],
    "include_files": [
        ("src/kensho/resources", "src/kensho/resources"),
    ],
    "excludes": ["tkinter", "unittest", "email", "http", "xml", "pydoc"],
}

# Base set to "Win32GUI" for GUI application
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Kensho",
    version="1.0",
    description="Zen-inspired Focus Timer",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "run.py",
            base=base,
            target_name="Kensho.exe",
            shortcut_name="Kensho",
            shortcut_dir="DesktopFolder",
        ),
        Executable(
            "run.py",
            base=base,
            target_name="Kensho.exe",
            shortcut_name="Kensho",
            shortcut_dir="ProgramMenuFolder",
        )
    ],
)

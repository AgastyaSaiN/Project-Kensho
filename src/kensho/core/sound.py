import os
import sys
from pathlib import Path
from typing import List
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect

class SoundManager:
    _effect = None
    
    # Handle Frozen path (cx_Freeze or PyInstaller)
    if getattr(sys, 'frozen', False):
        # PyInstaller uses _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            _base_path = Path(sys._MEIPASS) / "src" / "kensho" / "resources"
        else:
            # cx_Freeze: Resources are relative to the executable
            # We copied "src/kensho/resources" to "src/kensho/resources" in setup.py
            # So it should be at {EXE_DIR}/src/kensho/resources
            _base_path = Path(sys.executable).parent / "src" / "kensho" / "resources"
    else:
        _base_path = Path(__file__).parent.parent / "resources"
        
    _sounds_dir = _base_path / "sounds"

    @classmethod
    def get_available_sounds(cls) -> List[str]:
        if not cls._sounds_dir.exists():
            return []
        
        files = [f.stem for f in cls._sounds_dir.glob("*.wav")]
        files.sort()
        
        # Format names: "piano_c4" -> "Piano - C4"
        formatted = []
        for f in files:
            parts = f.split('_')
            if len(parts) >= 2:
                category = parts[0].capitalize()
                note = parts[1].upper()
                formatted.append(f"{category} - {note}")
            else:
                formatted.append(f.replace('_', ' ').title())
                
        return formatted

    @classmethod
    def play_sound(cls, sound_name: str):
        if not sound_name:
            return
            
        # Convert "Piano - C4" back to "piano_c4"
        filename = sound_name.lower().replace(' - ', '_').replace(' ', '_')
        
        file_path = cls._sounds_dir / f"{filename}.wav"
        if not file_path.exists():
            return
            
        if cls._effect is None:
            cls._effect = QSoundEffect()
            
        cls._effect.setSource(QUrl.fromLocalFile(str(file_path)))
        cls._effect.setVolume(1.0)
        cls._effect.play()

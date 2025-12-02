import PyInstaller.__main__
import os
import shutil

def build():
    print("Building Kensho...")
    
    # Clean dist/build
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
        
    # PyInstaller Args
    args = [
        "run.py",
        "--name=Kensho",
        "--noconfirm",
        "--windowed",  # No console
        "--clean",
        # Add data: source;dest
        "--add-data=src/kensho/resources;src/kensho/resources",
        # Icon (if we had one)
        # "--icon=icon.ico", 
    ]
    
    PyInstaller.__main__.run(args)
    print("Build Complete! Check dist/Kensho")

if __name__ == "__main__":
    build()

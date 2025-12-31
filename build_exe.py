import os
import subprocess
import sys

def build():
    print("Starting build process with PyInstaller...")
    
    # PyInstaller command
    # --onefile: Create a single executable
    # --noconsole: Hide the console window (optional, depends on if you want it)
    # --add-data: Bundle data files (format: "source;dest" on Windows)
    # --hidden-import: Ensure PIL and tkinter are included
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "main",
        "--add-data", f"images{os.pathsep}images",
        "--add-data", f"questions-auto.json{os.pathsep}.",
        "--add-data", f"instruction.pdf{os.pathsep}.",
        "--add-data", f"lib{os.pathsep}lib",
        "main.py"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild successful! You can find main.exe in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
    except FileNotFoundError:
        print("\nError: PyInstaller not found. Please install it with 'pip install pyinstaller'.")

if __name__ == "__main__":
    build()

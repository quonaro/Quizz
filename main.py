#!/usr/bin/env python3
"""
Main entry point for the Quiz Application.
"""

import sys
import argparse
import json
import base64
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.ui.main_window import main  # noqa: E402
from src.quiz_builder import QuizBuilder, create_sample_quiz  # noqa: E402
from src.quiz_loader import QuizValidationError  # noqa: E402


def select_quiz_file():
    """
    Show file dialog to select a quiz JSON file.

    Returns:
        Path to selected file or None if cancelled.
    """
    try:
        from PyQt6.QtWidgets import QApplication, QFileDialog

        # Create minimal QApplication for file dialog
        app = QApplication(sys.argv)

        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Выберите файл квиза",
            str(Path.home()),
            "JSON Files (*.json);;All Files (*)",
        )

        # Clean up application
        app.quit()

        if file_path:
            return Path(file_path)
        return None
    except Exception as e:
        print(f"Error showing file dialog: {e}")
        return None


def load_quiz_from_path(quiz_path: Path):
    """
    Load quiz from a given path (file or folder).

    Args:
        quiz_path: Path to quiz JSON file or folder containing quiz.

    Returns:
        Tuple of (quiz_data, quiz_file_path) or (None, None) on error.
    """
    # Resolve relative paths relative to current working directory
    if not quiz_path.is_absolute():
        quiz_path = Path.cwd() / quiz_path
    
    # Normalize the path (resolve .. and .)
    quiz_path = quiz_path.resolve()
    
    if not quiz_path.exists():
        print(f"Error: Quiz path does not exist: {quiz_path}", file=sys.stderr)
        print(f"Current working directory: {Path.cwd()}", file=sys.stderr)
        return None, None

    try:
        if quiz_path.is_file():
            # Single JSON file
            quiz_folder = quiz_path.parent
            with open(quiz_path, "r", encoding="utf-8") as f:
                quiz_data = json.load(f)

            # Check if it's new schema format and convert if needed
            is_new_schema = False
            if "questions" in quiz_data and len(quiz_data["questions"]) > 0:
                first_question = quiz_data["questions"][0]
                if "text" in first_question:
                    is_new_schema = True
                elif "options" in first_question and len(first_question["options"]) > 0:
                    if isinstance(first_question["options"][0], dict):
                        is_new_schema = True

            # Convert if needed
            if is_new_schema:
                quiz_data = QuizBuilder.convert_from_new_schema(quiz_data, quiz_folder)
            else:
                quiz_data = QuizBuilder._resolve_image_paths(quiz_data, quiz_folder)

            # Validate converted data
            from src.quiz_loader import QuizLoader  # noqa: E402

            loader = QuizLoader()
            loader.validate_quiz(quiz_data)
            quiz_file_path = str(quiz_path.absolute())
            print(f"Loaded quiz from: {quiz_file_path}")
            return quiz_data, quiz_file_path
        else:
            # Folder
            quiz_data, quiz_file_path = QuizBuilder.load_from_quiz_folder(quiz_path)
            print(f"Loaded quiz from folder: {quiz_path}")
            return quiz_data, quiz_file_path
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None, None
    except QuizValidationError as e:
        print(f"Quiz validation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None, None
    except Exception as e:
        print(f"Error loading quiz: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None, None


def load_embedded_quiz():
    """
    Load quiz embedded in the executable.
    Only loads embedded quiz when running from a compiled executable (exe).
    """
    # Only load embedded quiz if running from compiled executable
    # Nuitka sets sys.frozen = True when running from exe
    if not getattr(sys, "frozen", False):
        return None, None

    try:
        # Try to import embedded quiz module
        from src import embedded_quiz  # noqa: E402

        if hasattr(embedded_quiz, "get_quiz_data"):
            quiz_data = embedded_quiz.get_quiz_data()
            # Check if quiz_data is not empty (empty dict means no embedded quiz)
            if quiz_data and quiz_data.get("questions"):
                return quiz_data, None
    except (ImportError, Exception):
        pass
    return None, None


def embed_quiz_in_code(quiz_path: Path, output_path: Path):
    """
    Embed quiz JSON and images into a Python module for building into exe.

    Args:
        quiz_path: Path to quiz JSON file or folder containing quiz.
        output_path: Path where to save the embedded_quiz.py module.
    """
    # Load quiz data and collect original image paths before conversion
    original_image_paths = {}  # Map question index -> original image paths

    if quiz_path.is_file():
        # Single JSON file
        quiz_folder = quiz_path.parent
        quiz_file = quiz_path
        with open(quiz_file, "r", encoding="utf-8") as f:
            raw_quiz_data = json.load(f)

        # Save original image paths before conversion
        for idx, question in enumerate(raw_quiz_data.get("questions", [])):
            if "images" in question:
                original_image_paths[idx] = question["images"]

        # Check if it's new schema format and convert if needed
        is_new_schema = False
        if "questions" in raw_quiz_data and len(raw_quiz_data["questions"]) > 0:
            first_question = raw_quiz_data["questions"][0]
            if "text" in first_question:
                is_new_schema = True
            elif "options" in first_question and len(first_question["options"]) > 0:
                if isinstance(first_question["options"][0], dict):
                    is_new_schema = True

        if is_new_schema:
            quiz_data = QuizBuilder.convert_from_new_schema(raw_quiz_data, quiz_folder)
        else:
            quiz_data = QuizBuilder._resolve_image_paths(raw_quiz_data, quiz_folder)

        # Validate
        from src.quiz_loader import QuizLoader  # noqa: E402

        loader = QuizLoader()
        loader.validate_quiz(quiz_data)
    else:
        # Folder - use load_from_quiz_folder
        quiz_folder = quiz_path
        # Load raw data first to get original paths
        json_files = list(quiz_folder.glob("*.json"))
        if json_files:
            with open(json_files[0], "r", encoding="utf-8") as f:
                raw_quiz_data = json.load(f)
            # Save original image paths
            for idx, question in enumerate(raw_quiz_data.get("questions", [])):
                if "images" in question:
                    original_image_paths[idx] = question["images"]
        quiz_data, _ = QuizBuilder.load_from_quiz_folder(quiz_folder)

    # Collect all images referenced in the quiz
    # Use original paths from raw data if available, otherwise use converted paths
    images_data = {}
    for idx, question in enumerate(quiz_data.get("questions", [])):
        if "images" in question:
            # Try to use original paths first (before conversion to absolute)
            image_paths = original_image_paths.get(idx, question["images"])
            if isinstance(image_paths, str):
                image_paths = [image_paths]
            elif not isinstance(image_paths, list):
                image_paths = (
                    question["images"]
                    if isinstance(question["images"], list)
                    else [question["images"]]
                )

            # Also get converted paths for file lookup
            converted_images = question["images"]
            if isinstance(converted_images, str):
                converted_images = [converted_images]

            for orig_path, conv_path in zip(image_paths, converted_images):
                # Use original relative path as key
                rel_path = (
                    str(Path(orig_path).as_posix())
                    if isinstance(orig_path, str)
                    else str(Path(conv_path).name)
                )

                # Find the actual file using converted (absolute) path
                img_path_obj = Path(conv_path)
                if not img_path_obj.is_absolute():
                    img_path_obj = quiz_folder / conv_path

                # Try to find the image file
                if img_path_obj.exists() and img_path_obj.is_file():
                    # Read image and encode as base64
                    with open(img_path_obj, "rb") as f:
                        img_data = f.read()
                        img_base64 = base64.b64encode(img_data).decode("utf-8")
                    images_data[rel_path] = img_base64

    # Convert image paths in quiz_data to use embedded images
    # We'll use a special prefix to indicate embedded images
    for idx, question in enumerate(quiz_data.get("questions", [])):
        if "images" in question:
            # Use original paths for keys
            orig_paths = original_image_paths.get(idx, question["images"])
            if isinstance(orig_paths, str):
                orig_paths = [orig_paths]
            elif not isinstance(orig_paths, list):
                orig_paths = (
                    [question["images"]]
                    if isinstance(question["images"], str)
                    else question["images"]
                )

            images = question["images"]
            if isinstance(images, str):
                images = [images]

            embedded_images = []
            for orig_path, conv_path in zip(orig_paths, images):
                # Use original relative path as key
                if isinstance(orig_path, str):
                    rel_path = str(Path(orig_path).as_posix())
                else:
                    # Fallback: try to extract from converted path
                    try:
                        rel_path = str(Path(conv_path).relative_to(quiz_folder))
                    except (ValueError, TypeError):
                        rel_path = Path(conv_path).name

                if rel_path in images_data:
                    embedded_images.append(f"__EMBEDDED__:{rel_path}")
                else:
                    embedded_images.append(conv_path)

            if len(embedded_images) == 1:
                question["images"] = embedded_images[0]
            else:
                question["images"] = embedded_images

    # Generate Python module code
    quiz_json_str = json.dumps(quiz_data, indent=2, ensure_ascii=False)

    module_code = f'''"""
Embedded quiz data for standalone executable.
This file is auto-generated during build process.
"""

import base64
from pathlib import Path
import tempfile
import os

# Embedded quiz JSON data
QUIZ_JSON = """{quiz_json_str}"""

# Embedded images (base64 encoded)
EMBEDDED_IMAGES = {{
'''

    # Add images data
    for rel_path, img_base64 in images_data.items():
        # Escape quotes in path
        safe_path = rel_path.replace('"', '\\"')
        module_code += f'    "{safe_path}": "{img_base64}",\n'

    module_code += '''}

# Cache for temporary image files
_temp_image_cache = {}


def get_quiz_data():
    """Load and return quiz data from embedded JSON."""
    import json
    return json.loads(QUIZ_JSON)


def get_embedded_image_path(embedded_path: str):
    """
    Get a temporary file path for an embedded image.
    
    Args:
        embedded_path: Path in format "__EMBEDDED__:relative/path/to/image.jpg"
        
    Returns:
        Path to temporary file containing the image.
    """
    if not embedded_path.startswith("__EMBEDDED__:"):
        # Not an embedded image, return as-is
        return embedded_path
    
    # Extract relative path
    rel_path = embedded_path.replace("__EMBEDDED__:", "", 1)
    
    # Check cache
    if rel_path in _temp_image_cache:
        cached_path = _temp_image_cache[rel_path]
        if Path(cached_path).exists():
            return cached_path
    
    # Decode and save to temp file
    if rel_path not in EMBEDDED_IMAGES:
        return embedded_path
    
    img_base64 = EMBEDDED_IMAGES[rel_path]
    img_data = base64.b64decode(img_base64)
    
    # Create temp file
    temp_dir = Path(tempfile.gettempdir()) / "quiz_embedded_images"
    temp_dir.mkdir(exist_ok=True)
    
    # Use filename from rel_path
    filename = Path(rel_path).name
    temp_file = temp_dir / filename
    
    with open(temp_file, 'wb') as f:
        f.write(img_data)
    
    # Cache it
    _temp_image_cache[rel_path] = str(temp_file)
    
    return str(temp_file)


def resolve_embedded_images(quiz_data):
    """
    Resolve embedded image paths in quiz data to temporary file paths.
    
    Args:
        quiz_data: Quiz data dictionary (may be modified in-place).
        
    Returns:
        Quiz data with resolved image paths.
    """
    for question in quiz_data.get("questions", []):
        if "images" in question:
            images = question["images"]
            if isinstance(images, str):
                question["images"] = get_embedded_image_path(images)
            elif isinstance(images, list):
                resolved_images = []
                for img in images:
                    resolved_images.append(get_embedded_image_path(img))
                question["images"] = resolved_images
    
    return quiz_data
'''

    # Write module
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(module_code)

    print(f"Embedded quiz data written to: {output_path}")
    print(f"Embedded {len(images_data)} images")


def build_exe(quiz_path: Path, platform: str = None):
    """
    Build executable with embedded quiz.

    Args:
        quiz_path: Path to quiz JSON file or folder.
        platform: Target platform (linux, windows, macos). If None, uses current platform.
    """
    import subprocess

    project_root = Path(__file__).parent
    embedded_quiz_path = project_root / "src" / "embedded_quiz.py"

    print(f"Embedding quiz from: {quiz_path}")
    embed_quiz_in_code(quiz_path, embedded_quiz_path)

    print("\nBuilding executable with Nuitka...")

    # Check if Nuitka is installed
    try:
        import nuitka  # noqa: F401
    except ImportError:
        print("Error: Nuitka is not installed.")
        print("Install it with: pip install nuitka")
        sys.exit(1)

    # Check for cross-compilation requirements
    import shutil
    import platform as platform_module

    if platform == "windows" and platform_module.system() == "Linux":
        print("\nCross-compiling for Windows from Linux...")
        # Check for MinGW-w64
        if not shutil.which("x86_64-w64-mingw32-gcc") and not shutil.which(
            "i686-w64-mingw32-gcc"
        ):
            print(
                "\nWarning: MinGW-w64 not found. It's required for cross-compilation to Windows."
            )
            print("Install it with one of the following commands:")
            print("  Ubuntu/Debian: sudo apt-get install mingw-w64")
            print("  Fedora/RHEL:   sudo dnf install mingw64-gcc")
            print("  Arch:          sudo pacman -S mingw-w64-gcc")
            print(
                "\nNuitka will attempt to download MinGW automatically, but manual installation is recommended."
            )
            response = input("\nContinue anyway? (y/N): ")
            if response.lower() != "y":
                print("Build cancelled.")
                sys.exit(1)
        else:
            print("MinGW-w64 found. Cross-compilation should work.")

    # Check if patchelf is installed (required for standalone mode on Linux)
    if platform != "windows" and platform_module.system() == "Linux":
        if not shutil.which("patchelf"):
            print(
                "\nWarning: 'patchelf' is not installed, which is required for standalone mode on Linux."
            )
            print("Install it with one of the following commands:")
            print("  Ubuntu/Debian: sudo apt install patchelf")
            print("  Fedora/RHEL:   sudo dnf install patchelf")
            print("  Arch:          sudo pacman -S patchelf")
            print(
                "\nAlternatively, you can build without standalone mode (not recommended for distribution)."
            )
            response = input("\nContinue anyway? (y/N): ")
            if response.lower() != "y":
                print("Build cancelled.")
                sys.exit(1)

    # Determine Nuitka command
    nuitka_cmd = (
        "nuitka3"
        if Path("/usr/bin/nuitka3").exists() or Path("/usr/local/bin/nuitka3").exists()
        else "nuitka"
    )

    # Build directory
    build_dir = project_root / "build"
    build_dir.mkdir(exist_ok=True)
    
    # Cache directory for Nuitka
    cache_dir = build_dir / ".nuitka-cache"
    cache_dir.mkdir(exist_ok=True)
    
    # Determine number of jobs for parallel compilation
    import os
    jobs = os.environ.get("NUITKA_JOBS")
    if not jobs:
        # Auto-detect CPU cores
        import multiprocessing
        jobs = str(multiprocessing.cpu_count())
    
    # Build command
    cmd = [
        nuitka_cmd,
        "--standalone",
        "--onefile",
        "--enable-plugin=pyqt6",
        "--jobs=" + jobs,
        "--cache-dir=" + str(cache_dir),
    ]

    # Include schema directory if it exists
    schema_dir = project_root / "schema"
    if schema_dir.exists() and schema_dir.is_dir():
        cmd.append("--include-data-dir=schema=schema")

    # Continue building the command
    cmd.extend(
        [
            "--include-package=src",
            "--output-dir=" + str(build_dir),
            "--output-filename=quiz",
            "--assume-yes-for-downloads",
            "--show-progress",
            "--show-memory",
        ]
    )

    # Add platform-specific options
    if platform:
        if platform == "windows":
            # Enable console mode to show errors and debug output
            cmd.append("--windows-console-mode=force")
            # Add MinGW for cross-compilation from Linux
            if platform_module.system() == "Linux":
                cmd.append("--mingw64")
        elif platform == "macos":
            cmd.append("--macos-create-app-bundle")
        elif platform == "linux":
            # Linux is default, no extra options needed
            pass

    cmd.append(str(project_root / "main.py"))

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        print("\nBuild completed successfully!")
        # Find executable
        exe_paths = [
            build_dir / "quiz.exe",
            build_dir / "quiz",
            project_root / "quiz.exe",
            project_root / "quiz",
        ]
        for exe_path in exe_paths:
            if exe_path.exists():
                print(f"Executable location: {exe_path}")
                break
    else:
        print("\nBuild failed!")
        sys.exit(1)


if __name__ == "__main__":
    # Enable console output for error messages (especially important for Windows exe)
    import os
    if getattr(sys, "frozen", False) and os.name == "nt":
        # Running as compiled exe on Windows - ensure console is available
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Allocate console if not already available
            kernel32.AllocConsole()
            # Redirect stdout and stderr to console
            sys.stdout = open("CONOUT$", "w", encoding="utf-8")
            sys.stderr = open("CONOUT$", "w", encoding="utf-8")
        except Exception:
            pass  # Console already available or allocation failed
    
    parser = argparse.ArgumentParser(
        description="Quiz Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default quiz
  python main.py /path/to/quiz.json # Run with specified quiz file
  python main.py /path/to/quiz/folder # Run with quiz from folder
        """,
    )
    parser.add_argument(
        "quiz_path", nargs="?", help="Path to quiz JSON file or folder containing quiz"
    )

    args = parser.parse_args()
    
    # Debug output
    if args.quiz_path:
        print(f"Loading quiz from: {args.quiz_path}")
        print(f"Current working directory: {Path.cwd()}")

    # Normal run mode
    quiz_data = None
    quiz_file_path = None

    # Try to load embedded quiz first (if running from exe)
    quiz_data, quiz_file_path = load_embedded_quiz()
    if quiz_data:
        print("Loaded embedded quiz from executable")
        # Resolve embedded images
        try:
            from src.embedded_quiz import resolve_embedded_images  # noqa: E402

            quiz_data = resolve_embedded_images(quiz_data)
        except ImportError:
            # embedded_quiz module not found, skip image resolution
            pass

    # If quiz_path provided, load from that
    if quiz_data is None and args.quiz_path:
        quiz_path = Path(args.quiz_path)
        quiz_data, quiz_file_path = load_quiz_from_path(quiz_path)
        if quiz_data is None:
            print("\nFailed to load quiz. Press any key to exit...", file=sys.stderr)
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                pass
            sys.exit(1)

    # Try to load from quiz folder if no quiz loaded yet
    if quiz_data is None:
        # If no quiz_path was provided, show file selection dialog
        if not args.quiz_path:
            print("No quiz path provided. Opening file selection dialog...")
            selected_path = select_quiz_file()
            if selected_path:
                quiz_data, quiz_file_path = load_quiz_from_path(selected_path)
                if quiz_data is None:
                    sys.exit(1)
            else:
                print("No file selected. Exiting...")
                sys.exit(0)
        else:
            # Try to load from default quiz folder
            try:
                quiz_data, quiz_file_path = QuizBuilder.load_from_quiz_folder()
                print("Loaded quiz from quiz folder")
            except FileNotFoundError as e:
                print(f"Quiz folder not found or empty: {e}")
                print("Falling back to sample quiz...")
            except QuizValidationError as e:
                print(f"Quiz validation failed: {e}")
                print("Falling back to sample quiz...")
            except Exception as e:
                print(f"Error loading quiz: {e}")
                print("Falling back to sample quiz...")

    # Fallback to sample quiz if loading from folder failed
    if quiz_data is None:
        quiz_data = create_sample_quiz()

    main(quiz_data, quiz_file_path)

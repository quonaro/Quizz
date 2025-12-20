#!/bin/bash
# Build script for Quiz Application using PyInstaller
# Usage:
#   ./build.sh                                    # Build without embedded quiz
#   ./build.sh /path/to/quiz.json                 # Build with embedded quiz from JSON file
#   ./build.sh /path/to/quiz                      # Build with embedded quiz from folder
#   ./build.sh --platform linux                  # Build for Linux
#   ./build.sh --platform windows                # Build for Windows
#   ./build.sh --platform macos                  # Build for macOS
#   ./build.sh /path/to/quiz.json --platform windows  # Build with quiz for Windows
#   ./build.sh --no-clean                        # Incremental build (keep cache)

set -e  # Exit on error

QUIZ_PATH=""
PLATFORM=""
BUILD_MODE=""
CLEAN_BUILD=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --no-clean|--incremental)
            CLEAN_BUILD=false
            shift
            ;;
        *)
            if [ -z "$QUIZ_PATH" ]; then
                QUIZ_PATH="$1"
            fi
            shift
            ;;
    esac
done

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed."
    echo "Install it from: https://github.com/astral-sh/uv"
    echo "Or with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Validate platform if provided
if [ -n "$PLATFORM" ]; then
    case "$PLATFORM" in
        linux|windows|macos)
            echo "Target platform: $PLATFORM"
            ;;
        *)
            echo "Error: Invalid platform '$PLATFORM'"
            echo "Supported platforms: linux, windows, macos"
            exit 1
            ;;
    esac
fi

# Note: PyInstaller doesn't support cross-compilation
# You need to build on the target platform or use Docker/CI
if [ -n "$PLATFORM" ] && [ "$PLATFORM" = "windows" ] && [ "$(uname -s)" = "Linux" ]; then
    echo "Warning: PyInstaller doesn't support cross-compilation from Linux to Windows."
    echo "You need to build on Windows or use a Windows CI runner."
    echo "Continuing anyway, but the build may fail..."
fi

# If quiz path provided, use Python's --build mode
if [ -n "$QUIZ_PATH" ]; then
    echo "Building Quiz Application with embedded quiz: $QUIZ_PATH"
    if [ -n "$PLATFORM" ]; then
        uv run python main.py --build "$QUIZ_PATH" --platform "$PLATFORM"
    else
        uv run python main.py --build "$QUIZ_PATH"
    fi
    exit $?
fi

# Otherwise, use traditional PyInstaller build
echo "Building Quiz Application with PyInstaller..."

# Sync dependencies with uv
echo "Syncing dependencies with uv..."
uv sync --quiet

# Build directory
BUILD_DIR="build"
DIST_DIR="dist"
WORK_DIR="${BUILD_DIR}/.pyinstaller-work"
CACHE_DIR="${BUILD_DIR}/.pyinstaller-cache"

# Clean previous builds (only if not incremental)
if [ "$CLEAN_BUILD" = true ]; then
    echo "Cleaning previous builds..."
    rm -rf "$BUILD_DIR" "$DIST_DIR" "*.spec"
else
    echo "Incremental build: keeping cache..."
    # Only clean final executables, keep cache
    rm -rf "$BUILD_DIR/quiz" "$BUILD_DIR/quiz.exe" "$DIST_DIR/quiz" "$DIST_DIR/quiz.exe"
fi

# Create build directories
mkdir -p "$BUILD_DIR"
mkdir -p "$DIST_DIR"
mkdir -p "$WORK_DIR"
mkdir -p "$CACHE_DIR"

# Set PyInstaller cache directory via environment variable
export PYINSTALLER_CACHE_DIR="$CACHE_DIR"

# Build with PyInstaller using uv
echo "Starting PyInstaller build..."

# Base PyInstaller command
PYINSTALLER_CMD="uv run pyinstaller \
    --onefile \
    --name=quiz \
    --distpath=$DIST_DIR \
    --workpath=$WORK_DIR \
    --clean"

# Include schema directory if it exists
if [ -d "schema" ]; then
    PYINSTALLER_CMD="$PYINSTALLER_CMD --add-data=schema:schema"
fi

# Continue building the command
PYINSTALLER_CMD="$PYINSTALLER_CMD \
    --hidden-import=src \
    --hidden-import=PyQt6 \
    --hidden-import=jsonschema \
    --hidden-import=requests"

# Add platform-specific options
if [ -n "$PLATFORM" ]; then
    case "$PLATFORM" in
        windows)
            # PyInstaller on Windows uses console by default
            # Add --noconsole if you want windowed mode
            ;;
        macos)
            # PyInstaller on macOS creates app bundle by default with --onefile
            ;;
        linux)
            # Linux is default, no extra options needed
            ;;
    esac
fi

# Add main.py and execute
PYINSTALLER_CMD="$PYINSTALLER_CMD main.py"

eval $PYINSTALLER_CMD

# Move executable to build directory for consistency
if [ -f "$DIST_DIR/quiz.exe" ]; then
    mv "$DIST_DIR/quiz.exe" "$BUILD_DIR/quiz.exe"
elif [ -f "$DIST_DIR/quiz" ]; then
    mv "$DIST_DIR/quiz" "$BUILD_DIR/quiz"
fi

echo ""
echo "Build completed successfully!"

# Find the executable (PyInstaller creates files in dist/ or build/)
EXECUTABLE=""
if [ -f "$BUILD_DIR/quiz.exe" ]; then
    EXECUTABLE="$BUILD_DIR/quiz.exe"
elif [ -f "$BUILD_DIR/quiz" ]; then
    EXECUTABLE="$BUILD_DIR/quiz"
elif [ -f "$DIST_DIR/quiz.exe" ]; then
    EXECUTABLE="$DIST_DIR/quiz.exe"
elif [ -f "$DIST_DIR/quiz" ]; then
    EXECUTABLE="$DIST_DIR/quiz"
elif [ -f "quiz.exe" ]; then
    EXECUTABLE="quiz.exe"
elif [ -f "quiz" ]; then
    EXECUTABLE="quiz"
fi

if [ -n "$EXECUTABLE" ]; then
    echo "Executable location: $EXECUTABLE"
    echo ""
    echo "To run the application:"
    echo "  ./$EXECUTABLE"
    echo ""
    echo "Usage:"
    echo "  1. Place this exe in any folder"
    echo "  2. Create a 'quiz' folder next to the exe"
    echo "  3. Put JSON quiz files in the 'quiz' folder"
    echo "  4. Run the exe - it will load the first quiz found"
    echo ""
    echo "To build an exe with embedded quiz, use:"
    echo "  uv run python main.py --build /path/to/quiz.json"
else
    echo "Warning: Executable not found in expected location."
    echo "Searching for executable..."
    find . -maxdepth 3 -name "quiz*" -type f -executable 2>/dev/null | head -5
fi


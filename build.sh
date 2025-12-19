#!/bin/bash
# Build script for Quiz Application using Nuitka
# Usage:
#   ./build.sh                                    # Build without embedded quiz
#   ./build.sh /path/to/quiz.json                 # Build with embedded quiz from JSON file
#   ./build.sh /path/to/quiz                      # Build with embedded quiz from folder
#   ./build.sh --platform linux                  # Build for Linux
#   ./build.sh --platform windows                # Build for Windows
#   ./build.sh --platform macos                  # Build for macOS
#   ./build.sh /path/to/quiz.json --platform windows  # Build with quiz for Windows

set -e  # Exit on error

QUIZ_PATH=""
PLATFORM=""
BUILD_MODE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORM="$2"
            shift 2
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

# Check for cross-compilation requirements
if [ -n "$PLATFORM" ] && [ "$PLATFORM" = "windows" ]; then
    # Check if we're on Linux and need MinGW for cross-compilation
    if [ "$(uname -s)" = "Linux" ]; then
        echo "Cross-compiling for Windows from Linux..."
        if ! command -v x86_64-w64-mingw32-gcc &> /dev/null && ! command -v i686-w64-mingw32-gcc &> /dev/null; then
            echo ""
            echo "Warning: MinGW-w64 not found. It's required for cross-compilation to Windows."
            echo "Install it with one of the following commands:"
            echo "  Ubuntu/Debian: sudo apt-get install mingw-w64"
            echo "  Fedora/RHEL:   sudo dnf install mingw64-gcc"
            echo "  Arch:          sudo pacman -S mingw-w64-gcc"
            echo ""
            echo "Nuitka will attempt to download MinGW automatically, but manual installation is recommended."
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            echo "MinGW-w64 found. Cross-compilation should work."
        fi
    fi
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

# Otherwise, use traditional Nuitka build
echo "Building Quiz Application with Nuitka..."

# Sync dependencies with uv
echo "Syncing dependencies with uv..."
uv sync --quiet

# Build directory
BUILD_DIR="build"
DIST_DIR="dist"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf "$BUILD_DIR" "$DIST_DIR" "*.build" "*.dist" "*.onefile-build"

# Create build directory
mkdir -p "$BUILD_DIR"

# Build with Nuitka using uv
echo "Starting Nuitka build..."

# Base Nuitka command
NUITKA_CMD="uv run nuitka \
    --standalone \
    --onefile \
    --enable-plugin=pyqt6"

# Include schema directory if it exists
if [ -d "schema" ]; then
    NUITKA_CMD="$NUITKA_CMD --include-data-dir=schema=schema"
fi

# Continue building the command
NUITKA_CMD="$NUITKA_CMD \
    --include-package=src \
    --output-dir=$BUILD_DIR \
    --output-filename=quiz \
    --assume-yes-for-downloads \
    --show-progress \
    --show-memory"

# Add platform-specific options
if [ -n "$PLATFORM" ]; then
    case "$PLATFORM" in
        windows)
            NUITKA_CMD="$NUITKA_CMD --windows-console-mode=disable"
            # Add MinGW for cross-compilation from Linux
            if [ "$(uname -s)" = "Linux" ]; then
                NUITKA_CMD="$NUITKA_CMD --mingw64"
            fi
            ;;
        macos)
            NUITKA_CMD="$NUITKA_CMD --macos-create-app-bundle"
            ;;
        linux)
            # Linux is default, no extra options needed
            ;;
    esac
fi

# Add main.py and execute
NUITKA_CMD="$NUITKA_CMD main.py"

eval $NUITKA_CMD

echo ""
echo "Build completed successfully!"

# Find the executable (Nuitka creates different paths for onefile builds)
EXECUTABLE=""
if [ -f "$BUILD_DIR/quiz.exe" ]; then
    EXECUTABLE="$BUILD_DIR/quiz.exe"
elif [ -f "$BUILD_DIR/quiz" ]; then
    EXECUTABLE="$BUILD_DIR/quiz"
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


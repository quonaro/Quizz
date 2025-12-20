"""
Quiz cache module for saving and loading user answers.
Cache is saved in user's application data directory.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def get_cache_path() -> Path:
    """
    Get path to cache file in user's application data directory.
    Uses platform-specific user data directories to avoid permission issues.
    
    Windows: %LOCALAPPDATA%/quiz/.quiz_cache.json
    Linux: ~/.cache/quiz/.quiz_cache.json
    macOS: ~/Library/Application Support/quiz/.quiz_cache.json
    """
    if sys.platform == 'win32':
        # Windows: Use LOCALAPPDATA (user-specific, writable)
        appdata = os.environ.get('LOCALAPPDATA')
        if appdata:
            cache_dir = Path(appdata) / "quiz"
        else:
            # Fallback to user home
            cache_dir = Path.home() / ".quiz"
    elif sys.platform == 'darwin':
        # macOS: Use Application Support
        cache_dir = Path.home() / "Library" / "Application Support" / "quiz"
    else:
        # Linux and other Unix-like systems: Use XDG cache directory
        xdg_cache = os.environ.get('XDG_CACHE_HOME')
        if xdg_cache:
            cache_dir = Path(xdg_cache) / "quiz"
        else:
            cache_dir = Path.home() / ".cache" / "quiz"
    
    # Create cache directory if it doesn't exist
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError):
        # If we can't create in user directory, fallback to temp directory
        import tempfile
        cache_dir = Path(tempfile.gettempdir()) / "quiz_cache"
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            # Last resort: use current directory (might fail, but we'll handle it in save_cache)
            cache_dir = Path.cwd()
    
    # Create hidden cache file (.quiz_cache.json)
    cache_file = cache_dir / ".quiz_cache.json"
    return cache_file


def save_cache(quiz_id: str, user_answers: Dict[str, Any]) -> bool:
    """
    Save user answers to cache file.
    
    Args:
        quiz_id: Unique identifier for the quiz (e.g., quiz file path or title)
        user_answers: Dictionary of user answers {question_id: answer}
        
    Returns:
        True if saved successfully, False otherwise.
    """
    try:
        cache_path = get_cache_path()
        cache_data = {}
        
        # Load existing cache if exists
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                # If cache is corrupted, start fresh
                cache_data = {}
        
        # Update cache for this quiz
        cache_data[quiz_id] = {
            "user_answers": user_answers,
            "timestamp": None  # Can add timestamp if needed
        }
        
        # Save cache
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        # Make file hidden on Windows
        if sys.platform == 'win32':
            try:
                import ctypes
                # FILE_ATTRIBUTE_HIDDEN = 0x2
                ctypes.windll.kernel32.SetFileAttributesW(str(cache_path), 0x2)
            except Exception:
                pass  # Ignore if can't set hidden attribute
        
        return True
    except Exception as e:
        print(f"Error saving cache: {e}", file=sys.stderr)
        return False


def load_cache(quiz_id: str) -> Optional[Dict[str, Any]]:
    """
    Load user answers from cache file.
    
    Args:
        quiz_id: Unique identifier for the quiz
        
    Returns:
        Dictionary of user answers or None if not found.
    """
    try:
        cache_path = get_cache_path()
        
        if not cache_path.exists():
            return None
        
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        quiz_cache = cache_data.get(quiz_id)
        if quiz_cache:
            return quiz_cache.get("user_answers")
        
        return None
    except (json.JSONDecodeError, IOError, KeyError) as e:
        print(f"Error loading cache: {e}", file=sys.stderr)
        return None


def clear_cache(quiz_id: Optional[str] = None) -> bool:
    """
    Clear cache for specific quiz or all quizzes.
    
    Args:
        quiz_id: Quiz ID to clear. If None, clears all cache.
        
    Returns:
        True if cleared successfully, False otherwise.
    """
    try:
        cache_path = get_cache_path()
        
        if not cache_path.exists():
            return True  # Already cleared
        
        if quiz_id is None:
            # Clear all cache - delete file
            cache_path.unlink()
            return True
        
        # Clear specific quiz
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        if quiz_id in cache_data:
            del cache_data[quiz_id]
            
            # If no quizzes left, delete file
            if not cache_data:
                cache_path.unlink()
            else:
                # Save updated cache
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error clearing cache: {e}", file=sys.stderr)
        return False


def get_quiz_id(quiz_data: Dict[str, Any], quiz_file_path: Optional[str] = None) -> str:
    """
    Generate unique identifier for quiz.
    
    Args:
        quiz_data: Quiz data dictionary
        quiz_file_path: Optional path to quiz file
        
    Returns:
        Unique quiz identifier.
    """
    if quiz_file_path:
        # Use file path as ID
        return str(Path(quiz_file_path).absolute())
    
    # Use title + first question ID as fallback
    title = quiz_data.get("title", "quiz")
    questions = quiz_data.get("questions", [])
    if questions:
        first_q_id = questions[0].get("id", "q1")
        return f"{title}_{first_q_id}"
    
    return title





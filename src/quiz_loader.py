"""
Quiz loader and validator module.
Loads and validates quiz JSON files against the schema.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import jsonschema
from jsonschema import validate, ValidationError


class QuizValidationError(Exception):
    """Raised when quiz JSON validation fails."""
    pass


def _find_schema_path() -> Optional[Path]:
    """
    Find schema file path, handling both development and compiled (onefile) modes.
    
    Returns:
        Path to schema file or None if not found.
    """
    # Try multiple locations
    possible_paths = []
    
    # In onefile mode, Nuitka extracts files to a temp directory
    # Files from --include-data-dir are available relative to __file__ in onefile mode
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        if hasattr(sys, "_MEIPASS"):
            # PyInstaller temporary directory
            base_path = Path(sys._MEIPASS)
            possible_paths.append(base_path / "schema" / "quiz_schema.json")
        else:
            # Nuitka onefile - files from --include-data-dir are available
            # relative to the module's __file__ location
            # Try using __file__ from this module
            try:
                # In Nuitka onefile, __file__ points to the extracted location
                module_dir = Path(__file__).parent.parent
                possible_paths.append(module_dir / "schema" / "quiz_schema.json")
            except Exception:
                pass
            
            # Also try relative to executable
            if sys.argv and sys.argv[0]:
                exe_dir = Path(sys.argv[0]).parent
                possible_paths.append(exe_dir / "schema" / "quiz_schema.json")
    else:
        # Running as Python script - use relative to source file
        schema_dir = Path(__file__).parent.parent / "schema"
        possible_paths.append(schema_dir / "quiz_schema.json")
    
    # Also try current working directory
    possible_paths.append(Path.cwd() / "schema" / "quiz_schema.json")
    
    # Try to find existing schema file
    for path in possible_paths:
        try:
            if path.exists() and path.is_file():
                return path
        except Exception:
            continue
    
    return None


class QuizLoader:
    """Loads and validates quiz JSON files."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the quiz loader.
        
        Args:
            schema_path: Path to JSON schema file. If None, uses default schema.
        """
        if schema_path is None:
            found_path = _find_schema_path()
            if found_path:
                schema_path = str(found_path)
            else:
                # Schema not found - will skip validation
                schema_path = None
        
        self.schema_path = Path(schema_path) if schema_path else None
        self._schema = None
    
    @property
    def schema(self) -> Optional[Dict[str, Any]]:
        """
        Load and cache the JSON schema.
        
        Returns:
            Schema dictionary or None if schema file not found (validation will be skipped).
        """
        if self._schema is None:
            if self.schema_path is None or not self.schema_path.exists():
                # Schema not available - return None to skip validation
                return None
            try:
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    self._schema = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                # Schema file not found or invalid - skip validation
                print(f"Warning: Could not load schema file: {e}", file=sys.stderr)
                return None
        return self._schema
    
    def load_quiz(self, quiz_path: str) -> Dict[str, Any]:
        """
        Load and validate a quiz JSON file.
        
        Args:
            quiz_path: Path to the quiz JSON file.
            
        Returns:
            Validated quiz dictionary.
            
        Raises:
            QuizValidationError: If validation fails.
            FileNotFoundError: If quiz file doesn't exist.
        """
        quiz_path = Path(quiz_path)
        
        if not quiz_path.exists():
            raise FileNotFoundError(f"Quiz file not found: {quiz_path}")
        
        try:
            with open(quiz_path, 'r', encoding='utf-8') as f:
                quiz_data = json.load(f)
        except json.JSONDecodeError as e:
            raise QuizValidationError(f"Invalid JSON format: {e}")
        
        # Validate against schema (if available)
        schema = self.schema
        if schema is not None:
            try:
                validate(instance=quiz_data, schema=schema)
            except ValidationError as e:
                raise QuizValidationError(f"Quiz validation failed: {e.message}")
        
        return quiz_data
    
    def validate_quiz(self, quiz_data: Dict[str, Any]) -> bool:
        """
        Validate quiz data against schema without loading from file.
        
        Args:
            quiz_data: Quiz dictionary to validate.
            
        Returns:
            True if valid, or True if schema not available (validation skipped).
            
        Raises:
            QuizValidationError: If validation fails.
        """
        schema = self.schema
        if schema is None:
            # Schema not available - skip validation
            return True
        try:
            validate(instance=quiz_data, schema=schema)
            return True
        except ValidationError as e:
            raise QuizValidationError(f"Quiz validation failed: {e.message}")
    
    def get_question_by_id(self, quiz_data: Dict[str, Any], question_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a question by its ID.
        
        Args:
            quiz_data: Quiz dictionary.
            question_id: ID of the question to find.
            
        Returns:
            Question dictionary or None if not found.
        """
        for question in quiz_data.get("questions", []):
            if question.get("id") == question_id:
                return question
        return None





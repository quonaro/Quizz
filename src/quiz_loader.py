"""
Quiz loader and validator module.
Loads and validates quiz JSON files against the schema.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import jsonschema
from jsonschema import validate, ValidationError


class QuizValidationError(Exception):
    """Raised when quiz JSON validation fails."""
    pass


class QuizLoader:
    """Loads and validates quiz JSON files."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the quiz loader.
        
        Args:
            schema_path: Path to JSON schema file. If None, uses default schema.
        """
        if schema_path is None:
            # Default schema path relative to this file
            schema_dir = Path(__file__).parent.parent / "schema"
            schema_path = schema_dir / "quiz_schema.json"
        
        self.schema_path = Path(schema_path)
        self._schema = None
    
    @property
    def schema(self) -> Dict[str, Any]:
        """Load and cache the JSON schema."""
        if self._schema is None:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self._schema = json.load(f)
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
        
        # Validate against schema
        try:
            validate(instance=quiz_data, schema=self.schema)
        except ValidationError as e:
            raise QuizValidationError(f"Quiz validation failed: {e.message}")
        
        return quiz_data
    
    def validate_quiz(self, quiz_data: Dict[str, Any]) -> bool:
        """
        Validate quiz data against schema without loading from file.
        
        Args:
            quiz_data: Quiz dictionary to validate.
            
        Returns:
            True if valid.
            
        Raises:
            QuizValidationError: If validation fails.
        """
        try:
            validate(instance=quiz_data, schema=self.schema)
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




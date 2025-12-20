"""
Quiz data model classes.
"""

from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any
from enum import Enum


class QuestionType(Enum):
    """Question type enumeration."""
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT_INPUT = "text_input"
    MATCHING = "matching"
    ORDERING = "ordering"


@dataclass
class QuizMetadata:
    """Quiz metadata."""
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None


@dataclass
class BaseQuestion:
    """Base question class."""
    id: str
    type: QuestionType
    question: str
    images: Optional[Union[str, List[str]]] = None
    points: float = 1.0
    explanation: Optional[str] = None


@dataclass
class SingleChoiceQuestion(BaseQuestion):
    """Single choice question."""
    options: List[str] = None
    correct_answer: int = 0
    
    def __post_init__(self):
        if self.options is None:
            self.options = []
        if self.type != QuestionType.SINGLE_CHOICE:
            self.type = QuestionType.SINGLE_CHOICE


@dataclass
class MultipleChoiceQuestion(BaseQuestion):
    """Multiple choice question."""
    options: List[str] = None
    correct_answers: List[int] = None
    partial_credit: bool = False
    
    def __post_init__(self):
        if self.options is None:
            self.options = []
        if self.correct_answers is None:
            self.correct_answers = []
        if self.type != QuestionType.MULTIPLE_CHOICE:
            self.type = QuestionType.MULTIPLE_CHOICE


@dataclass
class TextInputQuestion(BaseQuestion):
    """Text input question."""
    correct_answers: Union[str, List[str]] = ""
    case_sensitive: bool = False
    trim_whitespace: bool = True
    
    def __post_init__(self):
        if self.type != QuestionType.TEXT_INPUT:
            self.type = QuestionType.TEXT_INPUT


@dataclass
class Match:
    """A single match in a matching question."""
    left: int
    right: int


@dataclass
class MatchingQuestion(BaseQuestion):
    """Matching question."""
    left_items: List[str] = None
    right_items: List[str] = None
    matches: List[Match] = None
    
    def __post_init__(self):
        if self.left_items is None:
            self.left_items = []
        if self.right_items is None:
            self.right_items = []
        if self.matches is None:
            self.matches = []
        if self.type != QuestionType.MATCHING:
            self.type = QuestionType.MATCHING


@dataclass
class OrderingQuestion(BaseQuestion):
    """Ordering question."""
    items: List[str] = None
    correct_order: List[int] = None
    
    def __post_init__(self):
        if self.items is None:
            self.items = []
        if self.correct_order is None:
            self.correct_order = []
        if self.type != QuestionType.ORDERING:
            self.type = QuestionType.ORDERING


@dataclass
class Quiz:
    """Complete quiz model."""
    metadata: QuizMetadata
    questions: List[BaseQuestion]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quiz':
        """Create Quiz instance from dictionary."""
        metadata = QuizMetadata(
            title=data["title"],
            description=data.get("description"),
            author=data.get("author"),
            version=data.get("version")
        )
        
        questions = []
        for q_data in data.get("questions", []):
            q_type = QuestionType(q_data["type"])
            
            if q_type == QuestionType.SINGLE_CHOICE:
                question = SingleChoiceQuestion(
                    id=q_data["id"],
                    type=q_type,
                    question=q_data["question"],
                    images=q_data.get("images"),
                    points=q_data.get("points", 1.0),
                    explanation=q_data.get("explanation"),
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"]
                )
            elif q_type == QuestionType.MULTIPLE_CHOICE:
                question = MultipleChoiceQuestion(
                    id=q_data["id"],
                    type=q_type,
                    question=q_data["question"],
                    images=q_data.get("images"),
                    points=q_data.get("points", 1.0),
                    explanation=q_data.get("explanation"),
                    options=q_data["options"],
                    correct_answers=q_data["correct_answers"],
                    partial_credit=q_data.get("partial_credit", False)
                )
            elif q_type == QuestionType.TEXT_INPUT:
                question = TextInputQuestion(
                    id=q_data["id"],
                    type=q_type,
                    question=q_data["question"],
                    images=q_data.get("images"),
                    points=q_data.get("points", 1.0),
                    explanation=q_data.get("explanation"),
                    correct_answers=q_data["correct_answers"],
                    case_sensitive=q_data.get("case_sensitive", False),
                    trim_whitespace=q_data.get("trim_whitespace", True)
                )
            elif q_type == QuestionType.MATCHING:
                matches = [Match(**m) for m in q_data["matches"]]
                question = MatchingQuestion(
                    id=q_data["id"],
                    type=q_type,
                    question=q_data["question"],
                    images=q_data.get("images"),
                    points=q_data.get("points", 1.0),
                    explanation=q_data.get("explanation"),
                    left_items=q_data["left_items"],
                    right_items=q_data["right_items"],
                    matches=matches
                )
            elif q_type == QuestionType.ORDERING:
                question = OrderingQuestion(
                    id=q_data["id"],
                    type=q_type,
                    question=q_data["question"],
                    images=q_data.get("images"),
                    points=q_data.get("points", 1.0),
                    explanation=q_data.get("explanation"),
                    items=q_data["items"],
                    correct_order=q_data["correct_order"]
                )
            else:
                raise ValueError(f"Unknown question type: {q_type}")
            
            questions.append(question)
        
        return cls(metadata=metadata, questions=questions)





"""
Quiz builder library - helper library for creating quizzes programmatically.
"""

import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path


class QuizBuilder:
    """Builder class for creating quiz JSON structures programmatically."""

    def __init__(self):
        self.quiz_data: Dict[str, Any] = {"title": "", "questions": []}

    def set_title(self, title: str) -> "QuizBuilder":
        """Set quiz title."""
        self.quiz_data["title"] = title
        return self

    def set_description(self, description: str) -> "QuizBuilder":
        """Set quiz description."""
        self.quiz_data["description"] = description
        return self

    def set_author(self, author: str) -> "QuizBuilder":
        """Set quiz author."""
        self.quiz_data["author"] = author
        return self

    def set_version(self, version: str) -> "QuizBuilder":
        """Set quiz version."""
        self.quiz_data["version"] = version
        return self

    def add_single_choice(
        self,
        question_id: str,
        question: str,
        options: List[str],
        correct_answer: int,
        points: float = 1.0,
        images: Optional[Union[str, List[str]]] = None,
        explanation: Optional[str] = None,
    ) -> "QuizBuilder":
        """Add a single choice question."""
        question_data = {
            "id": question_id,
            "type": "single_choice",
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "points": points,
        }
        if images:
            question_data["images"] = images
        if explanation:
            question_data["explanation"] = explanation

        self.quiz_data["questions"].append(question_data)
        return self

    def add_multiple_choice(
        self,
        question_id: str,
        question: str,
        options: List[str],
        correct_answers: List[int],
        points: float = 1.0,
        partial_credit: bool = False,
        images: Optional[Union[str, List[str]]] = None,
        explanation: Optional[str] = None,
    ) -> "QuizBuilder":
        """Add a multiple choice question."""
        question_data = {
            "id": question_id,
            "type": "multiple_choice",
            "question": question,
            "options": options,
            "correct_answers": correct_answers,
            "partial_credit": partial_credit,
            "points": points,
        }
        if images:
            question_data["images"] = images
        if explanation:
            question_data["explanation"] = explanation

        self.quiz_data["questions"].append(question_data)
        return self

    def add_text_input(
        self,
        question_id: str,
        question: str,
        correct_answers: Union[str, List[str]],
        points: float = 1.0,
        case_sensitive: bool = False,
        trim_whitespace: bool = True,
        images: Optional[Union[str, List[str]]] = None,
        explanation: Optional[str] = None,
    ) -> "QuizBuilder":
        """Add a text input question."""
        question_data = {
            "id": question_id,
            "type": "text_input",
            "question": question,
            "correct_answers": correct_answers
            if isinstance(correct_answers, list)
            else [correct_answers],
            "case_sensitive": case_sensitive,
            "trim_whitespace": trim_whitespace,
            "points": points,
        }
        if images:
            question_data["images"] = images
        if explanation:
            question_data["explanation"] = explanation

        self.quiz_data["questions"].append(question_data)
        return self

    def add_matching(
        self,
        question_id: str,
        question: str,
        left_items: List[str],
        right_items: List[str],
        matches: List[Dict[str, int]],
        points: float = 1.0,
        images: Optional[Union[str, List[str]]] = None,
        explanation: Optional[str] = None,
    ) -> "QuizBuilder":
        """Add a matching question."""
        question_data = {
            "id": question_id,
            "type": "matching",
            "question": question,
            "left_items": left_items,
            "right_items": right_items,
            "matches": matches,
            "points": points,
        }
        if images:
            question_data["images"] = images
        if explanation:
            question_data["explanation"] = explanation

        self.quiz_data["questions"].append(question_data)
        return self

    def add_ordering(
        self,
        question_id: str,
        question: str,
        items: List[str],
        correct_order: List[int],
        points: float = 1.0,
        images: Optional[Union[str, List[str]]] = None,
        explanation: Optional[str] = None,
    ) -> "QuizBuilder":
        """Add an ordering question."""
        question_data = {
            "id": question_id,
            "type": "ordering",
            "question": question,
            "items": items,
            "correct_order": correct_order,
            "points": points,
        }
        if images:
            question_data["images"] = images
        if explanation:
            question_data["explanation"] = explanation

        self.quiz_data["questions"].append(question_data)
        return self

    def build(self, validate: bool = True) -> Dict[str, Any]:
        """
        Build and return the quiz dictionary.

        Args:
            validate: If True, validate the quiz against the schema from schema/ folder.

        Returns:
            Quiz dictionary.

        Raises:
            QuizValidationError: If validation fails and validate=True.
        """
        quiz_data = self.quiz_data.copy()

        if validate:
            # Import here to avoid circular import
            from .quiz_loader import QuizLoader

            loader = QuizLoader()  # Loads schema from schema/quiz_schema.json
            loader.validate_quiz(quiz_data)

        return quiz_data

    def to_json(self, indent: int = 2) -> str:
        """Convert quiz to JSON string."""
        return json.dumps(self.quiz_data, indent=indent, ensure_ascii=False)

    @staticmethod
    def convert_from_new_schema(
        new_schema_data: Dict[str, Any], base_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Convert quiz data from new schema format to old schema format.

        New schema format:
        - questions[].text instead of questions[].question
        - questions[].options as [{text, correct}] instead of [strings] + correct_answer
        - questions[].expected instead of questions[].correct_answers for text_input
        - questions[].pairs as [{left, right}] (strings) instead of left_items, right_items, matches (indices)

        Args:
            new_schema_data: Quiz data in new schema format.
            base_path: Base path for resolving relative image paths. If None, paths are not resolved.

        Returns:
            Quiz data in old schema format.
        """
        converted = {"title": new_schema_data.get("title", ""), "questions": []}

        # Copy optional fields
        if "description" in new_schema_data:
            converted["description"] = new_schema_data["description"]
        if "author" in new_schema_data:
            converted["author"] = new_schema_data["author"]
        if "version" in new_schema_data:
            converted["version"] = new_schema_data["version"]

        # Convert questions
        for idx, question in enumerate(new_schema_data.get("questions", [])):
            question_type = question.get("type")
            converted_question = {
                "id": question.get("id", f"q{idx + 1}"),
                "type": question_type,
                "question": question.get("text", question.get("question", "")),
            }

            # Copy optional fields
            if "images" in question:
                converted_question["images"] = question["images"]
            if "explanation" in question:
                converted_question["explanation"] = question["explanation"]
            if "points" in question:
                converted_question["points"] = question["points"]

            # Convert based on question type
            if question_type == "single_choice":
                # Convert options from [{text, correct}] to [strings] and find correct_answer index
                options = []
                correct_answer = None
                for opt_idx, option in enumerate(question.get("options", [])):
                    if isinstance(option, dict):
                        options.append(option.get("text", ""))
                        if option.get("correct", False):
                            correct_answer = opt_idx
                    else:
                        # Fallback: if option is already a string
                        options.append(option)

                converted_question["options"] = options
                if correct_answer is not None:
                    converted_question["correct_answer"] = correct_answer
                else:
                    # Default to first option if no correct answer found
                    converted_question["correct_answer"] = 0

            elif question_type == "multiple_choice":
                # Convert options from [{text, correct}] to [strings] and find correct_answers indices
                options = []
                correct_answers = []
                for opt_idx, option in enumerate(question.get("options", [])):
                    if isinstance(option, dict):
                        options.append(option.get("text", ""))
                        if option.get("correct", False):
                            correct_answers.append(opt_idx)
                    else:
                        # Fallback: if option is already a string
                        options.append(option)

                converted_question["options"] = options
                converted_question["correct_answers"] = correct_answers
                if "partial_credit" in question:
                    converted_question["partial_credit"] = question["partial_credit"]

            elif question_type == "text_input":
                # Convert expected to correct_answers
                expected = question.get("expected", [])
                if isinstance(expected, str):
                    expected = [expected]
                converted_question["correct_answers"] = expected
                if "case_sensitive" in question:
                    converted_question["case_sensitive"] = question["case_sensitive"]
                else:
                    # Default to case-insensitive for new schema
                    converted_question["case_sensitive"] = False
                if "trim_whitespace" in question:
                    converted_question["trim_whitespace"] = question["trim_whitespace"]

            elif question_type == "matching":
                # Convert pairs from [{left, right}] (strings) to left_items, right_items, matches (indices)
                pairs = question.get("pairs", [])
                left_items = []
                right_items = []
                matches = []

                # Collect unique left and right items
                left_to_index = {}
                right_to_index = {}

                for pair in pairs:
                    left_str = pair.get("left", "")
                    right_str = pair.get("right", "")

                    # Add left item if not seen
                    if left_str not in left_to_index:
                        left_to_index[left_str] = len(left_items)
                        left_items.append(left_str)

                    # Add right item if not seen
                    if right_str not in right_to_index:
                        right_to_index[right_str] = len(right_items)
                        right_items.append(right_str)

                    # Create match
                    matches.append(
                        {
                            "left": left_to_index[left_str],
                            "right": right_to_index[right_str],
                        }
                    )

                converted_question["left_items"] = left_items
                converted_question["right_items"] = right_items
                converted_question["matches"] = matches

            elif question_type == "ordering":
                # Ordering format is the same, just copy
                converted_question["items"] = question.get("items", [])
                converted_question["correct_order"] = question.get("correct_order", [])

            converted["questions"].append(converted_question)

        # Resolve image paths if base_path is provided
        if base_path is not None:
            converted = QuizBuilder._resolve_image_paths(converted, base_path)

        return converted

    @staticmethod
    def load_from_quiz_folder(
        quiz_folder: Optional[Union[str, Path]] = None,
    ) -> tuple:
        """
        Load quiz from quiz folder. Automatically finds and loads the first JSON file.

        Args:
            quiz_folder: Path to quiz folder. If None, uses 'quiz' folder in project root.

        Returns:
            Tuple of (quiz_data, quiz_file_path) where quiz_file_path is the path to the JSON file.

        Raises:
            FileNotFoundError: If quiz folder or quiz file not found.
            QuizValidationError: If quiz validation fails.
        """
        if quiz_folder is None:
            # Default to quiz folder - try to find it relative to executable
            import sys

            # Determine base path (where executable or script is located)
            if getattr(sys, "frozen", False):
                # Running as compiled executable (Nuitka, PyInstaller, etc.)
                if hasattr(sys, "_MEIPASS"):
                    # PyInstaller temporary directory
                    base_path = Path(sys.executable).parent
                else:
                    # Nuitka onefile - executable is in sys.argv[0]
                    base_path = Path(sys.argv[0]).parent
            else:
                # Running as Python script
                # Try to use script directory, fallback to current working directory
                script_path = Path(__file__).parent.parent
                if script_path.exists():
                    base_path = script_path
                else:
                    base_path = Path.cwd()

            # Look for quiz folder next to executable/script
            quiz_folder = base_path / "quiz"

            # If not found, try current working directory
            if not quiz_folder.exists():
                quiz_folder = Path.cwd() / "quiz"
        else:
            quiz_folder = Path(quiz_folder)

        if not quiz_folder.exists():
            raise FileNotFoundError(f"Quiz folder not found: {quiz_folder}")

        # Find first JSON file in quiz folder
        json_files = list(quiz_folder.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(
                f"No JSON files found in quiz folder: {quiz_folder}"
            )

        # Load first JSON file
        quiz_file = json_files[0]
        with open(quiz_file, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)

        # Check if it's new schema format (has questions with 'text' field) or old format
        is_new_schema = False
        if "questions" in quiz_data and len(quiz_data["questions"]) > 0:
            first_question = quiz_data["questions"][0]
            # Check if it uses new schema: has 'text' field or 'options' as objects
            if "text" in first_question:
                is_new_schema = True
            elif "options" in first_question and len(first_question["options"]) > 0:
                if isinstance(first_question["options"][0], dict):
                    is_new_schema = True

        # Convert if needed
        if is_new_schema:
            quiz_data = QuizBuilder.convert_from_new_schema(quiz_data, quiz_folder)
        else:
            # Resolve image paths for old schema too
            quiz_data = QuizBuilder._resolve_image_paths(quiz_data, quiz_folder)

        # Validate converted data
        from .quiz_loader import QuizLoader

        loader = QuizLoader()
        loader.validate_quiz(quiz_data)

        return quiz_data, str(quiz_file.absolute())

    @staticmethod
    def _resolve_image_paths(
        quiz_data: Dict[str, Any], base_path: Path
    ) -> Dict[str, Any]:
        """
        Resolve relative image paths relative to base_path.

        Args:
            quiz_data: Quiz data dictionary.
            base_path: Base path for resolving relative image paths.

        Returns:
            Quiz data with resolved image paths.
        """
        for question in quiz_data.get("questions", []):
            if "images" in question:
                images = question["images"]
                if isinstance(images, str):
                    # Single image
                    if not Path(images).is_absolute():
                        question["images"] = str(base_path / images)
                elif isinstance(images, list):
                    # Multiple images
                    resolved_images = []
                    for img in images:
                        if not Path(img).is_absolute():
                            resolved_images.append(str(base_path / img))
                        else:
                            resolved_images.append(img)
                    question["images"] = resolved_images
        return quiz_data


def create_sample_quiz() -> Dict[str, Any]:
    """Create a sample quiz using the builder."""
    builder = QuizBuilder()

    builder.set_title("Пример научного квиза")
    builder.set_description("Демонстрационный квиз со всеми типами вопросов")
    builder.set_author("Quiz App")
    builder.set_version("1.0.0")

    # Single choice
    builder.add_single_choice(
        question_id="q1",
        question="Какой химический символ у воды?",
        options=["H2O", "CO2", "O2", "NaCl"],
        correct_answer=0,
        points=1,
        explanation="Вода состоит из двух атомов водорода и одного атома кислорода, отсюда H2O.",
    )

    # Multiple choice
    builder.add_multiple_choice(
        question_id="q2",
        question="Какие из следующих являются языками программирования? (Выберите все подходящие)",
        options=["Python", "HTML", "JavaScript", "CSS"],
        correct_answers=[0, 2],
        partial_credit=True,
        points=2,
        explanation="Python и JavaScript - языки программирования. HTML и CSS - языки разметки и стилей соответственно.",
    )

    # Text input
    builder.add_text_input(
        question_id="q3",
        question="Какая столица Франции?",
        correct_answers=["Париж", "Paris", "paris"],
        case_sensitive=False,
        points=1,
        explanation="Париж - столица и крупнейший город Франции.",
    )

    # Matching
    builder.add_matching(
        question_id="q4",
        question="Сопоставьте страны с их столицами:",
        left_items=["Франция", "Германия", "Италия", "Испания"],
        right_items=["Мадрид", "Берлин", "Париж", "Рим"],
        matches=[
            {"left": 0, "right": 2},
            {"left": 1, "right": 1},
            {"left": 2, "right": 3},
            {"left": 3, "right": 0},
        ],
        points=4,
        explanation="Франция-Париж, Германия-Берлин, Италия-Рим, Испания-Мадрид",
    )

    # Ordering
    builder.add_ordering(
        question_id="q5",
        question="Расположите эти планеты от ближайшей к Солнцу к самой дальней:",
        items=["Юпитер", "Меркурий", "Земля", "Марс", "Венера"],
        correct_order=[1, 4, 2, 3, 0],
        points=5,
        explanation="Правильный порядок: Меркурий, Венера, Земля, Марс, Юпитер",
    )

    return builder.build()

"""
Results window showing quiz results.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette


class ResultsWindow(QDialog):
    """Window displaying quiz results."""

    def __init__(self, results: dict, parent=None):
        super().__init__(parent)
        self.results = results
        self.setWindowTitle("Результаты квиза")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Header with summary
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #4A90E2, stop:1 #357ABD);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)

        title_label = QLabel("Результаты квиза")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)

        # Score summary
        total_questions = self.results.get("total_questions", 0)
        correct_answers = self.results.get("correct_answers", 0)
        total_points = self.results.get("total_points", 0.0)
        earned_points = self.results.get("earned_points", 0.0)
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0

        score_text = f"Правильных ответов: {correct_answers} из {total_questions}"
        points_text = (
            f"Баллов: {earned_points:.1f} из {total_points:.1f} ({percentage:.1f}%)"
        )

        score_label = QLabel(score_text)
        score_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        score_label.setStyleSheet("color: white;")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(score_label)

        points_label = QLabel(points_text)
        points_label.setFont(QFont("Arial", 14))
        points_label.setStyleSheet("color: white;")
        points_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(points_label)

        layout.addWidget(header_frame)

        # Scroll area for questions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # Add question results
        for i, q_result in enumerate(self.results.get("questions", []), 1):
            question_frame = self.create_question_result_widget(q_result, i)
            scroll_layout.addWidget(question_frame)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Закрыть")
        close_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 30px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2A5F8F;
            }
        """)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def create_question_result_widget(
        self, q_result: dict, question_num: int
    ) -> QFrame:
        """Create a widget for a single question result."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #e0e0e0;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Question header
        header_layout = QHBoxLayout()

        is_correct = q_result.get("is_correct", False)
        status_color = "#4CAF50" if is_correct else "#F44336"
        status_text = "✓ Правильно" if is_correct else "✗ Неправильно"

        status_label = QLabel(status_text)
        status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_label.setStyleSheet(f"color: {status_color};")
        header_layout.addWidget(status_label)

        header_layout.addStretch()

        points_label = QLabel(
            f"Баллы: {q_result.get('earned_points', 0):.1f}/{q_result.get('points', 0):.1f}"
        )
        points_label.setFont(QFont("Arial", 11))
        points_label.setStyleSheet("color: #666;")
        header_layout.addWidget(points_label)

        layout.addLayout(header_layout)

        # Question text
        question_label = QLabel(
            f"Вопрос {question_num}: {q_result.get('question', '')}"
        )
        question_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        question_label.setWordWrap(True)
        question_label.setStyleSheet("color: #333;")
        layout.addWidget(question_label)

        # User answer
        user_answer = q_result.get("user_answer")
        user_answer_text = self.format_answer_detailed(
            user_answer, q_result, is_user=True
        )

        user_layout = QVBoxLayout()
        user_label_title = QLabel("Ваш ответ:")
        user_label_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        user_label_title.setStyleSheet("color: #666;")
        user_layout.addWidget(user_label_title)

        user_label = QLabel(user_answer_text)
        user_label.setFont(QFont("Arial", 11))
        user_label.setWordWrap(True)
        user_label.setStyleSheet(f"""
            color: {status_color};
            padding: 8px;
            background-color: #f8f8f8;
            border-radius: 5px;
            border-left: 3px solid {status_color};
        """)
        user_layout.addWidget(user_label)

        layout.addLayout(user_layout)

        # Correct answer
        correct_answer = q_result.get("correct_answer")
        # Format correct answer (it might already be formatted)
        if isinstance(correct_answer, (list, dict)):
            correct_answer_text = self.format_answer_detailed(
                correct_answer, q_result, is_user=False
            )
        else:
            # Already formatted string
            correct_answer_text = (
                str(correct_answer) if correct_answer is not None else "Не указано"
            )

        correct_layout = QVBoxLayout()
        correct_label_title = QLabel("Правильный ответ:")
        correct_label_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        correct_label_title.setStyleSheet("color: #666;")
        correct_layout.addWidget(correct_label_title)

        correct_label = QLabel(correct_answer_text)
        correct_label.setFont(QFont("Arial", 11))
        correct_label.setWordWrap(True)
        correct_label.setStyleSheet("""
            color: #4CAF50;
            padding: 8px;
            background-color: #f0f8f0;
            border-radius: 5px;
            border-left: 3px solid #4CAF50;
        """)
        correct_layout.addWidget(correct_label)

        layout.addLayout(correct_layout)

        # Explanation
        explanation = q_result.get("explanation", "")
        if explanation:
            explanation_label = QLabel(f"💡 {explanation}")
            explanation_label.setFont(QFont("Arial", 10))
            explanation_label.setWordWrap(True)
            explanation_label.setStyleSheet("""
                color: #555;
                background-color: #FFF9E6;
                padding: 10px;
                border-radius: 5px;
                border-left: 3px solid #FFC107;
            """)
            layout.addWidget(explanation_label)

        return frame

    def format_answer_detailed(
        self, answer: any, q_result: dict, is_user: bool = False
    ) -> str:
        """Format answer for detailed display with question context."""
        q_type = q_result.get("type", "")

        if answer is None:
            return "Не отвечено"

        if q_type == "single_choice":
            options = q_result.get("options", [])
            if isinstance(answer, int) and 0 <= answer < len(options):
                return options[answer]
            return f"Вариант {answer + 1}" if isinstance(answer, int) else str(answer)

        elif q_type == "multiple_choice":
            options = q_result.get("options", [])
            if isinstance(answer, list):
                if not answer:
                    return "Не выбрано"
                # Check if answer contains strings (already formatted) or integers (indices)
                selected = []
                for item in answer:
                    if isinstance(item, int):
                        # It's an index, get the option text
                        if 0 <= item < len(options):
                            selected.append(options[item])
                        else:
                            selected.append(f"Вариант {item + 1}")
                    elif isinstance(item, str):
                        # Already formatted text, use as is
                        selected.append(item)
                    else:
                        # Fallback for other types
                        selected.append(str(item))
                return ", ".join(selected)
            return str(answer)

        elif q_type == "text_input":
            return str(answer) if answer else "Пусто"

        elif q_type == "matching":
            left_items = q_result.get("left_items", [])
            right_items = q_result.get("right_items", [])
            if isinstance(answer, dict):
                if not answer:
                    return "Не сопоставлено"
                pairs = []
                for left_idx, right_idx in answer.items():
                    # Check if indices are integers
                    if isinstance(left_idx, int) and isinstance(right_idx, int):
                        left_text = (
                            left_items[left_idx]
                            if 0 <= left_idx < len(left_items)
                            else f"Элемент {left_idx + 1}"
                        )
                        right_text = (
                            right_items[right_idx]
                            if 0 <= right_idx < len(right_items)
                            else f"Элемент {right_idx + 1}"
                        )
                        pairs.append(f"{left_text} → {right_text}")
                    else:
                        # Already formatted or other type
                        pairs.append(f"{left_idx} → {right_idx}")
                return (
                    "\n".join(pairs)
                    if len(pairs) > 1
                    else pairs[0]
                    if pairs
                    else "Не сопоставлено"
                )
            elif isinstance(answer, list):
                # Already formatted list of strings
                if not answer:
                    return "Не сопоставлено"
                return (
                    "\n".join(answer)
                    if len(answer) > 1
                    else answer[0]
                    if answer
                    else "Не сопоставлено"
                )
            return str(answer)

        elif q_type == "ordering":
            items = q_result.get("items", [])
            if isinstance(answer, list):
                # Check if answer contains strings (already formatted) or integers (indices)
                ordered = []
                for item in answer:
                    if isinstance(item, int):
                        # It's an index, get the item text
                        if 0 <= item < len(items):
                            ordered.append(items[item])
                        else:
                            ordered.append(f"Элемент {item + 1}")
                    elif isinstance(item, str):
                        # Already formatted text, use as is
                        ordered.append(item)
                    else:
                        # Fallback for other types
                        ordered.append(str(item))
                return " → ".join(ordered)
            return str(answer)

        return str(answer)

    def format_answer(self, answer: any, q_type: str) -> str:
        """Format answer for display."""
        if answer is None:
            return "Не отвечено"

        if q_type == "single_choice":
            if isinstance(answer, int):
                return f"Вариант {answer + 1}"
            return str(answer)

        elif q_type == "multiple_choice":
            if isinstance(answer, list):
                if not answer:
                    return "Не выбрано"
                return ", ".join([f"Вариант {i + 1}" for i in answer])
            return str(answer)

        elif q_type == "text_input":
            return str(answer) if answer else "Пусто"

        elif q_type == "matching":
            if isinstance(answer, dict):
                if not answer:
                    return "Не сопоставлено"
                pairs = [f"{k + 1} → {v + 1}" for k, v in answer.items()]
                return "; ".join(pairs)
            return str(answer)

        elif q_type == "ordering":
            if isinstance(answer, list):
                return " → ".join([str(i + 1) for i in answer])
            return str(answer)

        return str(answer)

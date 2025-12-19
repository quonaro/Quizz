"""
Main application window.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..quiz_loader import QuizLoader, QuizValidationError
from ..quiz_builder import create_sample_quiz
from ..quiz_checker import AnswerChecker
from ..quiz_cache import save_cache, load_cache, clear_cache, get_quiz_id
from .question_widgets import create_question_widget
from .results_window import ResultsWindow


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, quiz_data: dict = None, quiz_file_path: str = None):
        super().__init__()
        self.quiz_data = quiz_data
        self.quiz_file_path = quiz_file_path
        self.quiz_id = None
        self.current_question_index = 0
        self.current_question_widget = None
        self.user_answers = {}  # Store user answers: {question_id: answer}
        self.results_shown = False  # Flag to prevent showing results multiple times
        self.restoring_answer = False  # Flag to prevent checking results during answer restoration
        self.results_data = None  # Store results data
        self.showing_results = False  # Flag to track if we're showing results
        self.init_ui()
        
        # Generate quiz ID and load cache
        if self.quiz_data:
            self.quiz_id = get_quiz_id(self.quiz_data, self.quiz_file_path)
            cached_answers = load_cache(self.quiz_id)
            if cached_answers:
                self.user_answers = cached_answers
            self.load_question(0)
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Приложение Квиз")
        self.setGeometry(100, 100, 1400, 1000)
        
        # Apply modern stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2A5F8F;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with gradient
        self.header_label = QLabel("Добро пожаловать! Загрузка квиза...")
        self.header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                padding: 25px;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(self.header_label)
        
        # Scroll area for question widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #e0e0e0;
            }
        """)
        self.scroll_area = scroll_area
        main_layout.addWidget(scroll_area)
        
        # Navigation and action buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        
        self.prev_button = QPushButton("◄ Назад")
        self.prev_button.clicked.connect(self.previous_question)
        self.prev_button.setEnabled(False)
        nav_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("Вперёд ►")
        self.next_button.clicked.connect(self.next_question)
        self.next_button.setEnabled(False)
        nav_layout.addWidget(self.next_button)
        
        nav_layout.addStretch()
        
        self.question_info_label = QLabel("")
        self.question_info_label.setFont(QFont("Arial", 11))
        self.question_info_label.setStyleSheet("color: #666; padding: 5px;")
        nav_layout.addWidget(self.question_info_label)
        
        main_layout.addLayout(nav_layout)
        
        # Status bar
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #e8e8e8;
                color: #333;
            }
        """)
        self.statusBar().showMessage("Готов")
    
    def load_question(self, index: int):
        """Load and display a question by index."""
        if not self.quiz_data:
            return
        
        # Don't allow loading questions if results are shown
        if self.showing_results:
            return
        
        # Save current answer before switching (only if widget exists and is valid)
        if self.current_question_widget is not None:
            try:
                # Quick check if widget is still valid
                _ = self.current_question_widget.parent()
                self.save_current_answer()
            except (RuntimeError, AttributeError):
                # Widget is deleted, skip saving
                pass
        
        questions = self.quiz_data.get("questions", [])
        if not questions or index < 0 or index >= len(questions):
            return
        
        # Update header
        quiz_title = self.quiz_data.get("title", "Квиз")
        self.header_label.setText(f"{quiz_title} - Вопрос {index + 1} из {len(questions)}")
        
        # Get question data
        question_data = questions[index]
        question_id = question_data.get("id")
        
        # Remove old widget safely - clear scroll area first
        old_widget = self.scroll_area.takeWidget()
        if old_widget:
            try:
                old_widget.setParent(None)
            except (RuntimeError, AttributeError):
                pass
        
        # Clear reference to current widget
        if self.current_question_widget is not None:
            try:
                self.current_question_widget.setParent(None)
            except (RuntimeError, AttributeError):
                # Widget already deleted, just clear reference
                pass
            finally:
                self.current_question_widget = None
        
        # Create new question widget
        try:
            self.current_question_widget = create_question_widget(question_data)
            # Connect to answer_changed signal to check if all questions are answered
            self.current_question_widget.answer_changed.connect(self._on_answer_changed)
            # Restore saved answer if exists
            if question_id in self.user_answers:
                self.restoring_answer = True
                self.restore_answer(self.current_question_widget, self.user_answers[question_id])
                self.restoring_answer = False
            self.scroll_area.setWidget(self.current_question_widget)
            
            # For ordering questions, save initial order as default answer if not already saved
            if question_id not in self.user_answers and question_data.get("type") == "ordering":
                self.restoring_answer = True
                initial_answer = self.current_question_widget.get_answer()
                if initial_answer:
                    self.user_answers[question_id] = initial_answer
                self.restoring_answer = False
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать виджет вопроса:\n{str(e)}")
            return
        
        # Update navigation buttons
        self.prev_button.setEnabled(index > 0)
        is_last_question = index >= len(questions) - 1
        if is_last_question:
            # On last question, change button text and behavior
            self.next_button.setText("✓ Показать результаты")
            self.next_button.setEnabled(True)
            # Disconnect all previous connections and connect to show results
            try:
                self.next_button.clicked.disconnect()
            except TypeError:
                pass  # No connections to disconnect
            self.next_button.clicked.connect(self._show_results_on_last_question)
        else:
            # On other questions, normal "Next" behavior
            self.next_button.setText("Вперёд ►")
            self.next_button.setEnabled(True)
            # Disconnect all previous connections and connect to next question
            try:
                self.next_button.clicked.disconnect()
            except TypeError:
                pass  # No connections to disconnect
            self.next_button.clicked.connect(self.next_question)
        
        # Update question info
        q_type = question_data.get("type", "unknown")
        type_names = {
            "single_choice": "Один вариант",
            "multiple_choice": "Несколько вариантов",
            "text_input": "Текстовый ввод",
            "matching": "Сопоставление",
            "ordering": "Упорядочивание"
        }
        type_name = type_names.get(q_type, q_type.replace('_', ' ').title())
        points = question_data.get("points", 1)
        self.question_info_label.setText(f"Тип: {type_name} | Баллы: {points}")
        
        self.current_question_index = index
    
    def save_current_answer(self):
        """Save current question answer."""
        if self.current_question_widget and self.quiz_data:
            questions = self.quiz_data.get("questions", [])
            if 0 <= self.current_question_index < len(questions):
                question_data = questions[self.current_question_index]
                question_id = question_data.get("id")
                if question_id:
                    try:
                        answer = self.current_question_widget.get_answer()
                        self.user_answers[question_id] = answer
                        # Save to cache
                        if self.quiz_id:
                            save_cache(self.quiz_id, self.user_answers)
                    except RuntimeError:
                        # Widget was deleted, skip saving
                        pass
    
    def _on_answer_changed(self, answer):
        """Handle answer change from question widget."""
        # Don't check results if we're restoring an answer
        if self.restoring_answer:
            return
        
        # Save the answer
        self.save_current_answer()
        # Note: Results are no longer shown automatically when all questions are answered
        # User can view results at any time by clicking the button on the last question
    
    def restore_answer(self, widget, answer):
        """Restore saved answer to widget."""
        widget_type = type(widget).__name__
        
        if widget_type == "SingleChoiceWidget":
            if isinstance(answer, int) and 0 <= answer < len(widget.radio_buttons):
                widget.radio_buttons[answer].setChecked(True)
        elif widget_type == "MultipleChoiceWidget":
            if isinstance(answer, list):
                for idx in answer:
                    if 0 <= idx < len(widget.checkboxes):
                        widget.checkboxes[idx].setChecked(True)
        elif widget_type == "TextInputWidget":
            if isinstance(answer, str):
                widget.text_input.setText(answer)
        elif widget_type == "MatchingWidget":
            if isinstance(answer, dict):
                widget.matches = answer.copy()
                # Restore reverse mapping and colors
                widget.right_to_left = {}
                widget.match_colors = {}
                for left_idx, right_idx in answer.items():
                    if 0 <= left_idx < widget.left_list.count() and 0 <= right_idx < widget.right_list.count():
                        widget.right_to_left[right_idx] = left_idx
                        # Assign color if not already assigned
                        if left_idx not in widget.match_colors:
                            widget.match_colors[left_idx] = widget._get_next_color_index()
                # Update visuals
                widget._update_visuals()
        elif widget_type == "OrderingWidget":
            # Restore ordering answer
            if isinstance(answer, list) and widget.items_list:
                # Clear current items
                widget.items_list.clear()
                # Get original items
                original_items = widget.original_items
                if original_items and len(answer) == len(original_items):
                    # Reorder items according to saved answer
                    # answer contains indices of original items in the saved order
                    reordered_items = [original_items[i] for i in answer if 0 <= i < len(original_items)]
                    for item_text in reordered_items:
                        widget.items_list.addItem(item_text)
    
    def next_question(self):
        """Navigate to next question."""
        if self.quiz_data:
            questions = self.quiz_data.get("questions", [])
            # Save current answer before moving
            self.save_current_answer()
            
            if self.current_question_index < len(questions) - 1:
                self.load_question(self.current_question_index + 1)
    
    def _show_results_on_last_question(self):
        """Show results when user clicks button on last question."""
        # Save current answer
        self.save_current_answer()
        # Always show results, even if not all questions are answered
        self.show_results()
    
    def previous_question(self):
        """Navigate to previous question."""
        if self.current_question_index > 0:
            self.load_question(self.current_question_index - 1)
    
    def show_results(self):
        """Show quiz results in the same window."""
        if self.results_shown and self.showing_results:
            return
        
        # Save current answer
        self.save_current_answer()
        
        if not self.quiz_data:
            QMessageBox.warning(self, "Предупреждение", "Квиз не загружен.")
            return
        
        # Set flags
        self.results_shown = True
        self.showing_results = True
        
        # Check answers
        self.results_data = AnswerChecker.check_quiz(self.quiz_data, self.user_answers)
        
        # Update header
        quiz_title = self.quiz_data.get("title", "Квиз")
        self.header_label.setText(f"{quiz_title} - Результаты")
        
        # Create results widget
        results_widget = self._create_results_widget(self.results_data)
        self.scroll_area.setWidget(results_widget)
        
        # Hide navigation buttons
        self.prev_button.setVisible(False)
        self.next_button.setVisible(False)
        self.question_info_label.setVisible(False)
    
    def _create_results_widget(self, results: dict) -> QWidget:
        """Create results widget to display in scroll area."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
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
        total_questions = results.get("total_questions", 0)
        correct_answers = results.get("correct_answers", 0)
        total_points = results.get("total_points", 0.0)
        earned_points = results.get("earned_points", 0.0)
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        
        score_text = f"Правильных ответов: {correct_answers} из {total_questions}"
        points_text = f"Баллов: {earned_points:.1f} из {total_points:.1f} ({percentage:.1f}%)"
        
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
        
        # Add question results
        for i, q_result in enumerate(results.get("questions", []), 1):
            question_frame = self._create_question_result_widget(q_result, i)
            layout.addWidget(question_frame)
        
        # Add "Restart quiz" button
        restart_button = QPushButton("🔄 Начать тест заново")
        restart_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        restart_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        restart_button.clicked.connect(self._restart_quiz)
        layout.addWidget(restart_button)
        
        layout.addStretch()
        return widget
    
    def _create_question_result_widget(self, q_result: dict, question_num: int) -> QFrame:
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
        
        points_label = QLabel(f"Баллы: {q_result.get('earned_points', 0):.1f}/{q_result.get('points', 0):.1f}")
        points_label.setFont(QFont("Arial", 11))
        points_label.setStyleSheet("color: #666;")
        header_layout.addWidget(points_label)
        
        layout.addLayout(header_layout)
        
        # Question text
        question_label = QLabel(f"Вопрос {question_num}: {q_result.get('question', '')}")
        question_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        question_label.setWordWrap(True)
        question_label.setStyleSheet("color: #333;")
        layout.addWidget(question_label)
        
        # User answer
        user_answer = q_result.get("user_answer")
        user_answer_text = self._format_answer_detailed(user_answer, q_result, is_user=True)
        
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
        if isinstance(correct_answer, (list, dict)):
            correct_answer_text = self._format_answer_detailed(correct_answer, q_result, is_user=False)
        else:
            correct_answer_text = str(correct_answer) if correct_answer is not None else "Не указано"
        
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
    
    def _format_answer_detailed(self, answer: any, q_result: dict, is_user: bool = False) -> str:
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
                selected = []
                for item in answer:
                    if isinstance(item, int):
                        if 0 <= item < len(options):
                            selected.append(options[item])
                        else:
                            selected.append(f"Вариант {item + 1}")
                    elif isinstance(item, str):
                        selected.append(item)
                    else:
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
                    if isinstance(left_idx, int) and isinstance(right_idx, int):
                        left_text = left_items[left_idx] if 0 <= left_idx < len(left_items) else f"Элемент {left_idx + 1}"
                        right_text = right_items[right_idx] if 0 <= right_idx < len(right_items) else f"Элемент {right_idx + 1}"
                        pairs.append(f"{left_text} → {right_text}")
                    else:
                        pairs.append(f"{left_idx} → {right_idx}")
                return "\n".join(pairs) if len(pairs) > 1 else pairs[0] if pairs else "Не сопоставлено"
            elif isinstance(answer, list):
                if not answer:
                    return "Не сопоставлено"
                return "\n".join(answer) if len(answer) > 1 else answer[0] if answer else "Не сопоставлено"
            return str(answer)
        
        elif q_type == "ordering":
            items = q_result.get("items", [])
            if isinstance(answer, list):
                ordered = []
                for item in answer:
                    if isinstance(item, int):
                        if 0 <= item < len(items):
                            ordered.append(items[item])
                        else:
                            ordered.append(f"Элемент {item + 1}")
                    elif isinstance(item, str):
                        ordered.append(item)
                    else:
                        ordered.append(str(item))
                return " → ".join(ordered)
            return str(answer)
        
        return str(answer)
    
    def _restart_quiz(self):
        """Restart quiz by clearing cache and resetting state."""
        # Clear cache for this quiz
        if self.quiz_id:
            clear_cache(self.quiz_id)
        
        # Clear scroll area first (this removes the widget from display)
        old_widget = self.scroll_area.takeWidget()
        if old_widget:
            try:
                old_widget.setParent(None)
            except (RuntimeError, AttributeError):
                pass
        
        # Clear reference to current widget
        if self.current_question_widget is not None:
            try:
                self.current_question_widget.setParent(None)
            except (RuntimeError, AttributeError):
                pass  # Widget already deleted
            finally:
                self.current_question_widget = None
        
        # Reset state
        self.user_answers = {}
        self.results_shown = False
        self.showing_results = False
        self.results_data = None
        self.current_question_index = 0
        
        # Show navigation buttons again
        self.prev_button.setVisible(True)
        self.next_button.setVisible(True)
        self.question_info_label.setVisible(True)
        
        # Show first question (don't save current answer as widget is already cleared)
        if self.quiz_data:
            # Temporarily disable saving to avoid errors
            questions = self.quiz_data.get("questions", [])
            if questions:
                self.load_question(0)


def main(quiz_data: dict = None, quiz_file_path: str = None):
    """Main entry point."""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern, cross-platform style
    
    # Load quiz if not provided
    if quiz_data is None:
        quiz_data = create_sample_quiz()
    
    window = MainWindow(quiz_data, quiz_file_path)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


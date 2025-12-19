"""
UI widgets for different question types.
"""

from typing import List, Optional, Union, Callable
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, 
    QCheckBox, QLineEdit, QPushButton, QScrollArea, QGroupBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
import requests
from urllib.parse import urlparse


class ImageLabel(QLabel):
    """Label widget for displaying images."""
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(True)
        self.setMaximumSize(400, 300)
        self.load_image(image_path)
    
    def load_image(self, image_path: str):
        """Load image from local path, URL, or embedded image."""
        try:
            # Check if it's an embedded image
            if image_path.startswith("__EMBEDDED__:"):
                try:
                    from ..embedded_quiz import get_embedded_image_path
                    image_path = get_embedded_image_path(image_path)
                except ImportError:
                    self.setText(f"Ошибка: модуль embedded_quiz не найден")
                    return
            
            # Check if it's a URL
            parsed = urlparse(image_path)
            if parsed.scheme in ('http', 'https'):
                # Load from URL
                response = requests.get(image_path, timeout=5)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    self.setPixmap(pixmap)
                else:
                    self.setText(f"Не удалось загрузить изображение с URL")
            else:
                # Load from local file
                path = Path(image_path)
                if path.exists():
                    pixmap = QPixmap(str(path))
                    if not pixmap.isNull():
                        self.setPixmap(pixmap)
                    else:
                        self.setText(f"Неверный файл изображения: {image_path}")
                else:
                    self.setText(f"Изображение не найдено: {image_path}")
        except Exception as e:
            self.setText(f"Ошибка загрузки изображения: {str(e)}")


class BaseQuestionWidget(QWidget):
    """Base class for question widgets."""
    
    answer_changed = pyqtSignal(object)  # Emitted when answer changes
    
    def __init__(self, question_data: dict, parent=None):
        super().__init__(parent)
        self.question_data = question_data
        self.layout = QVBoxLayout(self)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI. Override in subclasses."""
        # Question text with improved styling
        question_label = QLabel(self.question_data.get("question", ""))
        question_label.setWordWrap(True)
        question_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #4A90E2;
            }
        """)
        self.layout.addWidget(question_label)
        
        # Images
        images = self.question_data.get("images")
        if images:
            if isinstance(images, str):
                images = [images]
            
            images_layout = QHBoxLayout()
            for img_path in images:
                img_label = ImageLabel(img_path)
                images_layout.addWidget(img_label)
            self.layout.addLayout(images_layout)
    
    def get_answer(self):
        """Get the current answer. Override in subclasses."""
        return None


class SingleChoiceWidget(BaseQuestionWidget):
    """Widget for single choice questions."""
    
    def __init__(self, question_data: dict, parent=None):
        self.radio_buttons = []
        super().__init__(question_data, parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Radio buttons for options with improved styling
        options = self.question_data.get("options", [])
        for i, option in enumerate(options):
            radio = QRadioButton(option)
            radio.setStyleSheet("""
                QRadioButton {
                    font-size: 13pt;
                    color: #34495e;
                    padding: 10px;
                    spacing: 10px;
                }
                QRadioButton:hover {
                    background-color: #ecf0f1;
                    border-radius: 5px;
                }
                QRadioButton::indicator {
                    width: 20px;
                    height: 20px;
                }
                QRadioButton::indicator:unchecked {
                    border: 2px solid #bdc3c7;
                    border-radius: 10px;
                    background-color: white;
                }
                QRadioButton::indicator:checked {
                    border: 2px solid #4A90E2;
                    border-radius: 10px;
                    background-color: #4A90E2;
                }
            """)
            radio.toggled.connect(self._on_answer_changed)
            self.radio_buttons.append(radio)
            self.layout.addWidget(radio)
        
        self.layout.addStretch()
    
    def _on_answer_changed(self):
        """Handle radio button change."""
        self.answer_changed.emit(self.get_answer())
    
    def get_answer(self) -> Optional[int]:
        """Get selected answer index."""
        for i, radio in enumerate(self.radio_buttons):
            if radio.isChecked():
                return i
        return None


class MultipleChoiceWidget(BaseQuestionWidget):
    """Widget for multiple choice questions."""
    
    def __init__(self, question_data: dict, parent=None):
        self.checkboxes = []
        super().__init__(question_data, parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Checkboxes for options with improved styling
        options = self.question_data.get("options", [])
        for option in options:
            checkbox = QCheckBox(option)
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 13pt;
                    color: #34495e;
                    padding: 10px;
                    spacing: 10px;
                }
                QCheckBox:hover {
                    background-color: #ecf0f1;
                    border-radius: 5px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #bdc3c7;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #4CAF50;
                    border-radius: 4px;
                    background-color: #4CAF50;
                }
            """)
            checkbox.toggled.connect(self._on_answer_changed)
            self.checkboxes.append(checkbox)
            self.layout.addWidget(checkbox)
        
        self.layout.addStretch()
    
    def _on_answer_changed(self):
        """Handle checkbox change."""
        self.answer_changed.emit(self.get_answer())
    
    def get_answer(self) -> List[int]:
        """Get selected answer indices."""
        return [i for i, checkbox in enumerate(self.checkboxes) if checkbox.isChecked()]


class TextInputWidget(BaseQuestionWidget):
    """Widget for text input questions."""
    
    def setup_ui(self):
        super().setup_ui()
        
        # Text input field with improved styling
        self.text_input = QLineEdit()
        self.text_input.setStyleSheet("""
            QLineEdit {
                font-size: 13pt;
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        self.text_input.setPlaceholderText("Введите ваш ответ...")
        self.text_input.textChanged.connect(self._on_answer_changed)
        self.layout.addWidget(self.text_input)
        
        self.layout.addStretch()
    
    def _on_answer_changed(self):
        """Handle text input change."""
        self.answer_changed.emit(self.get_answer())
    
    def get_answer(self) -> str:
        """Get entered text."""
        return self.text_input.text()


class MatchingWidget(BaseQuestionWidget):
    """Widget for matching questions."""
    
    # Color palette for matched pairs
    MATCH_COLORS = [
        QColor(173, 216, 230),  # Light blue
        QColor(144, 238, 144),  # Light green
        QColor(255, 182, 193),  # Light pink
        QColor(255, 218, 185),  # Peach
        QColor(221, 160, 221),  # Plum
        QColor(176, 224, 230),  # Powder blue
        QColor(255, 228, 196),  # Bisque
        QColor(240, 255, 240),  # Honeydew
    ]
    
    def __init__(self, question_data: dict, parent=None):
        self.left_list = None
        self.right_list = None
        self.matches = {}  # left_index -> right_index
        self.match_colors = {}  # left_index -> color_index
        self.selected_left = -1  # Currently selected left item
        self.right_to_left = {}  # right_index -> left_index (reverse mapping)
        super().__init__(question_data, parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Two-column layout for matching
        columns_layout = QHBoxLayout()
        
        # Left items with improved styling
        left_group = QGroupBox("Левая колонка")
        left_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        left_layout = QVBoxLayout()
        self.left_list = QListWidget()
        self.left_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        self.left_list.itemClicked.connect(self._on_left_clicked)
        self.left_list.itemDoubleClicked.connect(self._on_left_double_clicked)
        left_items = self.question_data.get("left_items", [])
        for item in left_items:
            self.left_list.addItem(item)
        left_layout.addWidget(self.left_list)
        left_group.setLayout(left_layout)
        
        # Right items with improved styling
        right_group = QGroupBox("Правая колонка")
        right_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        right_layout = QVBoxLayout()
        self.right_list = QListWidget()
        self.right_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        self.right_list.itemClicked.connect(self._on_right_clicked)
        self.right_list.itemDoubleClicked.connect(self._on_right_double_clicked)
        right_items = self.question_data.get("right_items", [])
        for item in right_items:
            self.right_list.addItem(item)
        right_layout.addWidget(self.right_list)
        right_group.setLayout(right_layout)
        
        columns_layout.addWidget(left_group)
        columns_layout.addWidget(right_group)
        self.layout.addLayout(columns_layout)
        
        # Instructions with improved styling
        instructions = QLabel(
            "Нажмите на элемент слева, затем нажмите на соответствующий элемент справа.\n"
            "Двойной клик удаляет сопоставление."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                color: #7f8c8d;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(instructions)
        
        self.layout.addStretch()
    
    def _get_next_color_index(self) -> int:
        """Get next available color index for a new match."""
        used_indices = set(self.match_colors.values())
        for i in range(len(self.MATCH_COLORS)):
            if i not in used_indices:
                return i
        # If all colors are used, cycle through them
        return len(used_indices) % len(self.MATCH_COLORS)
    
    def _update_visuals(self):
        """Update visual appearance of all items based on current matches."""
        # Reset all items to default background
        for i in range(self.left_list.count()):
            item = self.left_list.item(i)
            if i in self.matches:
                # Item is matched, use its assigned color
                color_idx = self.match_colors.get(i, 0)
                color = self.MATCH_COLORS[color_idx % len(self.MATCH_COLORS)]
                item.setBackground(color)
            else:
                # Item is not matched, use default
                item.setBackground(Qt.GlobalColor.white)
        
        for i in range(self.right_list.count()):
            item = self.right_list.item(i)
            if i in self.right_to_left:
                # Item is matched, use the same color as its left partner
                left_idx = self.right_to_left[i]
                color_idx = self.match_colors.get(left_idx, 0)
                color = self.MATCH_COLORS[color_idx % len(self.MATCH_COLORS)]
                item.setBackground(color)
            else:
                # Item is not matched, use default
                item.setBackground(Qt.GlobalColor.white)
    
    def _on_left_clicked(self, item: QListWidgetItem):
        """Handle left item click."""
        left_index = self.left_list.row(item)
        self.selected_left = left_index
        
        # Highlight selected left item
        for i in range(self.left_list.count()):
            self.left_list.item(i).setSelected(i == left_index)
    
    def _on_left_double_clicked(self, item: QListWidgetItem):
        """Handle left item double click - remove match."""
        left_index = self.left_list.row(item)
        if left_index in self.matches:
            right_index = self.matches[left_index]
            # Remove from matches
            del self.matches[left_index]
            # Remove from reverse mapping
            if right_index in self.right_to_left:
                del self.right_to_left[right_index]
            # Remove color assignment
            if left_index in self.match_colors:
                del self.match_colors[left_index]
            # Update visuals
            self._update_visuals()
            self.selected_left = -1
    
    def _on_right_clicked(self, item: QListWidgetItem):
        """Handle right item click."""
        right_index = self.right_list.row(item)
        left_selected = self.selected_left
        
        # If right item is already matched, remove old match first
        if right_index in self.right_to_left:
            old_left = self.right_to_left[right_index]
            if old_left in self.matches:
                del self.matches[old_left]
            if old_left in self.match_colors:
                del self.match_colors[old_left]
            del self.right_to_left[right_index]
        
        # If left item is already matched, remove old match
        if left_selected >= 0:
            if left_selected in self.matches:
                old_right = self.matches[left_selected]
                if old_right in self.right_to_left:
                    del self.right_to_left[old_right]
                # Keep color assignment for reuse
            
            # Create new match
            self.matches[left_selected] = right_index
            self.right_to_left[right_index] = left_selected
            
            # Assign color if not already assigned
            if left_selected not in self.match_colors:
                self.match_colors[left_selected] = self._get_next_color_index()
            
            # Update visuals
            self._update_visuals()
            
            # Clear selection after matching
            self.selected_left = -1
            self.left_list.clearSelection()
    
    def _on_right_double_clicked(self, item: QListWidgetItem):
        """Handle right item double click - remove match."""
        right_index = self.right_list.row(item)
        if right_index in self.right_to_left:
            left_index = self.right_to_left[right_index]
            # Remove from matches
            if left_index in self.matches:
                del self.matches[left_index]
            # Remove from reverse mapping
            del self.right_to_left[right_index]
            # Remove color assignment
            if left_index in self.match_colors:
                del self.match_colors[left_index]
            # Update visuals
            self._update_visuals()
    
    def get_answer(self) -> dict:
        """Get current matches."""
        return self.matches.copy()


class OrderingWidget(BaseQuestionWidget):
    """Widget for ordering questions."""
    
    def __init__(self, question_data: dict, parent=None):
        self.items_list = None
        self.original_items = []  # Store original items list to map current order to original indices
        super().__init__(question_data, parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Instructions with improved styling
        instructions = QLabel("Перетащите элементы для изменения порядка. Порядок сверху вниз.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                color: #7f8c8d;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(instructions)
        
        # List widget with drag and drop and improved styling
        self.items_list = QListWidget()
        self.items_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        self.items_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        items = self.question_data.get("items", [])
        self.original_items = items.copy()  # Store original order
        for item in items:
            self.items_list.addItem(item)
        self.items_list.model().rowsMoved.connect(self._on_order_changed)
        self.layout.addWidget(self.items_list)
        
        # Buttons for manual reordering with improved styling
        buttons_layout = QHBoxLayout()
        move_up_btn = QPushButton("▲ Вверх")
        move_up_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        move_up_btn.clicked.connect(self._move_up)
        move_down_btn = QPushButton("▼ Вниз")
        move_down_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        move_down_btn.clicked.connect(self._move_down)
        buttons_layout.addWidget(move_up_btn)
        buttons_layout.addWidget(move_down_btn)
        buttons_layout.addStretch()
        self.layout.addLayout(buttons_layout)
        
        self.layout.addStretch()
    
    def _on_order_changed(self):
        """Handle order change."""
        self.answer_changed.emit(self.get_answer())
    
    def _move_up(self):
        """Move selected item up."""
        current = self.items_list.currentRow()
        if current > 0:
            item = self.items_list.takeItem(current)
            self.items_list.insertItem(current - 1, item)
            self.items_list.setCurrentRow(current - 1)
            self._on_order_changed()
    
    def _move_down(self):
        """Move selected item down."""
        current = self.items_list.currentRow()
        if current < self.items_list.count() - 1 and current >= 0:
            item = self.items_list.takeItem(current)
            self.items_list.insertItem(current + 1, item)
            self.items_list.setCurrentRow(current + 1)
            self._on_order_changed()
    
    def get_answer(self) -> List[int]:
        """Get current order (indices of original items in current order)."""
        if not self.items_list or not self.original_items:
            return []
        
        # For each item in current order, find its index in original items list
        current_order = []
        for i in range(self.items_list.count()):
            item_text = self.items_list.item(i).text()
            try:
                original_index = self.original_items.index(item_text)
                current_order.append(original_index)
            except ValueError:
                # Item not found in original list, skip or use current position
                current_order.append(i)
        
        return current_order


def create_question_widget(question_data: dict, parent=None) -> BaseQuestionWidget:
    """
    Factory function to create appropriate question widget.
    
    Args:
        question_data: Question dictionary from JSON.
        parent: Parent widget.
        
    Returns:
        Appropriate question widget instance.
    """
    q_type = question_data.get("type")
    
    if q_type == "single_choice":
        return SingleChoiceWidget(question_data, parent)
    elif q_type == "multiple_choice":
        return MultipleChoiceWidget(question_data, parent)
    elif q_type == "text_input":
        return TextInputWidget(question_data, parent)
    elif q_type == "matching":
        return MatchingWidget(question_data, parent)
    elif q_type == "ordering":
        return OrderingWidget(question_data, parent)
    else:
        raise ValueError(f"Unknown question type: {q_type}")


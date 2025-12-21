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
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint, QRect, QTimer
from PyQt6.QtGui import QPixmap, QColor, QDrag, QPainter, QPen
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


class MatchingContainerWidget(QWidget):
    """Container widget that draws lines between matched items in two lists."""
    
    def __init__(self, left_list, right_list, matches, match_colors, parent=None):
        super().__init__(parent)
        self.left_list = left_list
        self.right_list = right_list
        self.matches = matches  # Reference to matches dict
        self.match_colors = match_colors  # Reference to match_colors dict
        
        # Get MATCH_COLORS from parent if available
        if parent:
            matching_widget = parent
            while matching_widget:
                if hasattr(matching_widget, 'MATCH_COLORS'):
                    self.MATCH_COLORS = matching_widget.MATCH_COLORS
                    break
                matching_widget = matching_widget.parent()
            else:
                self.MATCH_COLORS = [
                    QColor(173, 216, 230), QColor(144, 238, 144), 
                    QColor(255, 182, 193), QColor(255, 218, 185)
                ]
        else:
            self.MATCH_COLORS = [
                QColor(173, 216, 230), QColor(144, 238, 144), 
                QColor(255, 182, 193), QColor(255, 218, 185)
            ]
        
        # Set background transparent so lines are visible
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setStyleSheet("background: transparent;")
        
        # Install event filter to resize when parent resizes
        if parent:
            parent.installEventFilter(self)
            # Make sure lines widget is on top
            self.raise_()
    
    def eventFilter(self, obj, event):
        """Handle resize events to update widget position."""
        if obj == self.parent() and event.type() == event.Type.Resize:
            self.setGeometry(0, 0, obj.width(), obj.height())
        return super().eventFilter(obj, event)
    
    def showEvent(self, event):
        """Update geometry when shown."""
        super().showEvent(event)
        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
    
    def paintEvent(self, event):
        """Draw lines connecting matched items."""
        if not self.matches:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get positions of both lists relative to parent
        parent = self.parent()
        if not parent:
            return
        
        # Ensure widget covers entire parent area
        if self.geometry() != parent.rect():
            self.setGeometry(parent.rect())
        
        for left_idx, right_idx in self.matches.items():
            try:
                left_idx = int(left_idx)
                right_idx = int(right_idx)
            except (ValueError, TypeError):
                continue
            
            # Get left item position
            left_item = None
            for i in range(self.left_list.count()):
                item = self.left_list.item(i)
                item_index = item.data(Qt.ItemDataRole.UserRole)
                try:
                    if int(item_index) == left_idx:
                        left_item = item
                        break
                except (ValueError, TypeError):
                    continue
            
            # Get right item position
            right_item = None
            for i in range(self.right_list.count()):
                item = self.right_list.item(i)
                item_index = item.data(Qt.ItemDataRole.UserRole)
                try:
                    if int(item_index) == right_idx:
                        right_item = item
                        break
                except (ValueError, TypeError):
                    continue
            
            if not left_item or not right_item:
                continue
            
            # Calculate item positions relative to their list widgets
            left_item_rect = self.left_list.visualItemRect(left_item)
            right_item_rect = self.right_list.visualItemRect(right_item)
            
            # Calculate center Y positions of items within their lists
            left_item_center_y = left_item_rect.y() + left_item_rect.height() // 2
            right_item_center_y = right_item_rect.y() + right_item_rect.height() // 2
            
            # Get list widget positions in parent coordinates
            left_list_pos_in_parent = self.left_list.mapTo(parent, QPoint(0, 0))
            right_list_pos_in_parent = self.right_list.mapTo(parent, QPoint(0, 0))
            
            # Get list widget sizes
            left_list_width = self.left_list.width()
            right_list_width = self.right_list.width()
            
            # Calculate absolute positions in parent coordinates
            # Left point: right edge of left list
            left_point_abs = QPoint(
                left_list_pos_in_parent.x() + left_list_width,
                left_list_pos_in_parent.y() + left_item_center_y
            )
            # Right point: left edge of right list
            right_point_abs = QPoint(
                right_list_pos_in_parent.x(),
                right_list_pos_in_parent.y() + right_item_center_y
            )
            
            # Convert to this widget's coordinates (this widget is on top of parent)
            left_point = left_point_abs
            right_point = right_point_abs
            
            # Get color for this match
            color_idx = self.match_colors.get(left_idx, 0)
            color = self.MATCH_COLORS[color_idx % len(self.MATCH_COLORS)] if self.MATCH_COLORS else QColor(173, 216, 230)
            
            # Draw line
            pen = QPen(color, 3)
            painter.setPen(pen)
            painter.drawLine(left_point, right_point)
    
    def update_lines(self):
        """Update the drawn lines."""
        if self.parent():
            parent = self.parent()
            # Set geometry to cover entire parent
            self.setGeometry(parent.rect())
            self.raise_()  # Make sure it's on top
            self.setVisible(True)
        self.update()
        self.repaint()  # Force repaint


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
        self.right_to_left = {}  # right_index -> left_index (reverse mapping)
        self.selected_left_index = None  # Currently selected left item index
        self.lines_widget = None  # Widget for drawing lines
        super().__init__(question_data, parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Container widget for lists and lines
        container_widget = QWidget()
        container_layout = QHBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
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
                background-color: white;
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
        for i, item_text in enumerate(left_items):
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)  # Store original index
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
                background-color: white;
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
        for i, item_text in enumerate(right_items):
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)  # Store original index
            self.right_list.addItem(item)
        right_layout.addWidget(self.right_list)
        right_group.setLayout(right_layout)
        
        container_layout.addWidget(left_group)
        
        # Add spacer for lines
        spacer = QWidget()
        spacer.setMinimumWidth(50)
        spacer.setMaximumWidth(50)
        spacer.setStyleSheet("background: transparent;")
        container_layout.addWidget(spacer)
        
        container_layout.addWidget(right_group)
        
        # Create a wrapper widget to hold container and lines widget
        wrapper_widget = QWidget()
        wrapper_layout = QVBoxLayout(wrapper_widget)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(container_widget)
        
        # Create lines widget that will draw lines between items
        self.lines_widget = MatchingContainerWidget(
            self.left_list, self.right_list, 
            self.matches, self.match_colors, wrapper_widget
        )
        # Pass MATCH_COLORS reference
        self.lines_widget.MATCH_COLORS = self.MATCH_COLORS
        
        self.layout.addWidget(wrapper_widget)
        
        # Show lines widget after layout and raise it to top
        self.lines_widget.show()
        self.lines_widget.raise_()
        
        # Update lines widget geometry after a short delay to ensure layout is complete
        QTimer.singleShot(100, self._update_lines_widget_geometry)
        QTimer.singleShot(200, self._update_lines_widget_geometry)  # Double check
        QTimer.singleShot(500, self._update_lines_widget_geometry)  # Triple check after everything is settled
    
    def _update_lines_widget_geometry(self):
        """Update lines widget geometry after layout is complete."""
        if self.lines_widget and self.lines_widget.parent():
            parent = self.lines_widget.parent()
            self.lines_widget.setGeometry(0, 0, parent.width(), parent.height())
            self.lines_widget.raise_()  # Make sure it's on top
            self.lines_widget.update()
            self.lines_widget.repaint()
        
        # Install event filter on lists to update lines when scrolled
        self.left_list.verticalScrollBar().valueChanged.connect(self._update_lines)
        self.right_list.verticalScrollBar().valueChanged.connect(self._update_lines)
        
        # Instructions with improved styling
        instructions = QLabel(
            "Нажмите на элемент в левой колонке, затем на соответствующий элемент в правой колонке для создания связи.\n"
            "Двойной клик на сопоставленном элементе удаляет связь."
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
        """Update visual appearance and lines based on current matches."""
        # Update item backgrounds
        for i in range(self.left_list.count()):
            item = self.left_list.item(i)
            left_index = item.data(Qt.ItemDataRole.UserRole)
            if left_index is not None:
                try:
                    left_index = int(left_index) if not isinstance(left_index, int) else left_index
                    if left_index == self.selected_left_index:
                        # Highlight selected item
                        item.setBackground(QColor(255, 200, 100))  # Orange highlight
                    elif left_index in self.matches:
                        # Item is matched - subtle background
                        item.setBackground(QColor(240, 240, 240))
                    else:
                        item.setBackground(Qt.GlobalColor.white)
                except (ValueError, TypeError):
                    item.setBackground(Qt.GlobalColor.white)
            else:
                item.setBackground(Qt.GlobalColor.white)
        
        for i in range(self.right_list.count()):
            item = self.right_list.item(i)
            right_index = item.data(Qt.ItemDataRole.UserRole)
            if right_index is not None:
                try:
                    right_index = int(right_index) if not isinstance(right_index, int) else right_index
                    if right_index in self.right_to_left:
                        # Item is matched - subtle background
                        item.setBackground(QColor(240, 240, 240))
                    else:
                        item.setBackground(Qt.GlobalColor.white)
                except (ValueError, TypeError):
                    item.setBackground(Qt.GlobalColor.white)
            else:
                item.setBackground(Qt.GlobalColor.white)
        
        # Update lines
        self._update_lines()
    
    def _update_lines(self):
        """Update the line visualization."""
        if self.lines_widget:
            self.lines_widget.update_lines()
    
    def _on_left_clicked(self, item: QListWidgetItem):
        """Handle left item click - select it for matching."""
        left_index = item.data(Qt.ItemDataRole.UserRole)
        if left_index is not None:
            try:
                left_index = int(left_index) if not isinstance(left_index, int) else left_index
                self.selected_left_index = left_index
                self._update_visuals()
            except (ValueError, TypeError):
                pass
    
    def _on_right_clicked(self, item: QListWidgetItem):
        """Handle right item click - create match if left item is selected."""
        right_index = item.data(Qt.ItemDataRole.UserRole)
        
        # If no left item is selected, just ignore
        if self.selected_left_index is None:
            # Try to deselect if clicking on already matched item
            if right_index is not None:
                try:
                    right_index = int(right_index) if not isinstance(right_index, int) else right_index
                    # Don't do anything, just return
                except (ValueError, TypeError):
                    pass
            return
        
        if right_index is not None:
            try:
                right_index = int(right_index) if not isinstance(right_index, int) else right_index
                left_index = self.selected_left_index
                
                # If right item is already matched, remove old match first
                if right_index in self.right_to_left:
                    old_left = self.right_to_left[right_index]
                    if old_left in self.matches:
                        del self.matches[old_left]
                    if old_left in self.match_colors:
                        del self.match_colors[old_left]
                    del self.right_to_left[right_index]
                
                # If left item is already matched, remove old match
                if left_index in self.matches:
                    old_right = self.matches[left_index]
                    if old_right in self.right_to_left:
                        del self.right_to_left[old_right]
                    # Keep color assignment for reuse
                
                # Create new match
                self.matches[left_index] = right_index
                self.right_to_left[right_index] = left_index
                
                # Assign color if not already assigned
                if left_index not in self.match_colors:
                    self.match_colors[left_index] = self._get_next_color_index()
                
                # Clear selection
                self.selected_left_index = None
                
                # Update visuals immediately
                self._update_visuals()
                
                # Force update of lines widget multiple times to ensure it's visible
                if self.lines_widget:
                    self.lines_widget.update_lines()
                    # Also schedule delayed update in case geometry wasn't ready
                    QTimer.singleShot(50, self.lines_widget.update_lines)
                    QTimer.singleShot(150, self.lines_widget.update_lines)
                
                # Emit signal that answer changed
                self.answer_changed.emit(self.get_answer())
            except (ValueError, TypeError):
                pass
    
    def _on_left_double_clicked(self, item: QListWidgetItem):
        """Handle left item double click - remove match."""
        left_index = item.data(Qt.ItemDataRole.UserRole)
        if left_index is not None and left_index in self.matches:
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
            # Emit signal that answer changed
            self.answer_changed.emit(self.get_answer())
    
    def _on_right_double_clicked(self, item: QListWidgetItem):
        """Handle right item double click - remove match."""
        right_index = item.data(Qt.ItemDataRole.UserRole)
        if right_index is not None and right_index in self.right_to_left:
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
            # Emit signal that answer changed
            self.answer_changed.emit(self.get_answer())
    
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


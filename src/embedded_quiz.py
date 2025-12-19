"""
Embedded quiz data for standalone executable.
This file is auto-generated during build process.
"""

import base64
from pathlib import Path
import tempfile
import os

# Embedded quiz JSON data
QUIZ_JSON = """{
  "title": "Пример квиза",
  "questions": [
    {
      "id": "q1",
      "type": "single_choice",
      "question": "Один правильный ответ",
      "images": "quiz/a.jpg",
      "options": [
        "A",
        "B"
      ],
      "correct_answer": 0
    },
    {
      "id": "q2",
      "type": "multiple_choice",
      "question": "Несколько правильных",
      "options": [
        "A",
        "B",
        "C"
      ],
      "correct_answers": [
        0,
        1
      ]
    },
    {
      "id": "q3",
      "type": "text_input",
      "question": "Введите ответ",
      "correct_answers": [
        "Москва",
        "Moscow"
      ],
      "case_sensitive": false
    },
    {
      "id": "q4",
      "type": "matching",
      "question": "Сопоставьте",
      "left_items": [
        "Франция",
        "Германия"
      ],
      "right_items": [
        "Париж",
        "Берлин"
      ],
      "matches": [
        {
          "left": 0,
          "right": 0
        },
        {
          "left": 1,
          "right": 1
        }
      ]
    },
    {
      "id": "q5",
      "type": "ordering",
      "question": "Расположите по порядку",
      "items": [
        "Второй",
        "Первый",
        "Третий"
      ],
      "correct_order": [
        1,
        0,
        2
      ]
    }
  ],
  "description": "Демонстрационный квиз со всеми типами вопросов"
}"""

# Embedded images (base64 encoded)
EMBEDDED_IMAGES = {
}

# Cache for temporary image files
_temp_image_cache = {}


def get_quiz_data():
    """Load and return quiz data from embedded JSON."""
    import json
    return json.loads(QUIZ_JSON)


def get_embedded_image_path(embedded_path: str):
    """
    Get a temporary file path for an embedded image.
    
    Args:
        embedded_path: Path in format "__EMBEDDED__:relative/path/to/image.jpg"
        
    Returns:
        Path to temporary file containing the image.
    """
    if not embedded_path.startswith("__EMBEDDED__:"):
        # Not an embedded image, return as-is
        return embedded_path
    
    # Extract relative path
    rel_path = embedded_path.replace("__EMBEDDED__:", "", 1)
    
    # Check cache
    if rel_path in _temp_image_cache:
        cached_path = _temp_image_cache[rel_path]
        if Path(cached_path).exists():
            return cached_path
    
    # Decode and save to temp file
    if rel_path not in EMBEDDED_IMAGES:
        return embedded_path
    
    img_base64 = EMBEDDED_IMAGES[rel_path]
    img_data = base64.b64decode(img_base64)
    
    # Create temp file
    temp_dir = Path(tempfile.gettempdir()) / "quiz_embedded_images"
    temp_dir.mkdir(exist_ok=True)
    
    # Use filename from rel_path
    filename = Path(rel_path).name
    temp_file = temp_dir / filename
    
    with open(temp_file, 'wb') as f:
        f.write(img_data)
    
    # Cache it
    _temp_image_cache[rel_path] = str(temp_file)
    
    return str(temp_file)


def resolve_embedded_images(quiz_data):
    """
    Resolve embedded image paths in quiz data to temporary file paths.
    
    Args:
        quiz_data: Quiz data dictionary (may be modified in-place).
        
    Returns:
        Quiz data with resolved image paths.
    """
    for question in quiz_data.get("questions", []):
        if "images" in question:
            images = question["images"]
            if isinstance(images, str):
                question["images"] = get_embedded_image_path(images)
            elif isinstance(images, list):
                resolved_images = []
                for img in images:
                    resolved_images.append(get_embedded_image_path(img))
                question["images"] = resolved_images
    
    return quiz_data

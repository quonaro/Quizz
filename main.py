import json
import time
import os
import sys

# Добавляем папку lib в пути поиска, чтобы использовать встроенные зависимости
# Add the lib folder to the search paths to use bundled dependencies
def get_resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу, работает для скрипта и для EXE """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    # Для Nuitka в режиме --onefile или обычного запуска
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    # Если мы в режиме разработки, проверяем текущую директорию
    if not os.path.exists(os.path.join(base_path, relative_path)):
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

lib_path = get_resource_path('lib')
if os.path.exists(lib_path):
    sys.path.append(lib_path)

# Импортируем библиотеки для работы с картинками (теперь они в папке lib)
# Import libraries for working with images (they are now in the lib folder)
try:
    from PIL import Image, ImageTk
    import tkinter as tk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

def show_image(image_path, duration=3):
    """Показывает картинку в окне на несколько секунд"""
    if not HAS_GUI:
        print(f"Ошибка: Библиотеки (PIL/tkinter) не загружены. Проверьте папку 'lib'.")
        return

    try:
        full_path = os.path.abspath(image_path)
        if not os.path.exists(full_path):
            print(f"Ошибка: Файл не найден по пути: {full_path}")
            return

        # Создаем окно
        root = tk.Tk()
        root.title("Quiz Image")
        
        # Попробуем поднять окно на передний план
        root.attributes("-topmost", True)
        
        # Убираем рамки окна
        root.overrideredirect(True)

        # Загружаем картинку
        img = Image.open(full_path)
        img.thumbnail((600, 600))
        
        photo = ImageTk.PhotoImage(img)
        label = tk.Label(root, image=photo, bg="black")
        label.pack()

        # Центрируем окно
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        # Закрываем через время
        root.after(int(duration * 1000), root.destroy)
        root.mainloop()

    except Exception as e:
        print(f"Критическая ошибка при отображении {image_path}: {e}")
        import traceback
        traceback.print_exc()

def main():
    # Открываем файл с вопросами. (Open the questions file)
    try:
        questions_path = get_resource_path('questions-auto.json')
        with open(questions_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Файл {questions_path} не найден!")
        return

    score = 0
    total = len(data)

    for key in data:
        print("\n--------------------------------")
        item = data[key]
        question_text = item['question']
        print(f"Вопрос {key}: {question_text}")

        # Показываем варианты ответов (Show answers)
        answers = item['answers']
        for num in answers:
            print(f"{num}: {answers[num]}")

        # Спрашиваем ответ (Ask for answer)
        user_input = input("Введите номер правильного ответа: ")
        correct = item['correct_answer']
        
        if user_input.strip() == correct:
            print("Правильно! Молодец!")
            score += 1
            image_to_show = item.get('good-image', item.get('image'))
        else:
            print(f"Неправильно :( Правильный ответ был: {correct}")
            image_to_show = item.get('bad-image', item.get('image'))

        # Показываем картинку (Show image)
        if image_to_show:
            show_image(get_resource_path(image_to_show), 3)

    # Итоги (Results)
    print("\n================================")
    print(f"Игра окончена! Твой счет: {score} из {total}")
    if score == total:
        print("Ты гений!")
    elif score > total / 2:
        print("Неплохо!")
    else:
        print("Попробуй еще раз!")

if __name__ == "__main__":
    main()

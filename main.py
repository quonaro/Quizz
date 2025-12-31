import os
import sys
import tkinter as tk
from lib.PIL import Image, ImageTk

def get_resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу, работает для скрипта и для EXE """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

def kartinka(image_path, duration=3):
    try:
        full_path = get_resource_path(image_path)
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
        print(f"Картинка не открылась: {e}")

# Счет
score = 0

def ask_question(lines, correct_answer, success_img):
    global score
    while True:
        for line in lines:
            print(line)
        otvet = input("Enter answer: ")
        
        is_correct = False
        if isinstance(correct_answer, list):
            if otvet in correct_answer:
                is_correct = True
        elif otvet == correct_answer:
            is_correct = True
            
        if is_correct:
            print("Правильно!")
            score += 1
            kartinka(success_img)
            break
        else:
            print("Wrong! Try again.")
            kartinka(r"images\image2.png")
    print("--------------------------------")

# Вопрос 1
ask_question([
    "The Christmas greeting is: (Рождественское приветствие звучит:)",
    "1: Happy Christmas!",
    "2: Merry Christmas!",
    "3: Lucky Christmas!",
    "4: Lovely Christmas!"
], "2", r"images\image1.png")

# Вопрос 2
ask_question([
    "The main Christmas treat: (Главное рождественское угощение:)",
    "1: Duck",
    "2: Goose",
    "3: Turkey",
    "4: Chicken"
], "3", r"images\image3.png")

# Вопрос 3
ask_question([
    "The symbol of Halloween is: (Символ Хэллоуина – это)",
    "1: Pumpkin",
    "2: Squash",
    "3: Watermelon",
    "4: Os"
], "1", r"images\image4.png")

# Вопрос 4
ask_question([
    "Which animal is most often used on Easter cards? (Какое животное чаще всего изображено на Пасхальных открытках?)",
    "1: Rabbit",
    "2: Fox",
    "3: Wolf",
    "4: Sheep"
], "1", r"images\image5.png")

# Вопрос 5
ask_question([
    "Which plant is associated with St. Patrick's Day? (Какое растение ассоциируется с Днем Святого Патрика?)",
    "1: Sunflower",
    "2: Fern",
    "3: Shamrock",
    "4: Spruce"
], "3", r"images\image6.png")

# Вопрос 6
ask_question([
    "One … a day, keeps doctors away!",
    "1: apple",
    "2: pear",
    "3: lemon",
    "4: ice cream"
], "1", r"images\image7.png")

# Вопрос 7
ask_question([
    "Measure thrice and cut …",
    "1: once",
    "2: twice",
    "3: first",
    "4: last"
], "1", r"images\image7.png")

# Вопрос 8
ask_question([
    "Don’t judge a book by its ...",
    "1: Pictures",
    "2: Pages Cover",
    "3: Author"
], "3", r"images\image7.png")

# Вопрос 9
ask_question([
    "A bird may be known by its …",
    "1: feathers",
    "2: break",
    "3: flight",
    "4: songs"
], "1", r"images\image7.png")

# Вопрос 10
ask_question([
    "Which phrase is a good luck wish?",
    "1: Break a leg!",
    "2: Not a fluff or a feather!",
    "3: Best of luck!",
    "4: Blow them away!"
], ["1", "2", "3", "4"], r"images\image7.png")

# Вопрос 11
ask_question([
    "What is the name of the tradition of afternoon tea drinking in England? (Как называется традиция послеобеденного чаепития в Англии?)",
    "1: 6 p.m",
    "2: 5 o'clock",
    "3: evening tea",
    "4: lunch"
], "2", r"images\image8.png")

# Вопрос 12
ask_question([
    "Santa  delivers gifts through the: (Санта-Клаус доставляет подарки через:)",
    "1: backdoor",
    "2: window",
    "3: door",
    "4: chimney"
], "4", r"images\image9.png")

# Вопрос 13
ask_question([
    "At Easter, parents hide, and children look for: (На Пасху родители прячутся, а дети ищут:)",
    "1: eggs",
    "2: cakes",
    "3: gifts",
    "4: candies"
], "1", r"images\image10.png")

# Вопрос 14
ask_question([
    "Halloween is one of the favorite holidays...",
    "1: Happy Halloween",
    "2: Not a fluff or a feather",
    "3: Trick or treat!",
    "4: Good luck!"
], "3", r"images\image11.png")

# Вопрос 15
ask_question([
    "In Ireland, it is customary to wear green clothes on St. Patrick's Day or attach a ** to one's clothing.",
    "1: Rose",
    "2: Shamrock",
    "3: Lily",
    "4: Fern"
], "2", r"images\image6.png")

print("================================")
print("Твой счет: " + str(score))

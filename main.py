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

# Вопрос 1
print("The Christmas greeting is: (Рождественское приветствие звучит:)")
print("1: Happy Christmas!")
print("2: Merry Christmas!")
print("3: Lucky Christmas!")
print("4: Lovely Christmas!")
otvet = input("Введите ответ: ")
if otvet == "2":
    print("Правильно!")
    score = score + 1
    # Открываем хорошую картинку
    kartinka(r"images\image1.png")
else:
    print("Неправильно!")
    # Открываем плохую картинку
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 2
print("The main Christmas treat: (Главное рождественское угощение:)")
print("1: Duck")
print("2: Goose")
print("3: Turkey")
print("4: Chicken")
otvet = input("Введите ответ: ")
if otvet == "3":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image3.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 3
print("The symbol of Halloween is: (Символ Хэллоуина – это)")
print("1: Pumpkin")
print("2: Squash")
print("3: Watermelon")
print("4: Os")
otvet = input("Введите ответ: ")
if otvet == "1":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image4.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 4
print("Which animal is most often used on Easter cards? (Какое животное чаще всего изображено на Пасхальных открытках?)")
print("1: Rabbit")
print("2: Fox")
print("3: Wolf")
print("4: Sheep")
otvet = input("Введите ответ: ")
if otvet == "1":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image5.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 5
print("Which plant is associated with St. Patrick's Day? (Какое растение ассоциируется с Днем Святого Патрика?)")
print("1: Sunflower")
print("2: Fern")
print("3: Shamrock")
print("4: Spruce")
otvet = input("Введите ответ: ")
if otvet == "3":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image6.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 6
print("One … a day, keeps doctors away!")
print("1: apple")
print("2: pear")
print("3: lemon")
print("4: ice cream")
otvet = input("Введите ответ: ")
if otvet == "1":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image7.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 7
print("Measure thrice and cut …")
print("1: once")
print("2: twice")
print("3: first")
print("4: last")
otvet = input("Введите ответ: ")
if otvet == "1":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image7.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 8
print("Don’t judge a book by its ...")
print("1: Pictures")
print("2: Pages Cover")
print("3: Author")
otvet = input("Введите ответ: ")
if otvet == "3":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image7.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 9
print("A bird may be known by its …")
print("1: feathers")
print("2: break")
print("3: flight")
print("4: songs")
otvet = input("Введите ответ: ")
if otvet == "1":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image7.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 10
print("Which phrase is a good luck wish?")
print("1: Break a leg!")
print("2: Not a fluff or a feather!")
print("3: Best of luck!")
print("4: Blow them away!")
otvet = input("Введите ответ: ")
if otvet in ["1", "2", "3", "4"]:
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image7.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 11
print("What is the name of the tradition of afternoon tea drinking in England? (Как называется традиция послеобеденного чаепития в Англии?)")
print("1: 6 p.m")
print("2: 5 o'clock")
print("3: evening tea")
print("4: lunch")
otvet = input("Введите ответ: ")
if otvet == "2":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image8.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 12
print("Santa  delivers gifts through the: (Санта-Клаус доставляет подарки через:)")
print("1: backdoor")
print("2: window")
print("3: door")
print("4: chimney")
otvet = input("Введите ответ: ")
if otvet == "4":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image9.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 13
print("At Easter, parents hide, and children look for: (На Пасху родители прячутся, а дети ищут:)")
print("1: eggs")
print("2: cakes")
print("3: gifts")
print("4: candies")
otvet = input("Введите ответ: ")
if otvet == "1":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image10.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 14
print("Halloween is one of the favorite holidays...")
print("1: Happy Halloween")
print("2: Not a fluff or a feather")
print("3: Trick or treat!")
print("4: Good luck!")
otvet = input("Введите ответ: ")
if otvet == "3":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image11.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("--------------------------------")

# Вопрос 15
print("In Ireland, it is customary to wear green clothes on St. Patrick's Day or attach a ** to one's clothing.")
print("1: Rose")
print("2: Shamrock")
print("3: Lily")
print("4: Fern")
otvet = input("Введите ответ: ")
if otvet == "2":
    print("Правильно!")
    score = score + 1
    kartinka(r"images\image6.png")
else:
    print("Неправильно!")
    kartinka(r"images\image2.png")

print("================================")
print("Твой счет: " + str(score))

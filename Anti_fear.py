#!/usr/bin/env python3
import sys
import time
import os
import random
import threading
import csv
import termios
import tty
from sys import platform

# Пути и файлы
LOG_FILE = "logs/activity_log.csv"
MUSIC_FILE = "/data/data/com.termux/files/home/Anti_fear.mp3"

# Вибрация
VIBE_SHORT = 100
VIBE_LONG = 300

music_process = None

# ====== Музыка ======
def play_music():
    global music_process
    if platform == "linux" and os.path.exists(MUSIC_FILE):
        music_process = threading.Thread(target=lambda: os.system(f"mpv --quiet --no-video '{MUSIC_FILE}'"))
        music_process.daemon = True
        music_process.start()
    else:
        print("Файл музыки не найден или mpv не установлен.")

def stop_music():
    os.system("pkill mpv")

# ====== Логирование ======
def log_activity(activity_type):
    if not os.path.exists("logs"):
        os.makedirs("logs")

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "activity"])

    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), activity_type])

# ====== Вспомогательные функции ======
def vibrate(duration):
    if platform == "linux" and os.path.exists("/data/data/com.termux/files/usr/bin/termux-vibrate"):
        os.system(f"termux-vibrate -d {duration}")
    else:
        print("\a", end='', flush=True)

def vibrate_pattern(count, duration):
    for _ in range(count):
        vibrate(duration)
        time.sleep(0.3)

def send_notification(title, message, vibe=False):
    if platform == "linux" and os.path.exists("/data/data/com.termux/files/usr/bin/termux-notification"):
        os.system(f"termux-notification -t '{title}' -c '{message}' --sound")
    if vibe:
        vibrate(VIBE_LONG)
    print(f"\n[{time.strftime('%H:%M:%S')}] {title}: {message}")

def speak(text):
    if platform == "linux" and os.path.exists("/data/data/com.termux/files/usr/bin/termux-tts-speak"):
        os.system(f"termux-tts-speak '{text}' &")
    else:
        print("Установите termux-api для синтеза речи!")

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def wait_for_enter():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == '\n' or ch == '\r':
                return
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ====== Основные модули ======
def show_welcome():
    ascii_art = r"""
   ___ _       _
  / __| |_ ___| |___ __  __ _ _ __
  \__ \  _/ _ \ / / '  \/ _` | '  \
  |___/\__\___/_\_\_|_|_\__,_|_|_|
    """
    border = "="*45
    title = "Анти-Тревога v3.5".center(45)
    subtitle = "Цифровой помощник для ментального здоровья".center(45)

    # Приветственная надпись
    print(ascii_art)
    print(border)
    print(title)
    print(subtitle)
    print(border)

    time.sleep(1)
    vibrate_pattern(3, 100)
    play_music()

def draw_circle(radius):
    """Рисование круга в псевдографике"""
    for y in range(-radius, radius + 1):
        line = ""
        for x in range(-radius * 2, radius * 2 + 1):
            if (x / 2)**2 + y**2 <= radius**2:
                line += "█"
            else:
                line += " "
        print(line.center(80))

def breathing_animation(cycles=3):
    radius_steps = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for _ in range(cycles):
        for r in radius_steps:
            print("\033c", end='')
            print("\nВдох...")
            draw_circle(r)
            time.sleep(0.3)
        print("\033c", end='')
        print("\nЗадержка дыхания...")
        draw_circle(radius_steps[-1])
        time.sleep(2)
        for r in reversed(radius_steps):
            print("\033c", end='')
            print("\nВыдох...")
            draw_circle(r)
            time.sleep(0.3)
        time.sleep(1)

def breathing_exercise():
    print("\n=== Техника медленного дыхания ===")
    vibrate(VIBE_SHORT)
    send_notification("Дыхание", "Начинаем упражнение...", True)
    log_activity("Дыхание")
    breathing_animation(3)
    send_notification("Отлично!", "Вы завершили дыхательную практику", True)
    feedback()

def affirmations():
    categories = {
        "Спокойствие": [
            "Я в безопасности здесь и сейчас",
            "Мое дыхание ровное и спокойное",
            "Я растворяю тревогу в своем спокойствии",
            "Мой разум чист и безмятежен"
        ],
        "Уверенность": [
            "Я доверяю себе",
            "Мои решения мудры",
            "Я сильнее, чем кажусь"
        ],
        "Мотивация": [
            "Я принимаю вызовы как возможности",
            "Мои действия создают успех"
        ]
    }

    print("\n=== Аффирмации ===")
    vibrate(VIBE_SHORT)
    log_activity("Аффирмации")

    all_quotes = [(cat, q) for cat, quotes in categories.items() for q in quotes]
    random.shuffle(all_quotes)

    for idx, (category, quote) in enumerate(all_quotes, 1):
        print(f"\n{category}:")
        print(f"→ {quote}")
        speak(quote)
        send_notification(category, quote, True)
        print(f"\nНажмите [Enter], чтобы перейти к следующей аффирмации... (Аффирмация {idx} из {len(all_quotes)})")
        wait_for_enter()
    send_notification("Аффирмации", "Вы просмотрели все аффирмации!", True)
    feedback()

def wisdom():
    quotes = [
        ("Сенека", "Счастливая жизнь начинается со спокойствия ума"),
        ("Будда", "Тысячи свечей можно зажечь от одной"),
        ("Ницше", "То, что не убивает нас, делает сильнее")
    ]

    print("\n=== Мудрость веков ===")
    vibrate(VIBE_SHORT)
    log_activity("Мудрые мысли")
    random.shuffle(quotes)

    for idx, (author, quote) in enumerate(quotes, 1):
        print(f"\n{author}:")
        print(f"«{quote}»")
        send_notification(author, quote, True)
        print(f"\nНажмите [Enter], чтобы перейти к следующей цитате... ({idx} из {len(quotes)})")
        wait_for_enter()
    send_notification("Мудрость", "Вы просмотрели все мысли!", True)
    feedback()

def feedback():
    print("\nОцените своё самочувствие по шкале от 1 до 5:")
    print("1 - Очень плохо, 5 - Отлично")
    try:
        choice = input("\nВаш выбор: ")
        score = int(choice)
        if 1 <= score <= 5:
            comment = input("Краткий комментарий (опционально): ")
            log_activity(f"Оценка: {score}/5 - {comment}")
            print("Спасибо за вашу обратную связь!")
        else:
            print("Введите число от 1 до 5!")
    except ValueError:
        print("Ошибка ввода!")

def print_menu():
    border = "═"*35
    menu_title = " Выберите действие:".center(35)

    print(f"\n{border}")
    print(f"{menu_title}")
    print(f"{border}")

    options = [
        ("1. Техника дыхания", ""),
        ("2. Аффирмации", ""),
        ("3. Мудрые мысли", ""),
        ("4. Экстренная помощь", ""),
        ("5. Выход", "")
    ]

    for text, _ in options:
        print(f" {text}")

    print(f"{border}")

# ====== Главная программа ======
def main():
    show_welcome()

    while True:
        print_menu()
        choice = get_key()
        vibrate(VIBE_SHORT)

        if choice == "1":
            breathing_exercise()
        elif choice == "2":
            affirmations()
        elif choice == "3":
            wisdom()
        elif choice == "4":
            log_activity("Экстренная помощь")
            send_notification("SOS", "Дышите глубже... Помощь рядом!", True)
            threading.Thread(target=lambda: vibrate_pattern(5, 300)).start()
        elif choice == "5":
            send_notification("До встречи", "Берегите себя ❤", True)
            stop_music()
            exit()
        else:
            print("Используйте клавиши 1-5")
            vibrate_pattern(2, 500)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Завершение работы...")
        stop_music()
        vibrate(VIBE_SHORT)
        exit()

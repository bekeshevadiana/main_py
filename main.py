import json
import os
import random
from dotenv import load_dotenv
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

# Загружаем данные из .env
load_dotenv()

# Считываем переменную TOKEN из файла .env
TOKEN = "8858708632:AAGT7h294BSCb_Ez9R9-rorG2dBC4AxhYhM"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "users.json"

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С JSON ---


def load_users() -> dict:
    """Загружает словарь пользователей из JSON файла."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Ошибка при чтении {DATA_FILE}: {e}")
            return {}
    return {}


def save_users(users_data: dict) -> None:
    """Сохраняет словарь пользователей в JSON файл."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(users_data, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка при сохранении {DATA_FILE}: {e}")


users = load_users()

MOVIE_FACTS = [
    "🎬 **Бойцовский клуб**: В большинстве сцен фильма на заднем плане можно заметить стаканчик из Starbucks.",
    "🎬 **Темный рыцарь**: Кристиан Бэйл действительно находился на краю крыши небоскреба Sears Tower без дублеров во время съемок.",
    "🎬 **Матрица**: Зеленый код в начале фильма — это на самом деле сканированные рецепты суши из японской кулинарной книги.",
    "🎬 **Властелин колец**: Шон Бин (Боромир) боялся летать на вертолете, поэтому каждый день поднимался на гору для съемок пешком в полном доспехе.",
    "🎬 **Джанго освобожден**: Леонардо Ди Каприо случайно порезал руку о стекло во время съемки сцены за ужином, но продолжил играть, и этот дубль вошел в фильм.",
    "🎬 **Терминатор**: Арнольд Шварценеггер произносит всего 14 строк диалога за весь первый фильм.",
    "🎬 **Интерстеллар**: Для съемок поля Кристофер Нолан вырастил 500 акров кукурузы, а после съемок урожай был продан с прибылью.",
    "🎬 **Парк Юрского периода**: Звук, который издают Velociraptor при общении, был записан с помощью спаривающихся черепах.",
]


# --- СОЗДАНИЕ КЛАВИАТУРЫ ---
def get_main_reply_keyboard():
    """Создает Reply-клавиатуру."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    btn_facts = KeyboardButton("🎬 Кинофакты")
    btn_about = KeyboardButton("ℹ️ О боте")
    btn_survey = KeyboardButton("📝 Рассказать о себе")
    btn_contact = KeyboardButton("📞 Связь")

    keyboard.row(btn_facts, btn_about)
    keyboard.row(btn_survey, btn_contact)
    return keyboard


# --- ОБРАБОТКА КОМАНДЫ /START ---
@bot.message_handler(commands=["start"])
def start_command(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    username = message.from_user.username

    if user_id not in users:
        users[user_id] = {
            "first_name": first_name,
            "username": username,
            "requests_count": 0,
            "custom_name": None,
            "favorite_movie": None,
        }
        save_users(users)

    welcome_text = (
        f"Привет, {first_name}! 👋\n\n"
        "Я бот-киноман! 🍿\n"
        "Воспользуйтесь кнопками внизу экрана, чтобы узнать факт или рассказать о себе!"
    )

    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=get_main_reply_keyboard(),
        parse_mode="Markdown",
    )


# --- ПОШАГОВЫЙ ОПРОС (АНКЕТИРОВАНИЕ) ---


def ask_favorite_movie(message):
    """Шаг 2: Сохраняем имя и спрашиваем любимый фильм."""
    user_id = str(message.from_user.id)

    # Сохраняем имя
    users[user_id]["custom_name"] = message.text
    save_users(users)

    bot.send_message(
        message.chat.id,
        f"Отлично, {message.text}! 🍿 А какой твой самый любимый фильм?",
    )

    # Регистрируем следующий шаг
    bot.register_next_step_handler(message, save_user_profile)


def save_user_profile(message):
    """Шаг 3: Сохраняем любимый фильм и завершаем опрос."""
    user_id = str(message.from_user.id)

    # Сохраняем любимый фильм
    users[user_id]["favorite_movie"] = message.text
    save_users(users)

    saved_name = users[user_id]["custom_name"]
    saved_movie = users[user_id]["favorite_movie"]

    bot.send_message(
        message.chat.id,
        f"Приятно познакомиться, **{saved_name}**! ✨\n"
        f"Фильм «**{saved_movie}**» — отличный выбор!\n\n"
        "Я запомнил эти данные в твоём профиле.",
        reply_markup=get_main_reply_keyboard(),
        parse_mode="Markdown",
    )


# --- ОБРАБОТКА ВСЕХ СООБЩЕНИЙ И КНОПОК ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text

    if user_id not in users:
        users[user_id] = {
            "first_name": message.from_user.first_name,
            "username": message.from_user.username,
            "requests_count": 0,
            "custom_name": None,
            "favorite_movie": None,
        }

    users[user_id]["requests_count"] += 1
    save_users(users)

    if text == "📝 Рассказать о себе":
        bot.send_message(
            message.chat.id, "Давай познакомимся! Напиши, как тебя зовут?"
        )
        # Переводим бота в режим ожидания имени от пользователя
        bot.register_next_step_handler(message, ask_favorite_movie)

    elif text == "🎬 Кинофакты":
        random_fact = random.choice(MOVIE_FACTS)
        bot.send_message(message.chat.id, random_fact, parse_mode="Markdown")

    elif text == "ℹ️ О боте":
        about_text = (
            "ℹ️ **О боте:**\n\n"
            "Этот бот создавался специально для любителей кино! "
            "Он умеет отправлять случайные интересные факты из культовых фильмов и запоминать твои предпочтения."
        )
        bot.send_message(message.chat.id, about_text, parse_mode="Markdown")

    elif text == "📞 Связь":
        contact_text = (
            "📞 **Обратная связь:**\n\n"
            "По всем вопросам и предложениям обращайтесь к автору: @sdiillh"
        )
        bot.send_message(message.chat.id, contact_text, parse_mode="Markdown")

    else:
        random_fact = random.choice(MOVIE_FACTS)
        bot.send_message(
            message.chat.id,
            f"Вот факт специально для вас:\n\n{random_fact}",
            parse_mode="Markdown",
        )


# --- ЗАПУСК БОТА ---
if __name__ == "__main__":
    print("Бот успешно запущен...")
    bot.infinity_polling()
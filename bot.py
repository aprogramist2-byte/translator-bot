import os
import telebot
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

TOKEN = os.getenv("TOKEN") or "PASTE_YOUR_TOKEN_HERE"  # в Railway возьмём из переменной
bot = telebot.TeleBot(TOKEN)

# Направление по умолчанию (куда переводить)
DEFAULT_DEST = "ru"
# Текущее направление для каждого пользователя
user_dest = {}

LANG_NAMES = {"ru": "русский", "tg": "таджикский", "en": "английский"}

def translate_text(text: str, dest: str) -> str:
    """Авто-определяем исходный язык и переводим в dest."""
    try:
        src = detect(text)
    except LangDetectException:
        src = "auto"
    # deep-translator принимает 'auto' как автоопределение
    return GoogleTranslator(source="auto", target=dest).translate(text)

@bot.message_handler(commands=["start", "help"])
def start(m):
    user_dest[m.from_user.id] = DEFAULT_DEST
    bot.reply_to(
        m,
        "Привет! Я переводчик RU↔TG↔EN.\n"
        "Команды: /ru /tg /en — выбрать язык назначения.\n"
        "Команда /mode — показать текущий язык.\n"
        "Просто пришли текст — я переведу 😉"
    )

@bot.message_handler(commands=["ru", "tg", "en"])
def set_mode(m):
    dest = m.text[1:]
    user_dest[m.from_user.id] = dest
    bot.reply_to(m, f"Готов переводить на {LANG_NAMES[dest]}.")

@bot.message_handler(commands=["mode"])
def show_mode(m):
    dest = user_dest.get(m.from_user.id, DEFAULT_DEST)
    bot.reply_to(m, f"Сейчас перевожу на: {LANG_NAMES[dest]} ({dest}).")

@bot.message_handler(func=lambda _m: True)
def handle_text(m):
    dest = user_dest.get(m.from_user.id, DEFAULT_DEST)
    try:
        translated = translate_text(m.text, dest)
        bot.reply_to(m, translated)
    except Exception as e:
        bot.reply_to(m, f"❗Ошибка перевода: {e}")

print("✅ Bot is running…")
bot.polling(none_stop=True)

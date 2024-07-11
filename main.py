import logging
from flask import Flask, request, redirect, make_response
import telebot
from telebot import types
from threading import Thread

API_TOKEN = '7029987670:AAFJAWnXXpxoPyIIB0PKt7l5UsHO26PVqb0'
ADMIN_ID = 7165921192

# Глобальная переменная для хранения целевого URL
targeturl = None

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Flask приложение
app = Flask(__name__)

@app.route('/')
def home():
    global targeturl
    if targeturl:
        resp = make_response(redirect(targeturl, 301))
        resp.set_cookie('my_cookie', '', expires=0)
        return resp
    else:
        return "Target URL not set."

# Стартовое сообщение для админа
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "Введите домен для редиректа:")
        bot.register_next_step_handler(message, process_domain)
    else:
        bot.send_message(message.chat.id, "Ошибка доступа")

# Обработка введенного домена админом
def process_domain(message):
    global targeturl
    targeturl = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Да', 'Нет')
    msg = bot.send_message(message.chat.id, "Подтвердить?", reply_markup=markup)
    bot.register_next_step_handler(msg, confirm_domain)

# Подтверждение домена
def confirm_domain(message):
    global targeturl
    if message.text == 'Да':
        # Сохранение домена перманентно
        with open('targeturl.txt', 'w') as f:
            f.write(targeturl)
        bot.send_message(message.chat.id, "Успешно!", reply_markup=types.ReplyKeyboardRemove())
    else:
        targeturl = None
        bot.send_message(message.chat.id, "Введите домен для редиректа:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, process_domain)

# Функция для запуска Flask-сервера в отдельном потоке
def start_flask():
    app.run(port=5001)

if __name__ == '__main__':
    # Запуск Flask-сервера в отдельном потоке
    Thread(target=start_flask).start()
    # Запуск Telegram-бота
    bot.polling()

# основной функционал бота
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
# парсим + разбираем
import requests
import json
import os
from dotenv import load_dotenv, find_dotenv
# для работы с БД
import sqlite3

# Подключение и создание базы данных
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

cursor.execute(''' 
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    chat_id INTEGER
)
''')
conn.commit()
conn.close()

# добавляем юзера в бд
def add_user_to_db(username, chat_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    # Проверяем, есть ли уже пользователь с таким именем
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        print(f"Пользователь {username} уже существует в базе.")
    else:
        # Если пользователя нет, добавляем его
        cursor.execute('''
        INSERT INTO users (username, chat_id)
        VALUES (?, ?)
        ''', (username, chat_id))

        conn.commit()
        print(f"Пользователь {username} добавлен в базу.")

    conn.close()

# Функция для получения всех пользователей из базы данных
def get_all_users_from_db():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    conn.close()

    return rows

# Инициализация бота
load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('telebot_token'))

catalog_list = InlineKeyboardMarkup(row_width=2)
catalog_list.add(InlineKeyboardButton(text='👋 Приветствие', callback_data='greetings'),
                 InlineKeyboardButton(text='⛅ Погода', callback_data='weather'),
                 InlineKeyboardButton(text='👥 Пользователи', callback_data='users'))

@bot.message_handler(commands=['start'])
def start(message):
    add_user_to_db(message.from_user.username, message.chat.id)
    bot.send_message(message.chat.id, 'Привет! Ты добавлен в базу данных.')
    bot.send_message(message.chat.id, 'А также я могу помочь тебе с прогнозом погоды!', reply_markup=catalog_list)

def menu_replier(message):
    bot.send_message(message.chat.id, 'Ознакомься с пунктами меню!', reply_markup=catalog_list)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    if call.data == 'greetings':
        bot.send_message(call.message.chat.id, "Привет, это твой погодный бот!")
        menu_replier(call.message)
        bot.answer_callback_query(call.id)
    if call.data == 'weather':
        bot.send_message(call.message.chat.id, "Пожалуйста, введите название города для прогноза погоды.")
        bot.register_next_step_handler(call.message, get_weather)
        bot.answer_callback_query(call.id)
    if call.data == 'users':
        users = get_all_users_from_db()
        if users:
            response = "Список пользователей:\n"
            for user in users:
                response += f"Имя: {user[1]}, ID: {user[2]}\n"
        else:
            response = "В базе данных пока нет пользователей."
        bot.send_message(call.message.chat.id, response)
        bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    result = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={os.getenv("open_weather_token")}&units=metric')
    if result.status_code == 200:
        data = json.loads(result.text)
        bot.reply_to(message, f'Погода сейчас: {data["main"]["temp"]}°C')
        menu_replier(message)
    else:
        bot.reply_to(message, f'Не могу найти такой город!')
        menu_replier(message)

bot.polling(non_stop=True)

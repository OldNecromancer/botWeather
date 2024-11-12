# чтобы бот работал
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# для работы с апи опенвезер
import requests
import json

# для корректной работы с токенами
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = telebot.TeleBot(os.getenv('telebot_token'))

catalog_list = InlineKeyboardMarkup(row_width=2)
catalog_list.add(InlineKeyboardButton(text='👋 Приветствие', callback_data='greetings'),
                 InlineKeyboardButton(text='⛅ Погода', callback_data='weather'))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Я помогу тебе узнать прогноз погоды!', reply_markup=catalog_list)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    if call.data == 'greetings':
        bot.send_message(call.message.chat.id, "Привет, это твой погодный бот!")
        bot.answer_callback_query(call.id)
    if call.data == 'weather':
        bot.send_message(call.message.chat.id, "Пожалуйста, введите название города для прогноза погоды.")
        bot.register_next_step_handler(call.message, get_weather)
        bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    result = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={os.getenv("open_weather_token")}&units=metric')
    if result.status_code == 200:
        data = json.loads(result.text)
        bot.reply_to(message, f'Погода сейчас: {data["main"]["temp"]}°C')
    else:
        bot.reply_to(message, f'Не могу найти такой город!')

bot.polling(non_stop=True)

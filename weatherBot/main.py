import telebot
import requests
import json
import os #для работы .env
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = telebot.TeleBot(os.getenv('telebot_token'))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Напиши название города!')

@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    result = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={os.getenv('open_weather_token')}&units=metric')
    if result.status_code == 200:
        data = json.loads(result.text)
        bot.reply_to(message, f'Погода сейчас: {data["main"]["temp"]}')
    else:
        bot.reply_to(message, f'Не могу найти такой город!')

bot.polling(non_stop=True)
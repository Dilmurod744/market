import os
from random import randint

import django
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

from django.core.cache import cache
from apps.models import User

bot = telebot.TeleBot('6209435504:AAFDZKq_wHJqEGpU7ziIKyOZ-cPwdEgKi70')


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    text = f"""
    Salom {message.from_user.first_name} 👋
@market_auth_bot'ning rasmiy botiga xush kelibsiz

⬇️ Kontaktingizni yuboring (tugmani bosib)"""
    rkm = ReplyKeyboardMarkup(resize_keyboard=True)
    rkm.add(KeyboardButton('Kontakt yuborish', request_contact=True))
    bot.send_message(message.chat.id, text, reply_markup=rkm)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(content_types=['contact'])
def echo_message(message):
    phone = message.contact.phone_number[-9:]
    obj, _ = User.objects.get_or_create(phone_number=phone)
    obj.first_name = message.from_user.first_name
    obj.save()
    code = randint(100_000, 999_999)
    while cache.get(code):
        code = randint(100_000, 999_999)

    cache.set(obj.phone_number, timeout=60)

    text = f'🔒 Kodingiz: \n ```{code}```'
    bot.send_message(message.chat.id, text, parse_mode='Markdown')
    text = '🔑 Yangi kod olish uchun /login ni bosing'
    bot.send_message(message.chat.id, text)


bot.infinity_polling()

import logging
import random
import string
import asyncio
from io import BytesIO
from PIL import ImageFilter

from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from PIL import Image, ImageDraw, ImageFont

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
BOT_TOKEN = "6962799243:AAGich1aEwXGxR9_WQI0gA415wnYhIvSqCs"

# ID для связи со мной
YOUR_CHAT_ID = "1748805076"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
# Переменная для хранения информации о прохождении капчи
captcha_passed = {}

# Функция для генерации капчи
def generate_captcha():
    # Генерация случайной строки
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Создание изображения для капчи
    image = Image.new('RGB', (200, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Настройка шрифта
    font = ImageFont.truetype("arial.ttf", 40)

    # Нарисовать текст на изображении с небольшими искажениями
    draw.text((10, 10), captcha_text, fill=(0, 0, 0), font=font)
    image = image.rotate(random.uniform(-20, 20), expand=1)
    image = image.transform(image.size, Image.AFFINE, (1, -0.1, 0, -0.1, 1, 0), fillcolor=(255, 255, 255))
    image = image.filter(ImageFilter.EDGE_ENHANCE)

    # Создание буфера для хранения изображения
    img_buffer = BytesIO()
    image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    return captcha_text, img_buffer

# Класс состояний для управления состоянием пользователя
class ChatState(StatesGroup):
    waiting_for_message = State()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.from_user.id not in captcha_passed:
        # Генерация и отправка капчи
        captcha_text, captcha_image = generate_captcha()
        captcha_passed[message.from_user.id] = captcha_text
        await message.reply("Добро пожаловать! Пройдите капчу, чтобы продолжить")
        await message.reply_photo(captcha_image, caption=f"Введите текс с капчи")
    else:
        # Отправка меню с инлайн кнопками
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="Связаться", callback_data="contact_admin"),
                   types.InlineKeyboardButton(text="Цены", callback_data="prices"))
        await message.reply("Выберите опцию:", reply_markup=markup)

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# Обработчик инлайн кнопок
@dp.callback_query_handler(lambda query: query.data == "prices")
async def process_callback_prices(callback_query: types.CallbackQuery):
    # Текст с ценами
    prices_text = """🌐Пишу на заказ:

💣Скрипты - от 1000₽
💣Боты[TG, DS, VK] - от 1000₽
💣Авторегеры - от 900₽
💣Сайты - от 5000₽
💣Чекеры - от 1000₽

🚨Продаю аккаунты с моменталкой FUNPAY - 5000₽
[36 отзывов + 22 год рег]

🔥Рассылка по чатам - 2000₽
🔥Рассылка по ЛС - 2500₽
🔥Авто-Подписка на чаты - 450₽
🔥Авторег STEAM - 2500₽
🔥Авторег DISCORD - 2000₽
🔥Авторег Arizona RP - 700₽
🔥Авторег Epic Games - 900₽

🔥Продам свой Ozon банк (Полностью вериф
Прогрет, более 100 операций)
🔥Продам поставщика фанпей аккаунтов и телеграм премиум.

🛒Принимаю оплату: Крипто-валютой, Сбербан, Тинькофф, СБП, Ozon"""
    
    # Создаем кнопку "Связь"
    contact_button = InlineKeyboardButton(text="Связь", url="https://t.me/ExTallentt")
    
    # Создаем клавиатуру с кнопкой "Связь"
    markup = InlineKeyboardMarkup().add(contact_button)
    
    # Отправляем сообщение с ценами и кнопкой "Связь"
    await bot.send_message(callback_query.from_user.id, prices_text, reply_markup=markup)


from datetime import datetime
from aiogram.types import ForceReply

# Обработчик инлайн кнопки "Связь с админом"
@dp.callback_query_handler(lambda query: query.data == "contact_admin")
async def process_callback_contact_admin(callback_query: types.CallbackQuery):
    # Создаем объект ForceReply
    force_reply = ForceReply()

    # Отправляем сообщение с запросом текста у пользователя
    await bot.send_message(callback_query.from_user.id, "Напишите ваше сообщение администратору:", reply_markup=force_reply)


# Обработчик инлайн кнопки "Ответить пользователю"
@dp.callback_query_handler(lambda query: query.data == "reply_to_user")
async def process_callback_reply_to_user(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Введите ваш ответ:")
    await ChatState.waiting_for_reply.set()

@dp.message_handler(state=ChatState.waiting_for_message)
async def process_reply_to_user(message: types.Message, state: ChatState):
    await bot.send_message(YOUR_CHAT_ID, f"Администратор отвечает: {message.text}")
    await message.answer("Ваше сообщение успешно отправлено администратору.")
    await state.finish()

# Обработчик текстовых сообщений с ForceReply
@dp.message_handler(content_types=ContentType.TEXT, is_reply=True)
async def process_reply_to_admin(message: types.Message):
    # Получаем информацию о пользователе
    user = message.from_user

    # Проверяем, является ли отправитель администратором
    if user.id == YOUR_CHAT_ID:
        # Получаем ID пользователя, который написал сообщение
        user_id = message.reply_to_message.from_user.id
        # Отправляем сообщение администратору
        await bot.send_message(YOUR_CHAT_ID, f"Пользователь {user.first_name} {user.last_name} (ID: {user.id}) написал: {message.text}")
        await bot.send_message(user_id, "Ваше сообщение передано администратору. Ожидайте ответа.")
    else:
        # Если отправитель не является администратором, то отправляем его сообщение администратору
        await bot.send_message(YOUR_CHAT_ID, f"Пользователь {user.first_name} {user.last_name} (ID: {user.id}) написал: {message.text}")
        await bot.send_message(user.id, "Ваше сообщение передано администратору. Ожидайте ответа.")


# Обработчик текстовых сообщений
@dp.message_handler(content_types=ContentType.TEXT)
async def process_text(message: types.Message):
    # Проверка введенного текста капчи
    if message.from_user.id in captcha_passed and message.text == captcha_passed[message.from_user.id]:
        del captcha_passed[message.from_user.id]
        # Отправка меню с инлайн кнопками
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="Связь с админом", callback_data="contact_admin"),
                   types.InlineKeyboardButton(text="Цены", callback_data="prices"))
        await message.reply("Капча пройдена. Выберите опцию:", reply_markup=markup)
    else:
        await message.reply("Неверный код капчи. Попробуйте еще раз.")

if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)

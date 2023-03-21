from aiogram import types
from loader import dp
import requests
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os
from urllib.parse import urlparse, parse_qs

@dp.message_handler(lambda message: message.text == "‍👨‍👧‍👧 Клиенты")
async def clients(message: types.Message):
    # Формируем URL для запроса
    url = f'http://localhost/allUsers'
    # Заголовки для запроса
    headers = {'Accept': 'application/json'}
    # Создаем сессию для выполнения запросов
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            script_dir = os.path.dirname(__file__)
            rel_path = "../../assets/images/bro.png"
            photo = open(os.path.join(script_dir, rel_path), "rb")
            keyboards = await pagination(data)
            await dp.bot.send_photo(message.from_user.id, photo=photo, reply_markup=keyboards)
        else:
            await dp.bot.send_message(message.from_user.id, text=f'Ошибка')
            
            
# Обработчик страниц
@dp.callback_query_handler(lambda c: c.data.startswith('page'))
async def proxy_mobile(query: types.CallbackQuery = None):
    page = query.data.split('#')[1]
    # Формируем URL для запроса
    url = f'http://localhost/allUsers?page={page}'
    # Заголовки для запроса
    headers = {'Accept': 'application/json'}
    # Создаем сессию для выполнения запросов
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            keyboards = await pagination(data)
            await query.message.edit_reply_markup(reply_markup=keyboards)
        else:
            await dp.bot.send_message(query.from_user.id, text=f'Ошибка')

# Сама функция paginate
async def pagination(data):
    buttons = []
    for x in data['data']:
        user_button = [
            InlineKeyboardButton(f'{x["login"]}', callback_data=f'userInfo-{x["id"]}')
        ]
        buttons.append(user_button)

    bottom_buttons = []
    if data["current_page"] != 1:
        parsed_url = urlparse(data["prev_page_url"])
        prevPage = parse_qs(parsed_url.query)
        bottom_buttons.append(InlineKeyboardButton(f'⬅️', callback_data=f'page#{prevPage["page"][0]}'))
    else:
        bottom_buttons.append(InlineKeyboardButton(f'⛔️', callback_data=f'stop'))

    bottom_buttons.append(
        InlineKeyboardButton(f'{data["current_page"]}/{data["last_page"]}', callback_data=f'back_proxy_type'))

    if data["current_page"] == data["last_page"]:
        bottom_buttons.append(InlineKeyboardButton(f'⛔️', callback_data=f'stop'))
    else:
        parsed_url = urlparse(data["next_page_url"])
        nextPage = parse_qs(parsed_url.query)
        bottom_buttons.append(InlineKeyboardButton(f'➡️', callback_data=f'page#{nextPage["page"][0]}'))

    buttons.append(bottom_buttons)

    keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)

    return keyboard

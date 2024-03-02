import requests
import vk_api
import time
import re
from datetime import datetime, timedelta
import pytz
import aiohttp
from vkbottle import GroupEventType
from vkbottle.bot import Bot, Message, rules
from bs4 import BeautifulSoup
import pyowm
from pyowm import OWM
from vkbottle.api import API
import random
import json
import asyncio
import sqlite3
import os
from os.path import exists
from vkbottle.dispatch.rules.base import ChatActionRule, FromUserRule
from vkbottle_types.objects import MessagesMessageActionStatus
import asyncio

api = API("")
token = ''
bot = Bot('')
owm = pyowm.OWM('')
super_owners = []
owners = []
owners.extend(super_owners)
mgr = owm.weather_manager()
RULES_FILE = "rules.json"
NOTES_FILE = "notes.json"
STATISTICA_FILE = 'static.json'
BLOCKED_USERS_FILE = 'blocked_users.json'
kick_all_enabled = False

def load_blocked_users():
    try:
        with open(BLOCKED_USERS_FILE, 'r') as file:
            blocked_users = json.load(file)
    except FileNotFoundError:
        blocked_users = []
    return blocked_users

def save_blocked_users(blocked_users):
    with open(BLOCKED_USERS_FILE, 'w') as file:
        json.dump(blocked_users, file)

blocked_users = load_blocked_users()

def load_notes():
    try:
        with open(NOTES_FILE, "r") as file:
            notes_data = json.load(file)
    except FileNotFoundError:
        notes_data = {"notes": []}
    return notes_data.get("notes", [])


def save_notes(notes):
    notes_data = {"notes": notes}
    with open(NOTES_FILE, "w") as file:
        json.dump(notes_data, file)


def load_rules():
    try:
        with open(RULES_FILE, "r") as file:
            rules = json.load(file)
    except FileNotFoundError:
        rules = []
    return rules


def save_rules(rules):
    with open(RULES_FILE, "w") as file:
        json.dump(rules, file)

def load_statistics():
    try:
        with open(STATISTICA_FILE, "r") as file:
            statistics = json.load(file)
    except FileNotFoundError:
        statistics = []
    return statistics

def save_statistics(statistics):
    with open(STATISTICA_FILE, "w") as file:
        json.dump(statistics, file)

statistics = load_statistics()
conn = sqlite3.connect('canto_bot.db')
cursor = conn.cursor()

try:
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        candies INTEGER,
                        last_bonus INTEGER
                    )''')
except sqlite3.OperationalError as e:
    print("Error:", e)

conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS users_info (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT
                )''')
conn.commit()

async def get_user_name(user_id: int) -> str:
    user_info = await bot.api.users.get(user_ids=user_id)
    if user_info:
        first_name = user_info[0].first_name
        last_name = user_info[0].last_name
        return f"[https://vk.com/id{user_id}|{first_name} {last_name}]"
    return f"[id{user_id}|Unknown]"

async def notify_receiver(receiver_id, sender_id, amount, comment=None):
    sender_info = await get_user_name(sender_id)
    message_text = f"🔔 Ваш мешок пополнен на {amount} Рио-Конфеток!\n💬 Отправитель: {sender_info}"
    if comment:
        message_text += f"\n\n💬Комментарий к переводу: {comment}"
    await bot.api.messages.send(
        peer_id=receiver_id,
        message=message_text,
        from_id=ID сообщества,
        random_id=0
    )


async def is_chat_admin(api, chat_id, user_id):
    response = await api.groups.get_members(group_id=chat_id, user_id=user_id)
    return response.get("items", [])[0].get("is_admin", False)


status_translation = {
    'clear sky': 'ясное небо',
    'few clouds': 'небольшая облачность',
    'scattered clouds': 'рассеянные облака',
    'broken clouds': 'облачно с прояснениями',
    'overcast clouds': 'пасмурно',
    'shower rain': 'ливень',
    'rain': 'дождь',
    'thunderstorm': 'гроза',
    'snow': 'снег',
    'light snow': 'слабый снег',
    'mist': 'туман'
}

status_emojis = {
    'ясное небо': '☀️',
    'небольшая облачность': '🌤️',
    'рассеянные облака': '⛅',
    'облачно с прояснениями': '🌥️',
    'пасмурно': '☁️',
    'ливень': '🌧️',
    'дождь': '🌧️',
    'гроза': '⛈️',
    'снег': '❄️',
    'слабый снег': '❄️',
    'туман': '🌫️'
}


async def user_id_get_mes(message: Message):
    if message.reply_message == None:
        vk_user = message.from_id
    else:
        vk_user = message.reply_message.from_id
    return vk_user


def get_user_info(user_id):
    try:
        vk = vk_api.VkApi(token=token)
        user_info = vk.method('users.get', {"user_ids": user_id, "fields": "first_name,last_name"})
        if user_info:
            return user_info[0]
        else:
            return None
    except Exception as ex:
        print(f"Ошибка при получении информации о пользователе: {ex}")
        return None

def get_user_id(text):
    result = []
    regex = r"(?:vk\.com\/(?P<user>[\w\.]+))|(?:\[id(?P<user_id>[\d]+)\|)"
    for user_domain, user_id in re.findall(regex, text):
        if user_domain:
            result.append(get_user_id_by_domain(user_domain))
        if user_id:
            result.append(int(user_id))
    _result = []
    for r in result:
        if r is not None:
            _result.append(r)
    return _result


def get_user_id_by_domain(user_domain: str):
    vk = vk_api.VkApi(token=token)
    obj = vk.method('utils.resolveScreenName', {"screen_name": user_domain})
    if isinstance(obj, list):
        return
    if obj['type'] == 'user':
        return obj["object_id"]


async def get_users_top(count=10):
    cursor.execute("SELECT user_id, candies FROM users WHERE candies > 1 ORDER BY candies DESC LIMIT ?", (count,))
    users = cursor.fetchall()
    return users


async def generate_top_message():
    users = await get_users_top()
    if not users:
        return "☢ Список пуст."

    message = "☢ Топ-10 пользователей по Рио-Конфеткам:\n"
    for idx, user in enumerate(users, start=1):
        user_id, candies = user
        user_info = await get_user_info(user_id)
        if user_info:
            first_name, last_name = user_info
            message += f"{idx}. [https://vk.com/id{user_id}|{first_name} {last_name}] - {candies} монет\n"
    return message


async def get_user_info(user_id):
    try:
        cursor.execute("SELECT first_name, last_name FROM users_info WHERE user_id = ?", (user_id,))
        user_info = cursor.fetchone()
        if user_info:
            return user_info[0], user_info[1]
        user = await bot.api.users.get(user_ids=user_id)
        first_name = user[0].first_name
        last_name = user[0].last_name
        cursor.execute("INSERT INTO users_info (user_id, first_name, last_name) VALUES (?, ?, ?)",
                       (user_id, first_name, last_name))
        conn.commit()
        return first_name, last_name
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе {user_id}: {e}")
        return None, None


async def get_user_candies(user_id):
    cursor.execute("SELECT candies FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0


@bot.on.message(text=['ид', 'Ид', 'id', 'Id', 'ID', 'ИД', 'айди', 'Айди'])
async def iduser(message: Message):
    user_id = await user_id_get_mes(message)
    await message.answer(f'🆔 [https://vk.com/id{user_id}|Пользователя] => {user_id}')

@bot.on.message(
    text=['ид <url>', 'Ид <url>', 'id <url>', 'Id <url>', 'ID <url>', 'ИД <url>', 'айди <url>', 'Айди <url>'])
async def iduser(message: Message, url: str):
    user_id = get_user_id(url)[0]
    await message.answer(f'🆔 [https://vk.com/id{user_id}|Пользователя] => {user_id}')

@bot.on.chat_message(text=['Пинг', 'пинг'])
async def pingbota(message: Message):
    delta = round(time.time() - message.date, 2)
    text = f'[ ✅ ] ПОНГ!\n[ ⌛ ] Ответ за {delta} секунд.\n[ ✅ ] => Работает'
    await message.reply(text)

@bot.on.message(text=['кик', 'Кик'])
async def kick_user(message: Message):
    if message.from_id in owners:
        user_id = await user_id_get_mes(message)
        await message.ctx_api.request("messages.removeChatUser",{"member_id": user_id, "chat_id": message.peer_id - 2000000000})
    else:
        print('')

@bot.on.message(text=['кик <url>', 'Кик <url>'])
async def kick_user(message: Message, url: str):
    if message.from_id in owners:
        user_id = get_user_id(url)[0]
        await message.ctx_api.request("messages.removeChatUser",{"member_id": user_id, "chat_id": message.peer_id - 2000000000})
    else:
        print('')

@bot.on.message(text=['!+ас', '!+Ас'])
async def asus(message: Message):
    if message.from_id not in owners:
        return
    user = await user_id_get_mes(message)
    targ = await get_user_name(user)
    if user in owners:
        return
    if user in blocked_users:
        await message.answer(f'{targ} уже в спам-листе.')
        return
    await message.answer(f'Добавил {targ} в спам-лист.')
    blocked_users.append(user)
    save_blocked_users(blocked_users)

@bot.on.message(text=['!-ас', '!-Ас'])
async def asus(message: Message):
    if message.from_id not in owners:
        return
    user = await user_id_get_mes(message)
    targ = await get_user_name(user)
    if user in owners:
        return
    if user not in blocked_users:
        await message.answer(f'{targ} отсутствует в спам-листе.')
        return
    await message.answer(f'Удалил {targ} из спам-листа.')
    blocked_users.remove(user)
    save_blocked_users(blocked_users)

@bot.on.message(text=['!+ас <url>', '!+Ас <url>'])
async def asus(message: Message, url: str):
    if message.from_id not in owners:
        return
    user = get_user_id(url)[0]
    targ = await get_user_name(user)
    if user in owners:
        return
    if user in blocked_users:
        await message.answer(f'{targ} уже в спам-листе.')
        return
    await message.answer(f'Добавил {targ} в спам-лист.')
    blocked_users.append(user)
    save_blocked_users(blocked_users)

@bot.on.message(text=['!-ас <url>', '!-Ас <url>'])
async def asus(message: Message, url: str):
    if message.from_id not in owners:
        return
    user = get_user_id(url)[0]
    targ = await get_user_name(user)
    if user in owners:
        return
    if user not in blocked_users:
        await message.answer(f'{targ} отсутствует в спам-листе.')
        return
    await message.answer(f'Удалил {targ} из спам-листа.')
    blocked_users.remove(user)
    save_blocked_users(blocked_users)

@bot.on.message(text='!асинфа')
async def infoas(message: Message):
    user_id = await user_id_get_mes(message)
    target = await get_user_name(user_id)
    if user_id not in owners:
        return
    if user_id == message.from_id:
        print('')
    if user_id in blocked_users:
        await message.answer(f'📒 {target} находится в спам-листе.')
    if user_id not in blocked_users:
        await message.answer(f'📒 {target} отсутствует в спам-листе.')

@bot.on.message(text='!асинфа <url>')
async def infoas(message: Message, url: str):
    user_id = get_user_id(url)
    target = await get_user_name(user_id)
    if user_id not in owners:
        return
    if user_id == message.from_id:
        print('')
    if user_id in blocked_users:
        await message.answer(f'📒 {target} находится в спам-листе.')
    if user_id not in blocked_users:
        await message.answer(f'📒 {target} отсутствует в спам-листе.')

@bot.on.message(text=["включитькиквсех", 'Включитькиквсех'])
async def enable_kick_all(message: Message):
    global kick_all_enabled
    if message.from_id in super_owners:
        kick_all_enabled = True
        await message.answer("Команда «киквсех» успешно включена.")
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@bot.on.message(text=["выключитькиквсех", 'Выключитькиквсех'])
async def disable_kick_all(message: Message):
    global kick_all_enabled
    if message.from_id in super_owners:
        kick_all_enabled = False
        await message.answer("Команда «киквсех» успешно выключена.")
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@bot.on.message(text=["киквсех", 'Киквсех'])
async def kick_all(message: Message):
    global kick_all_enabled
    if kick_all_enabled:
        if message.from_id in super_owners:
            sender = message.from_id
            send = await get_user_name(sender)
            chat_info = await bot.api.messages.get_conversations_by_id(peer_ids=[message.peer_id], extended=1)
            members_count = chat_info.items[0].chat_settings.members_count
            chat_id = message.peer_id - 2000000000
            profiles = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
            await message.answer(f'{send} запускает чистку всего чата. Начало через 3 секунды.')
            time.sleep(3)
            for profile in profiles.profiles:
                if profile.id > 0:
                    try:
                        await bot.api.messages.remove_chat_user(
                            chat_id=chat_id,
                            member_id=profile.id
                        )
                    except Exception as e:
                        print(f"Ошибка при кике пользователя с ID {profile.id}: {e}")
            await message.answer("Все пользователи исключены из чата.")
        else:
            await message.answer("У вас нет прав на выполнение этой команды.")
    else:
        await message.answer("Команда «киквсех» отключена.\nВключить ее: включитькиквсех")

@bot.on.message(text=['реши <equation>', 'Реши <equation>'])
async def solve_equation(message: Message, equation: str):
    try:
        result = eval(equation)
        await message.answer(f"⌛ Результат: {result}")
    except Exception as e:
        error_message = f"⚠ Неправильное использование команды. Вот пример:\n реши 5+5"
        await message.reply(error_message)

@bot.on.message(text=['погода <city>', 'Погода <city>'])
async def weather_info(message: Message, city: str):
    try:
        observation = mgr.weather_at_place(city)
        w = observation.weather
        temperature = w.temperature('celsius')["temp"]
        wind = w.wind()["speed"]
        humidity = w.humidity
        status = w.detailed_status.lower()
        translated_status = status_translation.get(status, status)
        emoji = status_emojis.get(translated_status, '')
        local_time = datetime.now()
        response = (
            f"☁ Погода на сегодня в «{city}»:\n\n"
            f"🌡 Температура: {temperature}°C\n"
            f"⛱ Скорость ветра: {wind} м/с\n"
            f"🌧 Влажность: {humidity}%\n"
            f"{emoji} Статус: {translated_status}"
        )

        await message.answer(response)
    except Exception as e:
        await message.answer(f"☕ Произошла ошибка при получении информации о погоде: {str(e)}")

@bot.on.message(text=['музыка <author>', 'Музыка <author>'])
async def handle_music(message: Message, author: str):
    try:
        response = await api.request("audio.search", {"q": author, "count": 50})
        if 'response' in response and 'items' in response['response']:
            tracks = response['response']['items']
            if tracks:
                random_tracks = random.sample(tracks, 5)
                attachments = ",".join([f"audio{track['owner_id']}_{track['id']}" for track in random_tracks])
                await message.reply(f"⌛ Вот 5 случайных треков от «{author}»:\n\n", attachment=attachments)
            else:
                await message.answer(f"⌛ Извините, треки от «{author}» не найдены.")
        else:
            await message.answer(f"Произошла ошибка при получении треков: неверный формат ответа от сервера.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при получении треков: {str(e)}")

@bot.on.chat_message(text=['чатинфо', 'Чатинфо'])
async def get_chat_info(message: Message):
    try:
        chat_info = await bot.api.messages.get_conversations_by_id(peer_ids=[message.peer_id], extended=1)
        chat_title = chat_info.items[0].chat_settings.title
        members = chat_info.items[0].chat_settings.members_count
        profiles = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        male_count = 0
        female_count = 0

        for member in profiles.profiles:
            if member.sex == 2:
                male_count += 1
            elif member.sex == 1:
                female_count += 1

        bot_count = members - (male_count + female_count)

        await message.answer(
            f"🆔: {message.peer_id - int(2e9)}\n"
            f"Название чата: {chat_title}\n"
            f"Количество участников: {members}\n"
            f"Количество мужчин: {male_count}\n"
            f"Количество женщин: {female_count}\n"
            f"Количество сообществ (приблизительно): {bot_count}"
        )

    except Exception as e:
        error_message = f"⚠Произошла ошибка: {e}"
        await message.answer(error_message)

@bot.on.message(text=['рандом <number:int>', 'Рандом <number:int>'])
async def random_number(message: Message, number: int):
    user_id = message.from_id
    random_num = random.randint(0, number)
    await message.answer(f"💎 Случайное число до {number} это {random_num}")

@bot.on.message(text=['рандом <from_number:int> <to_number:int>', 'Рандом <from_number:int> <to_number:int>'])
async def random_number_range(message: Message, from_number: int, to_number: int):
    user_id = message.from_id
    if from_number >= to_number:
        print('')
        return
    random_num = random.randint(from_number, to_number)
    await message.answer(f"💎Случайное число от {from_number} до {to_number} это {random_num}")

@bot.on.message(text=["регвсех", "Регвсех"])
async def handle_greeting(message: Message):
    if message.from_id not in owners:
        return
    chat_info = await bot.api.messages.get_conversations_by_id(peer_ids=[message.peer_id], extended=1)
    members = chat_info.items[0].chat_settings.members_count
    profiles = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    registered_count = 0 
    for profile in profiles.profiles:
        user_id = profile.id
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user_data = cursor.fetchone()
        if user_data is None:
            cursor.execute("INSERT INTO users (user_id, candies, last_bonus) VALUES (?, ?, ?)",
                           (user_id, 0, 0))
            conn.commit()
            print(f"♻ Пользователь с ID {user_id} зарегистрирован.")
            registered_count += 1
    await message.reply(f'Было зарегистрировано {registered_count} пользователей.')

@bot.on.message(text=["/reg"])
async def register_user(message: Message):
    if message.from_id not in owners:
        return
    user_id = await user_id_get_mes(message)
    target = await get_user_name(user_id)
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()
    if user_data is None:
        cursor.execute("INSERT INTO users (user_id, candies, last_bonus) VALUES (?, ?, ?)", (user_id, 0, 0))
        conn.commit()
        await message.answer(f"♻ Успешно зарегистрирован пользователь {target}!")
    else:
        await message.answer(f"♻ Пользователь {target} уже зарегистрирован.")

@bot.on.message(text=["/reg <url>"])
async def register_user(message: Message, url: str):
    if message.from_id not in owners:
        return
    user_id = get_user_id(url)[0]
    target = await get_user_name(user_id)
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()
    if user_data is None:
        cursor.execute("INSERT INTO users (user_id, candies, last_bonus) VALUES (?, ?, ?)", (user_id, 0, 0))
        conn.commit()
        await message.answer(f"♻ Успешно зарегистрирован пользователь {target}!")
    else:
        await message.answer(f"♻ Пользователь {target} уже зарегистрирован.")

@bot.on.message(text=["передать <amount:int> <url>", "Передать <amount:int> <url>"])
async def handle_transfer_with_comment(message: Message, amount: int, url: str):
    from_user_id = message.from_id
    to_user_id = get_user_id(url)[0]
    target = await get_user_name(to_user_id)
    if to_user_id is not None:
        cursor.execute("SELECT * FROM users WHERE user_id=?", (from_user_id,))
        from_user_data = cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (to_user_id,))
        to_user_data = cursor.fetchone()
        if from_user_data is not None and to_user_data is not None:
            from_user_candies = from_user_data[1]
            if from_user_candies >= amount:
                to_user_candies = to_user_data[1]
                cursor.execute("UPDATE users SET candies=? WHERE user_id=?", (from_user_candies - amount, from_user_id))
                cursor.execute("UPDATE users SET candies=? WHERE user_id=?", (to_user_candies + amount, to_user_id))
                conn.commit()
                await message.answer(f"✅ Вы передали {amount} Рио-Конфеток для {target}!")
                await notify_receiver(to_user_id, from_user_id, amount)
            else:
                await message.answer("😓 У вас недостаточно конфет для передачи.")
        else:
            await message.answer(f"👤 Пользователь {target} не найден в базе данных.")
    else:
        await message.answer("👤 Неверный формат упоминания пользователя.")

@bot.on.message(text=["выдать <amount:int>", 'Выдать <amount:int>'])
async def handle_transfer_with_comment(message: Message, amount: int):
    if message.from_id not in owners:
        return
    from_user_id = await user_id_get_mes(message)
    to_user_id = await user_id_get_mes(message)
    target = await get_user_name(to_user_id)
    if to_user_id is not None:
        cursor.execute("SELECT * FROM users WHERE user_id=?", (from_user_id,))
        from_user_data = cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (to_user_id,))
        to_user_data = cursor.fetchone()
        if from_user_data is not None and to_user_data is not None:
            from_user_candies = from_user_data[1]
            if from_user_candies >= 0:
                to_user_candies = to_user_data[1]
                cursor.execute("UPDATE users SET candies=? WHERE user_id=?", (to_user_candies + amount, to_user_id))
                conn.commit()
                await message.answer(f"✅ Вы выдали {target} {amount} конфеток!")
            else:
                await message.answer("😓 У вас недостаточно конфет для передачи.")
        else:
            await message.answer("👤 Пользователь не найден в базе данных.")
    else:
        await message.answer("👤 Неверный формат упоминания пользователя.")

@bot.on.message(text=["выдать <amount:int> <url>", "Выдать <amount:int> <url>"])
async def handle_transfer_with_comment(message: Message, amount: int, url: str):
    if message.from_id not in owners:
        return
    from_user_id = message.from_id
    to_user_id = get_user_id(url)[0]
    target = await get_user_name(to_user_id)
    if to_user_id is not None:
        cursor.execute("SELECT * FROM users WHERE user_id=?", (from_user_id,))
        from_user_data = cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (to_user_id,))
        to_user_data = cursor.fetchone()
        if from_user_data is not None and to_user_data is not None:
            from_user_candies = from_user_data[1]
            if from_user_candies >= 0:
                to_user_candies = to_user_data[1]
                cursor.execute("UPDATE users SET candies=? WHERE user_id=?", (to_user_candies + amount, to_user_id))
                conn.commit()
                await message.answer(f"✅ Вы выдали {target} {amount} конфеток!")
            else:
                await message.answer("😓 У вас недостаточно конфет для передачи.")
        else:
            await message.answer("👤 Пользователь не найден в базе данных.")
    else:
        await message.answer("👤 Неверный формат упоминания пользователя.")

@bot.on.message(text=["передать <amount:int>", "Передать <amount:int>"])
async def handle_transfer_with_comment(message: Message, amount: int):
    from_user_id = message.from_id
    to_user_id = await user_id_get_mes(message)
    target = await get_user_name(to_user_id)
    if to_user_id is not None:
        cursor.execute("SELECT * FROM users WHERE user_id=?", (from_user_id,))
        from_user_data = cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (to_user_id,))
        to_user_data = cursor.fetchone()
        if from_user_data is not None and to_user_data is not None:
            from_user_candies = from_user_data[1]
            if from_user_candies >= amount:
                to_user_candies = to_user_data[1]
                cursor.execute("UPDATE users SET candies=? WHERE user_id=?", (from_user_candies - amount, from_user_id))
                cursor.execute("UPDATE users SET candies=? WHERE user_id=?", (to_user_candies + amount, to_user_id))
                conn.commit()
                await message.answer(f"✅ Вы передали {amount} Рио-Конфет для {target}!")
                await notify_receiver(to_user_id, from_user_id, amount)
            else:
                await message.answer("☢ У вас недостаточно Рио-Конфеток для передачи.")
        else:
            await message.answer(f"👤 Пользователь {target} не найден в базе данных.")
    else:
        await message.answer("👤 Неверный формат упоминания пользователя.")

@bot.on.message(text=["мешок", 'Мешок'])
async def handle_bag(message: Message):
    user_id = await user_id_get_mes(message)
    target = await get_user_name(user_id)
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()
    if user_data is not None:
        candies = user_data[1]
        await message.answer(
            f"☢ У {target} в мешке {candies} конфет!")
    else:
        await message.answer(
            f"🗯 У пользователя {target} пока нет Рио-Конфеток.")

@bot.on.message(text=["мешок <url>", "Мешок <url>"])
async def handle_other_user_bag(message: Message, url: str):
    user_id = get_user_id(url)[0]
    target = await get_user_name(user_id)
    if user_id is not None:
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user_data = cursor.fetchone()
        if user_data is not None:
            candies = user_data[1]
            await message.answer(f"☢ У {target} в мешке {candies} конфет.")
        else:
            await message.answer(f"👤 У {target} нет конфет или его нет в базе данных.")
    else:
        await message.answer("👤 Неверный формат пользователя.")

@bot.on.message(text=["Очиститьтоп", 'очиститьтоп'])
async def handle_clear_top(message: Message):
    if message.from_id in owners:
        cursor.execute("UPDATE users SET candies=0")
        conn.commit()
        await message.answer("🔑 Топ пользователей по количеству конфет был успешно сброшен.")
    else:
        await message.answer("🔑 У вас нету доступа к сбросу топа.")

@bot.on.message(text=["топ", 'Топ'])
async def top_command(message: Message):
    top_message = await generate_top_message()
    candies = await get_user_candies(message.from_id)
    top_message += f"\n\n☢ Ваше количество конфет: {candies}."
    print(top_message)
    await message.answer(top_message)

@bot.on.message(text=["+заметка <title>\n<text>"])
async def add_note(message: Message, title: str, text: str):
    if message.from_id not in owners:
        return
    if len(title) == 1 and title.isdigit():
        await message.answer("📖 Название заметки не может состоять только из одной цифры.")
        return
    notes = load_notes()
    for note in notes:
        if note["title"] == title:
            await message.answer(f"📖 Заметка с названием «{title}» уже существует.")
            return
    notes.append({"title": title, "content": text})
    save_notes(notes)
    await message.answer(f"✅ Заметка «{title}» успешно добавлена.")

@bot.on.message(text=["-заметка <title_or_number>"])
async def remove_note(message: Message, title_or_number: str):
    if message.from_id not in owners:
        return
    notes = load_notes()
    if title_or_number.isdigit():
        note_number = int(title_or_number)
        if 0 < note_number <= len(notes):
            title = notes[note_number - 1]["title"]
            del notes[note_number - 1]
            save_notes(notes)
            await message.answer(f"✅ Заметка «{title}» успешно удалена.")
        else:
            await message.answer("📖 Неверный номер заметки.")
    else:
        for note in notes:
            if note["title"] == title_or_number.strip():
                notes.remove(note)
                save_notes(notes)
                await message.answer(f"✅ Заметка «{title_or_number}» успешно удалена.")
                return
        await message.answer(f"📖 Заметка «{title_or_number}» не найдена.")

@bot.on.message(text=["заметки", "Заметки"])
async def list_notes(message: Message):
    notes = load_notes()
    if notes:
        notes_list = "\n".join([f"{i + 1}. {note['title']}" for i, note in enumerate(notes)])
        await message.answer("📖 Список заметок:\n" + notes_list)
    else:
        await message.answer("📖 Список заметок пуст.")

@bot.on.message(text=["заметка <title_or_number>", "Заметка <title_or_number>"])
async def show_note_by_title_or_number(message: Message, title_or_number: str):
    notes = load_notes()
    if title_or_number.isdigit():
        note_number = int(title_or_number)
        if 0 < note_number <= len(notes):
            note = notes[note_number - 1]
            await message.answer(f"📖 Заметка «{note['title']}»:\n{note['content']}")
        else:
            await message.answer("📖 Неверный номер заметки.")
    else:
        for note in notes:
            if note["title"] == title_or_number.strip():
                await message.answer(f"📖 Заметка «{note['title']}»:\n{note['content']}")
                return
        await message.answer(f"📖 Заметка «{title_or_number}» не найдена.")

@bot.on.message(text=["+правила <text>"])
async def add_rules(message: Message, text: str):
    if message.from_id not in owners:
        return
    save_rules(text)
    await message.answer("✅ Правила чата установлены.")

@bot.on.message(text=["-правила"])
async def remove_rules(message: Message):
    if message.from_id not in owners:
        return
    save_rules("")
    await message.answer("✅ Правила чата удалены.")

@bot.on.message(text=["правила", "Правила"])
async def show_rules(message: Message):
    rules = load_rules()
    if rules:
        await message.answer("📖 Правила чата:\n" + rules)
    else:
        await message.answer("📖 Правила чата отсутствуют.")

@bot.on.message(text=["команды", "Команды"])
async def help(message: Message):
    await message.answer('💬 Список актуальных команд: vk.com/@-224827653-commands')

@bot.on.message(text=["!аг"])
async def help(message: Message):
    if message.from_id not in super_owners:
        return
    user_id = await user_id_get_mes(message)
    target = await get_user_name(user_id)
    if user_id in owners:
        await message.answer(f'🦋 Пользователь {target} уже на этой должности.')
        return
    owners.append(user_id)
    await message.answer(f'🦋 Пользователю {target} выдан ранг агента.')

@bot.on.message(text=["!-аг"])
async def help(message: Message):
    if message.from_id not in super_owners:
        return
    user_id = await user_id_get_mes(message)
    target = await get_user_name(user_id)
    if user_id not in owners:
        await message.answer(f'🦋 Пользователя {target} нет в списке агентов.')
        return
    if user_id in super_owners:
        await message.answer(f'🦋 Вы не можете снять ранг создателю.')
        return
    owners.remove(user_id)
    await message.answer(f'🦋 Пользователю {target} снят ранг агента.')

@bot.on.message(text=["!аг <url>"])
async def help(message: Message, url: str):
    if message.from_id not in super_owners:
        return
    user_id = get_user_id(url)[0]
    target = await get_user_name(user_id)
    if user_id in owners:
        await message.answer(f'🦋 Пользователь {target} уже на этой должности.')
        return
    owners.append(user_id)
    await message.answer(f'🦋 Пользователю {target} выдан ранг агентов.')

@bot.on.message(text=["!-аг <url>"])
async def help(message: Message, url: str):
    if message.from_id not in super_owners:
        return
    user_id = get_user_id(url)[0]
    target = await get_user_name(user_id)
    if user_id not in owners:
        await message.answer(f'🦋 Пользователя {target} нет в списке агентов.')
        return
    if user_id in super_owners:
        await message.answer(f'🦋 Вы не можете снять ранг создателю.')
        return
    owners.remove(user_id)
    await message.answer(f'🦋 Пользователю {target} снят ранг агента.')

@bot.on.message(text=["помощь", 'Помощь'])
async def show_admins(message: Message):
    admins_info = []
    for user_id in owners:
        user_info = await bot.api.users.get(user_ids=user_id)
        user_name = f"{user_info[0].first_name} {user_info[0].last_name}"
        user_link = f"[id{user_id}|{user_name}]"
        admins_info.append(user_link)
    admins_text = "\n".join(admins_info)
    greeting_text = "📌 Актуальный список команд: (ссылка)\n\n"
    if admins_text:
        await message.answer(greeting_text + "📃 Агенты помощи:\n" + admins_text)
    else:
        await message.answer(greeting_text + "🦋 Нет агентов.")

@bot.on.message(text=['стата', 'Стата'])
async def show_stats(message: Message):
    stats_text = "📊 СТАТИСТИКА ПО СООБЩЕНИЯМ ЗА ВСЁ ВРЕМЯ:\n"
    sorted_statistics = sorted(statistics, key=lambda x: x["count"], reverse=True)[:30]
    for idx, user_stats in enumerate(sorted_statistics, start=1):
        user_info = await bot.api.users.get(user_ids=user_stats["user_id"])
        user_link = f"https://vk.com/id{user_stats['user_id']}"
        stats_text += f"{idx}. [{user_link}|{user_info[0].first_name} {user_info[0].last_name}] – {user_stats['count']}\n"
    total_messages = sum(user_stats["count"] for user_stats in statistics)
    stats_text += f"\n📖 Общее количество: {total_messages}"
    await message.answer(stats_text)

@bot.on.message(text=["очиститьстату", 'Очиститьстату'])
async def clear_static_file(message: Message):
    if message.from_id in super_owners:
        try:
            os.remove('static.json')
            await message.answer("✅ Файл статистики успешно удален. При перезапуске бота все сообщения будут сброшены.")
        except FileNotFoundError:
            await message.answer("Файл статистики не найден.")
    else:
        print('')

@bot.on.message(text=["Обновить чат", 'обновить чат'])
async def obnova_chata(message: Message):
    if message.from_id not in owners:
        return
    message.asnwer('🗃 Сведения об участниках были синхронизированы.')
    chat_info_response = await bot.api.messages.get_conversations_by_id(peer_ids=[message.peer_id], extended=1)
    chat_info = chat_info_response.items[0]
    members_count = chat_info.chat_settings.members_count
    chat_id = message.peer_id - 2000000000
    profiles_response = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    profiles = profiles_response.profiles
    filtered_profiles = [profile for profile in profiles if profile.id not in blocked_users]
    for profile in profiles:
        if profile.id in blocked_users:
            try:
                target = await get_user_name(profile.id)
                await message.ctx_api.request("messages.removeChatUser", {"member_id": profile.id, "chat_id": chat_id})
                await message.answer(f'🚷 Пользователь {target} находится в списке подозрительных ботов, в целях безопасности исключен из беседы.')
            except ZeroDivisionError:
                print('')

@bot.on.chat_message(ChatActionRule(MessagesMessageActionStatus.CHAT_INVITE_USER.value))
async def invitedbot(message: Message) -> None:
    if (
        message.action is not None
        and message.group_id is not None
        and message.action.member_id > 0
    ):
        user_id = message.action.member_id
        target = await get_user_name(user_id)
        if user_id in blocked_users:
            chat_id = message.peer_id - 2000000000
            await message.ctx_api.request("messages.removeChatUser", {"member_id": user_id, "chat_id": chat_id})
            await message.answer(f"🚷 Пользователь {target} находится в списке подозрительных ботов, в целях безопасности исключен из беседы.")
        else:
            await message.answer("""Пользователь {target} присоединился к чату.""")

@bot.on.message()
async def handle_message(message: Message):
    if message.from_id > 0:
        user_id = message.from_id
        target = await get_user_name(user_id)
        if user_id in blocked_users:
            try:
                await message.ctx_api.request("messages.removeChatUser", {"member_id": user_id, "chat_id": message.peer_id - 2000000000})
                await message.answer(f'🚷 Пользователь {target} находится в списке подозрительных ботов, в целях безопасности исключен из беседы.')
                return
            except ZeroDivisionError:
                print('')
        chat_info_response = await bot.api.messages.get_conversations_by_id(peer_ids=[message.peer_id], extended=1)
        chat_info = chat_info_response.items[0]
        members_count = chat_info.chat_settings.members_count
        chat_id = message.peer_id - 2000000000
        profiles_response = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        profiles = profiles_response.profiles
        filtered_profiles = [profile for profile in profiles if profile.id not in blocked_users]
        for profile in profiles:
            if profile.id in blocked_users:
                try:
                    target = await get_user_name(profile.id)
                    await message.ctx_api.request("messages.removeChatUser", {"member_id": profile.id, "chat_id": chat_id})
                    await message.answer(f'🚷 Пользователь {target} находится в списке подозрительных ботов, в целях безопасности исключен из беседы.')
                except ZeroDivisionError:
                    print('')
        registered_count = 0
        for profile in filtered_profiles:
            user_id = profile.id
            cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            user_data = cursor.fetchone()
            if user_data is None:
                cursor.execute("INSERT INTO users (user_id, candies, last_bonus) VALUES (?, ?, ?)",
                               (user_id, 0, 0))
                conn.commit()
                print(f"Пользователь с ID {user_id} зарегистрирован.")
                registered_count += 1

bot.run_forever()

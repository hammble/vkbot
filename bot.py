# -*- coding: utf-8 -*-
import vk_api
import time
import random
import os
import loguru

from vkbottle.bot import Bot, Message, MessageEvent, rules
from vkbottle.api import API
from vkbottle.dispatch.rules.base import ChatActionRule
from vkbottle_types.objects import MessagesMessageActionStatus
from vkbottle.tools import DocMessagesUploader, PhotoMessageUploader
from vkbottle import Callback, GroupEventType, Keyboard, KeyboardButtonColor, VKAPIError

from config import *

from modules.user_name_id import get_user_name, user_id_get_mes, get_user_id
from modules.vk_reg import data_reg

from utils.audio_settings import get_audio_setting, save_settings_audio
from utils.audiomsg_settings import get_audio_message_setting, save_settings_audio_message
from utils.blocked_users import blocked_users, save_blocked_users
from utils.blocked_words import load_blocked_words, save_blocked_words
from utils.chat_settings import save_chat_settings_to_file
from utils.close_settings import get_close_setting, save_settings_close
from utils.closechat_settings import get_close_chat_setting, save_close_chat
from utils.doc_settings import get_doc_setting, save_settings_doc
from utils.graffiti_settings import get_graffiti_setting, save_settings_graffiti
from utils.invite_community import get_invite_community_setting, save_settings
from utils.kickall_settings import get_kickall_setting, save_settings_kickall
from utils.lensms_settings import get_lensms_setting, set_lensms_setting, save_lensms_settings  
from utils.log import save_message, get_logs
from utils.mute import remove_mute_entry, mute_save, get_mute
from utils.muted_users import save_muted_users, muted_users
from utils.photo_settings import get_photo_setting, save_settings_photo
from utils.ruletka_settings import get_ruletka_setting, save_settings_ruletka
from utils.save_load_chat_settings import save_chat_settings_to_file, load_chat_settings_once
from utils.spam_settings import get_spam_setting, save_settings_spam
from utils.sticker_settings import get_stick_setting, save_settings_stick
from utils.treshold_settings import get_message_threshold_setting, set_message_threshold_setting
from utils.video_settings import get_video_setting, save_settings_video

from json_utils.json_struc import (
    invite_settings,
    close_chat_settings,
    close_settings,
    spam_settings,
    ruletka_settings,
    stick_settings,
    photo_settings,
    audio_settings,
    video_settings,
    audio_message_settings,
    graffiti_settings,
    doc_settings,
    lensms_settings,
    blocked_words_dict,
    chat_settings,
    kickall_settings
)

api = API(token_user)
token = token_user
tokenbot = token_bot
bot = Bot(token_bot)

vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
vk_session_bot = vk_api.VkApi(token=tokenbot)
vkbot = vk_session.get_api()

doc_uploader = DocMessagesUploader(bot.api)
photo_uploader = PhotoMessageUploader(bot.api)

loguru.logger.disable("vkbottle")

@bot.on.chat_message(text=['<pref>рег' for pref in prefixes])
async def regg(message: Message):
    user_id = await user_id_get_mes(message)
    target = await get_user_name(user_id)
    await message.reply(data_reg(user_id, target))


@bot.on.chat_message(text=['<pref>рег <url>' for pref in prefixes])
async def regg(message: Message, url: str):
    user_id = get_user_id(url)[0]
    target = await get_user_name(user_id)
    await message.reply(data_reg(user_id, target))


@bot.on.chat_message(text=['<pref>пинг' for pref in prefixes])
async def pingbota(message: Message):
    delta = round(time.time() - message.date, 2)
    if message.from_id in owners:
        start_time = time.time()
        await bot.api.messages.get_conversations()
        end_time = time.time()
        execution_time = end_time - start_time 
        rounded_execution_time = round(execution_time, 2)
        await message.reply(f'🔧 Понг!\ndb: {delta}ms | API: {rounded_execution_time}ms')
    else:
        await message.answer(f'🔧 Понг!\ndb: {delta}ms')

@bot.on.chat_message(text=['<pref>+ас' for pref in prefixes])
async def asus(message: Message):
    if message.from_id not in owners:
        return
    user = await user_id_get_mes(message)
    targ = await get_user_name(user)
    if user in owners:
        return
    if user in blocked_users:
        await message.reply(f'💬 {targ} уже в спам-листе.')
        return
    await message.reply(f'🛡 Пользователь {targ} добавлен спам-лист.\n\n#{user}')
    blocked_users.append(user)
    save_blocked_users(blocked_users)


@bot.on.chat_message(text=['<pref>-ас' for pref in prefixes])
async def asus(message: Message):
    if message.from_id not in owners:
        return
    user = await user_id_get_mes(message)
    targ = await get_user_name(user)
    if user in owners:
        return
    if user not in blocked_users:
        await message.reply(f'❌ {targ} отсутствует в спам-листе.')
        return
    await message.reply(f'🛡 Пользователь {targ} удален из спам-листа.')
    blocked_users.remove(user)
    save_blocked_users(blocked_users)


@bot.on.chat_message(text=['<pref>+ас <url>' for pref in prefixes])
async def asus(message: Message, url: str):
    if message.from_id not in owners:
        return
    user = get_user_id(url)[0]
    targ = await get_user_name(user)
    if user in owners:
        return
    if user in blocked_users:
        await message.reply(f'💬 {targ} уже в спам-листе.')
        return
    await message.reply(f'🛡 Пользователь {targ} добавлен спам-лист.\n\n#{user}')
    blocked_users.append(user)
    save_blocked_users(blocked_users)


@bot.on.chat_message(text=['<pref>-ас <url>' for pref in prefixes])
async def asus(message: Message, url: str):
    if message.from_id not in owners:
        return
    user = get_user_id(url)[0]
    targ = await get_user_name(user)
    if user in owners:
        return
    if user not in blocked_users:
        await message.reply(f'❌ {targ} отсутствует в спам-листе.')
        return
    await message.reply(f'🛡 Пользователь {targ} удален из спам-листа.')
    blocked_users.remove(user)
    save_blocked_users(blocked_users)


#-------------#
@bot.on.chat_message(text=['мут', 'Мут'])
async def asus22(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            user = await user_id_get_mes(message)
            targ = await get_user_name(user)
            if user in muted_users:
                await message.reply(f'💬 {targ} уже в мут-листе.')
                return
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            mute_save(message.peer_id, user, timestamp)  # Записываем время мута
            
            await message.reply(f'🛡 Пользователь {targ} добавлен мут-лист.\n\n#{user}')
            muted_users.append(user)
            save_muted_users(muted_users)
    
@bot.on.chat_message(text=['-мут'])
async def asus23(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            user = await user_id_get_mes(message)
            targ = await get_user_name(user)
            if user not in muted_users:
                await message.reply(f'❌ {targ} отсутствует в мут-листе.')
                return
            
            muted_users.remove(user)
            save_muted_users(muted_users)
            
            remove_mute_entry(message.peer_id, user)  # Удаление записи о муте из файла
            await message.reply(f'🛡 Пользователь {targ} удален из мут-листа.')

@bot.on.chat_message(text=['мут <url>', 'Мут <url>'])
async def asus24(message: Message, url: str):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            user = get_user_id(url)[0]
            targ = await get_user_name(user)
            if user in muted_users:
                await message.reply(f'💬 {targ} уже в мут-листе.')
                return
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            mute_save(message.peer_id, user, timestamp)  # Записываем время мута
            
            await message.reply(f'🛡 Пользователь {targ} добавлен мут-лист.\n\n#{user}')
            muted_users.append(user)
            save_muted_users(muted_users)

@bot.on.chat_message(text=['-мут <url>'])
async def asus25(message: Message, url: str):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            user = get_user_id(url)[0]
            targ = await get_user_name(user)
            if user not in muted_users:
                await message.reply(f'❌ {targ} отсутствует в мут-листе.')
                return
            
            muted_users.remove(user)
            save_muted_users(muted_users)
            
            remove_mute_entry(message.peer_id, user)  # Удаление записи о муте из файла
            await message.reply(f'🛡 Пользователь {targ} удален из мут-листа.')


@bot.on.chat_message(text=['мутлист', 'Мутлист'])
async def mute_list(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            muted_users = get_mute(message.peer_id)
            if not muted_users:
                await message.reply("В мут-листе пока нет пользователей.")
                return
            
            response = "Список пользователей в муте:\n"
            for mute_entry in muted_users:
                timestamp = time.strptime(mute_entry["timestamp"], '%Y-%m-%d %H:%M:%S')
                sender_id = mute_entry['sender_id']
                sender_name = await get_user_name(sender_id)  # Получаем имя пользователя
                user_info = f"{time.strftime('%d:%m:%Y %H:%M:%S', timestamp)} | {sender_name}"
                response += f"{user_info}\n"
            
            await message.reply(response)
#--------------#

@bot.on.chat_message(text=['<pref>музыка <author>' for pref in prefixes])
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
            await message.answer(f"🚫 Произошла ошибка при получении треков: неверный формат ответа от сервера.")
    except Exception as e:
        await message.answer(f"🚫 Произошла ошибка при получении треков: {str(e)}")

@bot.on.chat_message(text=['<pref>настройка 1 вкл' for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            invite_settings[chat_id] = True
            save_settings()
            await message.reply("🛡 Приглашение сообществ в этой беседе разрешено.")

@bot.on.chat_message(text=['<pref>настройка 1 выкл' for pref in prefixes])
async def disable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            invite_settings[chat_id] = False
            save_settings()
            await message.reply("🛡 Приглашение сообществ в этой беседе запрещено.")

# -------------------#

@bot.on.chat_message(text=['<pref>настройка 2 выкл' for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            spam_settings[chat_id] = True
            save_settings_spam()
            await message.reply("🛡 Антиспам выключен.")

@bot.on.chat_message(text=['<pref>настройка 2 вкл' for pref in prefixes])
async def disable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            spam_settings[chat_id] = False
            save_settings_spam()
            await message.reply("🛡 Антиспам включен.")

@bot.on.chat_message(text=['<pref>рулетка выкл' for pref in prefixes])
async def enable_ruletka_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            ruletka_settings[chat_id] = True
            save_settings_ruletka()
            await message.reply("🛡 Рулетка отключена.")


@bot.on.chat_message(text=['<pref>рулетка вкл' for pref in prefixes])
async def disable_ruletka_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            ruletka_settings[chat_id] = False
            save_settings_ruletka()
            await message.reply("🛡 Рулетка включена.")

# -------------------#
@bot.on.chat_message(text=['<pref>настройка 10 выкл' for pref in prefixes])
async def enable_close_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            close_settings[chat_id] = True
            save_settings_close()
            await message.reply("🛡 Запрет инвайт юзеров отключен.")


@bot.on.chat_message(text=['<pref>настройка 10 вкл' for pref in prefixes])
async def disable_close_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            close_settings[chat_id] = False
            save_settings_close()
            await message.reply("🛡 Запрет инвайт юзеров включен.\n🔧 В чатах от сообщества данная функция нестабильна.")


# -------------------#

@bot.on.chat_message(text=['<pref>настройка 3 выкл' for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            stick_settings[chat_id] = True
            save_settings_stick()
            await message.reply("🛡 Стикеры запрещены.")


@bot.on.chat_message(text=['<pref>настройка 3 вкл' for pref in prefixes])
async def disable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            stick_settings[chat_id] = False
            save_settings_stick()
            await message.reply("🛡 Стикеры разрешены.")


@bot.on.chat_message(text=['<pref>настройка 4 выкл' for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            photo_settings[chat_id] = True
            save_settings_photo()
            await message.reply("🛡 Фотографии запрещены.")


@bot.on.chat_message(text=['<pref>настройка 4 вкл' for pref in prefixes])
async def disable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            photo_settings[chat_id] = False
            save_settings_photo()
            await message.reply("🛡 Фотографии разрешены.")


@bot.on.chat_message(text=['<pref>настройка 5 выкл' for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            doc_settings[chat_id] = True
            save_settings_doc()
            await message.reply("🛡 Документы запрещены.")


@bot.on.chat_message(text=['<pref>настройка 5 вкл' for pref in prefixes])
async def disable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            doc_settings[chat_id] = False
            save_settings_doc()
            await message.reply("🛡 Документы разрешены.")


# ---------------------#

@bot.on.chat_message(text=['<pref>настройка 6 выкл' for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            audio_settings[chat_id] = True
            save_settings_audio()
            await message.reply("🛡 Аудиофайлы запрещены.")


@bot.on.chat_message(text=['<pref>настройка 6 вкл' for pref in prefixes])
async def disable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            audio_settings[chat_id] = False
            save_settings_audio()
            await message.reply("🛡 Аудиофайлы разрешены.")


# ---------------------#

@bot.on.chat_message(text=['<pref>настройка 7 выкл' for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            video_settings[chat_id] = True
            save_settings_video()
            await message.reply("🛡 Видео запрещены.")


@bot.on.chat_message(text=['<pref>настройка 7 вкл' for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            video_settings[chat_id] = False
            save_settings_video()
            await message.reply("🛡 Видео разрешены.")

#----------------------#

@bot.on.chat_message(text=['<pref>закрыть чат' for pref in prefixes])
async def enable_close_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            close_chat_settings[chat_id] = True
            save_close_chat()
            await message.reply("🛡 Чат закрыт для общения. Писать могут только администраторы чата.")


@bot.on.chat_message(text=['<pref>открыть чат' for pref in prefixes])
async def enable_close_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            close_chat_settings[chat_id] = False
            save_close_chat()
            await message.reply("🛡 Чат открыт для общения.")

# ---------------------#

@bot.on.chat_message(text=['<pref>настройка 8 выкл' for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            audio_message_settings[chat_id] = True
            save_settings_audio_message()
            await message.reply("🛡 Голосовые сообщения запрещены.")

@bot.on.chat_message(text=['<pref>настройка 8 вкл' for pref in prefixes])
async def disable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            audio_message_settings[chat_id] = False
            save_settings_audio_message()
            await message.reply("🛡 Голосовые сообщения разрешены.")
# ---------------------#
@bot.on.chat_message(text=['<pref>настройка 9 вкл' for pref in prefixes])
async def disable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            graffiti_settings[chat_id] = False
            save_settings_graffiti()
            await message.reply("🛡 Граффити разрешены.")

@bot.on.chat_message(text=['<pref>настройка 9 выкл' for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            graffiti_settings[chat_id] = True
            save_settings_graffiti()
            await message.reply("🛡 Граффити запрещены.")

@bot.on.chat_message(attachment='sticker')
async def stickers(message: Message):
    chat_id = message.peer_id - 2000000000
    if get_close_chat_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id != admin.member_id:
                await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    if message.from_id in muted_users:
        await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    user = message.from_id
    targ = await get_user_name(user)
    if get_stick_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id == admin.member_id:
                return
        try:
            await message.ctx_api.request("messages.removeChatUser", {"member_id": user, "chat_id": chat_id})
            await message.answer(f'🚷 Стикеры были запрещены. Исключаю пользователя {targ}.')
            await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
        except ZeroDivisionError:
            print('')


@bot.on.chat_message(attachment='photo')
async def photos(message: Message):
    chat_id = message.peer_id - 2000000000
    if get_close_chat_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id != admin.member_id:
                await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    if message.from_id in muted_users:
        await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    user = message.from_id
    targ = await get_user_name(user)
    if get_photo_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id == admin.member_id:
                return
        try:
            await message.ctx_api.request("messages.removeChatUser", {"member_id": user, "chat_id": chat_id})
            await message.answer(f'🚷 Фотографии были запрещены. Исключаю пользователя {targ}.')
            await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
        except ZeroDivisionError:
            print('')


@bot.on.chat_message(attachment='doc')
async def docs(message: Message):
    chat_id = message.peer_id - 2000000000
    if get_close_chat_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id != admin.member_id:
                await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    if message.from_id in muted_users:
        await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    user = message.from_id
    targ = await get_user_name(user)
    if get_photo_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id == admin.member_id:
                return
        try:
            await message.ctx_api.request("messages.removeChatUser", {"member_id": user, "chat_id": chat_id})
            await message.answer(f'🚷 Документы были запрещены. Исключаю пользователя {targ}.')
            await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
        except ZeroDivisionError:
            print('')


@bot.on.chat_message(attachment='audio')
async def audio(message: Message):
    chat_id = message.peer_id - 2000000000
    if get_close_chat_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id != admin.member_id:
                await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    if message.from_id in muted_users:
        await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    user = message.from_id
    targ = await get_user_name(user)
    if get_audio_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id == admin.member_id:
                return
        try:
            await message.ctx_api.request("messages.removeChatUser", {"member_id": user, "chat_id": chat_id})
            await message.answer(f'🚷 Аудиофайлы были запрещены. Исключаю пользователя {targ}.')
            await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
        except ZeroDivisionError:
            print('')


@bot.on.chat_message(attachment='video')
async def docs(message: Message):
    chat_id = message.peer_id - 2000000000
    if get_close_chat_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id != admin.member_id:
                await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    if message.from_id in muted_users:
        await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    user = message.from_id
    targ = await get_user_name(user)
    if get_video_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id == admin.member_id:
                return
        try:
            await message.ctx_api.request("messages.removeChatUser", {"member_id": user, "chat_id": chat_id})
            await message.answer(f'🚷 Видео были запрещены. Исключаю пользователя {targ}.')
            await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
        except ZeroDivisionError:
            print('')


@bot.on.chat_message(attachment='audio_message')
async def docs(message: Message):
    chat_id = message.peer_id - 2000000000
    if get_close_chat_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id != admin.member_id:
                await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    if message.from_id in muted_users:
        await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    user = message.from_id
    targ = await get_user_name(user)
    if get_audio_message_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id == admin.member_id:
                return
        try:
            await message.ctx_api.request("messages.removeChatUser", {"member_id": user, "chat_id": chat_id})
            await message.answer(f'🚷 Голосовые сообщения были запрещены. Исключаю пользователя {targ}.')
            await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
        except ZeroDivisionError:
            print('')


@bot.on.chat_message(attachment='graffiti')
async def docs(message: Message):
    chat_id = message.peer_id - 2000000000
    if get_close_chat_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id != admin.member_id:
                await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    if message.from_id in muted_users:
        await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    user = message.from_id
    targ = await get_user_name(user)
    if get_graffiti_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id == admin.member_id:
                return
        try:
            await message.ctx_api.request("messages.removeChatUser", {"member_id": user, "chat_id": chat_id})
            await message.answer(f'🚷 Граффити были запрещены. Исключаю пользователя {targ}.')
            await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
        except ZeroDivisionError:
            print('')


# -------------------#
@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({"error": "snackbar"}),
)
async def show_snackbar(event: MessageEvent):
    await event.show_snackbar("Нет доступа.")


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({"cmd": "close"}),
)
async def edit_message(event: MessageEvent):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=event.object.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if event.object.from_id == admin.member_id:
            text_lines = [
                '🗃 Сведения об участниках были синхронизированы.',
                '⚙ Советую написать <<.настройка 2 вкл>> для защиты чата.'
                '⚙ Список настроек <<.настройки>>',
                '',
                '📜 Команды бота: ССЫЛКА',
                '👨‍⚖ Правила использования БОТА: ССЫЛКА']
            text = "\n".join(text_lines)
            await event.edit_message(text)
            time.sleep(1)
            chat_info_response = await bot.api.messages.get_conversations_by_id(
                peer_ids=[event.object.peer_id],
                extended=1
            )
            chat_info = chat_info_response.items[0]
            chat_id = event.object.peer_id - 2000000000
            profiles_response = await bot.api.messages.get_conversation_members(
                peer_id=event.object.peer_id
            )
            profiles = profiles_response.profiles
            for profile in profiles:
                if profile.id in blocked_users:
                    target = await get_user_name(profile.id)
                    await bot.api.messages.remove_chat_user(
                        member_id=profile.id,
                        chat_id=chat_id
                    )
                    await bot.api.messages.send(
                        peer_id=event.object.peer_id,
                        random_id=0,
                        message=f'🚷 Пользователь {target} находится в списке подозрительных ботов, в целях безопасности исключен из беседы.'
                    )


@bot.on.chat_message(text=["<pref>обновитьчат" for pref in prefixes])
async def obnova_chata(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            time.sleep(1)
            chat_info_response = await bot.api.messages.get_conversations_by_id(peer_ids=[message.peer_id], extended=1)
            chat_info = chat_info_response.items[0]
            chat_id = message.peer_id - 2000000000
            profiles_response = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
            profiles = profiles_response.profiles
            if get_spam_setting(chat_id):
                await message.reply('🗃 Сведения об участниках были синхронизированы.')
                return
            for profile in profiles:
                if profile.id in blocked_users:
                    try:
                        await message.reply('🗃 Сведения об участниках были синхронизированы.')
                        target = await get_user_name(profile.id)
                        await message.ctx_api.request("messages.removeChatUser",
                                                      {"member_id": profile.id, "chat_id": chat_id})
                        await message.answer(
                            f'🚷 Пользователь {target} находится в списке подозрительных ботов, в целях безопасности исключен из беседы.')
                    except ZeroDivisionError:
                        print('')


@bot.on.message(ChatActionRule(MessagesMessageActionStatus.CHAT_INVITE_USER.value))
async def invitedbot(message: Message) -> None:
    if (
            message.action is not None
            and message.group_id is not None
            and message.action.member_id > 0
    ):
        user_id = message.action.member_id
        chat_id = message.peer_id - 2000000000
        target = await get_user_name(user_id)
        close_setting = get_close_setting(chat_id)
        if not close_setting:
            await message.ctx_api.request("messages.removeChatUser", {"member_id": user_id, "chat_id": chat_id})
            await message.answer(
                '🚷 Приглашение пользователей в чат было запрещено.\nОтключить защиту:\n!настройка 10 выкл')
        if not get_spam_setting(chat_id):
            if user_id in blocked_users:
                chat_id = message.peer_id - 2000000000
                await message.ctx_api.request("messages.removeChatUser", {"member_id": user_id, "chat_id": chat_id})
                await message.answer(
                    f"🚷 Пользователь {target} находится в списке подозрительных ботов, в целях безопасности исключен из беседы.")
            else:
                print(f"""🔗 Пользователь {target} присоединился к чату.""")
    if (
            message.action is not None
            and message.group_id is not None
            and message.action.member_id < 0
    ):
        user_id = message.action.member_id
        chat_id = message.peer_id - 2000000000
        if not get_invite_community_setting(chat_id):
            await message.ctx_api.request("messages.removeChatUser", {"member_id": user_id, "chat_id": chat_id})
            await message.answer(
                '🚷 Приглашение сообществ было отключено. Разрешить приглашение: !инвайт сообществ выкл')

    if (
            message.action is not None
            and message.group_id is not None
            and message.action.member_id == -GROUP_ID_FOR_INVITE
    ):
        text_lines = [
            'Доброго времени суток!',
            'Мне нужны права администратора для того, чтобы я работал в этом чате. После выдачи администратора, можете нажать на кнопку ниже (или же написать <<.обновитьчат>>).',
            '',
            '⚙ Советую написать <<.настройка 2 вкл>> для защиты чата.',
            '⚙ Список настроек <<.настройки>>.',
            '',
            '📜 Команды бота: ССЫЛКА',
            '👨‍⚖ Правила использования БОТА: ССЫЛКА'
        ]
        text = "\n".join(text_lines)
        attachment = "ссылка на картинку"
        KEYBOARD = (
            Keyboard(one_time=False, inline=True)
            .add(Callback("⚙ Обновить чат", payload={"cmd": "close"}))
            .get_json()
        )
        await message.answer(text, attachment, keyboard=KEYBOARD)

@bot.on.message(ChatActionRule(MessagesMessageActionStatus.CHAT_KICK_USER.value))
async def leave(message: Message) -> None:
     if (
            message.action is not None
            and message.group_id is not None 
            and message.action.member_id > 0
    ):
        user_id = message.action.member_id
        target = await get_user_name(user_id)
        print(f"""🔗 Пользователь {target} покинул чат.""")

@bot.on.chat_message(text=['<pref>запретитьслово <word>' for pref in prefixes])
async def zapret(message: Message, word: str):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            global blocked_words_dict
            if chat_id not in blocked_words_dict:
                blocked_words_dict[chat_id] = load_blocked_words(chat_id)
            word_lower = word.lower()
            if word_lower not in blocked_words_dict[chat_id]:
                blocked_words_dict[chat_id].append(word_lower)
                save_blocked_words(chat_id, blocked_words_dict[chat_id])
                await message.reply(
                    f'🛡 Слово было добавлено в список запрещенных слов.')
            else:
                await message.reply(f'🛡 Слово уже находится в списке запрещенных слов.')


@bot.on.chat_message(text=['<pref>разрешитьслово <word>' for pref in prefixes])
async def razreshit(message: Message, word: str):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            blocked_words = load_blocked_words(chat_id)
            word_lower = word.lower()
            if word_lower in blocked_words:
                blocked_words.remove(word_lower)
                save_blocked_words(chat_id, blocked_words)
                await message.reply(f'🛡 Слово было удалено из списка запрещенных слов.')
            else:
                await message.reply(f'🛡 Слово не найдено в списке запрещенных слов.')


@bot.on.chat_message(text=['<pref>запрещенныеслова' for pref in prefixes])
async def show_blocked_words(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            blocked_words = load_blocked_words(chat_id)
            if not blocked_words:
                await message.reply("🛡 Список запрещенных слов пуст.")
            else:
                blocked_words_str = "\n".join(blocked_words)
                await message.reply(f"🛡 Список запрещенных слов:\n{blocked_words_str}")


@bot.on.chat_message(text=['<pref>очиститьслова' for pref in prefixes])
async def clear_blocked_words(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            save_blocked_words(chat_id, [])
            await message.reply("🛡 Список запрещенных слов был очищен.")


# ------------------------------------------------------------------------#

@bot.on.chat_message(text=['<pref>команды' for pref in prefixes])
async def send_callback_button(message: Message):
    await message.reply("📜 Команды бота: ССЫЛКА")


# ------------------------------------------------------------------------#

KEYBOARD = (
    Keyboard(one_time=False, inline=True)
    .add(Callback("⚙", payload={"cmd": "tipanu"}))
    .get_json()
)


@bot.on.chat_message(text=['<pref>настройки' for pref in prefixes])
async def send_callback_button(message: Message):
    await message.reply("Настройки чата:", keyboard=KEYBOARD)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({"cmd": "tipanu"}),
)
async def edit_invite_settings(event: MessageEvent):
    chat_id = event.object.peer_id - 2000000000
    text = "⚙ Настройки защиты чата:\n"

    text += "1. Запрет инвайт групп: "
    if get_invite_community_setting(chat_id):
        text += "❌\n"
    else:
        text += "✅\n"

    text += "2. Антиспам: "
    if get_spam_setting(chat_id):
        text += "❌\n"
    else:
        text += "✅\n"

    text += "3. Стикеры: "
    if get_stick_setting(chat_id):
        text += "❌\n"
    else:
        text += "✅\n"

    text += "4. Фотографии: "
    if get_photo_setting(chat_id):
        text += "❌\n"
    else:
        text += "✅\n"

    text += "5. Документы: "
    if get_doc_setting(chat_id):
        text += "❌\n"
    else:
        text += "✅\n"

    text += "6. Аудио: "
    if get_audio_setting(chat_id):
        text += "❌\n"
    else:
        text += "✅\n"

    text += "7. Видео: "
    if get_video_setting(chat_id):
        text += "❌\n"
    else:
        text += "✅\n"

    text += "8. Голосовые: "
    if get_audio_message_setting(chat_id):
        text += "❌\n"
    else:
        text += "✅\n"

    text += "9. Граффити: "
    if get_doc_setting(chat_id):
        text += "❌\n"
    else:
        text += "✅\n"

    text += "10. Инвайт юзеров: "
    if get_close_setting(chat_id):
        text += "✅\n"
    else:
        text += "❌\n"

    message_threshold = chat_settings.get(chat_id, {}).get("message_threshold")
    text += f"11. Медленный режим: {'❌' if message_threshold is None else message_threshold} сек\n"
    message_length = lensms_settings.get(chat_id, 4096)
    text += f"12. Длина сообщений: {message_length} символов\n"

    text += "13. Чат: "
    if get_close_chat_setting(chat_id):
        text += "Закрыт\n"
    else:
        text += "Открыт\n"

    await event.edit_message(text)


# ------------------------------------------------------------------------#

@bot.on.chat_message(text=['<pref>настройка 11 <threshold:int>' for pref in prefixes])
async def set_message_threshold(message: Message, threshold: int):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            set_message_threshold_setting(chat_id, threshold)
            save_chat_settings_to_file()
            await message.reply(
                f"🛡 Установлен медленный режим в {threshold} сек.")


@bot.on.chat_message(text=['<pref>настройка 12 <threshold:int>' for pref in prefixes])
async def set_message_length(message: Message, threshold: int):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            set_lensms_setting(chat_id, threshold)
            save_lensms_settings()
            await message.reply(
                f"🛡 Длина сообщений установлена в {threshold} символов.")


@bot.on.chat_message(text=["<pref>команда киквсех выкл" for pref in prefixes])
async def enable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            kickall_settings[chat_id] = True
            save_settings_kickall()
            await message.reply("🛡 Команда для исключения всех пользователей отключена.")


@bot.on.chat_message(text=["<pref>команда киквсех вкл" for pref in prefixes])
async def disable_invite_community(message: Message):
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            chat_id = message.peer_id - 2000000000
            kickall_settings[chat_id] = False
            save_settings_kickall()
            await message.reply("🛡 Команда для исключения всех пользователей включена.")


@bot.on.chat_message(text=['<pref>чистка киквсех' for pref in prefixes])
async def kickall(message: Message):
    chat_id = message.peer_id - 2000000000
    if get_kickall_setting(chat_id):
        await message.reply('🛡 Данная команда отключена. Включить:\n!команда киквсех вкл')
        return
    chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
    admins = [member for member in chat_info.items if member.is_admin]
    for admin in admins:
        if message.from_id == admin.member_id:
            sender = message.from_id
            send = await get_user_name(sender)
            chat_info = await bot.api.messages.get_conversations_by_id(peer_ids=[message.peer_id], extended=1)
            members_count = chat_info.items[0].chat_settings.members_count
            chat_id = message.peer_id - 2000000000
            profiles = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
            await message.answer(f'💬 {send} запускает чистку всего чата. Начало через 3 секунды.')
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



@bot.on.chat_message(text=['<pref>рандомхелп' for pref in prefixes])
async def helprand(message: Message):
    await message.reply('!рандомчисло <num1:int> <num2:int> <count:int> -- именно такая структура в данном модуле.\n<num1> - число, от которого начинается диапазон рандома, соответственно <num2> - число, до которого считается диапазон рандома. <count> - число, сколько кнопок (рандомных) чисел выведет бот.\nМаксимальное значение <count> - 5.')

@bot.on.chat_message(text=['<pref>рандомчисло <num1:int> <num2:int> <count:int>' for pref in prefixes])
async def numbers(message: Message, num1: int, num2: int, count: int):
    if count > 5:
        await message.reply(f'🛡 Максимальное значение в <<count>> 5. Введите:\n!рандомхелп')
        return
    colors = [KeyboardButtonColor.PRIMARY, KeyboardButtonColor.SECONDARY, KeyboardButtonColor.NEGATIVE, KeyboardButtonColor.POSITIVE]
    keyboard = Keyboard(one_time=False, inline=True)
    for i in range(count):
        random_number = random.randint(num1, num2)
        color = colors[i % len(colors)]
        keyboard.add(Callback(f"{random_number}", payload={"game": "rundoms", "number": random_number}), color=color)  
    await message.reply("Рандомные числа:", keyboard=keyboard.get_json())

@bot.on.chat_message(text=['<pref>админпанель' for pref in prefixes])
async def admins(message: Message):
    keyboard = Keyboard(inline=True, one_time=False)
    keyboard.add(Callback("hide", payload={"action": "hide"}))
    keyboard.add(Callback("del db", payload={"action": "delete"}))
    keyboard.add(Callback("stop", payload={"action": "stop"}))
    keyboard.add(Callback("ids", payload={"action": "show_ids"}))
    await message.reply("ADMIN:", keyboard=keyboard.get_json())

@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({"action": "hide"}),
)
async def send_chat_members(event: MessageEvent):
    user_id = event.user_id
    if user_id not in super_owners:
        return
    await event.edit_message(':D')

@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({"action": "show_ids"}),
)
async def send_chat_members(event: MessageEvent):
    user_id = event.user_id
    if user_id not in super_owners:
        return
    chat_info = await bot.api.messages.get_conversations_by_id(peer_ids=[event.peer_id], extended=1)
    members_count = chat_info.items[0].chat_settings.members_count
    chat_id = event.peer_id - 2000000000
    profiles = await bot.api.messages.get_conversation_members(peer_id=event.peer_id)
    for profile in profiles.profiles:
        if profile.id > 0:
            members_ids = [profile.id for profile in profiles.profiles if profile.id > 0]
    await bot.api.messages.send(user_id=ownertop, random_id=0, message=f"Список участников чата: {' '.join(map(str, members_ids))}")
    await event.edit_message(':D')

@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({"action": "stop"}),
)
async def delete_all_files(event: MessageEvent):
    user_id = event.user_id
    if user_id not in super_owners:
        return
    await event.send_message('🛡 Бот остановлен!')
    await event.edit_message(':D')
    exit()

@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({"action": "delete"}),
)
async def delete_all_files(event: MessageEvent):
    user_id = event.user_id
    if user_id not in super_owners:
        return
    folder_path = r'ПУТЬ'
    bot_file_name = 'bot.py'
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path) and file_name != bot_file_name:
                os.remove(file_path)
    except Exception as e:
        await event.send_message(f'🛡  Не удалось удалить файлы. Проверьте правильность указанного пути.')
        return
    await event.send_message('🛡 Все файлы, кроме файла бота, были удалены.')
    await event.edit_message(':D')

@bot.on.message(text=['<pref>рулетка' for pref in prefixes])
async def rul(message: Message):
    random1 = random.randint(0, 3)
    random2 = random.randint(0, 3)
    chat_id = message.peer_id - 2000000000
    user = message.from_id
    target = await get_user_name(user)
    if not get_ruletka_setting(chat_id):
        if random1 == random2:
            try:
                await message.ctx_api.request("messages.removeChatUser", {"member_id": message.from_id, "chat_id": chat_id})
                await message.reply(f'🔫 {target} проиграл в рулетку!\n💬 И был успешно исключён с чата :(')
            except VKAPIError:
                print('')
        else:
            await message.reply('💬 Вот это везение! Подумай о маме с папой и не пытайся совершить самоубийство.')
    else:
        await message.reply('💬 Как жаль, рулетка выключена. Включить её: !рулетка вкл')

@bot.on.chat_message(text=['<pref>настройки помощь' for pref in prefixes])
async def help(message: Message):
    text = '🔧 Как настраиваются настройки для беседы?\nЧтобы настроить или же включить настройку, пользуемся: .настройка (номер) вкл/выкл/params\n\n💬 Вкл - включает. Выкл - выключает. Params - параметры. К примеру:\n.настройка 1 вкл\n.настройка 11 6'
    await message.reply(text)

@bot.on.chat_message(text=['<pref>логи' for pref in prefixes])
async def log(message: Message):
    if message.from_id in owners:
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id == admin.member_id:
                peer_id = message.peer_id - 2000000000
                logs = get_logs(peer_id)
                if logs:
                    response = "✅ Логи сообщений всего чата:\n"
                    for log in logs:
                        sender_name = await get_user_name(log["sender_id"])
                        response += f"{sender_name} | {log['timestamp']}: {log['text']}\n"
                else:
                    response = "🗯 Логи сообщений пусты.\nВведите <<.обновитьчат>>"
                await message.answer(response)

@bot.on.chat_message(text=['<pref>-смс' for pref in prefixes])
async def delete_message(message: Message):
    cmids: list[int] = []
    if m := message.reply_message:
        cmids = [m.conversation_message_id]
    elif message.fwd_messages:
        cmids = [m.conversation_message_id for m in message.fwd_messages]
    try:
        await bot.api.messages.delete(group_id=GROUP_ID, delete_for_all=True, peer_id=message.peer_id, cmids=cmids)
        await message.reply(f"✅ Сообщения успешно удалены!")
    except VKAPIError:
        await message.reply(f'❌ Произошла ошибка VK.')

@bot.on.chat_message(text=['<pref>-смс тихо' for pref in prefixes])
async def delete_message(message: Message):
    cmids: list[int] = []
    if m := message.reply_message:
        cmids = [m.conversation_message_id]
    elif message.fwd_messages:
        cmids = [m.conversation_message_id for m in message.fwd_messages]
    await bot.api.messages.delete(group_id=GROUP_ID, delete_for_all=True, peer_id=message.peer_id, cmids=cmids)

@bot.on.message()
async def handle_message(message: Message):
    chat_id = message.peer_id - 2000000000
    if get_close_chat_setting(chat_id):
        chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        admins = [member for member in chat_info.items if member.is_admin]
        for admin in admins:
            if message.from_id != admin.member_id:
                await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    if message.from_id in muted_users:
        await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    save_message(message.peer_id - 2000000000, message.from_id, message.text)
    users = message.from_id
    target = await get_user_name(users)
    load_chat_settings_once()
    if chat_id not in chat_settings:
        chat_settings[chat_id] = {"message_threshold": 0, "last_message_time": 0}
    current_time = time.time()
    last_message_time = chat_settings[chat_id].get("last_message_time", 0)
    message_threshold = get_message_threshold_setting(chat_id)
    if current_time - last_message_time < message_threshold:
        if message.from_id > 0:
            chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
            admins = [member for member in chat_info.items if member.is_admin]
            for admin in admins:
                if message.from_id != admin.member_id:
                    await message.ctx_api.request("messages.removeChatUser",{"member_id": message.from_id, "chat_id": chat_id})
                    await message.answer(f"🚷 Слишком много сообщений подряд от пользователя {target}. Исключаю пользователя с чата.")
                    await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
    chat_settings[chat_id]["last_message_time"] = current_time
    save_chat_settings_to_file()
    if message.from_id < 0:
        chat_id = message.peer_id - 2000000000
        if not get_invite_community_setting(chat_id):
            try:
                await message.ctx_api.request("messages.removeChatUser", {"member_id": user_id, "chat_id": chat_id})
                await message.answer('🚷 Приглашение сообществ было отключено. Разрешить приглашение: !инвайт сообществ выкл')
            except ZeroDivisionError:
                print('')
            chat_info_response = await bot.api.messages.get_conversations_by_id(peer_ids=[message.peer_id], extended=1)
            chat_info = chat_info_response.items[0]
            chat_id = message.peer_id - 2000000000
            profiles_response = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
            profiles = profiles_response.profiles
            if not get_invite_community_setting(chat_id):
                for profile in profiles:
                    if profile.id in blocked_users:
                        try:
                            target = await get_user_name(profile.id)
                            await message.ctx_api.request("messages.removeChatUser",
                                                          {"member_id": profile.id, "chat_id": chat_id})
                            await message.answer(
                                '🚷 Приглашение сообществ было отключено. Разрешить приглашение: !настройка 1 выкл')
                        except ZeroDivisionError:
                            print('')
                            return
    if message.from_id > 0:
        max_message_length = get_lensms_setting(message.peer_id - 2000000000)
        if len(message.text) > max_message_length:
            chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
            admins = [member for member in chat_info.items if member.is_admin]
            for admin in admins:
                if message.from_id != admin.member_id:
                    targ = await get_user_name(message.from_id)
                    await message.ctx_api.request("messages.removeChatUser", {"member_id": message.from_id, "chat_id": chat_id})
                    await message.answer(f'🚷 Пользователь {targ} нарушил допустимую длину сообщения. Исключаю с чата.')
                    await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
                    return
        user_id = message.from_id
        target = await get_user_name(user_id)
        chat_id = message.peer_id - 2000000000
        blocked_words = load_blocked_words(chat_id)
        if not get_spam_setting(chat_id):
            if user_id in blocked_users:
                try:
                    chat_id = message.peer_id - 2000000000
                    await message.ctx_api.request("messages.removeChatUser",{"member_id": user_id, "chat_id": message.peer_id - 2000000000})
                    await message.answer(f'🚷 Пользователь {target} находится в списке подозрительных ботов, в целях безопасности исключен из беседы.')
                    await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
                    return
                except ZeroDivisionError:
                    print('')
                    return
        for word in blocked_words:
            if word.lower() in message.text.lower():
                chat_info = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
                admins = [member for member in chat_info.items if member.is_admin]
                for admin in admins:
                    if message.from_id != admin.member_id:
                        if message.from_id > 0:
                            try:
                                chat_id = message.peer_id - 2000000000
                                sender = await get_user_name(message.from_id)
                                await message.ctx_api.request("messages.removeChatUser", {"member_id": message.from_id, "chat_id": message.peer_id - 2000000000})
                                await message.answer(
                                    f'🚷 Сообщение от пользователя {sender} содержит запрещенное слово «{word}». Исключаю пользователя.')
                                await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
                            except ZeroDivisionError:
                                print('')
                                return
        if not get_spam_setting(chat_id):
            if message.from_id in blocked_users:
                try:
                    chat_id = message.peer_id - 2000000000
                    target = message.from_id
                    targ = await get_user_name(target)
                    await message.ctx_api.request("messages.removeChatUser", {"member_id": message.from_id,
                                                                              "chat_id": message.peer_id - 2000000000})
                    await message.answer(
                        f'🚷 Пользователь {targ} находится в списке подозрительных ботов, в целях безопасности исключен из беседы.')
                    await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
                except ZeroDivisionError:
                    print('')
                    return
        chat_info_response = await bot.api.messages.get_conversations_by_id(peer_ids=[message.peer_id], extended=1)
        chat_info = chat_info_response.items[0]
        chat_id = message.peer_id - 2000000000
        profiles_response = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        profiles = profiles_response.profiles
        if not get_spam_setting(chat_id):
            for profile in profiles:
                if profile.id in blocked_users:
                    try:
                        chat_id = message.peer_id - 2000000000
                        target = await get_user_name(profile.id)
                        await message.ctx_api.request("messages.removeChatUser",
                                                    {"member_id": profile.id, "chat_id": chat_id})
                        await message.answer(
                            f'🚷 Пользователь {target} находится в списке подозрительных ботов, в целях безопасности исключен из беседы.')
                        await bot.api.messages.delete(peer_id=message.peer_id, delete_for_all=True, conversation_message_ids=[message.conversation_message_id])
                    except ZeroDivisionError:
                        print('')

bot.run_forever()
import vk_api
import re

from vkbottle.bot import Message

from config import token_user

from bot import bot

token = token_user

async def get_user_name(user_id: int) -> str:
    user_info = await bot.api.users.get(user_ids=user_id)
    if user_info:
        first_name = user_info[0].first_name
        last_name = user_info[0].last_name
        return f"[https://vk.com/id{user_id}|{first_name} {last_name}]"
    return f"[id{user_id}|Unknown]"


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
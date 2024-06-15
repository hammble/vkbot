import requests

from bs4 import BeautifulSoup

def data_reg(akk_id, target):
    try:
        response = requests.get(f'https://vk.com/foaf.php?id={akk_id}')
        xml = response.text
        soup = BeautifulSoup(xml, 'html.parser')
        created = soup.find('ya:created').get('dc:date')
        dates = created.split("T")[0].split("-")
        times = created.split("T", maxsplit=1)[1].split("+", maxsplit=1)[0]
        created = f"{dates[2]}-{dates[1]}-{dates[0]} | {times}"
        return f"📖 Дата регистрации {target}: {created}."
    except Exception as error:
        return f"⚠ Ошибка выполнения.\n⚙ Информация об ошибке:\n{error}" 
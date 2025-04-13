from aiogram import Router, F
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiogram.types import Message
import aiohttp
import os


load_dotenv()
router = Router(name=__name__)
API_KEY = os.getenv('API_KEY')
url = 'https://api.openweathermap.org/data/2.5/weather'


@router.message(CommandStart())
async def cmd(mes: Message):
    await mes.answer('Добро пожаловать этот бот выводит погоду в вашем городе')


@router.message(F.text)
async def your_waether(mes: Message):
    city = mes.text
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                temp = data['main']['temp']
                feels = data['main']['feels_like']
                desc = data['weather'][0]['description']
                name = data['name']
                await mes.answer(f'🌤️ Погода в {name}: {desc} \n'
                                f'🌡️ Температура: {temp}°C (ощущается как {feels}°C)')
    except KeyError:
        await mes.answer(f'Города {city} не существует, проверте верно ли написано название города')

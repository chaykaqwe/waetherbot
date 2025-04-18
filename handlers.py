from aiogram import Router, F
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import aiohttp
import os
from datetime import datetime
import asyncio

import keyboard as kb
from database.reqiest import giv_newletters, commit_user
from bot import bot


class City(StatesGroup):
    your_city = State()        # Состояние ожидания имени


class Newsletter(StatesGroup):
    your_city = State()
    time = State()


load_dotenv()
router = Router(name=__name__)
API_KEY = os.getenv('API_KEY')
url = 'https://api.openweathermap.org/data/2.5/weather'
tasks = {}

@router.message(CommandStart())
async def cmd(mes: Message):
    await mes.answer('Добро пожаловать этот бот выводит погоду в вашем городе, также можно получать погоду каждый день!', reply_markup=kb.main)


@router.message(F.text == 'Узнать погоду')
async def your_waether_now1(mes: Message, state: FSMContext):
    await state.set_state(City.your_city)
    await mes.answer('Напишите город, в котором вы хотите узнать погоду')


@router.message(City.your_city)
async def your_weather_now2(mes: Message, state: FSMContext):
    city = mes.text
    await mes.answer(await your_waether(city), reply_markup=kb.main)
    await state.clear()


async def your_waether(city: str):
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
                return (f'🌤️ Погода в {name}: {desc} \n'
                                f'🌡️ Температура: {temp}°C (ощущается как {feels}°C)')
    except KeyError:
        return (f'Города {city} не существует, провертье верно ли написано название города')


@router.message(F.text == 'Создать рассылку')
async def create_newsletter(mes: Message, state: FSMContext):
    await state.set_state(Newsletter.your_city)
    await mes.answer('Напишите название города, в которм хотите узнавать погоду')


@router.message(Newsletter.your_city)
async def create_newsletter2(mes: Message, state: FSMContext):
    await state.update_data(your_city=mes.text)
    await state.set_state(Newsletter.time)
    await mes.answer('Напишите время когда хотите получать сообщения (13:00, 8:45 и т.д')


@router.message(Newsletter.time)
async def create_newletter3(mes: Message, state: FSMContext):
    try:
        hour, minute = map(int, mes.text.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
        await state.update_data(time=f"{hour:02}:{minute:02}")
        data = await state.get_data()
        await mes.answer(f"✅ Рассылка создана!\nГород: {data['your_city']}\nВремя: {data['time']}")
        await state.update_data(newletter_user=True)
        await commit_user(data, mes.from_user.id)
        task = asyncio.create_task(newletter(tg_id=mes.from_user.id))
        tasks[mes.from_user.id] = task
        await state.clear()
    except ValueError:
        await mes.answer("Неверный формат времени. Используй HH:MM")


async def newletter(tg_id):
    newlett = await giv_newletters(tg_id)
    while True:
        now = datetime.now().time()
        h, m = map(int, newlett.time.split(":"))
        target_time = datetime.strptime(newlett.time, "%H:%M").time()
        if now.hour == target_time.hour and now.minute == target_time.minute:
            weather_text = await your_waether(newlett.city)
            await bot.send_message(chat_id=tg_id, text=weather_text)
            await asyncio.sleep(10)  # чтобы не отправлять сообщение каждую секунду
        await asyncio.sleep(1)


@router.message(F.text == 'Удалить рассылку')
async def delete_newletter(mes: Message):
    task = tasks.get(mes.from_user.id)
    task.cancel()
    del tasks[mes.from_user.id]
    await mes.answer("❌ Рассылка удалена")


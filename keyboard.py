from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Узнать погоду'), KeyboardButton(text='Создать рассылку')],
                                        [KeyboardButton(text='Удалить рассылку'), KeyboardButton(text='Помощь')]
                                        ], resize_keyboard=True)
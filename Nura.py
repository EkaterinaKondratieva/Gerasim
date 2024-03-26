from telebot import types

from main import bot


def nura_start(message):
    mupcup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Помидоры', callback_data='tomatoes')
    btn2 = types.InlineKeyboardButton('Огурцы', callback_data='cucumbers')
    btn3 = types.InlineKeyboardButton('Перцы', callback_data='peppers')
    btn4 = types.InlineKeyboardButton('Кабачки', callback_data='zucchini')
    btn5 = types.InlineKeyboardButton('Морковь', callback_data='carrot')
    btn6 = types.InlineKeyboardButton('Клубника', callback_data='strawberry')
    btn7 = types.InlineKeyboardButton('Назад', callback_data='return')
    mupcup.row(btn1, btn2)
    mupcup.row(btn3, btn4)
    mupcup.row(btn5, btn6)
    mupcup.row(btn7)
    bot.send_message(message.chat.id, 'Привет, внучок! \n'
                                      'Меня зовут Баба Нюра и я знаю все о помидорках и клубнике!\n'
                                      'Если тебе нужна моя помощь, то просто выбирай нужную культуру',
                     reply_markup=mupcup)

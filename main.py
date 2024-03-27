import sqlite3

import telebot
from telebot import types

bot = telebot.TeleBot('7190036484:AAG1KC_QhMtZLDPopV3gW6ELKpvFlhrcvGo')
about_user = []


@bot.message_handler(commands=['start'])
def start(message):
    murcup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    murcup.add(types.KeyboardButton('Зарегистрироваться'))
    murcup.add(types.KeyboardButton('Войти'))
    bot.send_message(message.chat.id, 'Чтобы воспользоваться помощью Герасима нужно зарегистрироваться или войти',
                     reply_markup=murcup)


@bot.message_handler(content_types=['text'])
def form(message):
    if message.text == 'Зарегистрироваться':
        bot.send_message(message.chat.id, 'Введите логин')
        bot.register_next_step_handler(message, user_name)


def user_name(message):
    login = message.text
    con = sqlite3.connect('bd.sql')
    cur = con.cursor()
    users = [elem[0] for elem in cur.execute('''SELECT login FROM Users''').fetchall()]
    if login not in users:
        about_user.append(login)
        bot.send_message(message.chat.id, f'Введите пароль')
        bot.register_next_step_handler(message, user_password)
    else:
        bot.send_message(message.chat.id, f'К сожалению, такой пользователь уже есть(\nПридумайте другой логин')
        bot.register_next_step_handler(message, user_name)


def user_password(message):
    password = message.text
    con = sqlite3.connect('bd.sql')
    cur = con.cursor()
    cur.execute('''INSERT INTO Users (login, password, points) VALUES (?, ?, ?)''', (about_user[0], password, 0))
    con.commit()
    murcup = types.ReplyKeyboardMarkup()
    murcup.add(types.KeyboardButton('Ура🎉'))
    bot.send_message(message.chat.id, f'Вы зарегистрированны в сети\n'
                                      f'Теперь Герасим готов вам помочь!', reply_markup=murcup)
    bot.register_next_step_handler(message, help_g)


def help_g(message):
    marcup = types.ReplyKeyboardMarkup()
    marcup.add(types.KeyboardButton('В гостях у Бабы Нюры'))
    marcup.add(types.KeyboardButton('В шашлычной у Ашота'))
    marcup.add(types.KeyboardButton('Игры на выживание'))
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}! Видишь кнопки снизу?\nДавай объясню, о чём эти разделы: '
                     f'\n🌸 «В гостях у Бабы Нюры» - советы о посадках самых популярных культур '
                     f'\n🥩 «В шашлычной у Ашота» - викторина о шашлыке для тех, кто в поиске идеального рецепта '
                     f'\n⚽️ «Игры на выживание» - идеи для отдыха: как занять всю компанию и не заскучать',
                     parse_mode='html', reply_markup=marcup)
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    if message.text == 'В гостях у Бабы Нюры':
        start_nura(message)
    elif message.text == 'В шашлычной у Ашота':
        pass
    elif message.text == 'Игры на выживание':
        pass


def start_nura(message):
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


bot.polling(none_stop=True)

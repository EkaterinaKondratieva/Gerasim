import json
import sqlite3
import telebot
from telebot import types
import pymorphy2
import requests

bot = telebot.TeleBot('7190036484:AAG1KC_QhMtZLDPopV3gW6ELKpvFlhrcvGo')
morph = pymorphy2.MorphAnalyzer()
about_user = []
about_seed = []
SEEDS = {'tomatoes': 'Помидоры',
         'cucumbers': "Огурцы",
         'peppers': "Болгарские перцы",
         'zucchini': "Кабачки",
         'carrot': "Морковь",
         'strawberry': "Клубника"
         }
BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast?'
API_KEY = 'a7cd0d9a75754013bea6553cc27adc54'


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
    elif message.text == 'Войти' or message.text == 'Попробовать еще раз':
        bot.send_message(message.chat.id, 'Введите логин')
        bot.register_next_step_handler(message, check_name)


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


def check_name(message):
    global about_user
    login = message.text
    about_user.append(login)
    con = sqlite3.connect('bd.sql')
    cur = con.cursor()
    users = [elem[0] for elem in cur.execute('''SELECT login FROM Users''').fetchall()]
    if login in users:
        bot.send_message(message.chat.id, 'Введите пароль')
        bot.register_next_step_handler(message, check_password)
    else:
        mupcup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Зарегистрироваться', callback_data='login')
        btn2 = types.InlineKeyboardButton('Попробовать еще раз', callback_data='repeat')
        mupcup.row(btn1, btn2)
        about_user = []
        bot.send_message(message.chat.id,
                         "Такого пользователя нет\nЗарегистрируйтесь в сиситеме или введите логин еще раз",
                         reply_markup=mupcup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global about_seed
    if callback.data == 'login':
        bot.send_message(callback.message.chat.id, 'Введите логин')
        bot.register_next_step_handler(callback.message, user_name)
    elif callback.data == 'repeat':
        bot.send_message(callback.message.chat.id, 'Введите логин')
        bot.register_next_step_handler(callback.message, check_name)
    elif callback.data == 'return':
        marcup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        marcup.add(types.KeyboardButton('В гостях у Бабы Нюры'))
        marcup.add(types.KeyboardButton('В шашлычной у Ашота'))
        marcup.add(types.KeyboardButton('Игры на выживание'))
        bot.send_message(callback.message.chat.id, 'С возвразщением', reply_markup=marcup)
        bot.register_next_step_handler(callback.message, on_click)
    else:
        con = sqlite3.connect('bd.sql')
        cur = con.cursor()
        sort_of_seed = SEEDS[callback.data]
        about_seed_temp = cur.execute('''SELECT Information FROM Seeds WHERE Name = ?''', (sort_of_seed,)).fetchone()[
            0].split('-')
        best_temp = [int(about_seed_temp[0]), int(about_seed_temp[-1])]
        # СПРОСИТЬ ПОЧЕМУ ЗАДВАИВАЮТСЯ СООБЩЕНИЯ, ЕСЛИ МЕНЯТЬ ВЫБОР НЕ ДОЖИДАЯСЬ ОТВЕТА
        about_seed = []
        about_seed.append(callback.data)
        about_seed.append(sort_of_seed)
        about_seed.append(best_temp)

        marcup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        marcup.add(types.KeyboardButton("Отправить местоположение📍", request_location=True))
        marcup.add(types.KeyboardButton('Посмотреть советы'))

        bot.send_message(callback.message.chat.id,
                         'Дружок, чтобы моя помощь была максимальной, мне нужно узнать твою геолокацию',
                         reply_markup=marcup)
        bot.register_next_step_handler(callback.message, help_nura)


def check_password(message):
    password = message.text
    con = sqlite3.connect('bd.sql')
    cur = con.cursor()
    info = {}
    users = [(elem[1], elem[2]) for elem in cur.execute('''SELECT * FROM Users''').fetchall()]
    for elem in users:
        info[elem[0]] = elem[1]
    if info[about_user[0]] == password:
        murcup = types.ReplyKeyboardMarkup()
        murcup.add(types.KeyboardButton('Ура🎉'))
        bot.send_message(message.chat.id, f'Мы нашли вас в системе\nГерасим готов вам помочь', reply_markup=murcup)
        bot.register_next_step_handler(message, help_g)
    else:
        bot.send_message(message.chat.id, f'Попробуйте ввести свой пароль еще раз')
        bot.register_next_step_handler(message, check_password)


def help_g(message):
    marcup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
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
        bot.send_message(message.chat.id, 'Вай')
    elif message.text == 'Игры на выживание':
        pass


def start_nura(message):
    mupcup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Помидоры🍅', callback_data='tomatoes')
    btn2 = types.InlineKeyboardButton('Огурцы🥒', callback_data='cucumbers')
    btn3 = types.InlineKeyboardButton('Перцы🫑', callback_data='peppers')
    btn4 = types.InlineKeyboardButton('Кабачки🤮', callback_data='zucchini')
    btn5 = types.InlineKeyboardButton('Морковь🥕', callback_data='carrot')
    btn6 = types.InlineKeyboardButton('Клубника🍓', callback_data='strawberry')
    btn7 = types.InlineKeyboardButton('Назад', callback_data='return')
    mupcup.row(btn1, btn2)
    mupcup.row(btn3, btn4)
    mupcup.row(btn5, btn6)
    mupcup.add(btn7)
    bot.send_message(message.chat.id, 'Привет, внучок! \n'
                                      'Меня зовут Баба Нюра и я знаю все о помидорках и клубнике!\n'
                                      'Если тебе нужна моя помощь, то просто выбирай нужную культуру',
                     reply_markup=mupcup)


def help_nura(message):
    if message.text == 'Посмотреть советы':
        bot.send_photo(message.chat.id, photo=open(f'vegetables/{about_seed[0]}.jpeg', 'rb'))
    else:
        lat = message.location.latitude
        lon = message.location.longitude
        url = BASE_URL + 'lat=' + str(lat) + '&lon=' + str(lon) + '&appid=' + API_KEY + '&units=metric' + '&cnt=5'
        response = requests.get(url).json()
        now_temp = 0
        ok = True
        for i in range(5):
            if response['list'][i]['main']['temp'] > 15:
                now_temp += response['list'][i]['main']['temp']
            else:
                ok = False
                break
        seed = morph.parse(about_seed[1].lower())[0].inflect({"accs"}).word
        if ok:
            now_temp /= 5
            if about_seed[-1][0] <= now_temp <= about_seed[-1][-1]:
                bot.send_message(message.chat.id,
                                 f'{now_temp} - хорошая погода, чтобы посадить {seed}')
            else:
                bot.send_message(message.chat.id, f'Нужно подождать, чтобы посадить {seed}')
        else:
            bot.send_message(message.chat.id, f'Нужно подождать, чтобы посадить {seed}')
        bot.send_message(message.chat.id, 'Вот несколько рекомендаций для посадки')
        bot.send_photo(message.chat.id, photo=open(f'vegetables/{about_seed[0]}.jpeg', 'rb'))


bot.polling(none_stop=True)

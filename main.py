import json
import sqlite3
import telebot
from telebot import types
import pymorphy2
import requests
from seeds import SEEDS

bot = telebot.TeleBot('7190036484:AAG1KC_QhMtZLDPopV3gW6ELKpvFlhrcvGo')
morph = pymorphy2.MorphAnalyzer()
about_user = []
about_seed = []
BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast?'
API_KEY = 'a7cd0d9a75754013bea6553cc27adc54'


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_photo(message.chat.id, photo=open(f'gerasim.jpeg', 'rb'))
    # bot.send_message(message.chat.id, 'ХАЙ ЮЗЕР ВЫБИРАЙ РАЗДЕЛ')
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


@bot.message_handler(content_types=['text'])
def on_click(message):
    if message.text.lower() == 'в гостях у бабы нюры':
        start_nura(message)
    elif message.text.lower() == 'в шашлычной у ашота':
        greeting(message)
    elif message.text.lower() == 'игры на выживание':
        games(message)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global about_seed
    if callback.data == 'return':
        marcup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        marcup.add(types.KeyboardButton('В гостях у Бабы Нюры'))
        marcup.add(types.KeyboardButton('В шашлычной у Ашота'))
        marcup.add(types.KeyboardButton('Игры на выживание'))
        bot.send_message(callback.message.chat.id, 'С возвразщением', reply_markup=marcup)
        bot.register_next_step_handler(callback.message, on_click)
    if callback.data == 'return_to_list':
        only_buttons(callback.message)
    elif callback.data in ['tomatoes', 'cucumbers', 'peppers', 'zucchini', 'carrot', 'strawberry']:
        bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)
        con = sqlite3.connect('bd.sql')
        cur = con.cursor()
        sort_of_seed = SEEDS[callback.data][0]
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
        marcup.add(types.KeyboardButton('Вернуться к списку'))
        bot.send_message(callback.message.chat.id,
                         'Дружок, чтобы моя помощь была максимальной, мне нужно узнать твою геолокацию',
                         reply_markup=marcup)

        bot.register_next_step_handler(callback.message, help_nura)


def create_buttuns():
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
    return mupcup


def only_buttons(message):
    bot.send_message(message.chat.id, 'А вот и список',
                     reply_markup=create_buttuns())


@bot.message_handler(commands=['nura'])
def start_nura(message):
    bot.send_animation(message.chat.id, open('video/ogorod.mp4', 'rb'))
    bot.send_message(message.chat.id, 'Привет, внучок! \n'
                                      'Меня зовут Баба Нюра и я знаю все о помидорках и клубнике!\n'
                                      'Если тебе нужна моя помощь, то просто выбирай нужную культуру',
                     reply_markup=create_buttuns())


def help_nura(message):
    if message.text == 'Посмотреть советы':
        bot.send_photo(message.chat.id, photo=open(f'vegetables/{about_seed[0]}.jpeg', 'rb'))
        mupcup = types.InlineKeyboardMarkup()
        for i in range(len(SEEDS[about_seed[0]][1])):
            mupcup.add(
                types.InlineKeyboardButton(f'{SEEDS[about_seed[0]][1][i][0]}', url=SEEDS[about_seed[0]][1][i][1]))
        mupcup.add(types.InlineKeyboardButton('Назад', callback_data='return'))
        mupcup.add(types.InlineKeyboardButton('Вернуться к списку', callback_data='return_to_list'))
        bot.send_message(message.chat.id, 'А это мои лучшие семена)', reply_markup=mupcup)
    elif message.text == 'Вернуться к списку':
        only_buttons(message)

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
                bot.send_message(message.chat.id, f'Средняя температура на неделе - {now_temp}, недостаточно тепло.'
                                                  f'Нужно подождать, чтобы посадить {seed}')
        else:
            bot.send_message(message.chat.id, f'На неделе ожидается низкая температура,'
                                              f' нужно подождать, чтобы посадить {seed}')
        bot.send_message(message.chat.id, 'Вот несколько рекомендаций для посадки:')
        bot.send_photo(message.chat.id, photo=open(f'vegetables/{about_seed[0]}.jpeg', 'rb'))
        mupcup = types.InlineKeyboardMarkup()
        for i in range(len(SEEDS[about_seed[0]][1])):
            mupcup.add(
                types.InlineKeyboardButton(f'{SEEDS[about_seed[0]][1][i][0]}', url=SEEDS[about_seed[0]][1][i][1]))
        mupcup.add(types.InlineKeyboardButton('Назад', callback_data='return'))
        mupcup.add(types.InlineKeyboardButton('Вернуться к списку', callback_data='return_to_list'))
        bot.send_message(message.chat.id, 'А это мои лучшие семена)', reply_markup=mupcup)


##ASHOT
@bot.message_handler(commands=['ashot'])
def greeting(message):
    mupcup = types.InlineKeyboardMarkup()
    mupcup.add(types.InlineKeyboardButton('Назад', callback_data='return'))
    bot.send_animation(message.chat.id, open('video/meat.mp4', 'rb'))
    bot.send_message(message.chat.id, 'Вай, кого я вижу! \n'
                                      'Мой сладкий пирожок захотел познать искусство'
                                      ' приготовления идеального шашлыка? Давай посмотрим, сможешь ли ты создать такой'
                                      ' шедевр, поедая который гости не заметят, что съели собственные усы 🤌',
                     reply_markup=mupcup)


@bot.message_handler(commands=['games'])
def games(message):
    mupcup = types.InlineKeyboardMarkup()
    mupcup.add(types.InlineKeyboardButton('Назад', callback_data='return'))
    bot.send_animation(message.chat.id, open('video/game.mp4', 'rb'), reply_markup=mupcup)


bot.polling(none_stop=True)

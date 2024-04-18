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


@bot.message_handler(content_types=['text'])
def on_click(message):
    if message.text.lower() == 'в гостях у бабы нюры':
        start_nura(message)
    elif message.text.lower() == 'в шашлычной у ашота':
        greeting(message)
    elif message.text.lower() == 'игры на выживание':
        games(message)
    elif message.text.lower() == 'к начальному меню':
        menu(message)


def menu(message):
    marcup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    marcup.add(types.KeyboardButton('В гостях у Бабы Нюры'))
    marcup.add(types.KeyboardButton('В шашлычной у Ашота'))
    marcup.add(types.KeyboardButton('Игры на выживание'))
    bot.send_message(message.chat.id, 'С возвразщением', reply_markup=marcup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global about_seed
    global k
    bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)
    if callback.data == 'return':
        marcup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        marcup.add(types.KeyboardButton('В гостях у Бабы Нюры'))
        marcup.add(types.KeyboardButton('В шашлычной у Ашота'))
        marcup.add(types.KeyboardButton('Игры на выживание'))
        bot.send_message(callback.message.chat.id, 'С возвращением', reply_markup=marcup)
        bot.register_next_step_handler(callback.message, on_click)
    elif callback.data == 'return_to_list':
        only_buttons(callback.message)
    elif callback.data in ['tomatoes', 'cucumbers', 'peppers', 'zucchini', 'carrot', 'strawberry']:
        con = sqlite3.connect('bd.sql')
        cur = con.cursor()
        sort_of_seed = SEEDS[callback.data][0]
        about_seed_temp = cur.execute('''SELECT Information FROM Seeds WHERE Name = ?''', (sort_of_seed,)).fetchone()[
            0].split('-')
        best_temp = [int(about_seed_temp[0]), int(about_seed_temp[-1])]
        about_seed = []
        about_seed.append(callback.data)
        about_seed.append(sort_of_seed)
        about_seed.append(best_temp)
        marcup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        marcup.row(types.KeyboardButton("Отправить местоположение📍", request_location=True),
                   types.KeyboardButton('Посмотреть советы'))
        marcup.row(types.KeyboardButton('Вернуться к списку'), types.KeyboardButton('К начальному меню'))
        bot.send_message(callback.message.chat.id,
                         'Дружок, чтобы моя помощь была максимальной, мне нужно узнать твою геолокацию',
                         reply_markup=marcup)
        bot.register_next_step_handler(callback.message, help_nura)
    elif callback.data == 'return_to_games':
        bot.send_message(callback.message.chat.id, 'С возвращением', reply_markup=create_buttons_for_game())
    elif callback.data == 'two' or callback.data == 'three and more' or callback.data == 'big company':
        if callback.data == 'two':
            n = 2
        elif callback.data == 'three and more':
            n = 3
        elif callback.data == 'big company':
            n = 7
        marcup = types.InlineKeyboardMarkup()
        marcup.add(types.InlineKeyboardButton('К начальному меню', callback_data='return'))
        marcup.add(types.InlineKeyboardButton('Вернуться за помощью', callback_data='return_to_games'))
        con = sqlite3.connect('bd.sql')
        cur = con.cursor()
        games_in_bd = cur.execute('''SELECT Game FROM Games WHERE number_of_people = ?''', (n,)).fetchall()
        text = 'Вот в такие игры вы можете поиграть:'
        if n == 2:
            emoji = '⚽'
        elif n == 3:
            emoji = '🏀'
        elif n == 7:
            emoji = '🏐'
        for i in range(len(games_in_bd)):
            text += f'\n{emoji} {games_in_bd[i][0]}'
        bot.send_message(callback.message.chat.id, text, reply_markup=marcup)
    elif callback.data == 'lets go':
        k = 0
        bot.send_message(callback.message.chat.id, '', reply_markup=shashlik(callback.message, k))
    elif callback.data == 'return no message':
        bot.send_message(callback.message.chat.id, '', reply_markup=shashlik(callback.message, k))
    elif callback.data == 'forward':
        k += 1
        bot.send_message(callback.message.chat.id, '', reply_markup=shashlik(callback.message, k))


def create_buttons_for_game():
    mupcup = types.InlineKeyboardMarkup()
    mupcup.add(types.InlineKeyboardButton('2 человека', callback_data='two'))
    mupcup.add(types.InlineKeyboardButton('3-6 человек', callback_data='three and more'))
    mupcup.add(types.InlineKeyboardButton('Большая компания', callback_data='big company'))
    mupcup.add(types.InlineKeyboardButton('К начальному меню', callback_data='return'))
    return mupcup


def create_buttons_for_nura():
    mupcup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Помидоры🍅', callback_data='tomatoes')
    btn2 = types.InlineKeyboardButton('Огурцы🥒', callback_data='cucumbers')
    btn3 = types.InlineKeyboardButton('Перцы🫑', callback_data='peppers')
    btn4 = types.InlineKeyboardButton('Кабачки🤮', callback_data='zucchini')
    btn5 = types.InlineKeyboardButton('Морковь🥕', callback_data='carrot')
    btn6 = types.InlineKeyboardButton('Клубника🍓', callback_data='strawberry')
    btn7 = types.InlineKeyboardButton('К начальному меню', callback_data='return')
    mupcup.row(btn1, btn2)
    mupcup.row(btn3, btn4)
    mupcup.row(btn5, btn6)
    mupcup.add(btn7)
    return mupcup


def only_buttons(message):
    bot.send_message(message.chat.id, 'А вот и список', reply_markup=create_buttons_for_nura())


def answer(message):
    bot.send_message(message.chat.id, 'Вот несколько рекомендаций для посадки:')
    bot.send_photo(message.chat.id, photo=open(f'vegetables/{about_seed[0]}.jpeg', 'rb'))
    mupcup = types.InlineKeyboardMarkup()
    for i in range(len(SEEDS[about_seed[0]][1])):
        mupcup.add(
            types.InlineKeyboardButton(f'{SEEDS[about_seed[0]][1][i][0]}', url=SEEDS[about_seed[0]][1][i][1]))
    mupcup.add(types.InlineKeyboardButton('К начальному меню', callback_data='return'))
    mupcup.add(types.InlineKeyboardButton('Вернуться к списку', callback_data='return_to_list'))
    bot.send_message(message.chat.id, 'А это мои лучшие семена)', reply_markup=mupcup)


def start_nura(message):
    bot.send_animation(message.chat.id, open('video/ogorod.mp4', 'rb'), reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, 'Привет, внучок! \n'
                                      'Меня зовут Баба Нюра и я знаю все о помидорках и клубнике!\n'
                                      'Если тебе нужна моя помощь, то просто выбирай нужную культуру',
                     reply_markup=create_buttons_for_nura())


def help_nura(message):
    if message.text == 'Посмотреть советы':
        answer(message)
    elif message.text == 'Вернуться к списку':
        only_buttons(message)
    elif message.text == 'К начальному меню':
        menu(message)
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
                                 f'<b>{now_temp} - хорошая погода, чтобы посадить {seed}</b>', parse_mode='html')
            else:
                bot.send_message(message.chat.id, f'<b>Средняя температура на неделе - {now_temp}, недостаточно тепло.'
                                                  f'Нужно подождать, чтобы посадить {seed}</b>', parse_mode='html')
        else:
            bot.send_message(message.chat.id, f'<b>На неделе ожидается низкая температура,'
                                              f' нужно подождать, чтобы посадить {seed}</b>', parse_mode='html')
        answer(message)


##ASHOT
@bot.message_handler(commands=['ashot'])
def greeting(message):
    mupcup = types.InlineKeyboardMarkup()
    mupcup.add(types.InlineKeyboardButton('Поехали', callback_data='lets go'))
    mupcup.add(types.InlineKeyboardButton('К начальному меню', callback_data='return'))
    bot.send_animation(message.chat.id, open('video/meat.mp4', 'rb'), reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, 'Вай, кого я вижу! \n'
                                      'Мой сладкий пирожок захотел познать искусство'
                                      ' приготовления идеального шашлыка? Давай посмотрим, сможешь ли ты создать такой'
                                      ' шедевр, поедая который гости не заметят, что съели собственные усы)',
                     reply_markup=mupcup)


def shashlik(message, k):
    mupcup = types.InlineKeyboardMarkup()
    mupcup.add(types.InlineKeyboardButton('Конечно, Ашотик', callback_data='forward'))
    mupcup.add(types.InlineKeyboardButton('К начальному меню', callback_data='return no message'))
    if k == 0:
        bot.send_message(message.chat.id, 'Ради таких смелых людей сбрил бы бороду!')
        bot.send_poll(message.chat.id, 'Начну с простого: из какого мяса традиционно делается шашлык?',
                      ['Свинина', 'Говядина', 'Курица', 'Баранина'], None, 'quiz', None, 3,
                      'Традиционный шашлык — это еда кочевников Азии. Он изготавливался из баранины,'
                      ' которая жарилась на металлических или деревянных прутьях над огнем')

        bot.send_message(message.chat.id, 'Ну что, продолжаем познавать азы готовки?', reply_markup=mupcup)
    elif k == 1:
        bot.send_poll(message.chat.id,
                      'У хорошего хозяина шашлыка хватает всегда и на всех! По сколько грамм на человека'
                      'принято покупать мяса?',
                      ['100-200 грамм', '200-300 грамм', '300-400 грамм'], None, 'quiz', None, 2,
                      'Мясо обычно берут из расчета 300-400 г на каждого горячо любимого гостя'
                      '. Больше – можно, меньше – не стоит\n'
                      'В процессе приготовления этот продукт обязательно потеряет в весе')
        bot.send_message(message.chat.id, 'Был бы ты воробьём, тебя бы звали Орёл! Идём дальше?', reply_markup=mupcup)
    elif k == 2:
        bot.send_poll(message.chat.id, 'Уточним технические моменты: '
                                       'какие шампуры лучше использовать для "шашлычного" мяса?',
                      ['Плоские', 'Угловые'], None, 'quiz', None, 0,
                      'ПЛОСКИЕ шампуры - универсальные: подойдут и для приготовления люля кебаб(он не сползет и'
                      ' будет хорошо держаться, больших кусков мяса\n'
                      'УГЛОВЫЕ подойдут для жарки грибов и небольших кусков мяса')
        bot.send_message(message.chat.id, 'Пойду покажу своей маме, какой волк проходит мой тест. Вперёд?',
                         reply_markup=mupcup)
    elif k == 3:
        bot.send_poll(message.chat.id, 'Шампуры помыты, мясо куплено. Как следует его нарезать?',
                      ['Вдоль мышечных волокон', 'Поперёк мышечных волокон'], None, 'quiz', None, 1,
                      ' Делая это поперёк волокон, а не вдоль, ты укорачиваешь их, мой золотой.'
                      ' Мясо станет мягче, его будет легко прожевать.')

        bot.send_message(message.chat.id, 'Вайя, какое рвение к победе! Заводим мою ниву и едем дальше?',
                         reply_markup=mupcup)
    elif k == 5:
        bot.send_message(message.chat.id, 'Это конец, моя маковая росинка! До встречи в моей шашлычной, пусть все твои '
                                          'шашлыки будут вкуснее, чем у соседей!')

    # GAMES


def games(message):
    mupcup = types.InlineKeyboardMarkup()
    mupcup.add(types.InlineKeyboardButton('2 человека', callback_data='two'))
    mupcup.add(types.InlineKeyboardButton('3-6 человек', callback_data='three and more'))
    mupcup.add(types.InlineKeyboardButton('Большая компания', callback_data='big company'))
    mupcup.add(types.InlineKeyboardButton('К начальному меню', callback_data='return'))
    bot.send_animation(message.chat.id, open('video/game.mp4', 'rb'), reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, 'Привет👋\n'
                                      'Этот раздел поможет тебе, если дни на даче проходят очень скучно\n'
                                      'Выбирай количество людей в компании и узнай, чем скоротать время',
                     reply_markup=mupcup)


bot.polling(none_stop=True)

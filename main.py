import telebot
from telebot import types

from Nura import nura_start

bot = telebot.TeleBot('7190036484:AAG1KC_QhMtZLDPopV3gW6ELKpvFlhrcvGo')


@bot.message_handler(commands=['start'])
def start(message):
    marcup = types.ReplyKeyboardMarkup()
    marcup.add(types.KeyboardButton('В гостях у Бабы Нюры'))
    marcup.add(types.KeyboardButton('В шашлычной у Ашота'))
    marcup.add(types.KeyboardButton('Игры на выживание'))
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}!\nО чем эти разделы: '
                     f'\n🌸 В гостях у Бабы Нюры - раздел с советами о посадках '
                     f'\n🥩 В шашлычной у Ашота - викторина о шашлыке '
                     f'\n⚽️ Игры на выживание - идеи для отдыха',
                     parse_mode='html', reply_markup=marcup)
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    if message.text == 'В гостях у Бабы Нюры':
        nura_start(message)
    elif message.text == 'В шашлычной у Ашота':
        pass
    elif message.text == 'Игры на выживание':
        pass


bot.polling(none_stop=True)

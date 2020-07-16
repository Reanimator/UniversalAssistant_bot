__author__ = 'Агеев Михаил Михайлович'

import telebot
from telebot import *
import datetime
from time import time, sleep
import MySQLdb


def lang():
    """translation base/база языков"""
    if lang_index == 1:
        menu = [
            'Заметки',
            'Список покупок',
            'Выбор языка/Select language/Sprachauswahl',
            'Выберете действие:',
            'Готово',
            'Добрый день!',
            'Для продолжения введите любой символ']
    elif lang_index == 2:
        menu = [
            'Notes',
            'Shopping list',
            'Выбор языка/Select language/Sprachauswahl',
            'Choose action:',
            'Done',
            'Good day!',
            'Enter any character to continue.']
    elif lang_index == 3:
        menu = [
            'Notizen',
            'Einkaufsliste',
            'Выбор языка/Select language/Sprachauswahl',
            'Aktion auswählen',
            'Fertig',
            'Guten Tag!',
            'Geben Sie ein beliebiges Zeichen ein, um fortzufahren.']
    return menu


def sleep_timer(x):
    """deferral of execution/отсрочка выполнения"""
    start = time()
    sleep((time() - start) + x)


def lang_mess(menu):
    """language selection/выбор языка"""
    global delete_mess
    delete_mess = bot.send_message(menu.message.chat.id, lang()[4]).message_id
    sleep_timer(2)
    mess_delete(2)
    bot.send_message(menu.message.chat.id, lang()[6])


def mess_delete(x):
    """delete recent posts/удаление последних сообщений"""
    global delete_mess
    i = 0
    while i < x:
        bot.delete_message(delete_chat, delete_mess)
        delete_mess -= 1
        i += 1


bot = telebot.TeleBot('1196186813:AAHNbYTl50KD2zdeT98gLW3e8Na20N4K3tk')
lang_index = 1
delete_mess = 0
delete_chat = 0
start_index = 0
add_index = 0


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    """input processing/обработка ввода"""
    global user_id
    global delete_chat
    global delete_mess
    global start_index
    global add_index

    log = open('log.txt', 'a', encoding='utf8')
    log.write(str(datetime.datetime.today()) + ' --- ' +
              message.text + ' --- ' + str(message.from_user.id) + '\n')
    log.close()
    user_id = message.from_user.id
    print(user_id)
    if add_index == 1:
        conn = MySQLdb.connect(
            'localhost',
            'root',
            'mike159753',
            'universalassistant')
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO notes(user, note) VALUES (%d, %r)""" %
            (user_id, message.text))
        conn.commit()
        conn.close()
        bot.send_message(user_id, text='Заметка добавлена').chat.id
        add_index = 0
    if start_index == 0:
        # !!!Добавить в перевод
        bot.send_message(user_id, text='Для начала введите start').chat.id
    elif start_index == 1:
        start_index = 0
    if message.text == 'start':
        start_index = 1
        keyboard = types.InlineKeyboardMarkup()
        key_notes = types.InlineKeyboardButton(
            text=lang()[0], callback_data='notes')
        key_shop_list = types.InlineKeyboardButton(
            text=lang()[1], callback_data='shop_list')
        key_select_lang = types.InlineKeyboardButton(
            text=lang()[2], callback_data='select_lang')
        keyboard.add(key_notes, key_shop_list)
        keyboard.add(key_select_lang)

        delete_chat = bot.send_message(
            message.from_user.id, text=lang()[5]).chat.id
        delete_mess = bot.send_message(
            message.from_user.id,
            text=lang()[3],
            reply_markup=keyboard).message_id


@bot.callback_query_handler(func=lambda menu: True)
def inline(menu):
    """click processing/обработка нажатий"""
    global lang_index
    global add_index
    global mass_notes

    if menu.data == 'notes':
        mess_delete(2)
        bot.send_message(menu.message.chat.id, 'Ваш список заметок:')

        conn = MySQLdb.connect(
            'localhost',
            'root',
            'mike159753',
            'universalassistant')
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, note FROM notes WHERE user = '%d'""" %
            user_id)
        rows = cursor.fetchall()
        mass_notes = {}
        j = 1
        for i in range(len(rows)):
            bot.send_message(
                menu.message.chat.id, ('%d -- %s' %
                                       (j, rows[i][1])))  # rows[i][0]
            mass_notes[rows[i][0]] = rows[i][1]
            j += 1
        conn.close()

        key = types.InlineKeyboardMarkup()
        key_add = types.InlineKeyboardButton(
            text="Добавить заметку", callback_data="add")
        key_del = types.InlineKeyboardButton(
            text="Удалить заметку", callback_data="del")
        key_del_all = types.InlineKeyboardButton(
            text="Удалить все заметки", callback_data="del_all")
        key.add(key_add)
        key.add(key_del)
        key.add(key_del_all)
        bot.send_message(
            menu.message.chat.id,
            'Что вы хотите сделать?',
            reply_markup=key)

    if menu.data == 'shop_list':
        mess_delete(2)
        bot.send_message(menu.message.chat.id, 'Это кнопка 2')
        bot.send_message(menu.message.chat.id, lang()[6])
    if menu.data == 'select_lang':
        mess_delete(2)
        key = types.InlineKeyboardMarkup()
        key_rus = types.InlineKeyboardButton(
            text="Русский", callback_data="rus")
        key_eng = types.InlineKeyboardButton(
            text="English", callback_data="eng")
        key_deut = types.InlineKeyboardButton(
            text="Deutsch", callback_data="deut")
        key.add(key_rus, key_eng, key_deut)
        bot.send_message(
            menu.message.chat.id,
            'Язык / Language / Sprache',
            reply_markup=key)
    if menu.data == 'rus':
        lang_index = 1
        lang_mess(menu)
    if menu.data == 'eng':
        lang_index = 2
        lang_mess(menu)
    if menu.data == 'deut':
        lang_index = 3
        lang_mess(menu)
    if menu.data == 'add':
        add_index = 1
        bot.send_message(menu.message.chat.id, 'Введите заметку')
    if menu.data == 'del':
        key = types.InlineKeyboardMarkup()
        j = 1
        for i in mass_notes:
            temp_key = types.InlineKeyboardButton(
                text='%d -- %s' %
                (j, mass_notes[i]), callback_data='del_file%i' %
                i)
            key.add(temp_key)
            j += 1
        bot.send_message(
            menu.message.chat.id,
            'Какую запись удалить?',
            reply_markup=key)
    if menu.data == 'del_all':
        conn = MySQLdb.connect(
            'localhost',
            'root',
            'mike159753',
            'universalassistant')
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM notes WHERE user = '%d'""" % user_id)
        conn.commit()
        conn.close()
        bot.send_message(menu.message.chat.id, 'Все заметки удалены')
        # bot.send_message(menu.message.chat.id, 'Заглушка')
    if mass_notes != {}:
        for i in mass_notes:
            if menu.data == 'del_file%i' % i:
                conn = MySQLdb.connect(
                    'localhost', 'root', 'mike159753', 'universalassistant')
                cursor = conn.cursor()
                cursor.execute("""DELETE FROM notes WHERE id = '%d'""" % i)
                conn.commit()
                conn.close()
                bot.send_message(menu.message.chat.id, 'Заметка удалена')
                print(i)
                print(menu.data)


bot.polling(none_stop=True, interval=0)

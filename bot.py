__author__ = 'Агеев Михаил Михайлович'

import telebot
from telebot import *
import datetime
from time import time, sleep
import MySQLdb


def lang():  # Передавать lang_index чтобы избавиться от глобальной переменной ????
    """
    language base/база языков
    :return: menu - словарь фраз
    """
    """translation base/база языков"""
    if lang_index == 1:
        menu = [
            'Заметки',  # 0
            'Список покупок',
            'Выбор языка/Select language/Sprachauswahl',
            'Выберете действие:',
            'Готово',
            'Добрый день!',  # 5
            'Для продолжения введите любой символ',
            'Заметка добавлена',
            'Для начала введите start',
            'Ваш список заметок:',
            'Добавить заметку',  # 10
            'Удалить заметку',
            'Удалить все заметки',
            'Что вы хотите сделать?',
            'Введите заметку',
            'Какую запись удалить?',  # 15
            'Все заметки удалены'
            'Заметка удалена']
    elif lang_index == 2:
        menu = [
            'Notes',
            'Shopping list',
            'Выбор языка/Select language/Sprachauswahl',
            'Choose action:',
            'Done',
            'Good day!',
            'Enter any character to continue.',
            'Note added',
            'First enter start',
            'Your list of notes:',
            'Add note',
            'Delete note',
            'Delete all notes',
            'What do you want to do?',
            'Enter note',
            'Which entry to delete?',
            'All notes deleted',
            'Note deleted']
    elif lang_index == 3:
        menu = [
            'Notizen',
            'Einkaufsliste',
            'Выбор языка/Select language/Sprachauswahl',
            'Aktion auswählen',
            'Fertig',
            'Guten Tag!',
            'Geben Sie ein beliebiges Zeichen ein, um fortzufahren.',
            'Hinweis hinzugefügt',
            'Zuerst Start eingeben',
            'Ihre Liste von Notizen:',
            'Notiz hinzufügen',
            'Notiz löschen',
            'Alle Notizen löschen',
            'Was möchten Sie tun?',
            'Notiz eingeben',
            'Welchen Eintrag soll gelöscht werden?',
            'Alle Notizen gelöscht',
            'Notiz gelöscht']
    return menu


def sleep_timer(x):
    """
    deferral of execution/отсрочка выполнения
    """
    start = time()
    sleep((time() - start) + x)


def lang_mess(menu):
    """
    language selection/выбор языка
    """
    global delete_mess
    delete_mess = bot.send_message(menu.message.chat.id, lang()[4]).message_id
    sleep_timer(2)
    mess_delete(2)
    bot.send_message(menu.message.chat.id, lang()[6])


def mess_delete(x):
    """
    delete recent posts/удаление последних сообщений
    """
    global delete_mess
    i = 0
    while i < x:
        bot.delete_message(delete_chat, delete_mess)
        delete_mess -= 1
        i += 1


bot = telebot.TeleBot('1196186813:AAHNbYTl50KD2zdeT98gLW3e8Na20N4K3tk')  # ключ бота
lang_index = 1  # selected language key/ключ выбранного языка
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
    if add_index == 1:  # adding a note/добавление заметки
        conn = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='mike159753',
            db='universalassistant',
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO notes(user, note) VALUES (%d, %r)""" %
            (user_id, message.text))
        conn.commit()
        conn.close()
        bot.send_message(user_id, text=lang()[7]).chat.id


        add_index = 0
    if start_index == 0:
        # !!!Добавить в перевод
        bot.send_message(user_id, text=lang()[8]).chat.id
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
    global add_index  # note adding key/ключ добавления заметки
    global mass_notes

    if menu.data == 'notes':
        mess_delete(2)
        # printing notes/печать заметок
        bot.send_message(menu.message.chat.id, lang()[9])
        conn = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='mike159753',
            db='universalassistant',
            charset='utf8')
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
        # button output/вывод кнопок
        key = types.InlineKeyboardMarkup()
        key_add = types.InlineKeyboardButton(
            text=lang()[10], callback_data="add")
        key_del = types.InlineKeyboardButton(
            text=lang()[11], callback_data="del")
        key_del_all = types.InlineKeyboardButton(
            text=lang()[12], callback_data="del_all")
        key.add(key_add)
        key.add(key_del)
        key.add(key_del_all)
        bot.send_message(
            menu.message.chat.id,
            lang()[13],
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
        bot.send_message(menu.message.chat.id, lang()[14])
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
            lang()[15],
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
        bot.send_message(menu.message.chat.id, lang()[16])
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
                bot.send_message(menu.message.chat.id, lang()[17])
                print(i)
                print(menu.data)


bot.polling(none_stop=True, interval=0)

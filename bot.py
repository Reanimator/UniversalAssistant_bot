__author__ = 'Агеев Михаил Михайлович'

import telebot
from telebot import *
import datetime
from time import time, sleep
import MySQLdb


bot = telebot.TeleBot(
    '1196186813:AAHNbYTl50KD2zdeT98gLW3e8Na20N4K3tk')  # ключ бота
lang_index = 1  # selected language key/ключ выбранного языка
delete_mess = {}
add_index = 0
mass_notes = {}
begin_message = None


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
            'Язык / Language / Sprache',
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
            'Все заметки удалены',
            'Заметка удалена',
            'Главное меню']
    elif lang_index == 2:
        menu = [
            'Notes',
            'Shopping list',
            'Язык / Language / Sprache',
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
            'Note deleted',
            'Main menu']
    elif lang_index == 3:
        menu = [
            'Notizen',
            'Einkaufsliste',
            'Язык / Language / Sprache',
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
            'Notiz gelöscht',
            'Hauptmenü']
    return menu


def mess_delete(chat_id, user_id):
    """
    delete recent posts/удаление последних сообщений
    """
    global delete_mess

    for mess in delete_mess[user_id]:
        bot.delete_message(chat_id, mess)
    delete_mess[user_id] = []


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    """input processing/обработка ввода"""
    global delete_mess
    global add_index
    global begin_message
    global begin_notes

    # Создание листа для сообщений пользователя, если он не существует
    try:
        delete_mess[message.from_user.id]
    except KeyError:
        delete_mess[message.from_user.id] = []

    log = open('log.txt', 'a', encoding='utf8')
    log.write(str(datetime.datetime.today()) + ' --- ' +
              message.text + ' --- ' + str(message.from_user.id) + '\n')
    log.close()

    if message != begin_message:
        delete_mess[message.from_user.id].append(message.message_id)

    mess_delete(message.chat.id, message.from_user.id)
    if message.text != 'start' and add_index != 1:
        delete_mess[message.from_user.id].append(
            bot.send_message(
                message.chat.id,
                lang()[8]).message_id)
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
            (message.from_user.id, message.text))
        conn.commit()
        conn.close()
        mess_delete(message.chat.id, message.from_user.id)
        add_index = 0
        inline(begin_notes)

    if message.text == 'start':

        begin_message = message
        keyboard = types.InlineKeyboardMarkup()
        key_notes = types.InlineKeyboardButton(
            text=lang()[0], callback_data='notes')
        key_shop_list = types.InlineKeyboardButton(
            text=lang()[1], callback_data='shop_list')
        key_select_lang = types.InlineKeyboardButton(
            text=lang()[2], callback_data='select_lang')
        keyboard.add(key_notes, key_shop_list)
        keyboard.add(key_select_lang)

        delete_mess[message.from_user.id].append(bot.send_message(
            message.chat.id, text=lang()[5]).message_id)
        delete_mess[message.from_user.id].append(bot.send_message(
            message.chat.id,
            text=lang()[3],
            reply_markup=keyboard).message_id)


@bot.callback_query_handler(func=lambda menu: True)
def inline(menu):
    """click processing/обработка нажатий"""
    global lang_index
    global add_index  # note adding key/ключ добавления заметки
    global mass_notes
    global delete_mess
    global begin_notes

    if menu.data == 'notes':

        mess_delete(menu.message.chat.id, menu.from_user.id)

        # printing notes/печать заметок
        begin_notes = menu
        delete_mess[menu.from_user.id].append(bot.send_message(menu.message.chat.id, lang()[9]).message_id)
        conn = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='mike159753',
            db='universalassistant',
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, note FROM notes WHERE user = '%d'""" %
            menu.from_user.id)
        rows = cursor.fetchall()
        mass_notes = {}
        j = 1
        for i in range(len(rows)):
            delete_mess[menu.from_user.id].append(bot.send_message(
                menu.message.chat.id, ('%d -- %s' %
                                       (j, rows[i][1]))).message_id)  # rows[i][0]
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
        key_main_menu = types.InlineKeyboardButton(
            text=lang()[18], callback_data="main_menu")
        key.add(key_add)
        key.add(key_del)
        key.add(key_del_all)
        key.add(key_main_menu)
        delete_mess[menu.from_user.id].append(bot.send_message(
            menu.message.chat.id,
            lang()[13],
            reply_markup=key).message_id)

    if menu.data == 'shop_list':
        mess_delete(menu.message.chat.id, menu.from_user.id)
        delete_mess[menu.from_user.id].append(bot.send_message(
            menu.message.chat.id, 'Это кнопка 2').chat.id)
        delete_mess[menu.from_user.id].append(
            bot.send_message(
                menu.message.chat.id,
                lang()[6]).message_id)
    if menu.data == 'select_lang':

        mess_delete(menu.message.chat.id, menu.from_user.id)
        key = types.InlineKeyboardMarkup()
        key_rus = types.InlineKeyboardButton(
            text="Русский", callback_data="rus")
        key_eng = types.InlineKeyboardButton(
            text="English", callback_data="eng")
        key_deut = types.InlineKeyboardButton(
            text="Deutsch", callback_data="deut")
        key.add(key_rus, key_eng, key_deut)
        delete_mess[menu.from_user.id].append(bot.send_message(
            menu.message.chat.id,
            'Язык / Language / Sprache',
            reply_markup=key).message_id)
    if menu.data == 'rus':
        lang_index = 1
        mess_delete(menu.message.chat.id, menu.from_user.id)
        get_text_messages(begin_message)
    if menu.data == 'eng':
        lang_index = 2
        mess_delete(menu.message.chat.id, menu.from_user.id)
        get_text_messages(begin_message)
    if menu.data == 'deut':
        lang_index = 3
        mess_delete(menu.message.chat.id, menu.from_user.id)
        get_text_messages(begin_message)
    if menu.data == 'add':
        add_index = 1
        mess_delete(menu.message.chat.id, menu.from_user.id)
        delete_mess[menu.from_user.id].append(
            bot.send_message(
                menu.message.chat.id,
                lang()[14]).message_id)
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
        mess_delete(menu.message.chat.id, menu.from_user.id)
        delete_mess[menu.from_user.id].append(
            bot.send_message(
                menu.message.chat.id,
                lang()[15],
                reply_markup=key).message_id)
    if menu.data == 'del_all':
        conn = MySQLdb.connect(
            'localhost',
            'root',
            'mike159753',
            'universalassistant')
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM notes WHERE user = '%d'""" % menu.from_user.id)
        conn.commit()
        conn.close()
        mess_delete(menu.message.chat.id, menu.from_user.id)
        inline(begin_notes)
    if menu.data == 'main_menu':
        get_text_messages(begin_message)
    if mass_notes != {}:
        for i in mass_notes:
            if menu.data == 'del_file%i' % i:
                conn = MySQLdb.connect(
                    'localhost', 'root', 'mike159753', 'universalassistant')
                cursor = conn.cursor()
                cursor.execute("""DELETE FROM notes WHERE id = '%d'""" % i)
                conn.commit()
                conn.close()
                mess_delete(menu.message.chat.id, menu.from_user.id)
                inline(begin_notes)


bot.polling(none_stop=True, interval=0)

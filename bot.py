__author__ = 'Агеев Михаил Михайлович'

import telebot
from telebot import *
import datetime
import MySQLdb


bot = telebot.TeleBot(
    '1196186813:AAHNbYTl50KD2zdeT98gLW3e8Na20N4K3tk')  # ключ бота
lang_index = {}  # selected language key/ключ выбранного языка
delete_mess = {}
add_index = {}
mass_notes = {}
begin_message = {}


def lang(lang_ind, chat_id):
    """
    language base/база языков
    :return: menu - словарь фраз
    """
    """translation base/база языков"""
    if lang_ind[chat_id] == 1:
        words = [
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
    elif lang_ind[chat_id] == 2:
        words = [
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
    elif lang_ind[chat_id] == 3:
        words = [
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
    return words


def mess_delete(chat_id):
    """
    delete recent posts/удаление последних сообщений
    """
    global delete_mess

    for mess in delete_mess[chat_id]:
        bot.delete_message(chat_id, mess)
    delete_mess[chat_id] = []


def begin_settings(chat_id):
    """
    Задание изначальных параметров для каждого пользователя
    :param chat_id: Номер чата
    """
    try:
        delete_mess[chat_id]
    except KeyError:
        delete_mess[chat_id] = []
    try:
        begin_message[chat_id]
    except KeyError:
        begin_message[chat_id] = None
    try:
        lang_index[chat_id]
    except KeyError:
        lang_index[chat_id] = 1
    try:
        add_index[chat_id]
    except KeyError:
        add_index[chat_id] = 0


@bot.message_handler(
    content_types=[
        "text",
        "audio",
        "document",
        "photo",
        "sticker",
        "video",
        "video_note",
        "voice",
        "location",
        "contact",
        "new_chat_members",
        "left_chat_member",
        "new_chat_title",
        "new_chat_photo",
        "delete_chat_photo",
        "group_chat_created",
        "supergroup_chat_created",
        "channel_chat_created",
        "migrate_to_chat_id",
        "migrate_from_chat_id",
        "pinned_message"])
def get_text_messages(message):
    """input processing/обработка ввода"""
    global delete_mess
    global add_index
    global begin_message
    global begin_notes

    begin_settings(message.chat.id)

    log = open('log.txt', 'a', encoding='utf8')
    try:
        log.write(str(datetime.datetime.today()) + ' --- ' +
                  message.text + ' --- ' + str(message.from_user.id) + '\n')
    except TypeError:
        pass
    log.close()

    if message != begin_message[message.chat.id]:
        delete_mess[message.chat.id].append(message.message_id)
    mess_delete(message.chat.id)
    if message.text != 'start' and add_index[message.chat.id] != 1:
        delete_mess[message.chat.id].append(
            bot.send_message(
                message.chat.id,
                text=lang(lang_index, message.chat.id)[8]).message_id)
    if add_index[message.chat.id] == 1:  # adding a note/добавление заметки
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
        mess_delete(message.chat.id)
        add_index[message.chat.id] = 0
        inline(begin_notes)

    if message.text == 'start':

        begin_message[message.chat.id] = message
        keyboard = types.InlineKeyboardMarkup()
        key_notes = types.InlineKeyboardButton(
            text=lang(lang_index, message.chat.id)[0], callback_data='notes')
        key_shop_list = types.InlineKeyboardButton(text=lang(
            lang_index, message.chat.id)[1], callback_data='shop_list')
        key_select_lang = types.InlineKeyboardButton(text=lang(
            lang_index, message.chat.id)[2], callback_data='select_lang')
        keyboard.add(key_notes, key_shop_list)
        keyboard.add(key_select_lang)

        delete_mess[message.chat.id].append(bot.send_message(
            message.chat.id, text=lang(lang_index, message.chat.id)[5]).message_id)
        delete_mess[message.chat.id].append(bot.send_message(
            message.chat.id,
            text=lang(lang_index, message.chat.id)[3],
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
        mess_delete(menu.message.chat.id)

        # printing notes/печать заметок
        begin_notes = menu
        delete_mess[menu.message.chat.id].append(bot.send_message(
            menu.message.chat.id, text=lang(lang_index, menu.message.chat.id)[9]).message_id)
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
        for i in range(len(rows)):
            delete_mess[menu.message.chat.id].append(bot.send_message(
                menu.message.chat.id, ('%d -- %s' %
                                       (i + 1, rows[i][1]))).message_id)  # rows[i][0]
            mass_notes[rows[i][0]] = rows[i][1]
        conn.close()

        # button output notes/вывод кнопок заметок
        key = types.InlineKeyboardMarkup()
        key_add = types.InlineKeyboardButton(
            text=lang(
                lang_index,
                menu.message.chat.id)[10],
            callback_data="add")
        key_del = types.InlineKeyboardButton(
            text=lang(
                lang_index,
                menu.message.chat.id)[11],
            callback_data="del")
        key_del_all = types.InlineKeyboardButton(
            text=lang(
                lang_index,
                menu.message.chat.id)[12],
            callback_data="del_all")
        key_main_menu = types.InlineKeyboardButton(
            text=lang(
                lang_index,
                menu.message.chat.id)[18],
            callback_data="main_menu")
        key.add(key_add)
        key.add(key_del)
        key.add(key_del_all)
        key.add(key_main_menu)
        delete_mess[menu.message.chat.id].append(bot.send_message(
            menu.message.chat.id,
            text=lang(lang_index, menu.message.chat.id)[13],
            reply_markup=key).message_id)

    if menu.data == 'shop_list':
        mess_delete(menu.message.chat.id)
        delete_mess[menu.message.chat.id].append(bot.send_message(
            menu.message.chat.id, 'Это кнопка 2').chat.id)
        delete_mess[menu.message.chat.id].append(
            bot.send_message(
                menu.message.chat.id,
                text=lang(lang_index, menu.message.chat.id)[6]).message_id)
    if menu.data == 'select_lang':
        mess_delete(menu.message.chat.id)
        key = types.InlineKeyboardMarkup()
        key_rus = types.InlineKeyboardButton(
            text="Русский", callback_data="rus")
        key_eng = types.InlineKeyboardButton(
            text="English", callback_data="eng")
        key_deut = types.InlineKeyboardButton(
            text="Deutsch", callback_data="deut")
        key.add(key_rus, key_eng, key_deut)
        delete_mess[menu.message.chat.id].append(bot.send_message(
            menu.message.chat.id,
            text='Язык / Language / Sprache',
            reply_markup=key).message_id)
    if menu.data == 'rus':
        lang_index[menu.message.chat.id] = 1
        mess_delete(menu.message.chat.id)
        get_text_messages(begin_message[menu.message.chat.id])
    if menu.data == 'eng':
        lang_index[menu.message.chat.id] = 2
        mess_delete(menu.message.chat.id)
        get_text_messages(begin_message[menu.message.chat.id])
    if menu.data == 'deut':
        lang_index[menu.message.chat.id] = 3
        mess_delete(menu.message.chat.id)
        get_text_messages(begin_message[menu.message.chat.id])
    if menu.data == 'add':
        add_index[menu.message.chat.id] = 1
        mess_delete(menu.message.chat.id)
        delete_mess[menu.message.chat.id].append(
            bot.send_message(
                menu.message.chat.id,
                text=lang(lang_index, menu.message.chat.id)[14]).message_id)
    if menu.data == 'del':
        key = types.InlineKeyboardMarkup()
        for seq_number, record_number in enumerate(mass_notes):
            temp_key = types.InlineKeyboardButton(
                text='%d -- %s' %
                (seq_number, mass_notes[record_number]), callback_data='del_file%i' %
                record_number)
            key.add(temp_key)
        mess_delete(menu.message.chat.id)
        delete_mess[menu.message.chat.id].append(
            bot.send_message(
                menu.message.chat.id,
                text=lang(lang_index, menu.message.chat.id)[15],
                reply_markup=key).message_id)
    if menu.data == 'del_all':
        conn = MySQLdb.connect(
            'localhost',
            'root',
            'mike159753',
            'universalassistant')
        cursor = conn.cursor()
        cursor.execute(
            """DELETE FROM notes WHERE user = '%d'""" %
            menu.from_user.id)
        conn.commit()
        conn.close()
        mess_delete(menu.message.chat.id)
        inline(begin_notes)
    if menu.data == 'main_menu':
        get_text_messages(begin_message[menu.message.chat.id])
    if mass_notes != {}:
        for i in mass_notes:
            if menu.data == 'del_file%i' % i:
                conn = MySQLdb.connect(
                    'localhost', 'root', 'mike159753', 'universalassistant')
                cursor = conn.cursor()
                cursor.execute("""DELETE FROM notes WHERE id = '%d'""" % i)
                conn.commit()
                conn.close()
                mess_delete(menu.message.chat.id)
                inline(begin_notes)


bot.polling(none_stop=True, interval=0)

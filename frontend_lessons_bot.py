import telebot
from telebot import types

import boto
from boto.s3.connection import S3Connection
token = S3Connection(os.environ['TOKEN'])

bot = telebot.TeleBot(token);

#Список описаний
dhelp = '\nВы можете продолжить вводить теги, или перейти назад при помощи кнопок.'
doctype_description = 'Тег <!DOCTYPE> описывает тип документа. Это одиночный тег. Пример: <!DOCTYPE html> указывает то, что документ написан на html. Также можно указать версию html, публичность, название организации и т.п. Однако обыччно это не требуется.'
html_description = 'Тег <html> - парный тег. Между тегами <html> и </html> содержится всё содержимое веб страницы. Открывающий тег идёт сразу после <!DOCTYPE>, закрывающий стоит в документе последним.'
head_description = 'Тег <head> - парный тег, содержащий элементы помогающие браузеру, метатеги. Внутри тегов <head> и </head> также подключаются стили и скрипты, эти теги указываются первыми внутри <html>.'
body_description = '<body> и </body> предназначенны для хранения содержания веб-страницы, которое отображается в окне браузера. Эти теги пишут после <head>, внутри <html>.'
meta_description = '<meta> - одиночный тег, указывающий информацию для браузеров и поисковых систем. Например <meta charset = "utf-8"> устанавливает кодировку текста utf-8. Также используются конструкции <meta name = "---" content = "---">, здесь name указывает на то, что устанавливает метатег, а content задаёт это значение. Например name = "description" показывает, что тег задаёт описание веб страницы, name = "keywords" задаёт ключевые слова. Описание и ключевые слова указываются в content. Например при помощи <meta name = "keywords" content = "html, css, коты"> мы сообщаем поисковой системе о том, что наша страница про html, css и котов.'
unknown_tag_description = 'Прости, но я не знаю этот тег. Возможно он ещё не был добавлен, а может ты ошибся при написании названия тега. Помни что тег нужно указывать без атрибутов, т.е. <meta> а не <meta charset>.'

#Список скобок:
brackets = ('<', '>', '(', ')', "'", '"', '/', '\\', '{', '}', '!')

#Нужно ли принимать теги:
tags_mode = False

#Текст для бота:
view_tags_text = 'Просто отправь мне имя интересующего тебя тега и я расскажу тебе о нём. Или можешь перейти к списку тегов тапнув по кнопке.'

#Главное меню бота
main_menu = types.InlineKeyboardMarkup()
view_tags = types.InlineKeyboardButton(text = 'Html-теги', callback_data = 'view_tags')
settings = types.InlineKeyboardButton(text = 'Настройки', callback_data = 'settings')
main_menu.add(view_tags)
main_menu.add(settings)

#Меню режима просмотра тегов
tags_menu = types.InlineKeyboardMarkup()
tags_list = types.InlineKeyboardButton(text = 'Список тегов', callback_data = 'tags_list')
back_to_main = types.InlineKeyboardButton(text = 'Назад', callback_data = 'back_to_main')
tags_menu.add(tags_list)
tags_menu.add(back_to_main)

#Меню после получения ответа
answer_menu = types.InlineKeyboardMarkup();
back_to_tags_menu = types.InlineKeyboardButton(text = 'Назад', callback_data = 'back_to_tags_menu')
back_to_main_menu = types.InlineKeyboardButton(text = 'Главная', callback_data = 'back_to_main')
answer_menu.add(back_to_tags_menu)
answer_menu.add(back_to_main_menu)

#Режим просмотра тегов
def view_tags(call):
	bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = view_tags_text, reply_markup = tags_menu)

#Приводит текст к "стандартному" виду. Убирает скобки, переводит буквы в строчные
def to_standart_mode(text):
	text = text.lower()
	changed = True
	while changed:
		changed = False
		if text[0] in brackets:
			text = text[1:]
			changed = True
		if text and text[len(text) - 1] in brackets:
			text = text[:len(text) - 2]
			changed = True
	return text

#Отработчик команды start
@bot.message_handler(commands = ['start'])
def start_message(message):
	bot.send_message(message.chat.id, "Привет, выбери одно из нижеперечисленных действий:", reply_markup = main_menu)

#Отработчик команды menu
@bot.message_handler(commands = ['menu'])
def start_message(message):
	bot.send_message(message.chat.id, "Выбери действие:", reply_markup = main_menu)

#Отработчик ввода тегов
@bot.message_handler(content_types = ['text'])
def answer(message):
	if tags_mode:
		tag = to_standart_mode(message.text)
		if tag == 'doctype':
			description = doctype_description
		elif tag == 'html':
			description = html_description
		elif tag == 'head':
			description = head_description
		elif tag == 'body':
			description = body_description
		elif tag == 'meta':
			description = meta_description
		else:
			description = unknown_tag_description
		bot.send_message(message.chat.id, description + dhelp, reply_markup = answer_menu)
	else:
		pass

#Отработчик callback кнопок
@bot.callback_query_handler(func = lambda call: True)
def get_calldata(call):
	global tags_mode

	if call.message:
		if call.data == 'view_tags':
			view_tags(call)
			tags_mode = True
		elif call.data == 'back_to_main':
			bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = 'Выбери действие:', reply_markup = main_menu)
			tags_mode = False
		elif call.data == 'back_to_tags_menu':
			view_tags(call)
			tags_mode = True

bot.polling()

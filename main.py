import telebot
from telebot import types
import random

token = '6782863174:AAHBWRhvn9V5l4-qRfBRRdA9Tqy4wBr5Dhg'
bot = telebot.TeleBot(token)

from phrases import phrases
current_index = 0

def get_chat_id(update, context):
  chat_id = -1

  if update.message is not None:
    chat_id = update.message.chat.id
  elif update.callback_query is not None:
    chat_id = update.callback_query.message.chat.id
  elif update.poll is not None:
    chat_id = context.bot_data[update.poll.id]

  return chat_id

@bot.message_handler(commands=['start'])
def greet(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("допомога"))
    markup.row(types.KeyboardButton("завчити"))
    markup.row(types.KeyboardButton("пройти тестування"))
    markup.row(types.KeyboardButton("контекстне використання фразеологізмів"))
    bot.send_message(message.chat.id, "Привіт! Я твій помічник у вивченні фразеологізмів. Обери режим!",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "допомога")
def send_help(message):
    bot.send_message(message.chat.id,
                     "Бот має два режими вивчення фразеологізмів. Натисни кнопку 'завчити', якщо хочеш "
                     "завчити фразеологізми! Натисни кнопку 'пройти тестування', якщо хочеш перевірити свої знання!")
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("назад"))
    markup.row(types.KeyboardButton("поширені запитання (FAQ)"))
    markup.row(types.KeyboardButton("написати розробнику"))
    bot.send_message(message.chat.id, "оберіть дію:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "написати розробнику")
def send_username(message):
    bot.send_message(message.chat.id,
                     "Повідомити про баги або запропонувати ідеї: @ktriiins <3")

@bot.message_handler(func=lambda message: message.text == "поширені запитання (FAQ)")
def send_username(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("назад"))
    markup.row(types.KeyboardButton("що таке фразеологія?"))
    markup.row(types.KeyboardButton("для чого цей бот?"))
    markup.row(types.KeyboardButton("чи можна проходити тести кілька разів?"))
    markup.row(types.KeyboardButton("чи зберігаються мої результати?"))
    bot.send_message(message.chat.id, "Що цікавить?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "що таке фразеологія?")
def send_username(message):
    bot.send_message(message.chat.id,
                     "Фразеологія (від грецького phrasis — вираження, logos — вчення) — розділ мовознавства, "
                     "у якому вивчаються лексично неподільні поєднання слів. "
                     "Фразеологією називають також сукупність властивих мові усталених зворотів і висловів.")

@bot.message_handler(func=lambda message: message.text == "для чого цей бот?")
def send_username(message):
    bot.send_message(message.chat.id,
                     "Цей бот допомагає вивчати фразеологізми через практику та приклади з контекстом.")

@bot.message_handler(func=lambda message: message.text == "чи можна проходити тести кілька разів?")
def send_username(message):
    bot.send_message(message.chat.id,
                     "Так! Проходь тести скільки завгодно — ніяких обмежень :)")

@bot.message_handler(func=lambda message: message.text == "чи зберігаються мої результати?")
def send_username(message):
    bot.send_message(message.chat.id,
                     "Поки що результати не зберігаються, але не хвилюйся — у майбутньому ти зможеш відстежувати свій прогрес!")
@bot.message_handler(func=lambda message: message.text == "завчити")
def send_cramming(message):
    global current_index
    phrase = phrases[current_index]
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("наступний фразеологізм"))
    markup.row(types.KeyboardButton("назад"))
    bot.send_message(message.chat.id, phrase["title"] + " - " + phrase["description"] + "\n" + "Приклад: "
                     + phrase["example"], reply_markup=markup)

from quizzes import quizzes

current_quiz = None
current_sentence = None

@bot.message_handler(func=lambda message: message.text == "пройти тестування")
def send_test(message):
    global current_quiz
    current_quiz = random.choice(quizzes)
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("наступний тест"))
    markup.row(types.KeyboardButton("назад"))
    bot.send_poll(reply_markup=markup, chat_id=message.chat.id, type="quiz", question=current_quiz["question"],
                  options=current_quiz["options"], correct_option_id=current_quiz["correct_option_id"])

@bot.message_handler(func=lambda message: message.text == "наступний фразеологізм")
def next_phrase(message):
    global current_index
    current_index = (current_index + 1) % len(phrases)
    phrase = phrases[current_index]
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("наступний фразеологізм"))
    markup.row(types.KeyboardButton("назад"))
    bot.send_message(message.chat.id, phrase["title"] + " - " + phrase["description"] + "\n" + "Приклад: "
                     + phrase["example"], reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "наступний тест")
def next_test(message):
    global current_quiz
    current_quiz = random.choice(quizzes)
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("наступний тест"))
    markup.row(types.KeyboardButton("назад"))
    bot.send_poll(chat_id=message.chat.id, type="quiz", question=current_quiz["question"],
                  options=current_quiz["options"], correct_option_id=current_quiz["correct_option_id"], reply_markup=markup)



from fill_in_the_blank import fill_in_the_blank_phrases

@bot.message_handler(func=lambda message: message.text == "контекстне використання фразеологізмів")
def send_fill_in_the_blank(message):
    global current_sentence
    current_sentence = random.choice(fill_in_the_blank_phrases)
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("наступне речення"))
    markup.row(types.KeyboardButton("назад"))

    bot.send_poll(chat_id=message.chat.id, type="quiz", question=current_sentence["phrase"],
                  options=current_sentence["variants"], correct_option_id=current_sentence["current_option_id"],
                  reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "наступне речення")
def next_test(message):
    global current_sentence
    current_sentence = random.choice(fill_in_the_blank_phrases)
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("наступнe речення"))
    markup.row(types.KeyboardButton("назад"))
    bot.send_poll(chat_id=message.chat.id, type="quiz", question=current_sentence["phrase"],
                  options=current_sentence["variants"], correct_option_id=current_sentence["current_option_id"])
@bot.message_handler(func=lambda message: message.text == "назад")
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("допомога"))
    markup.row(types.KeyboardButton("завчити"))
    markup.row(types.KeyboardButton("пройти тестування"))
    markup.row(types.KeyboardButton("контекстне використання фразеологізмів"))
    bot.send_message(message.chat.id, "Обери режим!", reply_markup=markup)

bot.polling()

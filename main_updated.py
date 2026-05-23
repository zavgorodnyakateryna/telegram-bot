import telebot
from telebot import types
import random
import sqlite3

token = '6782863174:AAHBWRhvn9V5l4-qRfBRRdA9Tqy4wBr5Dhg'
bot = telebot.TeleBot(token)

def get_phrases_by_category(category="all"):
    conn = sqlite3.connect('phraseologisms_similarity_and_syntax.db')
    cursor = conn.cursor()

    if category == "all":
        cursor.execute("""
            SELECT p.phrase, p.definition, p.example
            FROM phraseologisms 
            ORDER BY RANDOM()
        """)
    else:
        cursor.execute("""
            SELECT p.phrase, p.definition, p.example
            FROM phraseologisms p
            JOIN categories c ON p.category_id = c.id
            WHERE c.name = ?
            ORDER BY p.id
        """, (category.capitalize(),))

    phrases = cursor.fetchall()
    conn.close()
    return phrases

def escape_md2(text: str) -> str:
    if not text:
        return ""
    chars_to_escape = r'_*[]()~`>#+-=|{}.!'
    for char in chars_to_escape:
        text = text.replace(char, '\\' + char)
    return text

@bot.message_handler(commands=['start'])
def greet(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("допомога"))
    markup.row(types.KeyboardButton("завчити"))
    markup.row(types.KeyboardButton("пройти тестування"))
    markup.row(types.KeyboardButton("контекстне використання фразеологізмів"))

    bot.send_message(
        message.chat.id,
        "Привіт! Я твій помічник у вивченні фразеологізмів. Обери режим!",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "допомога")
def send_help(message):
    bot.send_message(
        message.chat.id,
        "Бот має два режими вивчення фразеологізмів. "
        "Натисни кнопку 'завчити', якщо хочеш завчити фразеологізми! "
        "Натисни кнопку 'пройти тестування' або 'контекстне використання фразеологізмів', якщо хочеш перевірити свої знання!"
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("назад"))
    markup.row(types.KeyboardButton("поширені запитання (FAQ)"))
    markup.row(types.KeyboardButton("написати розробнику"))

    bot.send_message(
        message.chat.id,
        "оберіть дію:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "написати розробнику")
def send_username(message):
    bot.send_message(
        message.chat.id,
        "Повідомити про баги або запропонувати ідеї: @ktriiins <3"
    )

@bot.message_handler(func=lambda message: message.text == "поширені запитання (FAQ)")
def faq(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("назад"))
    markup.row(types.KeyboardButton("що таке фразеологія?"))
    markup.row(types.KeyboardButton("звідки взято матеріал?"))
    markup.row(types.KeyboardButton("для чого цей бот?"))
    markup.row(types.KeyboardButton("чи можна проходити тести кілька разів?"))
    markup.row(types.KeyboardButton("чи зберігаються мої результати?"))

    bot.send_message(
        message.chat.id,
        "Що цікавить?",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "що таке фразеологія?")
def phraseology_info(message):
        bot.send_message(message.chat.id,
                         "Фразеологія (від грецького phrasis — вираження, logos — вчення) — розділ мовознавства, "
                         "у якому вивчаються лексично неподільні поєднання слів. "
                         "Фразеологією називають також сукупність властивих мові усталених зворотів і висловів.")

@bot.message_handler(func=lambda message: message.text == "звідки взято матеріал?")
def phraseology_source(message):
    bot.send_message(
        message.chat.id,
        "Усі фразеологіми, їх тлумачення та приклади вживання "
        "дібрані зі словника фразеологізмів української мови (Білоніженко В.М.)."
        " Ось посилання на нього: https://archive.org/details/slov557/page/158/mode/2up"
    )

@bot.message_handler(func=lambda message: message.text == "для чого цей бот?")
def bot_info(message):
    bot.send_message(
        message.chat.id,
        "Цей бот допомагає вивчати фразеологізми через практику та приклади з контекстом."
    )

@bot.message_handler(func=lambda message: message.text == "чи можна проходити тести кілька разів?")
def tests_info(message):
    bot.send_message(
        message.chat.id,
        "Так! Проходь тести скільки завгодно — ніяких обмежень :)"
    )

@bot.message_handler(func=lambda message: message.text == "чи зберігаються мої результати?")
def results_info(message):
    bot.send_message(
        message.chat.id,
        "Поки що результати не зберігаються, але не хвилюйся — у майбутньому ти зможеш відстежувати свій прогрес!"
    )

user_category = {}
user_index = {}

@bot.message_handler(func=lambda message: message.text == "завчити")
def choose_category(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    buttons = [
        "всі фразеологізми",
        "із компонентом «душа»",
        "із компонентом «серце»",
        "із компонентом «голова»",
        "із компонентом «думка»",
        "із компонентом «кров»",
        "із компонентом «дух»",
        "із компонентом «памʼять»",
        "із компонентом «розум»",
        "із компонентом «совість»",
        "назад"
    ]

    for btn in buttons:
        markup.add(types.KeyboardButton(btn))

    bot.send_message(
        message.chat.id,
        "Які фразеологізми ти хочеш пройти?",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text in [
    "всі фразеологізми", "із компонентом «душа»", "із компонентом «серце»",
    "із компонентом «голова»", "із компонентом «думка»", "із компонентом «кров»",
    "із компонентом «дух»", "із компонентом «памʼять»", "із компонентом «розум»",
    "із компонентом «совість»"
])
def start_cramming(message):
    chat_id = message.chat.id
    text = message.text

    if text == "всі фразеологізми":
        category = "all"
    else:
        category = text.split("«")[1].split("»")[0]

    user_category[chat_id] = category
    user_index[chat_id] = 0

    show_phrase(message, category)

def show_phrase(message, category):
    chat_id = message.chat.id
    phrases = get_phrases_by_category(category)

    if not phrases:
        bot.send_message(chat_id, "На жаль, у цій категорії поки що немає фразеологізмів.")
        return

    if category == "all":
        phrase, definition, example = random.choice(phrases)
    else:
        idx = user_index.get(chat_id, 0)

        if idx >= len(phrases):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row(types.KeyboardButton("вибрати іншу категорію"))
            markup.row(types.KeyboardButton("назад"))

            bot.send_message(
                chat_id,
                "Ти переглянув усі фразеологізми цієї категорії! Молодець!",
                reply_markup=markup
            )
            return

        phrase, definition, example = phrases[idx]
        user_index[chat_id] = idx + 1

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("наступний фразеологізм"))
    markup.row(types.KeyboardButton("вибрати іншу категорію"))
    markup.row(types.KeyboardButton("назад"))

    title = escape_md2(phrase)
    desc = escape_md2(definition)
    ex = escape_md2(example) if example else ""

    text = f"""*{title}*

{desc}

*Приклад:*
> {ex}
"""

    bot.send_message(
        message.chat.id,
        text,
        parse_mode='MarkdownV2',
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "наступний фразеологізм")
def next_phrase(message):
    chat_id = message.chat.id
    category = user_category.get(chat_id, "all")
    show_phrase(message, category)


@bot.message_handler(func=lambda message: message.text == "вибрати іншу категорію")
def back_to_categories(message):
    choose_category(message)

def generate_quiz():
    conn = sqlite3.connect('phraseologisms_similarity_and_syntax.db')
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT id, phrase, definition, similarity
                   FROM phraseologisms
                   ORDER BY RANDOM() LIMIT 1
                   """)

    correct = cursor.fetchone()
    correct_id = correct[0]
    correct_phrase = correct[1]
    correct_definition = correct[2]
    correct_similarity = correct[3]

    cursor.execute("""
                   SELECT definition
                   FROM phraseologisms
                   WHERE similarity != ?
        AND id != ?
                   ORDER BY RANDOM()
                       LIMIT 2
                   """, (correct_similarity, correct_id))

    wrong_answers = [row[0] for row in cursor.fetchall()]
    conn.close()

    options = wrong_answers + [correct_definition]
    random.shuffle(options)

    correct_option_id = options.index(correct_definition)

    return {
        "question": correct_phrase,
        "options": options,
        "correct_option_id": correct_option_id
    }


@bot.message_handler(func=lambda m: m.text in ["пройти тестування", "наступний тест"])
def send_test(message):
    current_quiz = generate_quiz()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("наступний тест"))
    markup.row(types.KeyboardButton("назад"))
    bot.send_poll(
        chat_id=message.chat.id,
        type="quiz",
        question=current_quiz["question"],
        options=current_quiz["options"],
        correct_option_id=current_quiz["correct_option_id"],
        reply_markup=markup
    )

def generate_context_quiz():
    conn = sqlite3.connect('phraseologisms_similarity_and_syntax.db')
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT id, phrase, context_usage, similarity, syntax_role
                   FROM phraseologisms
                   WHERE context_usage IS NOT NULL
                     AND context_usage != ''
                   ORDER BY RANDOM()
                       LIMIT 1
                   """)
    correct = cursor.fetchone()
    correct_id, correct_phrase, context_sentence, correct_similarity, correct_role = correct

    cursor.execute("""
                   SELECT phrase
                   FROM phraseologisms
                   WHERE syntax_role = ?
                     AND similarity != ?
          AND id != ?
                   ORDER BY RANDOM()
                       LIMIT 2
                   """, (correct_role, correct_similarity, correct_id))
    wrong_answers = [row[0] for row in cursor.fetchall()]

    if len(wrong_answers) < 2:
        already_used = wrong_answers + [correct_phrase]
        placeholders = ','.join('?' * len(already_used))
        cursor.execute(f"""
            SELECT phrase
            FROM phraseologisms
            WHERE similarity != ?
              AND id != ?
              AND phrase NOT IN ({placeholders})
            ORDER BY RANDOM()
            LIMIT {2 - len(wrong_answers)}
        """, [correct_similarity, correct_id] + already_used)
        wrong_answers += [row[0] for row in cursor.fetchall()]

    conn.close()

    options = wrong_answers + [correct_phrase]
    random.shuffle(options)
    correct_option_id = options.index(correct_phrase)

    return {
        "question": context_sentence,
        "options": options,
        "correct_option_id": correct_option_id
    }

@bot.message_handler(func=lambda m: m.text in ["контекстне використання фразеологізмів", "наступне речення"])
def send_context_quiz(message):
    current_sentence = generate_context_quiz()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("наступне речення"))
    markup.row(types.KeyboardButton("назад"))
    bot.send_poll(
        chat_id=message.chat.id,
        type="quiz",
        question=current_sentence["question"],
        options=current_sentence["options"],
        correct_option_id=current_sentence["correct_option_id"],
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "назад")
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("допомога"))
    markup.row(types.KeyboardButton("завчити"))
    markup.row(types.KeyboardButton("пройти тестування"))
    markup.row(types.KeyboardButton("контекстне використання фразеологізмів"))

    bot.send_message(
        message.chat.id,
        "Обери режим!",
        reply_markup=markup
    )

bot.polling()
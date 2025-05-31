import telebot
from telebot import types
import os
import json
import random
from dotenv import load_dotenv
from logic_solver import solve_formula

user_sessions = {}  # chat_id: shuffled_questions_list
NUM_QUESTIONS = 5  # можно менять

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Загрузка вопросов
with open("questions.json", "r", encoding="utf-8") as f:
    test_questions = json.load(f)
# Загрузка теории
with open("theory.json", "r", encoding="utf-8") as f:
    THEORY = json.load(f)

# Хранение прогресса пользователя
user_progress = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📋 Начать тест", "📖 Теория")
    markup.row("🧠 Разобрать формулу", "ℹ️ О проекте")
    bot.send_message(message.chat.id, "👋 Привет! Я бот-помощник по дискретной математике. Что будем делать?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📋 Начать тест")
def handle_start_test_button(message):
    start_test(message)

@bot.message_handler(func=lambda m: m.text == "📖 Теория")
def send_theory(message):
    texts = [f"📖 {title}:\n{content}" for title, content in THEORY.items()]
    bot.send_message(message.chat.id, "\n\n".join(texts))

@bot.message_handler(func=lambda m: m.text == "🧠 Разобрать формулу")
def ask_for_formula(message):
    msg = bot.send_message(message.chat.id, "Введите логическую формулу:")
    bot.register_next_step_handler(msg, handle_formula)

def handle_formula(message):
    try:
        steps = solve_formula(message.text)
        bot.send_message(message.chat.id, "\n".join(steps))
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка разбора: {e}")

@bot.message_handler(func=lambda message: message.text == "ℹ️ О проекте")
def handle_about(message):
    bot.send_message(message.chat.id, "📌 ЛогикБот — это Telegram-бот, созданный для помощи в изучении дискретной математики и алгебры логики. Он подойдёт студентам, школьникам и всем, кто хочет разобраться в основах логических операций и формальных выражений.")



def prepare_question(q):
    options = q["options"][:]
    # перемешиваем варианты
    shuffled = options[:]
    random.shuffle(shuffled)
    # находим новый индекс правильного варианта
    correct_answer = q["options"][q["answer_index"]]
    new_answer_index = shuffled.index(correct_answer)
    # возвращаем вопрос с перемешанными вариантами и новым индексом правильного ответа
    return {
        "question": q["question"],
        "options": shuffled,
        "answer_index": new_answer_index,
        "explanation": q["explanation"]
    }

@bot.message_handler(commands=['test'])
def start_test(message):
    chat_id = message.chat.id
    user_progress[chat_id] = 0
    selected_questions = random.sample(test_questions, min(NUM_QUESTIONS, len(test_questions)))
    # для каждого вопроса создаём копию с перемешанными вариантами
    user_sessions[chat_id] = [prepare_question(q) for q in selected_questions]
    bot.send_message(chat_id, f"📋 Тест начат! Вопросов: {len(user_sessions[chat_id])}")
    send_question(chat_id)

def send_question(chat_id):
    index = user_progress.get(chat_id, 0)
    questions = user_sessions.get(chat_id, [])
    if index < len(questions):
        q = questions[index]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for option in q["options"]:
            markup.add(option)
        bot.send_message(chat_id, q["question"], reply_markup=markup)
    else:
        bot.send_message(chat_id, "✅ Тест завершён! Введи /test, чтобы пройти снова.", reply_markup=telebot.types.ReplyKeyboardRemove())
        user_progress.pop(chat_id, None)
        user_sessions.pop(chat_id, None)

@bot.message_handler(func=lambda message: message.chat.id in user_sessions)
def check_answer(message):
    chat_id = message.chat.id
    index = user_progress.get(chat_id, 0)
    questions = user_sessions.get(chat_id, [])
    if index < len(questions):
        q = questions[index]
        if message.text == q["options"][q["answer_index"]]:
            bot.send_message(chat_id, "✅ Правильно!")
        else:
            correct = q["options"][q["answer_index"]]
            bot.send_message(chat_id, f"❌ Неверно! Правильный ответ: {correct}")
        if q["explanation"]:
            bot.send_message(chat_id, f"💡 {q['explanation']}")
        user_progress[chat_id] += 1
        send_question(chat_id)

bot.infinity_polling()

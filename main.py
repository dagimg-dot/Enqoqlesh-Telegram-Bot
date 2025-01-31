import threading
import telebot
import os
from dotenv import load_dotenv
from telebot import types
import requests

load_dotenv()
TOKEN = os.getenv('TOKEN')
data = {}
bot = telebot.TeleBot(TOKEN)

genre = ["All", "History", "Geography","Movie", "Literature", "Society", "Science"]
rounds = ["1 Rounds", "2 Rounds", "5 Rounds", "10 Rounds"]


def start_markup():
    markup = types.ReplyKeyboardMarkup()
    key1 = types.KeyboardButton('play With Friends')
    key2 = types.KeyboardButton('help')
    markup.add(key1, key2)
    return markup


def genre_markup():
    markup = types.ReplyKeyboardMarkup()
    genere1 = types.KeyboardButton('All')
    genere2 = types.KeyboardButton('History')
    genere3 = types.KeyboardButton('Geography')
    genere4 = types.KeyboardButton('Movie')
    genere5 = types.KeyboardButton('Literature')
    genere6 = types.KeyboardButton('Society')
    genere7 = types.KeyboardButton('Science')
    markup.row(genere1)
    markup.row(genere2, genere3)
    markup.row(genere4, genere5)
    markup.row(genere6, genere7)
    return markup


def round_chooser_markup():
    markup = types.ReplyKeyboardMarkup()
    round1 = types.KeyboardButton('1 Rounds')
    round2 = types.KeyboardButton('2 Rounds')
    round3 = types.KeyboardButton('5 Rounds')
    round4 = types.KeyboardButton('10 Rounds')
    markup.add(round1, round2, round3, round4)
    return markup


def make_request(round: int):
    try:
        print("what is going on")
        response = requests.get(f'http://localhost:5000/category/Biology/questions?round={round}')
        data = response.json()
        question_data = data.get('data', [])
        questions_answers = [{'question' : question.get('text', ''),'answer' : question.get('answer','')} for question in question_data]
        return questions_answers
    except requests.exceptions.RequestException as e:
        print(e)
        return None


@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = start_markup()
    bot.send_message(message.chat.id, 'Welcome to the bot!', reply_markup=markup)


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, 'This is a nodemon .')


@bot.message_handler(commands=['stop'])
def handle_stop(message):
    markup = start_markup()
    bot.reply_to(message, 'This is the stop message.', reply_markup=markup)


def handle_new_chat_members(message):
    group_title = message.chat.title

    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            bot.reply_to(message, f'Thank you for adding me to {group_title}! If you have any questions, feel free to ask.')


@bot.message_handler(func=lambda message: True, content_types=['new_chat_members'])
def handle_new_chat_members_wrapper(message):
    if bot.get_me() in message.new_chat_members:
        handle_new_chat_members(message)

def handle_timeout(message, questions, index):
    if index < len(questions):
        bot.send_message(message.chat.id, f"Time's up! The correct answer is {questions[index]['answer']}")
        quiz_flow(message, questions, index + 1)

def quiz_flow(message, questions, index=0):
    if index < len(questions):
        question = questions[index]
        bot.send_message(message.chat.id, question['question'])
        timer = threading.Timer(10, handle_timeout, args=(message, questions, index))
        timer.start()

def ask_questions(message, result):
    print('Asking Questions...')
    quiz_thread = threading.Thread(target=quiz_flow, args=(message, result))
    quiz_thread.start()


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'play With Friends':
        if message.chat.type == 'private':
            bot.send_message( message.chat.id, 'You have to add the bot to a group and type /play')
        else:
            markup = genre_markup()
            bot.send_message(message.chat.id, 'Choose agenre', reply_markup=markup)

    elif message.text in genre:
        markup = round_chooser_markup()
        bot.send_message(message.chat.id, 'Choose a round',reply_markup=markup)

    elif message.text in rounds:
        round = message.text.split(" ")[0]
        result = make_request(round)
        print (result)
        if result is not None:
            ask_questions(message, result)
            print("what is going on as well")

    elif message.text == 'help':
        bot.send_message(message.chat.id, 'Help message')
    else:
        # Check if the message is a response to the question
        bot.send_message(message.chat.id, "who are you")
        # if message.reply_to_message.text == "Who invented pencillin?":
            # Process the response to the question
        if message.text.lower() == "hello":
            bot.send_message(message.chat.id, 'Correct answer!')
        else:
            bot.send_message(message.chat.id, 'Incorrect answer. Try again!')
    

        
print("bot is running")
bot.polling()
import os
import logging
import redis

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from ChatGPT_HKBU import HKBU_ChatGPT
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

global redis1


def main():
    # Load your token and create an Updater for your Bot
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    # updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    updater = Updater(token=(os.environ['TLG_ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.from_url(
            url=os.environ['REDISS_URL'],
            decode_responses=True,
            health_check_interval=10,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            socket_keepalive=True
        )                 

    # You can set this logging module, so you will know when
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)

    # dispatcher for chatgpt
    global chatgpt
    global user, pref
    user = ''
    pref = ''
    chatgpt = HKBU_ChatGPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),
                                     equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("create", create))
    dispatcher.add_handler(CommandHandler("switch", switch))
    dispatcher.add_handler(CommandHandler("amend", amend))
    dispatcher.add_handler(CommandHandler("get", get))

    # To start the bot
    updater.start_polling()
    updater.idle()


def echo(update: Update, context: CallbackContext):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

    # Define a few command handlers. These usually take the two arguments update and
    # context. Error handlers also receive the raised TelegramError object in error.

def create(update: Update, context: CallbackContext):
    try:
        global redis1, user, pref
        
        if len(context.args) < 2:
            update.message.reply_text('Usage: /create <username> <preferences...>')
            return

        temp_user = context.args[0]
        temp_pref = ' '.join(context.args[1:])

        if redis1.exists(temp_user):
            update.message.reply_text('User already exists.')
            return
        else:
            redis1.set(temp_user, temp_pref)
            update.message.reply_text('User created and preferences saved.')
            user = temp_user
            pref = temp_pref
            logging.info(f"{user}, {pref}")

        update.message.reply_text(f'Welcome {user} to the chatbot.')
    except:
        update.message.reply_text('Usage: /create <username> <preferences>')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(f'''
    current_user:{user}\n
    current_preference:{pref}\n
    /create <username> <preferences> -- create a new user\n
    /switch <username> -- switch to another user\n
    /amend <username> <preferences> -- amend the preferences of a user\n
    /get <username> -- get the preference from redis
    ''')

def get(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /get is issued."""
    try:
        global redis1
        temp_user = context.args[0]
        if redis1.exists(temp_user):
            temp_pref = redis1.get(temp_user)
            logging.info(f"get: {temp_user}, {temp_pref}")
            update.message.reply_text(f'user({temp_user}), preferences({temp_pref})')
        else:
            update.message.reply_text('User does not exist.')
    
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /get <username>')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]  # /add keyword <-- this should store the keyword
        redis1.incr(msg)

        update.message.reply_text('You have said ' + msg + ' for ' +
                                  redis1.get(msg) + ' times.')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def switch(update: Update, context: CallbackContext) -> None:
    global redis1, user, pref
    try:
        logging.info(context.args[0])
        temp_user = context.args[0]
        if user != temp_user:
            if redis1.exists(temp_user):
                user = temp_user
                pref = redis1.get(user)
                logging.info(f"{user}, {pref}")
                update.message.reply_text('User switched.')
            else:
                update.message.reply_text('User does not exist.')

        else:
            update.message.reply_text('User already used.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /switch <username>')
    
def amend(update: Update, context: CallbackContext) -> None:
    global redis1, user, pref
    try:
        temp_user = context.args[0]
        temp_pref = ' '.join(context.args[1:])
        if redis1.exists(temp_user):
            redis1.set(temp_user, temp_pref)
            update.message.reply_text('User amended.')
        else:
            update.message.reply_text('User does not exist.')
        
        if user == temp_user:
            pref = temp_pref

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /amend <username> <preferences>')

def equiped_chatgpt(update, context):
    global redis1, chatgpt, user, pref

    prompt = ""
    if user and redis1.exists(user):
        # If we have a stored prompt for this user, remind ChatGPT of the preferences
        prompt = f"Remember: I am {user} and I'm interested in {pref}. Please tailor your responses to include information related to {pref} when relevant. Consider my interest in {pref} as you respond to my questions and provide recommendations.\n"
        logging.info("\n !!!!!!!!!!!!prompt triggered!!!!!!!!!!!! \n")
    
    input_text = prompt + update.message.text
    reply_message = chatgpt.submit(input_text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def hello(update, context):
    try:
        logging.info(context.args[0])
        update.message.reply_text(f'Good day, {context.args[0]}!')
    except:
        update.message.reply_text('Usage: /hello <keyword>')

if __name__ == '__main__':
    Thread(target=run_flask).start()
    main()

#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from typing import Dict
import json
import requests as rq

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE, CHOOSING_PLANTS, TYPING_PASS = range(5)

reply_keyboard_menu = [
    ['Log Watering', 'Edit Plants'],
    ['Statistics', 'Account settings'],
    ['Done'],
]
reply_keyboard_plants = [
    ['List plants', 'Add plants'],
    ['Edit a plant', 'Back'],
]
markup_menu = ReplyKeyboardMarkup(reply_keyboard_menu, one_time_keyboard=True)
markup_plants = ReplyKeyboardMarkup(reply_keyboard_plants, one_time_keyboard=True)

conf = json.load(open("config.json"))
is_connection_url = conf["test_connection_url"]

server_down_msg = "Our server is down. Please try again later. We apologize for the inconvenience!"

def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])

def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text(
        "Hi! Welcome to your home plant manager! "
        "Please select what you would like to do!",
        reply_markup=markup_menu,
    )
    return CHOOSING

def regular_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')

    return TYPING_REPLY

def custom_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for a description of a custom category."""
    update.message.reply_text(
        'Alright, please send me the category first, for example "Most impressive skill"'
    )
    return TYPING_CHOICE
    
def is_server_connection(test_connection_url):
    try:
        rq.get(test_connection_url)
    except rq.exceptions.ConnectionError:
        print("ERROR: Server is down.")
        return False
    except:
        print("ERROR: Unknown server error!")
        return False
    return True


def received_information(update: Update, context: CallbackContext) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    # category = user_data['choice']
    # user_data[category] = text
    # del user_data['choice']

    update.message.reply_text(
        "Neat! Just so you know, this is what you already told me:"
        f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
        " on something.",
        reply_markup=markup_menu,
    )
    return CHOOSING

def log_watering(update: Update, context: CallbackContext) -> int:
    """log watering functionality"""
    if is_server_connection(is_connection_url):
        update.message.reply_text(
            "You want to water a plant? Do it!"
        )
        return TYPING_REPLY
    else:
        update.message.reply_text(
        server_down_msg,
        reply_markup=markup_menu,
        )   
        return CHOOSING

def edit_plants(update: Update, context: CallbackContext) -> int:
    """edit plants menu"""
    if is_server_connection(is_connection_url):
        update.message.reply_text(
            "What do you wanna do with your plants?",
            reply_markup=markup_plants,
        )
        return CHOOSING_PLANTS
    else:
        update.message.reply_text(
        server_down_msg,
        reply_markup=markup_menu,
        )   
        return CHOOSING

def edit_a_plant(update: Update, context: CallbackContext) -> int:
    if is_server_connection(is_connection_url):
        update.message.reply_text(
            "You want to edit a plant? Do it!"
        )
        text = update.message.text
        context.user_data['choice'] = text
    else:
        update.message.reply_text(
        server_down_msg,
        reply_markup=markup_menu,
        )   
        return CHOOSING

    return TYPING_REPLY

def add_plants(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    if is_server_connection(is_connection_url):
        update.message.reply_text(
            "You want to add a plant? Do it!"
        )
        text = update.message.text
        context.user_data['choice'] = text
        return TYPING_REPLY
    else: 
        update.message.reply_text(
        server_down_msg,
        reply_markup=markup_menu,
        )   
        return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        "Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END

# def received_username(update: Update, context: CallbackContext) -> int:
#     user_data = context.user_data
#     context.user_data['choice'] = "username"
#     text = update.message.text
#     category = user_data['choice']
#     user_data[category] = text
#     chatid = update.message.chat.id
#     print(chatid)
#     del user_data['choice']

#     update.message.reply_text(
#         "Neat! Just so you know, this is what you already told me:"
#         f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
#         " on something.",
#         reply_markup=markup_menu,
#     )

#     update.message.reply_text(
#         "Now type in your password.")

#     update.message.reply_text(chatid)
#     update.message.reply_text(str(chatid))

#     return TYPING_PASS

# def received_pass(update: Update, context: CallbackContext) -> int:
#     user_data = context.user_data
#     context.user_data['choice'] = "password"
#     text = update.message.text
#     category = user_data['choice']
#     user_data[category] = text
#     del user_data['choice']

#     update.message.reply_text(
#         "Neat! Just so you know, this is what you already told me:"
#         f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
#         " on something.",
#         reply_markup=markup_menu,
#     )

#     r = rq.put("http://127.0.0.1:5000/test", json = {'username': user_data["username"], 'password': user_data["password"]})
#     # r = rq.get("http://127.0.0.1:5000/post")
#     update.message.reply_text(
#         str(r.text)
#     )
#     return CHOOSING

# def auth_username(update: Update, context: CallbackContext) -> int:
#     update.message.reply_text(
#         "Hi, welcome to your plant manager! Please type in your username."
#     )
#     return TYPING_USERNAME

# def auth_pass(update: Update, context: CallbackContext) -> int:
#     id = update.message.chat.id 
#     print(id)
#     update.message.reply_text(
#         "Now type in your password."
#     )
#     return TYPING_PASS
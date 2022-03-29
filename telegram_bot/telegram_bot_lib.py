import logging
from typing import Dict
import json
import requests
import ast

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# from telegram_bot.old_examples.telegram_bot_lib_old import CHOOSING

class TelegramBot:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.CHOOSING, self.TYPING_REPLY, self.TYPING_CHOICE, self.CHOOSING_PLANTS, self.TYPING_PASS, self.EDIT_ADD_PLANT = range(6)
        
        # possible options for user selection
        self.reply_keyboard_menu = [
            ['Log Watering', 'Edit Plants'],
            ['Statistics', 'Account settings'],
            ['Done'],
        ]
        self.reply_keyboard_plants = [
            ['List plants', 'Add plants'],
            ['Edit a plant', 'Back'],
        ]        
        self.markup_menu = ReplyKeyboardMarkup(self.reply_keyboard_menu, one_time_keyboard=True)
        self.markup_plants = ReplyKeyboardMarkup(self.reply_keyboard_plants, one_time_keyboard=True)

        try:
            self.conf = json.load(open("config.json"))
            self.update_conf_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["get_config_url"]
            self.is_connection_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["test_connection_url"]
            self.update_conf()            
        except: 
            print("Initialisation error: Could not update config.")
        try:
            self.is_connection_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["test_connection_url"]
            self.server_down_msg = "Our server is down. Please try again later. We apologize for the inconvenience!"
            self.list_plants_url = self.conf['data_base']["db_url"] + ":" + self.conf['data_base']["port"] + self.conf['data_base']['functions']["get_plant_list_url"]
            self.get_last_id_url = self.conf['data_base']["db_url"] + ":" + self.conf['data_base']["port"] + self.conf['data_base']['functions']["get_last_id_url"]
            self.add_plants_url = self.conf['data_base']["db_url"] + ":" + self.conf['data_base']["port"] + self.conf['data_base']['functions']["add_plant_url"]
            self.plant_keys = self.conf['data_base']['functions']['plant_info']
        except: 
            print("Initialisation error: Could not read from config.")

    def is_server_connection(self):
        try:
            requests.get(self.is_connection_url)
        except requests.exceptions.ConnectionError:
            print("ERROR: Server is down.")
            return False
        except:
            print("ERROR: Unknown server error!" + str(self.is_connection_url))
            return False
        return True

    def update_conf(self):
        if(self.is_server_connection):
            try:
                r = requests.get(self.update_conf_url)
                with open("config.json", "w") as myfile:
                    myfile.write(str(r.text))
            except:
                print("Error: Could not update configs although server is up")
        else: print("Server is down. Could not update configs")
    
    def facts_to_str(self, user_data: Dict[str, str]) -> str:
        """Helper function for formatting the gathered user info."""
        facts = [f'{key} - {value}' for key, value in user_data.items()]
        return "\n".join(facts).join(['\n', '\n'])

    def start(self, update: Update, context: CallbackContext) -> int:
        """Start the conversation and ask user for input."""
        update.message.reply_text(
            "Hi! Welcome to your home plant manager! "
            "Please select what you would like to do!",
            reply_markup= self.markup_menu,
        )
        return  self.CHOOSING

    def regular_choice(self, update: Update, context: CallbackContext) -> int:
        """Ask the user for info about the selected predefined choice."""
        text = update.message.text
        context.user_data['choice'] = text
        update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')

        return  self.TYPING_REPLY

    def custom_choice(self, update: Update, context: CallbackContext) -> int:
        """Ask the user for a description of a custom category."""
        update.message.reply_text(
            'Alright, please send me the category first, for example "Most impressive skill"'
        )
        return  self.TYPING_CHOICE

    def post_json(self, url, json_string):
        try:
            requests.post(url, json = json_string)
        except: 
            print("Error: Could not post.")
            print("url is: " + url)
            print("json is: " + str(json_string))
            return False
        return True

    def get_last_id(self,chat_id):
        return requests.get(self.get_last_id_url + "?chat_id=" + str(chat_id)).text

    def create_json(self,key_list,value_list):
        res = {}
        if len(key_list) == len(value_list):            
            for key in key_list:
                for value in value_list:
                    res[key] = value
                    value_list.remove(value)
                    break 
        else:
            print ("Error in create_json: keys and values must be same length")
        return res

    def received_information(self, update: Update, context: CallbackContext) -> int:
        """Store info provided by user and ask for the next category."""
        user_data = context.user_data
        text = update.message.text
        category = user_data['category']
        if category == "add plant":
            context.user_data["add_plant_info"].append(text)
            if len(context.user_data['add_plant_info']) >= len(self.plant_keys):
                chatid = update.message.chat.id
                id = str(int(self.get_last_id(chatid)) + 1)

                self.plant_keys.insert(0, "id")
                context.user_data["add_plant_info"].insert(0, id)
                json_plant = self.create_json(self.plant_keys, context.user_data["add_plant_info"])
                temp = self.add_plants_url

                if self.post_json(self.add_plants_url, json_plant) == True:
                    print("Sending")
                    msg = "That plant is now added: \n" + self.beautify_json(json_plant)
                else: msg = "Something went wrong with adding plant: \n" + self.beautify_json(json_plant)
                
                update.message.reply_text(msg, reply_markup= self.markup_menu)
                    
                del context.user_data['category']
                del context.user_data['add_plant_info']

                return self.CHOOSING
            else:       
                plant_key = self.plant_keys[len(user_data['add_plant_info'])]
                update.message.reply_text("What is the " + plant_key + "?")
                return self.TYPING_REPLY
                


        # user_data[category] = text
        # del user_data['choice']

        # update.message.reply_text(
        #     "Neat! Just so you know, this is what you already told me:"
        #     f"{ self.facts_to_str(user_data)} You can tell me more, or change your opinion"
        #     " on something.",
        #     reply_markup= self.markup_menu,
        # )
        return  self.CHOOSING_PLANTS

    def log_watering(self, update: Update, context: CallbackContext) -> int:
        """log watering functionality"""
        if  self.is_server_connection():
            update.message.reply_text(
                "You want to water a plant? Do it!"
            )
            return  self.TYPING_REPLY
        else:
            update.message.reply_text(
            self.server_down_msg,
            reply_markup= self.markup_menu,
            )   
            return self.CHOOSING

    def edit_plants(self, update: Update, context: CallbackContext) -> int:
        """edit plants menu"""
        if self.is_server_connection():
            update.message.reply_text(
                "What do you wanna do with your plants?",
                reply_markup=self.markup_plants,
            )
            return self.CHOOSING_PLANTS
        else:
            update.message.reply_text(
            self.server_down_msg,
            reply_markup=self.markup_menu,
            )   
            return self.CHOOSING

    def edit_a_plant(self, update: Update, context: CallbackContext) -> int:
        if self.is_server_connection():
            update.message.reply_text(
                "You want to edit a plant? Do it!"
            )
            text = update.message.text
            context.user_data['choice'] = text

            # user_data = context.user_data
            # context.user_data['choice'] = 
            # text = update.message.text
            # category = user_data['choice']
            # user_data[category] = text
            # del user_data['choice']
            
        else:
            update.message.reply_text(
            self.server_down_msg,
            reply_markup=self.markup_menu,
            )   
            return self.CHOOSING

        return self.TYPING_REPLY

    def add_plants(self, update: Update, context: CallbackContext) -> int:
        """Start the conversation and ask user for input."""
        if self.is_server_connection():
            # text = update.message.text
            # user_data = context.user_data        
            update.message.reply_text("What is the plant species?")
            context.user_data['add_plant_info'] = []
            context.user_data['category'] = "add plant"
            return self.TYPING_REPLY
            
                
            
            # context.user_data['choice'] = 
            # text = update.message.text
            # category = user_data['choice']
            # user_data[category] = text
            # del user_data['choice']
            
            return self.TYPING_REPLY
        else: 
            update.message.reply_text(
            self.server_down_msg,
            reply_markup=self.markup_menu,
            )   
            return self.CHOOSING

    def get_plant_list(self, chat_id):
        r = requests.get(self.list_plants_url + "?chat_id=" + str(chat_id)).text
        r = r[r.find("[")+1:r.rfind("]")]
        r = r[0:r.rfind("}")].split("},")
        plant_list = []
        for plant in r:
            plant_list.append(ast.literal_eval((plant[plant.find("{"):] + "}")))
        return plant_list        
        

    def beautify_json(self,plant_dict_string):
        keys = plant_dict_string.keys()
        string = ""

        for key in keys:
            string += (str(key) + ": " + str(plant_dict_string[key]) + "\n")

        return string

    def list_plants(self, update: Update, context: CallbackContext) -> int:
        """Start the conversation and ask user for input."""
        if self.is_server_connection():
            update.message.reply_text("Here are your plants")
            chatid = update.message.chat.id
            plant_list = self.get_plant_list(chatid)
            for plant in plant_list:
                a = self.beautify_json(plant)
                update.message.reply_text(a)
            update.message.reply_text("What now?", reply_markup=self.markup_plants)
            return self.CHOOSING_PLANTS
        else: 
            update.message.reply_text(
            self.server_down_msg,
            reply_markup=self.markup_menu,
            )   
            return self.CHOOSING


    def done(self, update: Update, context: CallbackContext) -> int:
        user_data = context.user_data
        if 'choice' in user_data:
            del user_data['choice']

        update.message.reply_text(
            "Until next time!",
            reply_markup=ReplyKeyboardRemove(),
        )

        user_data.clear()
        return ConversationHandler.END



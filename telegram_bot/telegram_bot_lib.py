import logging
from typing import Dict
import json
import requests
import ast
from datetime import date

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

        self.LOG_WATERING, self.CHOOSING, self.TYPING_REPLY, self.TYPING_CHOICE, self.CHOOSING_PLANTS, self.TYPING_PASS, self.EDIT_ADD_PLANT = range(7)
        
        # possible options for user selection
        self.reply_keyboard_menu = [
            ['Log Watering', 'Your Plants'],
            ['Statistics', 'Done'],
        ]
        self.reply_keyboard_plants = [
            ['List plants', 'Add plants'],
            ['Edit a plant', 'Delete a plant'],
            ['Back']
        ]
        self.reply_keyboard_watering = [
            ['Watered now', 'Watered in the past'],
            ['Back']
        ]          
        self.markup_menu = ReplyKeyboardMarkup(self.reply_keyboard_menu, one_time_keyboard=True)
        self.markup_plants = ReplyKeyboardMarkup(self.reply_keyboard_plants, one_time_keyboard=True)
        self.markup_watering = ReplyKeyboardMarkup(self.reply_keyboard_watering, one_time_keyboard=True)

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
            self.delete_plant_url = self.conf['data_base']["db_url"] + ":" + self.conf['data_base']["port"] + self.conf['data_base']['functions']["delete_plant_url"]
            self.plant_keys = self.conf['data_base']['functions']['plant_info_from_user']
            self.extra_plant_data = self.conf['data_base']['functions']['plant_info_auto']
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
    


    def start(self, update: Update, context: CallbackContext) -> int:
        """Start the conversation and ask user for input."""
        update.message.reply_text(
            "Hi! Welcome to your home plant manager! "
            "Please select what you would like to do!",
            reply_markup= self.markup_menu,
        )
        return  self.CHOOSING


    def rest_post_json(self, url, json_string, chatid):
        try:
            r = requests.post(url + "?chat_id="+str(chatid), json = json_string)
            if r.ok: return True
            else:
                print("Error: The data base server ran into an error") 
                return False
        except: 
            print("Error: Could not post.")
            print("url is: " + url)
            print("json is: " + str(json_string))
            return False

    def rest_get_last_id(self,chat_id):
        return requests.get(self.get_last_id_url + "?chat_id=" + str(chat_id)).text

    def rest_delete_plant(self, chat_id, plant_id):
        return requests.delete(self.delete_plant_url + "?chat_id=" + str(chat_id) + "&plant_id=" + str(plant_id))

    def create_json(self,key_list,value_list):
        res = {}
        try:
            if len(key_list) == len(value_list):            
                for key in key_list:
                    for value in value_list:
                        res[key] = value
                        value_list.remove(value)
                        break 
            else:
                print ("Error in create_json: keys and values must be same length")
        except:
            print("Error: Could not convert to json in 'create_json'")
        return res

    def add_auto_data_to_dict(self,json_dict):
        for dict in self.extra_plant_data:
            json_dict.update(dict)
        return json_dict

    def received_information(self, update: Update, context: CallbackContext) -> int:
        """Store info provided by user and ask for the next category."""
        user_data = context.user_data
        text = update.message.text
        category = user_data['category']
        if category == "add plant":
            context.user_data["add_plant_info"].append(text)
            if len(context.user_data['add_plant_info']) >= len(self.plant_keys):
                chatid = update.message.chat.id
                id = str(int(self.rest_get_last_id(chatid)) + 1)
                keys = self.plant_keys[:] # [:] is needed so a copy is created without linking
                keys.insert(0, "id")
                values = context.user_data["add_plant_info"][:] # [:] is needed so a copy is created without linking
                values.insert(0, id)
                json_plant = self.create_json(keys, values)
                json_plant = self.add_auto_data_to_dict(json_plant)
                if self.rest_post_json(self.add_plants_url, json_plant, chatid) == True:
                    msg = "That plant is now added: \n" + self.beautify_json(json_plant)
                else: msg = "Something went wrong with adding plant: \n" + self.beautify_json(json_plant)
                
                update.message.reply_text(msg, reply_markup= self.markup_menu)
                    
                del context.user_data['category']
                del context.user_data['add_plant_info']

                return self.CHOOSING
            else:       
                plant_key = self.plant_keys[len(user_data['add_plant_info'])]
                if plant_key == "room":
                    update.message.reply_text("In which " + plant_key + " is the plant?")
                else:
                    update.message.reply_text("What is the " + plant_key + "?")
                return self.TYPING_REPLY

        elif category == "delete plant":
            chatid = update.message.chat.id
            try:
                r = self.rest_delete_plant(chatid, text)
                if r.ok:
                    msg = "Plant number " + str(text) + " is deleted."
                else:
                    msg = "Could not delete plant number " + str(text) + "."
            except:
                msg = "Error deleting plant number " + str(text) + "."
                print(msg)
            update.message.reply_text(msg, reply_markup= self.markup_menu)
            return self.CHOOSING
        elif category == "water":
            pass
        elif category == "water past":
            update.message.reply_text(
            "Which plants did you water? Enter the Plant IDs, separated by comma ',' for example: 1,5,8")
            context.user_data['category'] = "water"
            context.user_data['date'] = text
            return  self.TYPING_REPLY
            
                
        return  self.CHOOSING_PLANTS

    def log_watering(self, update: Update, context: CallbackContext) -> int:
        """log watering functionality"""
        update.message.reply_text(
        "You watered your plants! That should keep them alive.")
        update.message.reply_text("You have two options: Log watering that you did today or in the past",
        reply_markup= self.markup_watering,
        )
        return  self.LOG_WATERING

    def watered_now(self, update: Update, context: CallbackContext) -> int:
        if  self.is_server_connection():
            today = date.today()
            update.message.reply_text(
            "Which plants did you just water? Enter the Plant IDs, separated by comma ',' for example: 1,5,8")
            context.user_data['category'] = "water"
            context.user_data['date'] = today.strftime("%d/%m/%Y")
            return  self.TYPING_REPLY
        else:
            update.message.reply_text(
            self.server_down_msg,
            reply_markup= self.markup_menu,
            )   
            return self.CHOOSING
    
    def watered_past(self, update: Update, context: CallbackContext) -> int:
        if  self.is_server_connection():
            update.message.reply_text(
            "When did you water your plants? Enter in format dd/mm/yyyy, for example 22.02.2022")
            context.user_data['category'] = "water past"
            return  self.TYPING_REPLY
        else:
            update.message.reply_text(
            self.server_down_msg,
            reply_markup= self.markup_menu,
            )   
            return self.CHOOSING

    def your_plants(self, update: Update, context: CallbackContext) -> int:
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
            "Hi! That functionality is not available yet...",
            reply_markup= self.markup_menu,
            )
            return  self.CHOOSING

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

    def add_plants(self, update: Update, context: CallbackContext) -> int:
        """Start the conversation and ask user for input."""
        if self.is_server_connection():       
            update.message.reply_text("What is the plant species?")
            context.user_data['add_plant_info'] = []
            context.user_data['category'] = "add plant"
            return self.TYPING_REPLY
        else: 
            update.message.reply_text(
            self.server_down_msg,
            reply_markup=self.markup_menu,
            )   
            return self.CHOOSING

    def get_plant_list(self, chat_id):
        r = requests.get(self.list_plants_url + "?chat_id=" + str(chat_id))
        plant_list = []
        success = False
        if r.ok:    
            success = True
            r = r.text    
            r = r[r.find("[")+1:r.rfind("]")]
            if bool(r):            
                r = r[0:r.rfind("}")].split("},")           
                for plant in r:
                    plant_list.append(ast.literal_eval((plant[plant.find("{"):] + "}")))       
        else:
            print("Getting the plant list resulted in Error 500")
        return [plant_list, success] 

    def beautify_json(self,plant_dict_string):
        keys = plant_dict_string.keys()
        string = ""

        for key in keys:
            string += (str(key) + ": " + str(plant_dict_string[key]) + "\n")

        return string

    def list_plants(self, update: Update, context: CallbackContext) -> int:
        """Start the conversation and ask user for input."""
        if self.is_server_connection():
            chatid = update.message.chat.id
            [plant_list, success] = self.get_plant_list(chatid)
            if success:
                if bool(plant_list): 
                    update.message.reply_text("Here are your plants")                
                    for plant in plant_list:
                        for extra_dict in self.extra_plant_data:
                            del(plant[list(extra_dict.keys())[0]])
                        update.message.reply_text(self.beautify_json(plant))
                else:
                    update.message.reply_text("You got no plants! Add some!")
            else:
                update.message.reply_text("Something went wrong. We can't get you your plants. Try later!")
            update.message.reply_text("What now?", reply_markup=self.markup_plants)
            return self.CHOOSING_PLANTS
        else: 
            update.message.reply_text(
            self.server_down_msg,
            reply_markup=self.markup_menu,
            )   
            return self.CHOOSING
    
    def delete_a_plant(self, update: Update, context: CallbackContext) -> int:
        if self.is_server_connection():    
            self.list_plants
            update.message.reply_text("Which plant do you want to delete? \n Type the id of the plant you want to delete.")
            context.user_data['category'] = "delete plant"
            return self.TYPING_REPLY
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


    # def regular_choice(self, update: Update, context: CallbackContext) -> int:
    #     """Ask the user for info about the selected predefined choice."""
    #     text = update.message.text
    #     context.user_data['choice'] = text
    #     update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')

    #     return  self.TYPING_REPLY

    # def custom_choice(self, update: Update, context: CallbackContext) -> int:
    #     """Ask the user for a description of a custom category."""
    #     update.message.reply_text(
    #         'Alright, please send me the category first, for example "Most impressive skill"'
    #     )
    #     return  self.TYPING_CHOICE
    # def facts_to_str(self, user_data: Dict[str, str]) -> str:
    #     """Helper function for formatting the gathered user info."""
    #     facts = [f'{key} - {value}' for key, value in user_data.items()]
    #     return "\n".join(facts).join(['\n', '\n'])

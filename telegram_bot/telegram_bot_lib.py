import logging
from typing import Dict
import json
import requests
import ast
from datetime import date
from datetime import datetime


from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# class with all functions for interacting with the telegram bot
class TelegramBot:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # states to be used by the Conversation Handler from the python-telegram-bot library
        self.LOG_WATERING, self.CHOOSING, self.TYPING_REPLY, self.TYPING_CHOICE, self.CHOOSING_PLANTS, self.TYPING_PASS, self.EDIT_ADD_PLANT = range(7)
        
        # possible options for user selection in the main menu
        self.reply_keyboard_menu = [
            ['Log Watering', 'Your Plants'],
            ['Statistics', 'Done'],
        ]
        # possible options for user selection in the plants menu
        self.reply_keyboard_plants = [
            ['List plants', 'Add plants'],
            ['Edit a plant', 'Delete a plant'],
            ['Back']
        ]
        # possible options for user selection in the watering menu
        self.reply_keyboard_watering = [
            ['Watered now', 'Watered in the past'],
            ['Back']
        ]          
        self.markup_menu = ReplyKeyboardMarkup(self.reply_keyboard_menu, one_time_keyboard=True)
        self.markup_plants = ReplyKeyboardMarkup(self.reply_keyboard_plants, one_time_keyboard=True)
        self.markup_watering = ReplyKeyboardMarkup(self.reply_keyboard_watering, one_time_keyboard=True)

        try:
            # get necessary data before updating the configuration file
            self.conf = json.load(open("config.json"))
            self.update_conf_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["get_config_url"]
            self.is_connection_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["test_connection_url"]    
        except: 
            print("Initialisation error: could not open config.")
        try:
            self.update_conf() 
        except:
            print("Initialisation error: Could not update config.")

        try:
            # extract data from the config
            self.is_connection_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["test_connection_url"]
            self.all_plants_url = self.conf['data_base']["db_url"] + ":" + self.conf['data_base']["port"] + self.conf['data_base']['endpoints']["all_plants_of_user_id"]
            self.one_plant_url = self.conf['data_base']["db_url"] + ":" + self.conf['data_base']["port"] + self.conf['data_base']['endpoints']["plant_id_of_user_id"]

            self.plant_keys = self.conf['data_base']['functions']['plant_info_from_user']
            self.extra_plant_data = self.conf['data_base']['functions']['plant_info_auto']
            self.server_down_msg = "Our server is down. Please try again later. We apologize for the inconvenience!"
        except: 
            print("Initialisation error: Could not read from config.")

    # function for checking if there is connection with the service catalogue
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

    # function for replacing the config file with the newest version of it
    def update_conf(self):
        if(self.is_server_connection):
            try:
                r = requests.get(self.update_conf_url)
                with open("config.json", "w") as myfile:
                    myfile.write(str(r.text))
            except:
                print("Error: Could not update configs although server is up")
        else: print("Server is down. Could not update configs")
    
    ################## TELEGRAM FUNCTIONS ############################

    # triggered when /start is written by user. 
    def start(self, update: Update, context: CallbackContext) -> int:
        """Start the conversation and ask user for input."""
        update.message.reply_text(
            "Hi! Welcome to your home plant manager! "
            "Please select what you would like to do!",
            reply_markup= self.markup_menu, # the user buttons in the chat defined by markum_menu
        )
        return  self.CHOOSING # following that is the menu for choosing from the main menu

    # handles typed in information from user based on "category"
    def received_information(self, update: Update, context: CallbackContext) -> int:
        """Store info provided by user and ask for the next category."""
        user_data = context.user_data 
        text = update.message.text # get input data from user
        category = user_data['category']

        ####### Handle the input text based on what its category is #####
        ### ADDING PLANTS 
        if category == "add plant":
            context.user_data["add_plant_info"].append(text) # save the input

            # if the user has added all the reqired plant info, then proceed to sending the plant info to the DB
            if len(context.user_data['add_plant_info']) >= len(self.plant_keys):
                chatid = update.message.chat.id
                # [id, success] = self.rest_get_last_id(chatid)
                # id = str(int(id)+1)
                keys = self.plant_keys[:] # [:] is needed so a copy is created without linking
                # keys.insert(0, "id")
                values = context.user_data["add_plant_info"][:] # [:] is needed so a copy is created without linking
                # values.insert(0, id)
                json_plant = self.create_json(keys, values)
                json_plant = self.add_auto_data_to_dict(json_plant) # add the default data, such as "watered: []"
                
                # posting the plant to the DB
                if self.rest_post_plant(json_plant, chatid):
                    msg = "That plant is now added: \n" + self.beautify_json(json_plant)
                else: msg = "Something went wrong with adding plant: \n" + self.beautify_json(json_plant)
                
                update.message.reply_text(msg, reply_markup= self.markup_menu)
                
                # task is done, so clear all the used temp data
                del context.user_data['category']
                del context.user_data['add_plant_info']

                return self.CHOOSING # go back to main menu

            # if the user hasn't added all the info yet, proceed to asking for more data
            else:       
                plant_key = self.plant_keys[len(user_data['add_plant_info'])]
                if plant_key == "room":
                    update.message.reply_text("In which " + plant_key + " is the plant?")
                else:
                    update.message.reply_text("What is the " + plant_key + "?")
                return self.TYPING_REPLY

        ### DELETING PLANTS 
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

        ### WATERING PLANTS
        # If the date of the watering is known already
        elif category == "water":
            plants_ids_str = text.replace(" ", "")
            plant_ids_list = plants_ids_str.split(",")
            watered_plants = []
            try:
                for plant_id in plant_ids_list:
                    r = self.get_plant(update.message.chat.id, str(int(plant_id)))
                    if r.ok:
                        watered_plants.append(json.loads(r.text))
                    else:
                        update.message.reply_text("Could not get plant with Plant_id" + str(plant_id) + ". Try again later.", self.markup_menu)
                        return self.CHOOSING

            except ValueError:
                update.message.reply_text("Input was not numbers, separated by commas. Enter the watered plant IDs, separated by comma ',' for example: 1,5,8")
                context.user_data['category'] = "water"
                return self.TYPING_REPLY
            except:
                print("Something went wrong with watering a plant. Try again later.")
                update.message.reply_text("Something went wrong with watering plants. Try again later.", self.markup_menu)
                return self.CHOOSING


            try:
                # watered_plants is now a list of dictionaries with plants. 
                water_date = context.user_data['date']
                
                for plant in watered_plants:
                    temp_plant = plant
                    temp_plant['watered'] = temp_plant['watered'].append(water_date)                
                    r = self.put_plant(update.message.chat.id, temp_plant['id'], json.loads(temp_plant))
                    if not r.ok:
                        update.message.reply_text("Could not update watering, Try again later.", self.markup_menu)
                        return self.CHOOSING
            except:
                update.message.reply_text("Something went wrong. Could not update plant watering", self.markup_menu)
                return self.CHOOSING
                
            update.message.reply_text("Plant watering complete!", self.markup_menu)
            return self.CHOOSING

        # If the watering date was in the past, and needs to be saved
        elif category == "water past":
            format = "%d/%m/%Y"
            try:
                datetime.strptime(text, format)
            except ValueError:
                # if format is incorrect, let user try again.
                update.message.reply_text("Incorrect date format. Enter watering date in format dd/mm/yyyy, for example 22.02.2022")
                context.user_data['category'] = "water past"
                return  self.TYPING_REPLY   

            context.user_data['date'] = text
            update.message.reply_text(
            "Which plants did you water? Enter the Plant IDs, separated by comma ',' for example: 1,5,8")
            context.user_data['category'] = "water"
            return  self.TYPING_REPLY           
                
        return  self.CHOOSING_PLANTS # 

    # function for the user to choose between logging a watering from today or from the past.
    def log_watering(self, update: Update, context: CallbackContext) -> int:
        """log watering functionality"""
        update.message.reply_text(
        "You watered your plants! That should keep them alive.")
        update.message.reply_text("You have two options: Log watering that you did today or in the past",
        reply_markup= self.markup_watering,
        )
        return  self.LOG_WATERING

    # If the user chooses to log watering from today, the date is known, so we only need the plant IDs
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
    
    # If the user chooses to log watering from the past, the date is unknown, so we need to ask him about it
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

    # your plants menu
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


    # if user chooses "edit a plant" from the plant menu
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

    # if user chooses "add a plant" from the plant menu
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

    # if user chooses "list plants" from the plant menu
    def list_plants(self, update: Update, context: CallbackContext) -> int:
        """Start the conversation and ask user for input."""
        if self.is_server_connection():
            chatid = update.message.chat.id
            [plant_list, success] = self.rest_get_plant_list(chatid)
            # if getting the plant list was succesful
            if success: 
                if bool(plant_list): 
                    update.message.reply_text("Here are your plants")                
                    for plant in plant_list:
                        # list plants without the extra unnecesary data (such as watering logs)
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
    
    # if user chooses "delete a plant" from the plant menu
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

    # if user at anu points writes "Done", then the chat is being closed.
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

###################### REST METHODS ###########################

    # send a "get" request to get all plants of a user
    def rest_get_plant_list(self, chat_id):
        success = False
        plant_list = []
        url = self.set_correct_url(self.all_plants_url, [chat_id])
        r = requests.get(url)
        if r.ok and str(chat_id) in url:    
            success = True
            r = r.text
            plant_list = list(ast.literal_eval(r)) # convert string to list of dictionaries
        else:
            print("Getting the plant list resulted in some error")
        return [plant_list, success] 

    # send a "post" request to a url, where querry is chat_id and payload is a json_string
    def rest_post_plant(self, json_string, chat_id):
        try:
        #     query = "?"
        #     for key in params_dict:
        #         if len(query) > 1:  query+= "&"
        #         query += str(key) + "=" + str(params_dict[key])
            url = self.set_correct_url(self.all_plants_url, [chat_id])
            r = requests.post(url, json = json_string)
            if r.ok: return True
            else:
                print("Error: Posting data to server ended up in an error") 
                return False
        except: 
            print("Error: Could not post.")
            print("url is: " + url)
            print("json is: " + str(json_string))
            return False

    # send a "delete" request for deleting plant by plant_id and chat_id
    def rest_delete_plant(self, chat_id, plant_id):
        url = self.set_correct_url(self.one_plant_url, [chat_id, plant_id])
        return requests.delete(url)

    def get_plant(self, chat_id, plant_id):
        url = self.set_correct_url(self.one_plant_url, [chat_id, plant_id])
        return requests.get(url)
    
    def put_plant(self, chat_id, plant_id, json_string):
        url = self.set_correct_url(self.one_plant_url, [chat_id, plant_id])
        return requests.get(url, json = json_string)
    
    ###################### AUXILIARY METHODS ####################

    # replaces <user_id> and <plant_id> from the url with the correct values
    def set_correct_url(self, url, list_of_vars):
        res = str(url)
        for var in list_of_vars:
            start = res.find("<")
            end = res.find(">")+1
            if start != -1 and end != -1:
                res = res.replace(res[start:end], str(var))
            else:
                print("Warning: in set_correct_url, expected more '<' or '>' in base url")
        return res

    # takes a dictionary and makes in representable form for the user
    def beautify_json(self,plant_dict_string):
        keys = plant_dict_string.keys()
        string = ""

        for key in keys:
            string += (str(key) + ": " + str(plant_dict_string[key]) + "\n")

        return string

    # creates a json from a list of keys and a list of values
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


    # takes as input a json dictionary and adds to it the default data key-value pairs (such as "watered: []")
    def add_auto_data_to_dict(self,json_dict):
        for dict in self.extra_plant_data:
            json_dict.update(dict)
        return json_dict

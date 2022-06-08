from hashlib import new
from flask import Flask, jsonify, abort
from flask import request as rq
import requests
import json
from markupsafe import escape
import pymongo

class myPlants:
    def __init__(self):
        # self.plants = json.load(open("plants.json"))
        self.config = json.load(open("config.json"))

        try:
            self.conf = json.load(open("config.json"))
            self.update_conf_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["get_config_url"]
            self.update_conf()
            self.is_connection_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["test_connection_url"]
            self.server_down_msg = "Our server is down. Please try again later. We apologize for the inconvenience!"
            self.db_server = [self.conf['data_base']["db_url"],self.conf['data_base']["port"]]       
            self.mongodb_user = self.conf['data_base']["mongodb_user"]       
            self.mongodb_pass = self.conf['data_base']["mongodb_pass"]
            self.mongodb_db_name = self.conf['data_base']["mongodb_db_name"]
        except: 
            print("Initialisation error: Could not read from config.")

        try:
            self.client = pymongo.MongoClient("mongodb+srv://" + str(self.mongodb_user) + ":" + str(self.mongodb_pass) + "@cluster0.o8rmbp3.mongodb.net/?retryWrites=true&w=majority")
            self.client.test
            self.db = self.client[str(self.mongodb_db_name)]
        except:
            print("Could not establish connection to the database.")

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

    def get_user_plants_json(self, chat_id):
        mycol = self.db[chat_id]
        plant_list_str = []
        for x in mycol.find({},{ "_id": 0 }):
            plant_list_str.append(x)
        return plant_list_str

    def get_plant_db(self, user_id, plant_id):
        myquery = { "id": plant_id }
        mycol = self.db[user_id]
        mydoc = mycol.find(myquery,{ "_id": 0 })
        for x in mydoc:
            print(x)
            return x

    def insert_plant_db(self, user_id, plant_dict):
        try:
            mycol = self.db[user_id]
            mydict = plant_dict
            x = mycol.insert_one(mydict)
        except:
            print("error 500: Something went wrong with inserting a plant.")
            abort(500)
        return True

    def replace_plant_db(self,replace_plant_index, user_id, plant_dict):
        try:
            myquery = { "id": replace_plant_index }
            mycol = self.db[user_id]
            mycol.replace_one(myquery, plant_dict)
        except:
            print("error 500: Something went wrong with replacing a plant.")
            abort(500)
        return True

    def delete_plant_db(self, user_id,plant_id):
        mycol = self.db[user_id]

        plant = self.get_plant_db(user_id,plant_id)
        if plant != None:
            myquery = { "id": plant_id }
            mycol.delete_one(myquery)
            return True
        else:
            return False


app = Flask(__name__)
my_plants = myPlants()
db_host = my_plants.db_server[0].replace("http://","",1)
db_port = my_plants.db_server[1]
print(db_host + db_port)

@app.route(my_plants.conf['data_base']['endpoints']['all_plants_of_user_id'], methods=['GET', 'POST'])
def plants(user_id):
    #### List plants 
    if rq.method == 'GET':
        try:
            chat_id = user_id
            plant_list = my_plants.get_user_plants_json(chat_id)
            print(plant_list)
        except:
            print("error 500: Something went wrong with listing plants.")
            abort(500)
        return str(plant_list)

    #### Add plants 
    elif rq.method == 'POST':
        print("Attempting to add a new plant...")
        try:
            chat_id = user_id
            my_plants.get_user_plants_json(chat_id)
        except KeyError:
            print("error 500: invalid chat id.")
            abort(500)
        except:
            print("error 500: Something went wrong with adding plants")
            abort(500)
        try:
            plant = rq.json
            print(plant)
        except:
            print("error 500: Something went wrong with the json while adding plants.")
            abort(500)

        try:
            if my_plants.get_user_plants_json(chat_id) == []:
                last_plant_id = "0"
            else:
                last_plant_id = my_plants.get_user_plants_json(chat_id)[-1]['id']
            print(last_plant_id)
            plant['id'] = str(int(last_plant_id) + 1)
        except:
            print("error 500: Could not assign an id to plant.")
            abort(500)

        if type(plant)== dict:
            if my_plants.insert_plant_db(chat_id, plant): print("New plant added!")
        else:
            print( "error 500: Input was not a dict")
            abort(500)

        return "True"


@app.route(my_plants.conf['data_base']['endpoints']['plant_id_of_user_id'], methods=['GET','PUT','DELETE'])
def one_plant(user_id,plant_id):
    
    all_plants = my_plants.get_user_plants_json(user_id)
    # print(all_plants)
    # get a plant by id
    if rq.method == 'GET':
        plant = my_plants.get_plant_db(user_id,plant_id)
        if  plant == None:
            print("The plant id was not found")
            abort(404)
        else:
            return plant
        
                    
    # deleting a plant
    elif rq.method == 'DELETE':
        try:
            if not my_plants.delete_plant_db(user_id,plant_id):
                print("No plant with this plant id.")
                abort(500)
        except:
            print("Something went wrong with deleting a plant")
            abort(500)
        return "True"

    elif rq.method == 'PUT':
        try:
            new_plant = json.loads(rq.json)
            new_plant_id = new_plant['id']
            if plant_id != new_plant_id:
                print("Error: inconsisten plant_id")
                abort(400)
        except:
            print('The new plant does not have an id or is not a json')
            abort(400)

        replace_plant_index = -1

        try:
        # find plant index
            for count, plant in enumerate(all_plants):
                if plant['id'] == plant_id:
                    replace_plant_index = count
                    break
            # replace plant
            if type(new_plant) is dict and replace_plant_index >= 0:
                my_plants.replace_plant_db(replace_plant_index, user_id,new_plant)
                return "True"
            else:
                print("The new plant is not a json or there was an issue with the index")
                abort(500)
        except:
            print("Something went wrong with updating a plant.")
            abort(500)

if __name__ == '__main__':
    app.run(host=db_host, port=db_port)
    
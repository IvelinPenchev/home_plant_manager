from hashlib import new
from flask import Flask, jsonify, abort
from flask import request as rq
import requests
import json
from markupsafe import escape

class myPlants:
    def __init__(self):
        self.plants = json.load(open("plants.json"))
        self.config = json.load(open("config.json"))

        try:
            self.conf = json.load(open("config.json"))
            self.update_conf_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["get_config_url"]
            self.update_conf()
            self.is_connection_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["test_connection_url"]
            self.server_down_msg = "Our server is down. Please try again later. We apologize for the inconvenience!"
            self.db_server = [self.conf['data_base']["db_url"],self.conf['data_base']["port"]]       
        except: 
            print("Initialisation error: Could not read from config.")
    
    def update_plants(self):
        self.plants = json.load(open("plants.json"))

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

    def get_plants_json(self, chat_id):
        self.update_plants()
        return str(self.plants[chat_id]["plants"])

    def create_user_if_not_exist(self, chat_id):
        self.update_plants()
        if len(chat_id) > 4:
            try:
                self.plants[chat_id]
            except KeyError:
                with open('plants.json', 'r+') as f:
                    all_plants = json.load(f)
                    all_plants[chat_id] = {}
                    all_plants[chat_id]["plants"] = []
                    f.seek(0)
                    json.dump(all_plants, f, indent=4)
                    f.truncate()     # remove remaining part
                my_plants.update_plants()

    

app = Flask(__name__)
my_plants = myPlants()
db_host = my_plants.db_server[0].replace("http://","",1)
db_port = my_plants.db_server[1]
print(db_host + db_port)

@app.route(my_plants.conf['data_base']['endpoints']['all_plants_of_user_id'], methods=['GET', 'POST'])
def plants(user_id):
    #### List plants 
    if rq.method == 'GET':
        my_plants.update_plants()
        try:
            # chat_id = rq.args.get('chat_id')
            chat_id = user_id
            my_plants.create_user_if_not_exist(chat_id)
            list = my_plants.get_plants_json(chat_id)
        except:
            print("error 500: Something went wrong with listing plants.")
            abort(500)
        return str(list)

    #### Add plants 
    elif rq.method == 'POST':
         my_plants.update_plants()
    print("Attempting to add a new plant...")
    try:
        chat_id = user_id
        my_plants.create_user_if_not_exist(chat_id)
        my_plants.get_plants_json(chat_id)
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
        if not bool(my_plants.plants[chat_id]["plants"]): return str(0)
        last_plant_id = my_plants.plants[chat_id]["plants"][-1]['id']
        plant['id'] = last_plant_id + 1
    except:
        print("error 500: Could not assign an id to plant.")
        abort(500)

    if plant is dict or type(plant)== dict:
        with open('plants.json', 'r+') as f:
            all_plants = json.load(f)
            all_plants[chat_id]["plants"].append(plant)
            f.seek(0)
            json.dump(all_plants, f, indent=4)
            f.truncate()     # remove remaining part
        print("New plant added!")
    else:
        print( "error 500: Input was not a dict")
        abort(500)

    return "True"


@app.route(my_plants.conf['data_base']['endpoints']['plant_id_of_user_id'], methods=['GET','PUT','DELETE'])
def one_plant(user_id,plant_id):
    
    my_plants.update_plants()
    all_plants = my_plants.plants

    # get a plant by id
    if rq.method == 'GET':
        for plant in all_plants:
            if str(plant['id']) == str(plant_id):
                return str(plant)
        print("The plant id was not found")
        abort(404)
                    
    # deleting a plant
    elif rq.method == 'DELETE':
        try:
            with open('plants.json', 'r+') as f:
                all_plants = json.load(f)
                list = all_plants[user_id]["plants"]
                success = False
                for count, dict in enumerate(list):
                    if dict['id'] == plant_id:
                        del all_plants[user_id]["plants"][count]
                        success = True
                        break
                f.seek(0)
                json.dump(all_plants, f, indent=4)
                f.truncate()     # remove remaining part
            if not success: 
                print("Could not delete that plant from that user.")
                abort(404)
        except:
            print("Something went wrong with deleting a plant")
            abort(500)
        return "True"

    elif rq.method == 'PUT':
        try:
            new_plant = rq.json
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
            if (new_plant is dict or type(new_plant)== dict) and replace_plant_index >= 0:
                with open('plants.json', 'r+') as f:
                    all_plants[user_id]["plants"][replace_plant_index] = new_plant
                    f.seek(0)
                    json.dump(all_plants, f, indent=4)
                    f.truncate()
            else:
                print("The new plant is not a json or there was an issue with the index")
                abort(500)
        except:
            print("Something went wrong with updating a plant.")
            abort(500)

# @app.route(my_plants.conf['data_base']['endpoints']['plant_id_of_user_id'], methods=['PUT'])
# def log_watering():
#     pass

# @app.route("/users/<user>/plant/<plant>", methods=['GET'])
# def Test(user,plant):
#     return f'User {escape(user)} and {escape(plant)}'

# @app.route("/users/<user>", methods=['GET'])
# def Test_2(user):
#     return f'User {escape(user)}'

if __name__ == '__main__':
    app.run(host=db_host, port=db_port)
    